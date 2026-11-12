interface Props {
  /** Posição na pauta (clave de sol): 0 = 1ª linha (Mi), 2 = Sol, 4 = Si, 6 = Ré... */
  position: number;
}

/** Pauta simples com uma nota. Cada passo (linha -> espaço) vale 6 unidades. */
export default function StaffNote({ position }: Props) {
  const bottom = 78;
  const step = 6;
  const x = 110;
  const y = bottom - position * step;
  const stemUp = position < 4;

  return (
    <svg
      viewBox="0 0 220 110"
      role="img"
      aria-label="Nota escrita na pauta"
      className="w-56 text-stone-800 dark:text-stone-100"
    >
      {[0, 1, 2, 3, 4].map((i) => (
        <line key={i} x1="10" x2="210" y1={bottom - i * 12} y2={bottom - i * 12}
          stroke="currentColor" strokeWidth="1.2" />
      ))}
      <ellipse cx={x} cy={y} rx="9" ry="6.5" transform={`rotate(-20 ${x} ${y})`}
        fill="currentColor" />
      {stemUp ? (
        <line x1={x + 8} y1={y - 1} x2={x + 8} y2={y - 34} stroke="currentColor" strokeWidth="1.6" />
      ) : (
        <line x1={x - 8} y1={y + 1} x2={x - 8} y2={y + 34} stroke="currentColor" strokeWidth="1.6" />
      )}
    </svg>
  );
}
