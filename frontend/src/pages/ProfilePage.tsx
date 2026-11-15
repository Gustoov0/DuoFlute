import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LogOut } from "lucide-react";

import ProgressBar from "../components/ProgressBar";
import Spinner from "../components/Spinner";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { useSummary } from "../lib/queries";
import type { ProgressSummary } from "../lib/types";

const GOALS = [10, 20, 30, 50];

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  const summary = useSummary();

  const changeGoal = useMutation({
    mutationFn: (goal: number) =>
      api<ProgressSummary>("/progress/goal", { method: "PUT", body: { daily_goal_xp: goal } }),
    onSuccess: (data) => queryClient.setQueryData(["summary"], data),
  });

  if (!user) return null;
  const stats = summary.data;

  const cards = stats
    ? [
        { label: "Nível", value: stats.level },
        { label: "XP total", value: stats.xp_total },
        { label: "Ofensiva atual", value: `${stats.current_streak} dias` },
        { label: "Maior ofensiva", value: `${stats.longest_streak} dias` },
      ]
    : [];

  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500 text-3xl font-extrabold text-white">
          {user.display_name.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-extrabold">{user.display_name}</h1>
          <p className="text-stone-500 dark:text-stone-400">{user.email}</p>
        </div>
      </div>

      {summary.isPending && (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      )}

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-3">
            {cards.map((card) => (
              <div key={card.label} className="rounded-2xl border-2 border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900">
                <p className="text-sm text-stone-500 dark:text-stone-400">{card.label}</p>
                <p className="text-xl font-extrabold">{card.value}</p>
              </div>
            ))}
          </div>

          <div className="mt-3 rounded-2xl border-2 border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900">
            <div className="mb-2 flex justify-between text-sm">
              <span className="text-stone-500 dark:text-stone-400">Progresso até o nível {stats.level + 1}</span>
              <span className="font-bold">
                {stats.xp_into_level}/{stats.xp_per_level} XP
              </span>
            </div>
            <ProgressBar value={(stats.xp_into_level / stats.xp_per_level) * 100} label="Progresso do nível" color="bg-sky-500" />
          </div>

          <div className="mt-3 rounded-2xl border-2 border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900">
            <p className="mb-3 font-bold">Meta diária</p>
            <div className="grid grid-cols-4 gap-2">
              {GOALS.map((goal) => (
                <button
                  key={goal}
                  type="button"
                  disabled={changeGoal.isPending}
                  onClick={() => changeGoal.mutate(goal)}
                  className={`rounded-xl border-2 px-2 py-2 font-extrabold transition ${
                    stats.daily_goal_xp === goal
                      ? "border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                      : "border-stone-300 text-stone-600 dark:border-stone-700 dark:text-stone-300"
                  }`}
                >
                  {goal} XP
                </button>
              ))}
            </div>
            {changeGoal.isError && (
              <p role="alert" className="mt-2 text-sm font-semibold text-red-700 dark:text-red-300">
                {changeGoal.error.message}
              </p>
            )}
          </div>
        </>
      )}

      <div className="mt-3 rounded-2xl border-2 border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900">
        <p className="text-sm text-stone-500 dark:text-stone-400">Instrumento</p>
        <p className="font-bold">Flauta doce soprano barroca</p>
      </div>

      <button
        type="button"
        onClick={logout}
        className="mt-8 flex w-full items-center justify-center gap-2 rounded-2xl border-2 border-b-4 border-red-400 px-4 py-3 font-extrabold uppercase tracking-wide text-red-600 transition active:translate-y-0.5 dark:text-red-400"
      >
        <LogOut size={20} aria-hidden="true" /> Sair
      </button>
    </div>
  );
}
