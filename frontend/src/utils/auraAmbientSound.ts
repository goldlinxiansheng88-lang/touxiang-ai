/**
 * 程序化氛围音：无外部音频文件。
 * 极低音量、偏暗暖的垫音 + 极轻的换句提示；可静音并写入 localStorage。
 */

const STORAGE_KEY = "aurashift-ambient-muted";

export function isAmbientMuted(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

export function setAmbientMuted(muted: boolean): void {
  try {
    localStorage.setItem(STORAGE_KEY, muted ? "1" : "0");
  } catch {
    /* ignore */
  }
}

let audioCtx: AudioContext | null = null;
let masterGain: GainNode | null = null;
const oscillators: OscillatorNode[] = [];

function newContext(): AudioContext | null {
  if (typeof window === "undefined") return null;
  const AC = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
  return AC ? new AC() : null;
}

export async function startAuraAmbient(): Promise<void> {
  if (isAmbientMuted()) return;
  await stopAuraAmbient();

  const ctx = newContext();
  if (!ctx) return;
  audioCtx = ctx;
  await ctx.resume();

  masterGain = ctx.createGain();
  masterGain.gain.value = 0.0001;

  /** 两级低通，去掉齿音与「金属感」，只留暗色底噪感 */
  const warmLowpass = ctx.createBiquadFilter();
  warmLowpass.type = "lowpass";
  warmLowpass.frequency.value = 210;
  warmLowpass.Q.value = 0.45;

  const soften = ctx.createBiquadFilter();
  soften.type = "lowpass";
  soften.frequency.value = 180;
  soften.Q.value = 0.35;

  const padGain = ctx.createGain();
  padGain.gain.value = 0.0075;

  /** 仅两路极低频正弦，无 detune 拍频，避免刺耳蜂鸣 */
  const freqs = [110.0, 146.83];
  for (const f of freqs) {
    const osc = ctx.createOscillator();
    osc.type = "sine";
    osc.frequency.value = f;
    osc.detune.value = 0;
    osc.connect(warmLowpass);
    osc.start();
    oscillators.push(osc);
  }

  warmLowpass.connect(soften);
  soften.connect(padGain);
  padGain.connect(masterGain);
  masterGain.connect(ctx.destination);

  const t = ctx.currentTime;
  masterGain.gain.cancelScheduledValues(t);
  masterGain.gain.setValueAtTime(0.0001, t);
  masterGain.gain.exponentialRampToValueAtTime(1, t + 3.2);
}

export async function stopAuraAmbient(): Promise<void> {
  oscillators.forEach((o) => {
    try {
      o.stop();
      o.disconnect();
    } catch {
      /* */
    }
  });
  oscillators.length = 0;
  masterGain = null;

  if (audioCtx) {
    const ctx = audioCtx;
    audioCtx = null;
    try {
      await ctx.close();
    } catch {
      /* */
    }
  }
}

/** 换句：低音高、包络慢、带低通，避免「叮」一声刺耳 */
export function playPhraseChime(): void {
  if (isAmbientMuted() || typeof window === "undefined") return;

  let ctx = audioCtx;
  if (!ctx || ctx.state === "closed") {
    ctx = newContext();
    if (!ctx) return;
    void ctx.resume();
    audioCtx = ctx;
  } else {
    void ctx.resume();
  }

  const osc = ctx.createOscillator();
  osc.type = "sine";
  osc.frequency.value = 261.63;

  const tone = ctx.createBiquadFilter();
  tone.type = "lowpass";
  tone.frequency.value = 520;
  tone.Q.value = 0.4;

  const g = ctx.createGain();
  const t = ctx.currentTime;
  const peak = 0.0032;

  g.gain.setValueAtTime(0.0001, t);
  g.gain.linearRampToValueAtTime(peak, t + 0.1);
  g.gain.setValueAtTime(peak, t + 0.12);
  g.gain.exponentialRampToValueAtTime(0.0001, t + 0.62);

  osc.connect(tone);
  tone.connect(g);
  g.connect(ctx.destination);
  osc.start(t);
  osc.stop(t + 0.65);
}

export async function disposeAuraAudio(): Promise<void> {
  await stopAuraAmbient();
}
