/**
 * AudioResampler
 * Stateful linear-interpolating audio downsampler from hardware sample rates
 * (typically 44,100Hz or 48,000Hz) down to 16,000Hz PCM 16-bit mono.
 * Preserves fractional sample offsets across chunk boundaries to prevent phase drift.
 */
export class AudioResampler {
  constructor(inputSampleRate = 48000, targetSampleRate = 16000) {
    this.inputSampleRate = inputSampleRate;
    this.targetSampleRate = targetSampleRate;
    this.ratio = inputSampleRate / targetSampleRate;
    this.offset = 0;
  }

  /**
   * Resample a Float32Array into an Int16Array of 16-bit linear PCM.
   * @param {Float32Array} float32Buffer - Raw audio samples in [-1.0, 1.0]
   * @returns {Int16Array} 16-bit signed integers at targetSampleRate
   */
  resample(float32Buffer) {
    if (this.inputSampleRate === this.targetSampleRate) {
      return this.floatTo16BitPCM(float32Buffer);
    }

    const outputLength = Math.floor((float32Buffer.length - this.offset) / this.ratio);
    if (outputLength <= 0) {
      this.offset -= float32Buffer.length;
      return new Int16Array(0);
    }

    const output = new Int16Array(outputLength);
    let outIdx = 0;
    let inIdx = this.offset;

    while (outIdx < outputLength) {
      const idxFloor = Math.floor(inIdx);
      const idxCeil = Math.min(idxFloor + 1, float32Buffer.length - 1);
      const weight = inIdx - idxFloor;

      const s0 = float32Buffer[idxFloor] !== undefined ? float32Buffer[idxFloor] : 0;
      const s1 = float32Buffer[idxCeil] !== undefined ? float32Buffer[idxCeil] : s0;
      const interpolated = s0 * (1 - weight) + s1 * weight;

      // Clamp [-1.0, 1.0]
      const clamped = Math.max(-1, Math.min(1, interpolated));
      // Convert to 16-bit signed PCM
      output[outIdx++] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff;

      inIdx += this.ratio;
    }

    this.offset = inIdx - float32Buffer.length;
    return output;
  }

  floatTo16BitPCM(float32Buffer) {
    const output = new Int16Array(float32Buffer.length);
    for (let i = 0; i < float32Buffer.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Buffer[i]));
      output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return output;
  }

  reset() {
    this.offset = 0;
  }
}
