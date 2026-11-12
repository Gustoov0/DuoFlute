import { useNavigate } from "react-router";
import {
  BookOpen,
  Eye,
  Flame,
  Music,
  RefreshCw,
  Shuffle,
  Trophy,
  Zap,
  type LucideIcon,
} from "lucide-react";

import Spinner from "../components/Spinner";
import { useAuth } from "../auth/AuthContext";
import { usePath } from "../lib/queries";

// Deslocamento horizontal de cada lição, para a trilha formar uma curva
const OFFSETS = [0, 40, 64, 40, 0, -40, -64, -40];

const LESSON_STYLES: Record<string, { icon: LucideIcon; color: string }> = {
  apresentacao: { icon: BookOpen, color: "border-emerald-700 bg-emerald-500" },
  reconhecimento: { icon: Eye, color: "border-sky-700 bg-sky-500" },
  pratica: { icon: Music, color: "border-violet-700 bg-violet-500" },
  combinacao: { icon: Shuffle, color: "border-pink-700 bg-pink-500" },
  revisao: { icon: RefreshCw, color: "border-teal-700 bg-teal-500" },
  desafio: { icon: Trophy, color: "border-amber-600 bg-amber-400" },
};

export default function LearnPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const path = usePath();

  return (
    <div>
      {/* Resumo do aluno */}
      <div className="sticky top-0 z-[5] -mx-4 mb-6 flex items-center justify-between bg-stone-50/90 px-4 py-3 backdrop-blur dark:bg-stone-950/90">
        <span className="font-bold">Olá, {user?.display_name}</span>
        <div className="flex gap-4 font-bold">
          <span className="flex items-center gap-1 text-orange-500" title="Ofensiva (dias seguidos)">
            <Flame size={20} aria-hidden="true" /> {user?.current_streak ?? 0}
          </span>
          <span className="flex items-center gap-1 text-amber-500" title="XP total">
            <Zap size={20} aria-hidden="true" /> {user?.xp_total ?? 0}
          </span>
          <span className="text-sky-500" title="Nível">Nv. {user?.level ?? 1}</span>
        </div>
      </div>

      {path.isPending && (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      )}

      {path.isError && (
        <p role="alert" className="rounded-xl bg-red-100 p-4 font-semibold text-red-800 dark:bg-red-950 dark:text-red-200">
          Não foi possível carregar a trilha. {path.error.message}
        </p>
      )}

      {path.data?.length === 0 && (
        <p className="text-center text-stone-500">
          Nenhum conteúdo cadastrado ainda. Rode o seed: <code>python -m app.seeds.run</code>
        </p>
      )}

      {path.data?.map((section) => (
        <section key={section.id} className="mb-12">
          <h2 className="text-xl font-extrabold">{section.title}</h2>
          {section.description && (
            <p className="mb-4 text-stone-600 dark:text-stone-300">{section.description}</p>
          )}

          {section.units.map((unit) => (
            <div key={unit.id} className="mb-8">
              <div className="rounded-2xl bg-emerald-600 p-4 text-white">
                <h3 className="text-lg font-extrabold">{unit.title}</h3>
                {unit.objective && <p className="text-sm text-emerald-50">{unit.objective}</p>}
              </div>

              <div className="flex flex-col items-center gap-5 py-6">
                {unit.lessons.map((lesson, i) => {
                  const style = LESSON_STYLES[lesson.lesson_type] ?? LESSON_STYLES.apresentacao;
                  const Icon = style.icon;
                  return (
                    <div
                      key={lesson.id}
                      className="flex flex-col items-center"
                      style={{ transform: `translateX(${OFFSETS[i % OFFSETS.length]}px)` }}
                    >
                      <button
                        type="button"
                        aria-label={lesson.title}
                        onClick={() => navigate(`/licao/${lesson.id}`)}
                        className={`flex h-16 w-16 items-center justify-center rounded-full border-b-4 text-white shadow-md transition active:translate-y-1 active:border-b-0 ${style.color}`}
                      >
                        <Icon size={28} aria-hidden="true" />
                      </button>
                      <span className="mt-1.5 max-w-32 text-center text-xs font-semibold text-stone-600 dark:text-stone-300">
                        {lesson.title}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}
