// Web Audio synthesized arcade SFX — no asset files needed.
// Lazy-create the AudioContext on first use (browser autoplay policies).

let ctx: AudioContext | null = null;
function getCtx(): AudioContext {
  if (!ctx) ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
  return ctx;
}

function beep(freq: number, durMs: number, type: OscillatorType = "square", gain = 0.08, when = 0) {
  const c = getCtx();
  const osc = c.createOscillator();
  const g = c.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  g.gain.value = gain;
  osc.connect(g);
  g.connect(c.destination);
  const start = c.currentTime + when;
  osc.start(start);
  g.gain.setValueAtTime(gain, start);
  g.gain.exponentialRampToValueAtTime(0.0001, start + durMs / 1000);
  osc.stop(start + durMs / 1000);
}

export const sfx = {
  waka() {
    beep(440, 60, "square", 0.07, 0);
    beep(330, 60, "square", 0.07, 0.06);
  },
  pellet() {
    beep(880, 50, "square", 0.06);
  },
  powerPellet() {
    beep(330, 90, "square", 0.08, 0);
    beep(440, 90, "square", 0.08, 0.09);
    beep(660, 120, "square", 0.08, 0.18);
  },
  levelClear() {
    const notes = [523, 659, 784, 1047, 1319];
    notes.forEach((n, i) => beep(n, 130, "square", 0.07, i * 0.12));
  },
  fail() {
    beep(200, 120, "sawtooth", 0.08, 0);
    beep(150, 200, "sawtooth", 0.08, 0.12);
  },
  click() {
    beep(660, 30, "square", 0.04);
  },
};
