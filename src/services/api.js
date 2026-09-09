/**
 * TrueDhwani REST API Service
 */

export async function fetchPresets() {
  const res = await fetch('/api/presets');
  if (!res.ok) {
    throw new Error(`Failed to load audio presets: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch('/api/health');
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function analyzeAudioFile(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch('/api/analyze-audio', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `File analysis failed: ${res.statusText}`);
  }

  return res.json();
}
