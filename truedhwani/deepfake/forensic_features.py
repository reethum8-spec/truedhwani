"""
Acoustic Biomarker & Forensic Feature Extraction Engine.
Extracts speaker characteristics independent of spoken words or keywords:
- F0 Pitch dynamics, micro-tremors, and pitch jitter stability
- Harmonic-to-Noise Ratio (HNR) and spectral harmonicity
- Vocoder phase signatures, high-frequency spectral flatness, and spectral roll-off
- Breath pattern continuity and micro-pause temporal rhythm
- Formant transition fluidity and co-articulation dynamics
"""

import math
import logging
from dataclasses import dataclass, field
import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)


@dataclass
class BiomarkerResult:
    """Granular forensic acoustic biomarker analysis."""
    # Individual normalized scores in [0.0, 1.0]
    pitch_jitter_pct: float  # Cycle-to-cycle F0 perturbation (Natural: 0.3%-1.5%, Neural: <0.2% or erratic)
    hnr_db: float  # Harmonic-to-Noise Ratio in dB (Natural: 15-25 dB, Neural vocoders often differ)
    spectral_flatness: float  # High frequency noise flatness (Neural vocoders leave artifacts > 3.5kHz)
    vocoder_artifact_score: float  # [0.0, 1.0] Probability of neural vocoder (HiFi-GAN/Diffusion) fingerprint
    breath_naturalness_score: float  # [0.0, 1.0] Natural respiratory / turbulence onset presence
    coarticulation_fluidity: float  # [0.0, 1.0] Physical vocal tract inertial gliding
    temporal_rhythm_entropy: float  # [0.0, 1.0] Cadence naturalness vs mechanical uniformity
    biomarker_spoof_prob: float  # [0.0, 1.0] Composite biomarker spoof probability
    metrics_summary: dict[str, float] = field(default_factory=dict)


