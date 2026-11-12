export default function Spinner() {
  return (
    <div
      role="status"
      aria-label="Carregando"
      className="h-8 w-8 animate-spin rounded-full border-4 border-stone-300 border-t-emerald-500 dark:border-stone-700"
    />
  );
}
