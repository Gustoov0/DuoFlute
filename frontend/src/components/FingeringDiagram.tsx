import type { Holes } from "../lib/types";

// Posição vertical dos furos frontais (viewBox 90 x 262)
const FRONT_HOLES = [
  { key: "h1", y: 68, double: false },
  { key: "h2", y: 92, double: false },
  { key: "h3", y: 116, double: false },
  { key: "h4", y: 154, double: false },
  { key: "h5", y: 178, double: false },
  { key: "h6", y: 208, double: true }, // furos duplos da flauta barroca
  { key: "h7", y: 232, double: true },
];

const NAMES: Record<string, string> = {
  thumb: "polegar",
  h1: "furo 1",
  h2: "furo 2",
  h3: "furo 3",
  h4: "furo 4",
  h5: "furo 5",
  h6: "furo 6",
  h7: "furo 7",
};

const WIDTHS = { sm: "w-12", md: "w-20", lg: "w-28" } as const;

interface HoleProps {
  cx: number;
  cy: number;
  r: number;
  state: number; // 0 aberto, 1 fechado, 2 meio furo
}

function Hole({ cx, cy, r, state }: HoleProps) {
  if (state === 1) {
    return <circle cx={cx} cy={cy} r={r} strokeWidth={1.5} className="fill-current stroke-current" />;
  }
  const open = (
    <circle
      cx={cx}
      cy={cy}
      r={r}
      strokeWidth={1.5}
      className="fill-white stroke-current dark:fill-stone-900"
    />
  );
  if (state === 2) {
    return (
      <g>
        {open}
        <path d={`M ${cx} ${cy - r} A ${r} ${r} 0 0 0 ${cx} ${cy + r} Z`} className="fill-current" />
      </g>
    );
  }
  return open;
}

interface Props {
  holes: Holes;
  size?: keyof typeof WIDTHS;
  showLabels?: boolean;
}

/** Desenho da flauta doce soprano barroca com os furos abertos/fechados. */
export default function FingeringDiagram({ holes, size = "md", showLabels = false }: Props) {
  const closed = Object.keys(NAMES)
    .filter((key) => holes[key] === 1)
    .map((key) => NAMES[key]);
  const label = closed.length
    ? `Digitação com ${closed.join(", ")} fechados`
    : "Digitação com todos os furos abertos";

  return (
    <svg
      viewBox="0 0 90 262"
      role="img"
      aria-label={label}
      className={`${WIDTHS[size]} text-stone-800 dark:text-stone-100`}
    >
      {/* bocal e corpo */}
      <rect x="38" y="4" width="14" height="32" rx="3" strokeWidth={1.5}
        className="fill-amber-100 stroke-stone-500 dark:fill-stone-700 dark:stroke-stone-400" />
      <rect x="33" y="30" width="24" height="226" rx="9" strokeWidth={1.5}
        className="fill-amber-100 stroke-stone-500 dark:fill-stone-700 dark:stroke-stone-400" />

      {/* furo do polegar (fica atrás da flauta) */}
      <line x1="25" y1="72" x2="33" y2="72" strokeWidth={1.5} strokeDasharray="2 2"
        className="stroke-stone-400" />
      <Hole cx={18} cy={72} r={7} state={holes.thumb ?? 0} />

      {/* furos frontais */}
      {FRONT_HOLES.map((hole) =>
        hole.double ? (
          <g key={hole.key}>
            <Hole cx={39} cy={hole.y} r={4.5} state={holes[hole.key] ?? 0} />
            <Hole cx={51} cy={hole.y} r={4.5} state={holes[hole.key] ?? 0} />
          </g>
        ) : (
          <Hole key={hole.key} cx={45} cy={hole.y} r={7} state={holes[hole.key] ?? 0} />
        ),
      )}

      {showLabels && (
        <g fontSize="9" textAnchor="middle" className="fill-current opacity-60">
          <text x="18" y="92">P</text>
          {FRONT_HOLES.map((hole, i) => (
            <text key={hole.key} x="73" y={hole.y + 3}>{i + 1}</text>
          ))}
        </g>
      )}
    </svg>
  );
}
