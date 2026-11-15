interface Props {
  value: number; // 0 a 100
  color?: string;
  label: string;
}

export default function ProgressBar({ value, color = "bg-emerald-500", label }: Props) {
  const percent = Math.max(0, Math.min(100, value));
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuenow={Math.round(percent)}
      aria-valuemin={0}
      aria-valuemax={100}
      className="h-3 w-full overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800"
    >
      <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${percent}%` }} />
    </div>
  );
}
