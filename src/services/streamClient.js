/**
 * TrueDhwani Live Stream WebSocket Client
 * Manages low-latency bidirectional connection to the FastAPI streaming backend.
 */
export class StreamClient {
  constructor(options = {}) {
    this.url = options.url || this.getDefaultWsUrl();
    this.onPacket = options.onPacket || (() => {});
    this.onStatusChange = options.onStatusChange || (() => {});
    this.onError = options.onError || (() => {});
    this.ws = null;
    this.isConnected = false;
    this.manualClose = false;
    this.reconnectTimer = null;
  }

  getDefaultWsUrl() {
    if (typeof window === 'undefined') return 'ws://127.0.0.1:8000/ws/stream';
    const loc = window.location;
    // If running under Vite dev server port 5173, Vite proxies /ws to :8000
    const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${loc.host}/ws/stream`;
  }

  connect() {
    this.manualClose = false;
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.onStatusChange('connecting');
    try {
      this.ws = new WebSocket(this.url);
      this.ws.binaryType = 'arraybuffer';

      this.ws.onopen = () => {
        this.isConnected = true;
        this.onStatusChange('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onPacket(data);
        } catch (e) {
          console.warn('[StreamClient] Failed to parse incoming packet:', event.data, e);
        }
      };

      this.ws.onerror = (err) => {
        console.error('[StreamClient] WebSocket error:', err);
        this.onError(err);
      };

      this.ws.onclose = (evt) => {
        this.isConnected = false;
        this.onStatusChange('disconnected');
        if (!this.manualClose) {
          // Attempt reconnect after delay
          this.reconnectTimer = setTimeout(() => this.connect(), 2000);
        }
      };
    } catch (e) {
      this.onError(e);
      this.onStatusChange('error');
    }
  }

  sendAudioChunk(int16Array) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(int16Array.buffer);
    }
  }

  resetStream() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'reset' }));
    }
  }

  flushStream() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'flush' }));
    }
  }

  disconnect() {
    this.manualClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      try {
        this.ws.close();
      } catch (e) {}
      this.ws = null;
    }
    this.isConnected = false;
    this.onStatusChange('disconnected');
  }
}