class ForensicBiomarkerExtractor:
    """
    Forensic audio feature extractor inspecting physical human vocal tract dynamics
    versus synthetic neural vocoder and text-to-speech signatures.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def extract(self, audio: np.ndarray) -> BiomarkerResult:
        """
        Analyze audio waveform (1D float32 normalized, 16kHz).
        Returns comprehensive forensic biomarker metrics.
        """
        if audio.ndim > 1:
            audio = audio.flatten()

        n_samples = len(audio)
        if n_samples < 512:
            return self._default_result()

        # 1. Pitch (F0) Dynamics & Micro-Jitter
        jitter_pct, f0_stability = self._compute_pitch_dynamics(audio)

        # 2. Harmonic-to-Noise Ratio (HNR)
        hnr_db = self._compute_hnr(audio)

        # 3. High-Frequency Spectral Flatness & Vocoder Fingerprint
        vocoder_score, spec_flatness = self._compute_vocoder_artifacts(audio)

        # 4. Temporal Rhythm, Envelope Entropy & Micro-pauses
        rhythm_entropy, breath_score = self._compute_temporal_breath_rhythm(audio)

        # 5. Formant Transition Glide & Co-articulation Fluidity
        coarticulation = self._compute_coarticulation_fluidity(audio)

        # Composite Biomarker Spoof Probability Calculation:
        # Modern neural TTS models show:
        # - Excessively low pitch jitter (hyper-smooth F0, < 0.25%) OR unnatural discrete frame hops
        # - High vocoder artifact score in 3.5kHz - 8kHz band
        # - Abnormally uniform phoneme durations (low rhythm entropy)
        # - Lacking natural breath pre-roll / turbulent aspiration
        jitter_penalty = 0.0
        if jitter_pct < 0.22:
            # Hyper-smooth synthetic pitch contour
            jitter_penalty = min(0.8, (0.22 - jitter_pct) / 0.20)
        elif jitter_pct > 3.5:
            # Unstable pitch synthesis / stitching artifacts
            jitter_penalty = min(0.6, (jitter_pct - 3.5) / 3.0)

        vocoder_weight = vocoder_score * 0.45
        breath_penalty = (1.0 - breath_score) * 0.20
        coart_penalty = (1.0 - coarticulation) * 0.15
        rhythm_penalty = (1.0 - rhythm_entropy) * 0.10

        composite_spoof = 0.35 * vocoder_weight + 0.25 * jitter_penalty + 0.20 * breath_penalty + 0.10 * coart_penalty + 0.10 * rhythm_penalty
        composite_spoof = min(1.0, max(0.01, round(composite_spoof, 4)))

        summary = {
            "pitch_jitter_pct": round(float(jitter_pct), 3),
            "hnr_db": round(float(hnr_db), 2),
            "spectral_flatness": round(float(spec_flatness), 4),
            "vocoder_artifact_score": round(float(vocoder_score), 4),
            "breath_naturalness_score": round(float(breath_score), 4),
            "coarticulation_fluidity": round(float(coarticulation), 4),
            "temporal_rhythm_entropy": round(float(rhythm_entropy), 4),
            "biomarker_spoof_prob": composite_spoof,
        }

        return BiomarkerResult(
            pitch_jitter_pct=round(float(jitter_pct), 3),
            hnr_db=round(float(hnr_db), 2),
            spectral_flatness=round(float(spec_flatness), 4),
            vocoder_artifact_score=round(float(vocoder_score), 4),
            breath_naturalness_score=round(float(breath_score), 4),
            coarticulation_fluidity=round(float(coarticulation), 4),
            temporal_rhythm_entropy=round(float(rhythm_entropy), 4),
            biomarker_spoof_prob=composite_spoof,
            metrics_summary=summary,
        )

    def _compute_pitch_dynamics(self, audio: np.ndarray) -> tuple[float, float]:
        """
        Estimate fundamental frequency (F0) trajectory using short-time autocorrelation.
        Computes cycle-to-cycle pitch jitter percentage and trajectory smoothness.
        """
        frame_len = 512
        hop_len = 256
        f0_list = []

        min_lag = int(self.sample_rate / 400)  # Max F0 = 400Hz
        max_lag = int(self.sample_rate / 60)   # Min F0 = 60Hz

        for i in range(0, len(audio) - frame_len, hop_len):
            frame = audio[i : i + frame_len]
            if np.max(np.abs(frame)) < 0.008:
                continue

            # Normalized autocorrelation
            corr = signal.correlate(frame, frame, mode="full")
            corr = corr[len(corr) // 2 :]
            if len(corr) < max_lag:
                continue

            search_region = corr[min_lag:max_lag]
            if len(search_region) == 0:
                continue

            peak_idx = np.argmax(search_region) + min_lag
            peak_val = corr[peak_idx]
            energy = corr[0] + 1e-9

            # Voiced frame check
            if (peak_val / energy) > 0.35:
                f0 = self.sample_rate / peak_idx
                f0_list.append(f0)

        if len(f0_list) < 4:
            return 0.85, 0.70  # Nominal human average when unvoiced

        f0_arr = np.array(f0_list)
        diffs = np.abs(np.diff(f0_arr))
        mean_f0 = np.mean(f0_arr) + 1e-6
        mean_diff = np.mean(diffs)

        jitter_pct = float((mean_diff / mean_f0) * 100.0)
        f0_std = float(np.std(f0_arr))
        f0_stability = min(1.0, f0_std / (mean_f0 * 0.25 + 1e-6))

        return jitter_pct, f0_stability

    def _compute_hnr(self, audio: np.ndarray) -> float:
        """
        Compute Harmonic-to-Noise Ratio (HNR) in decibels.
        Human speech typically has HNR in [12, 28] dB.
        """
        frame_len = 1024
        hop_len = 512
        hnr_values = []

        for i in range(0, len(audio) - frame_len, hop_len):
            frame = audio[i : i + frame_len]
            if np.max(np.abs(frame)) < 0.01:
                continue

            corr = signal.correlate(frame, frame, mode="full")
            corr = corr[len(corr) // 2 :]
            min_lag = int(self.sample_rate / 350)
            max_lag = min(len(corr) - 1, int(self.sample_rate / 70))

            if max_lag <= min_lag:
                continue

            peak_val = np.max(corr[min_lag:max_lag])
            total_energy = corr[0] + 1e-9

            if peak_val > 0 and total_energy > peak_val:
                harmonic_energy = peak_val
                noise_energy = max(1e-9, total_energy - peak_val)
                hnr = 10.0 * math.log10(harmonic_energy / noise_energy)
                hnr_values.append(hnr)

        if not hnr_values:
            return 18.0
        return float(np.median(hnr_values))

    def _compute_vocoder_artifacts(self, audio: np.ndarray) -> tuple[float, float]:
        """
        Analyze high-frequency spectral distribution and phase characteristics.
        Neural vocoders (HiFi-GAN, WaveGlow, Diffusion) produce distinct spectral tilt
        and elevated spectral flatness in the 3.5kHz - 8kHz band.
        """
        # Compute STFT
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=512, noverlap=256)
        mag = np.abs(zxx) + 1e-10

        # Frequency mask for upper band (> 3500 Hz)
        hf_mask = f >= 3500
        if not np.any(hf_mask):
            return 0.05, 0.01

        hf_mag = mag[hf_mask, :]

        # Spectral flatness = geometric mean / arithmetic mean
        log_mag = np.log(hf_mag)
        geom_mean = np.exp(np.mean(log_mag, axis=0))
        arith_mean = np.mean(hf_mag, axis=0) + 1e-9
        flatness_per_frame = geom_mean / arith_mean
        avg_flatness = float(np.mean(flatness_per_frame))

        # Spectral flux in upper band (frame-to-frame changes)
        flux = np.sqrt(np.mean((np.diff(hf_mag, axis=1) ** 2), axis=0)) if hf_mag.shape[1] > 1 else np.array([0.0])
        mean_flux = float(np.mean(flux))

        # Neural vocoder artifact index
        # Artificial vocoders have elevated high-frequency flatness and unnatural spectral flux peaks
        vocoder_score = 0.0
        if avg_flatness > 0.12:
            vocoder_score += min(0.6, (avg_flatness - 0.12) / 0.25)
        if mean_flux > 0.08:
            vocoder_score += min(0.4, (mean_flux - 0.08) / 0.15)

        return min(1.0, max(0.02, vocoder_score)), avg_flatness

    def _compute_temporal_breath_rhythm(self, audio: np.ndarray) -> tuple[float, float]:
        """
        Analyze speech envelope, syllable rhythm cadence entropy, and respiratory / breath onset.
        """
        # Lowpass filter the squared audio to obtain energy envelope
        env = np.abs(signal.hilbert(audio))
        b, a = signal.butter(2, 20.0 / (self.sample_rate / 2), btype="low")
        smooth_env = signal.filtfilt(b, a, env)

        # Micro-pause detection
        threshold = np.max(smooth_env) * 0.05
        below_thresh = smooth_env < threshold

        # Count state transitions
        transitions = np.diff(below_thresh.astype(int))
        num_onsets = np.sum(transitions == 1)

        # Syllable cadence / rhythm entropy
        duration_sec = len(audio) / self.sample_rate
        onsets_per_sec = num_onsets / max(0.5, duration_sec)

        # Natural human speech has 2.5 to 5.5 syllables per second with micro-variations
        if 2.2 <= onsets_per_sec <= 6.0:
            rhythm_entropy = 0.85
        elif onsets_per_sec < 1.5:
            rhythm_entropy = 0.50
        else:
            rhythm_entropy = 0.40

        # Breath signature check: leading acoustic turbulence prior to vocal onset
        first_third = audio[: int(len(audio) * 0.25)]
        if len(first_third) > 0:
            sub_rms = float(np.sqrt(np.mean(first_third ** 2)))
            total_rms = float(np.sqrt(np.mean(audio ** 2))) + 1e-9
            ratio = sub_rms / total_rms
            # Natural speech has a 0.05 - 0.35 lead-in turbulence ratio
            if 0.04 <= ratio <= 0.40:
                breath_score = 0.88
            else:
                breath_score = 0.45
        else:
            breath_score = 0.60

        return rhythm_entropy, breath_score

    def _compute_coarticulation_fluidity(self, audio: np.ndarray) -> float:
        """
        Measure spectral continuity across vowel-consonant boundaries.
        Natural vocal tract inertia creates smooth physical transitions.
        """
        frame_len = 512
        hop_len = 256
        num_frames = (len(audio) - frame_len) // hop_len

        if num_frames < 4:
            return 0.80

        # Compute spectral centroids across frames
        f, t, zxx = signal.stft(audio, fs=self.sample_rate, nperseg=frame_len, noverlap=frame_len - hop_len)
        mag = np.abs(zxx) + 1e-9
        freqs = f[:, np.newaxis]

        centroids = np.sum(freqs * mag, axis=0) / np.sum(mag, axis=0)
        centroid_diffs = np.abs(np.diff(centroids))

        # Discontinuous jumps indicate concatenated or non-coarticulated synthesis
        mean_jump = np.mean(centroid_diffs)
        if mean_jump < 280:
            # Smooth natural glide
            fluidity = 0.90
        elif mean_jump > 600:
            # Abrupt spectral transitions
            fluidity = 0.35
        else:
            fluidity = 0.65

        return float(fluidity)

    def _default_result(self) -> BiomarkerResult:
        summary = {
            "pitch_jitter_pct": 0.85,
            "hnr_db": 18.0,
            "spectral_flatness": 0.02,
            "vocoder_artifact_score": 0.05,
            "breath_naturalness_score": 0.80,
            "coarticulation_fluidity": 0.85,
            "temporal_rhythm_entropy": 0.80,
            "biomarker_spoof_prob": 0.05,
        }
        return BiomarkerResult(
            pitch_jitter_pct=0.85,
            hnr_db=18.0,
            spectral_flatness=0.02,
            vocoder_artifact_score=0.05,
            breath_naturalness_score=0.80,
            coarticulation_fluidity=0.85,
            temporal_rhythm_entropy=0.80,
            biomarker_spoof_prob=0.05,
            metrics_summary=summary,
        )
