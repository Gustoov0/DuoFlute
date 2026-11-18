import { Trophy } from "lucide-react";

import Spinner from "../components/Spinner";
import { useWeeklyRanking } from "../lib/queries";
import type { RankingEntry } from "../lib/types";

const BADGES: Record<number, string> = {
  1: "bg-yellow-400 text-yellow-900",
  2: "bg-stone-300 text-stone-800",
  3: "bg-orange-400 text-orange-900",
};

function timeLeft(weekEnd: string): string {
  // weekEnd é o domingo (inclusive); a semana acaba às 23:59 desse dia
  const end = new Date(`${weekEnd}T23:59:59`);
  const days = Math.ceil((end.getTime() - Date.now()) / 86_400_000);
  if (days <= 1) return "Termina hoje";
  return `Termina em ${days} dias`;
}

function Row({ rank, name, xp, isMe }: { rank: number; name: string; xp: number; isMe: boolean }) {
  return (
    <li
      className={`flex items-center gap-3 rounded-2xl border-2 px-4 py-3 ${
        isMe
          ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-950"
          : "border-stone-200 bg-white dark:border-stone-800 dark:bg-stone-900"
      }`}
    >
      <span
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full font-extrabold ${
          BADGES[rank] ?? "bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-300"
        }`}
      >
        {rank}
      </span>
      <span className="flex-1 truncate font-bold">
        {name}
        {isMe && <span className="ml-2 text-sm font-semibold text-emerald-600 dark:text-emerald-400">(você)</span>}
      </span>
      <span className="font-extrabold text-amber-600 dark:text-amber-400">{xp} XP</span>
    </li>
  );
}

export default function ProgressPage() {
  const ranking = useWeeklyRanking();
  const data = ranking.data;

  const meInTop = data?.entries.some((entry: RankingEntry) => entry.is_me) ?? false;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-extrabold">Progresso</h1>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-xl font-extrabold">
            <Trophy className="text-amber-500" aria-hidden="true" /> Ranking semanal
          </h2>
          {data && (
            <span className="rounded-full bg-stone-200 px-3 py-1 text-xs font-bold dark:bg-stone-800">
              {timeLeft(data.week_end)}
            </span>
          )}
        </div>

        {ranking.isPending && (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        )}

        {ranking.isError && (
          <p role="alert" className="rounded-xl bg-red-100 p-4 font-semibold text-red-800 dark:bg-red-950 dark:text-red-200">
            Não foi possível carregar o ranking. {ranking.error.message}
          </p>
        )}

        {data && data.entries.length === 0 && (
          <p className="rounded-2xl border-2 border-dashed border-stone-300 p-6 text-center text-stone-500 dark:border-stone-700">
            Ninguém pontuou nesta semana ainda. Conclua uma lição para abrir o ranking!
          </p>
        )}

        {data && data.entries.length > 0 && (
          <ol className="flex flex-col gap-2">
            {data.entries.map((entry) => (
              <Row key={entry.user_id} rank={entry.rank} name={entry.display_name} xp={entry.xp} isMe={entry.is_me} />
            ))}

            {/* O aluno está fora do top 10: mostra a posição dele separadamente */}
            {data.me && !meInTop && (
              <>
                <li aria-hidden="true" className="text-center text-stone-400">⋮</li>
                <Row rank={data.me.rank} name="Você" xp={data.me.xp} isMe />
              </>
            )}
          </ol>
        )}

        {data && data.entries.length > 0 && !data.me && (
          <p className="mt-3 text-center text-sm text-stone-500 dark:text-stone-400">
            Você ainda não pontuou nesta semana. Conclua uma lição para entrar no ranking.
          </p>
        )}

        {data && (
          <p className="mt-4 text-center text-xs text-stone-400 dark:text-stone-500">
            Dados servidos por: {data.source === "redis" ? "Redis (cache)" : "PostgreSQL (alternativa, Redis indisponível)"}
          </p>
        )}
      </section>

      <p className="mt-10 rounded-2xl bg-stone-100 p-4 text-center text-sm text-stone-500 dark:bg-stone-900 dark:text-stone-400">
        Estatísticas detalhadas e conquistas chegam em breve.
      </p>
    </div>
  );
}