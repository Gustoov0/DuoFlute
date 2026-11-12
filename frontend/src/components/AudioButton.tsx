import { Volume2 } from "lucide-react";

interface Props {
  onClick: () => void;
  label: string;
}

export default function AudioButton({ onClick, label }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-2 rounded-2xl border-2 border-b-4 border-sky-400 bg-sky-50 px-4 py-2 font-semibold text-sky-700 transition active:translate-y-0.5 dark:bg-sky-950 dark:text-sky-300"
    >
      <Volume2 size={20} aria-hidden="true" />
      {label}
    </button>
  );
}
