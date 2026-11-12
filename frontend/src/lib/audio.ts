// Sons de referência gerados no navegador com a Web Audio API (sem arquivos de áudio).

const BEATS: Record<string, number> = {
  semibreve: 4,
  minima: 2,
  seminima: 1,
  colcheia: 0.5,
};

let audioContext: AudioContext | null = null;

function getContext(): AudioContext {
  if (!audioContext) audioContext = new AudioContext();
  if (audioContext.state === "suspended") void audioContext.resume();
  return audioContext;
}

// Um tom suave: onda senoidal + um pouco do 2º harmônico, com entrada e saída suaves.
function tone(frequency: number, startAfter: number, seconds: number) {
  const ctx = getContext();
  const master = ctx.createGain();
  master.connect(ctx.destination);

  const t0 = ctx.currentTime + startAfter;
  const attack = 0.03;
  const release = Math.min(0.08, seconds / 3);
  const peak = 0.22;

  master.gain.setValueAtTime(0, t0);
  master.gain.linearRampToValueAtTime(peak, t0 + attack);
  master.gain.setValueAtTime(peak, t0 + Math.max(attack, seconds - release));
  master.gain.linearRampToValueAtTime(0, t0 + seconds);

  const partials = [
    { multiple: 1, level: 1 },
    { multiple: 2, level: 0.15 },
  ];
  for (const partial of partials) {
    const osc = ctx.createOscillator();
    osc.type = "sine";
    osc.frequency.value = frequency * partial.multiple;
    const level = ctx.createGain();
    level.gain.value = partial.level;
    osc.connect(level);
    level.connect(master);
    osc.start(t0);
    osc.stop(t0 + seconds + 0.02);
  }
}

export function playNote(frequency: number, seconds = 1.2) {
  tone(frequency, 0, seconds);
}

/** Toca uma sequência de notas. Retorna a duração total em segundos. */
export function playSequence(
  items: { frequency: number; duration: string }[],
  bpm: number,
): number {
  const beat = 60 / bpm;
  let elapsed = 0;
  for (const item of items) {
    const length = (BEATS[item.duration] ?? 1) * beat;
    tone(item.frequency, elapsed, length * 0.92);
    elapsed += length;
  }
  return elapsed;
}