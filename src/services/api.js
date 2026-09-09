const API_BASE = '/api';

export async function fetchHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchPresets() {
  const response = await fetch(`${API_BASE}/presets`);
  if (!response.ok) {
    throw new Error(`Failed to fetch presets: ${response.status}`);
  }
  return response.json();
}

export async function analyzeAudio(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/analyze-audio`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Analysis failed: ${response.status}`);
  }

  return response.json();
}

export function createStreamConnection() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return new WebSocket(`${protocol}//${window.location.host}/ws/stream`);
}
