import { useNavigate } from "react-router";
import {
  BookOpen,
  Check,
  Eye,
  Flame,
  Lock,
  Music,
  RefreshCw,
  Shuffle,
  Trophy,
  Zap,
  type LucideIcon,
} from "lucide-react";

import ProgressBar from "../components/ProgressBar";
import Spinner from "../components/Spinner";
import { useAuth } from "../auth/AuthContext";
import { useLessonStatuses, usePath, useSummary } from "../lib/queries";

// Deslocamento horizontal de cada lição, para a trilha formar uma curva
const OFFSETS = [0, 40, 64, 40, 0, -40, -64, -40];

const LESSON_STYLES: Record<string, { icon: LucideIcon; color: string }> = {
  apresentacao: { icon: BookOpen, color: "border-emerald-700 bg-emerald-500" },
  reconhecimento: { icon: Eye, color: "border-sky-700 bg-sky-500" },
  pratica: { icon: Music, color: "border-violet-700 bg-violet-500" },
  combinacao: { icon: Shuffle, color: "border-pink-700 bg-pink-500" },
  revisao: { icon: RefreshCw, color: "border-teal-700 bg-teal-500" },
  desafio: { icon: Trophy, color: "border-orange-700 bg-orange-500" },
};

const DONE_STYLE = "border-yellow-600 bg-yellow-500";
const LOCKED_STYLE = "border-stone-400 bg-stone-300 dark:border-stone-600 dark:bg-stone-700";

export default function LearnPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const path = usePath();
  const statuses = useLessonStatuses();
  const summary = useSummary();

  // Const local: o TypeScript mantém o "já carregou" dentro das funções abaixo
  const statusMap = statuses.data;

  // A lição atual é a primeira disponível (o Map preserva a ordem da trilha)
  const currentId = statusMap
    ? [...statusMap.values()].find((item) => item.status === "disponivel")?.lesson_id
    : undefined;

  const stats = summary.data;
  const goalPercent = stats ? (stats.xp_today / stats.daily_goal_xp) * 100 : 0;

  return (
    <div>
      {/* Resumo do aluno */}
      <div className="sticky top-0 z-[5] -mx-4 mb-6 bg-stone-50/90 px-4 py-3 backdrop-blur dark:bg-stone-950/90">
        <div className="flex items-center justify-between">
          <span className="font-bold">Olá, {user?.display_name}</span>
          <div className="flex gap-4 font-bold">
            <span
              className={`flex items-center gap-1 ${stats?.active_today ? "text-orange-500" : "text-stone-400"}`}
              title="Ofensiva (dias seguidos)"
            >
              <Flame size={20} aria-hidden="true" /> {stats?.current_streak ?? 0}
            </span>
            <span className="flex items-center gap-1 text-amber-500" title="XP total">
              <Zap size={20} aria-hidden="true" /> {stats?.xp_total ?? 0}
            </span>
            <span className="text-sky-500" title="Nível">Nv. {stats?.level ?? 1}</span>
          </div>
        </div>

        {stats && (
          <div className="mt-2 flex items-center gap-3">
            <span className="whitespace-nowrap text-xs font-bold text-stone-500 dark:text-stone-400">
              Meta de hoje
            </span>
            <ProgressBar
              value={goalPercent}
              label="Meta diária de XP"
              color={stats.goal_met_today ? "bg-yellow-500" : "bg-emerald-500"}
            />
            <span className="whitespace-nowrap text-xs font-bold">
              {Math.min(stats.xp_today, stats.daily_goal_xp)}/{stats.daily_goal_xp}
              {stats.goal_met_today && <Check size={14} className="ml-1 inline text-yellow-600" aria-hidden="true" />}
            </span>
          </div>
        )}
      </div>

      {(path.isPending || statuses.isPending) && (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      )}

      {(path.isError || statuses.isError) && (
        <p role="alert" className="rounded-xl bg-red-100 p-4 font-semibold text-red-800 dark:bg-red-950 dark:text-red-200">
          Não foi possível carregar a trilha. {path.error?.message ?? statuses.error?.message}
        </p>
      )}

      {path.data?.length === 0 && (
        <p className="text-center text-stone-500">
          Nenhum conteúdo cadastrado ainda. Rode o seed: <code>python -m app.seeds.run</code>
        </p>
      )}

      {statusMap &&
        path.data?.map((section) => (
          <section key={section.id} className="mb-12">
            <h2 className="text-xl font-extrabold">{section.title}</h2>
            {section.description && (
              <p className="mb-4 text-stone-600 dark:text-stone-300">{section.description}</p>
            )}

            {section.units.map((unit) => {
              const doneCount = unit.lessons.filter(
                (lesson) => statusMap.get(lesson.id)?.status === "concluida",
              ).length;

              return (
                <div key={unit.id} className="mb-8">
                  <div className="flex items-center justify-between gap-3 rounded-2xl bg-emerald-600 p-4 text-white">
                    <div>
                      <h3 className="text-lg font-extrabold">{unit.title}</h3>
                      {unit.objective && <p className="text-sm text-emerald-50">{unit.objective}</p>}
                    </div>
                    <span className="whitespace-nowrap rounded-full bg-emerald-800/60 px-3 py-1 text-sm font-bold">
                      {doneCount}/{unit.lessons.length}
                    </span>
                  </div>

                  <div className="flex flex-col items-center gap-5 py-6">
                    {unit.lessons.map((lesson, i) => {
                      const status = statusMap.get(lesson.id)?.status ?? "bloqueada";
                      const base = LESSON_STYLES[lesson.lesson_type] ?? LESSON_STYLES.apresentacao;
                      const locked = status === "bloqueada";
                      const done = status === "concluida";
                      const current = lesson.id === currentId;
                      const Icon = locked ? Lock : done ? Check : base.icon;
                      const color = locked ? LOCKED_STYLE : done ? DONE_STYLE : base.color;
                      const stateLabel = locked ? "bloqueada" : done ? "concluída" : "disponível";

                      return (
                        <div
                          key={lesson.id}
                          className="flex flex-col items-center"
                          style={{ transform: `translateX(${OFFSETS[i % OFFSETS.length]}px)` }}
                        >
                          {current && (
                            <span className="mb-1 rounded-lg border-2 border-emerald-500 bg-white px-2 py-0.5 text-xs font-extrabold uppercase text-emerald-600 dark:bg-stone-900 dark:text-emerald-400">
                              Começar
                            </span>
                          )}
                          <button
                            type="button"
                            disabled={locked}
                            aria-label={`${lesson.title} (${stateLabel})`}
                            onClick={() => navigate(`/licao/${lesson.id}`)}
                            className={`flex h-16 w-16 items-center justify-center rounded-full border-b-4 text-white shadow-md transition active:translate-y-1 active:border-b-0 disabled:cursor-not-allowed disabled:shadow-none disabled:active:translate-y-0 disabled:active:border-b-4 ${color} ${
                              current ? "ring-4 ring-emerald-300 ring-offset-2 dark:ring-emerald-700 dark:ring-offset-stone-950" : ""
                            }`}
                          >
                            <Icon size={28} aria-hidden="true" />
                          </button>
                          <span
                            className={`mt-1.5 max-w-32 text-center text-xs font-semibold ${
                              locked ? "text-stone-400 dark:text-stone-500" : "text-stone-600 dark:text-stone-300"
                            }`}
                          >
                            {lesson.title}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </section>
        ))}
    </div>
  );
}
