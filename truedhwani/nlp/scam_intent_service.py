import time
import logging
from dataclasses import dataclass, field
import numpy as np
from transformers import pipeline

from truedhwani.config import settings, MODELS_CACHE_DIR
from truedhwani.nlp.scam_categories import SCAM_CATEGORIES, ScamCategory

logger = logging.getLogger(__name__)


@dataclass
class ScamIntentResult:
    """Structured result from Scam Intent Analysis."""
    intent_label: str
    scam_intent_score: float  # [0.0, 1.0]
    confidence: float
    explanation: str
    category_scores: dict[str, float] = field(default_factory=dict)
    matched_signals: list[str] = field(default_factory=list)
    latency_ms: float = 0.0


class ScamIntentService:
    """
    Transformer-based Scam Intent Classifier with Hybrid Lexical-Semantic Grounding.
    Evaluates transcript semantics using zero-shot Natural Language Inference (NLI)
    combined with contextual scam keyword & coercion pattern detection.
    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ):
        self.model_name = model_name or settings.scam_intent.model_name
        self.device = device or settings.scam_intent.device
        device_idx = 0 if self.device == "cuda" else -1

        logger.info(f"Loading Scam Intent NLI model from: {self.model_name}...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from pathlib import Path
        
        p = Path(self.model_name)
        if p.exists():
            tokenizer = AutoTokenizer.from_pretrained(str(p))
            model = AutoModelForSequenceClassification.from_pretrained(str(p))
            self.classifier = pipeline(
                "zero-shot-classification",
                model=model,
                tokenizer=tokenizer,
                device=device_idx,
            )
        else:
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=device_idx,
                model_kwargs={"cache_dir": str(MODELS_CACHE_DIR)},
            )
        logger.info("Scam Intent NLI model loaded successfully.")

        self.candidate_labels = [cat.label for cat in SCAM_CATEGORIES.values()]
        self.label_to_category = {cat.label: cat for cat in SCAM_CATEGORIES.values()}

    def analyze(self, text: str) -> ScamIntentResult:
        """
        Analyze a transcript for scam intent.
        Returns a structured ScamIntentResult with scores, labels, and explanation.
        """
        start_time = time.perf_counter()
        clean_text = text.strip()

        if not clean_text or len(clean_text.split()) < 2:
            return ScamIntentResult(
                intent_label="Legitimate Dialogue",
                scam_intent_score=0.0,
                confidence=0.5,
                explanation="Insufficient conversational content to evaluate scam intent.",
                category_scores={"Legitimate Dialogue": 1.0},
                matched_signals=[],
                latency_ms=0.0,
            )

        # Run Zero-Shot classification across all defined categories
        nli_out = self.classifier(
            clean_text,
            candidate_labels=self.candidate_labels,
            hypothesis_template=settings.scam_intent.hypothesis_template,
            multi_label=False,
        )

        category_scores: dict[str, float] = {}
        for label, score in zip(nli_out["labels"], nli_out["scores"]):
            category_scores[label] = float(score)

        # Extract scam category scores excluding Legitimate Dialogue
        scam_scores = {
            lbl: sc for lbl, sc in category_scores.items() if lbl != "Legitimate Dialogue"
        }
        legit_score = category_scores.get("Legitimate Dialogue", 0.0)

        top_scam_label, top_scam_score = max(scam_scores.items(), key=lambda item: item[1])
        top_category_obj = self.label_to_category.get(top_scam_label)

        # Detect contextual lexical / semantic markers per category
        text_lower = clean_text.lower()
        matched_signals: list[str] = []
        category_match_counts: dict[str, int] = {}

        for cat in SCAM_CATEGORIES.values():
            if cat.id == "legitimate_dialogue":
                continue
            for kw in cat.keywords_and_phrases:
                if kw in text_lower and kw not in matched_signals:
                    matched_signals.append(kw)
                    category_match_counts[cat.label] = category_match_counts.get(cat.label, 0) + 1

        # Evaluate if conversation is benign or malicious
        # If no scam signals matched and NLI doesn't show strong confident anomaly
        if not matched_signals and (legit_score >= top_scam_score or top_scam_score < 0.40):
            effective_scam_score = round(top_scam_score * 0.4, 4)
            intent_label = "Legitimate Dialogue"
            explanation = "Conversation appears normal and benign with no deceptive demands."
            # Normalize category scores to reflect benign dominance
            category_scores["Legitimate Dialogue"] = max(0.85, legit_score)
        else:
            # Determine best intent: prioritize category with matched keywords
            if category_match_counts:
                # Find category with highest number of keyword matches
                best_signal_label = max(category_match_counts.items(), key=lambda x: x[1])[0]
                if category_match_counts[best_signal_label] >= 1 or top_scam_score < 0.35:
                    intent_label = best_signal_label
                else:
                    intent_label = top_scam_label
            else:
                intent_label = top_scam_label

            top_category_obj = self.label_to_category.get(intent_label)
            severity = top_category_obj.severity_weight if top_category_obj else 0.9

            # Calculate grounded scam score combining NLI + keyword signal density
            signal_weight = min(len(matched_signals), 4) * 0.15
            base_score = 0.40 * top_scam_score + 0.30 * (1.0 - legit_score) + signal_weight

            effective_scam_score = min(1.0, max(0.45, round(base_score * (0.85 + 0.15 * severity), 4)))
            category_scores[intent_label] = max(category_scores.get(intent_label, 0.0), effective_scam_score)
            explanation = self._generate_explanation(
                intent_label, effective_scam_score, matched_signals, top_category_obj
            )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ScamIntentResult(
            intent_label=intent_label,
            scam_intent_score=round(effective_scam_score, 4),
            confidence=round(category_scores.get(intent_label, 0.5), 4),
            explanation=explanation,
            category_scores={k: round(v, 4) for k, v in category_scores.items()},
            matched_signals=matched_signals,
            latency_ms=round(latency_ms, 2),
        )

    def _generate_explanation(
        self,
        label: str,
        score: float,
        signals: list[str],
        category: ScamCategory | None
    ) -> str:
        """Synthesize a clear, human-readable explanation from model findings."""
        if score < 0.35:
            return f"Low confidence indications of {label}. Content remains largely benign."
        
        desc = category.description if category else "Suspicious intent detected."
        if signals:
            signals_str = ", ".join(f"'{s}'" for s in signals[:4])
            return f"{label} detected (risk index: {int(score*100)}%). {desc} Trigger phrases identified: {signals_str}."
        else:
            return f"{label} detected (risk index: {int(score*100)}%). {desc}"
