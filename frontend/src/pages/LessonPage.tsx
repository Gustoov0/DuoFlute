import { useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Flame, Target, Trophy, X, Zap } from "lucide-react";

import ExerciseView from "../components/ExerciseView";
import ProgressBar from "../components/ProgressBar";
import Spinner from "../components/Spinner";
import { api } from "../lib/api";
import { useLesson, useLessonStatuses, useNotes } from "../lib/queries";
import type { AnswerResult, LessonResult } from "../lib/types";

// Tipos de exercício que o servidor corrige automaticamente
const GRADED = new Set(["multipla_escolha", "identificar_digitacao", "ouvir_e_reconhecer"]);

const BIG_BUTTON =
  "w-full rounded-2xl border-b-4 px-4 py-3 font-extrabold uppercase tracking-wide text-white transition active:translate-y-0.5 active:border-b-0 disabled:opacity-50";
const GREEN = "border-emerald-700 bg-emerald-500";

/**
 * O "key" faz o React recriar a lição do zero quando o id muda
 * (ex.: ao clicar em "Próxima lição"), zerando todo o estado.
 */
export default function LessonPage() {
  const { lessonId } = useParams();
  return <LessonRunner key={lessonId} id={Number(lessonId)} />;
}

function Centered({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      {children}
    </div>
  );
}

function LessonRunner({ id }: { id: number }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const lesson = useLesson(id);
  const notesQuery = useNotes();
  const statuses = useLessonStatuses();

  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [finished, setFinished] = useState(false);

  // Envia a resposta ao servidor, que confere com o gabarito e registra a tentativa
  const check = useMutation({
    mutationFn: (v: { exerciseId: number; answer: string }) =>
      api<AnswerResult>(`/learning/exercises/${v.exerciseId}/answer`, {
        method: "POST",
        body: { answer: v.answer },
      }),
    onSuccess: (data) => setResult(data),
  });

  // Conclui a lição: o servidor calcula acertos, XP, ofensiva e meta
  const complete = useMutation({
    mutationFn: () => api<LessonResult>(`/progress/lessons/${id}/complete`, { method: "POST" }),
    onSuccess: async () => {
      // Atualiza trilha e cabeçalho com os novos dados
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["summary"] }),
        queryClient.invalidateQueries({ queryKey: ["lessonStatuses"] }),
        queryClient.invalidateQueries({ queryKey: ["me"] }),
        queryClient.invalidateQueries({ queryKey: ["ranking"] }),
      ]);
    },
  });

  const backToPath = () => navigate("/");

  if (lesson.isPending || notesQuery.isPending || statuses.isPending) {
    return (
      <Centered>
        <Spinner />
      </Centered>
    );
  }

  const notes = notesQuery.data;
  const exercises = lesson.data?.exercises ?? [];
  const exercise = exercises[index];

  if (lesson.isError || !notes || !exercise) {
    return (
      <Centered>
        <p className="font-semibold">Não foi possível abrir esta lição.</p>
        <button type="button" onClick={backToPath} className={`${BIG_BUTTON} max-w-xs ${GREEN}`}>
          Voltar à trilha
        </button>
      </Centered>
    );
  }

  // O servidor também bloqueia, mas avisamos o aluno antes de começar
  if (!finished && statuses.data?.get(id)?.status === "bloqueada") {
    return (
      <Centered>
        <h1 className="text-2xl font-extrabold">Lição bloqueada</h1>
        <p className="text-stone-600 dark:text-stone-300">Conclua as lições anteriores para liberar esta.</p>
        <button type="button" onClick={backToPath} className={`${BIG_BUTTON} max-w-xs ${GREEN}`}>
          Voltar à trilha
        </button>
      </Centered>
    );
  }

  function next() {
    setSelected(null);
    setResult(null);
    check.reset();
    if (index + 1 >= exercises.length) {
      setFinished(true);
      complete.mutate();
    } else {
      setIndex(index + 1);
    }
  }

  // ---------- Tela final ----------
  if (finished) {
    if (complete.isError) {
      return (
        <Centered>
          <p role="alert" className="font-semibold text-red-700 dark:text-red-300">
            {complete.error.message}
          </p>
          <button type="button" onClick={() => complete.mutate()} className={`${BIG_BUTTON} max-w-xs ${GREEN}`}>
            Tentar de novo
          </button>
          <button type="button" onClick={backToPath} className="font-semibold text-sky-600 dark:text-sky-400">
            Voltar à trilha
          </button>
        </Centered>
      );
    }
    if (!complete.data) {
      return (
        <Centered>
          <Spinner />
          <p className="text-stone-500">Salvando seu progresso...</p>
        </Centered>
      );
    }
    return <ResultScreen result={complete.data} onBack={backToPath} onNext={(lessonId) => navigate(`/licao/${lessonId}`)} />;
  }

  // ---------- Botões da barra inferior ----------
  const isGraded = GRADED.has(exercise.exercise_type);
  let actions: ReactNode;
  if (exercise.exercise_type === "executar") {
    actions = (
      <div className="flex gap-3">
        <button type="button" onClick={next} className={`${BIG_BUTTON} border-stone-500 bg-stone-400`}>
          Preciso treinar
        </button>
        <button type="button" onClick={next} className={`${BIG_BUTTON} ${GREEN}`}>
          Consegui!
        </button>
      </div>
    );
  } else if (!isGraded) {
    actions = (
      <button type="button" onClick={next} className={`${BIG_BUTTON} ${GREEN}`}>
        Continuar
      </button>
    );
  } else if (!result) {
    actions = (
      <button
        type="button"
        disabled={!selected || check.isPending}
        onClick={() => selected && check.mutate({ exerciseId: exercise.id, answer: selected })}
        className={`${BIG_BUTTON} ${GREEN}`}
      >
        Verificar
      </button>
    );
  } else {
    actions = (
      <button
        type="button"
        onClick={next}
        className={`${BIG_BUTTON} ${result.correct ? GREEN : "border-red-700 bg-red-500"}`}
      >
        Continuar
      </button>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Topo: fechar + barra de progresso */}
      <header className="mx-auto flex w-full max-w-2xl items-center gap-4 px-4 py-4">
        <button type="button" onClick={backToPath} aria-label="Sair da lição" className="text-stone-500">
          <X size={28} />
        </button>
        <ProgressBar value={(index / exercises.length) * 100} label="Progresso da lição" />
      </header>

      {/* Exercício */}
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-6">
        <ExerciseView exercise={exercise} notes={notes} selected={selected} onSelect={setSelected} result={result} />
      </main>

      {/* Rodapé: feedback e botões */}
      <footer
        className={`border-t px-4 py-4 ${
          result
            ? result.correct
              ? "border-emerald-200 bg-emerald-100 dark:border-emerald-900 dark:bg-emerald-950"
              : "border-red-200 bg-red-100 dark:border-red-900 dark:bg-red-950"
            : "border-stone-200 dark:border-stone-800"
        }`}
      >
        <div className="mx-auto flex max-w-2xl flex-col gap-3">
          {result && (
            <p className={`text-lg font-extrabold ${result.correct ? "text-emerald-800 dark:text-emerald-200" : "text-red-800 dark:text-red-200"}`}>
              {result.correct ? "Muito bem!" : "Não foi dessa vez. A resposta correta está em verde."}
            </p>
          )}
          {check.isError && (
            <p role="alert" className="font-semibold text-red-700 dark:text-red-300">
              {check.error.message}
            </p>
          )}
          {actions}
        </div>
      </footer>
    </div>
  );
}

function ResultScreen({
  result,
  onBack,
  onNext,
}: {
  result: LessonResult;
  onBack: () => void;
  onNext: (lessonId: number) => void;
}) {
  const goalPercent = (result.xp_today / result.daily_goal_xp) * 100;

  const cards = [
    {
      icon: <Zap size={22} className="text-amber-500" aria-hidden="true" />,
      label: "XP ganho",
      value: result.first_completion ? `+${result.xp_earned}` : "+0",
    },
    {
      icon: <Target size={22} className="text-sky-500" aria-hidden="true" />,
      label: "Precisão",
      value: result.total > 0 ? `${result.score}%` : "—",
    },
    {
      icon: <Flame size={22} className="text-orange-500" aria-hidden="true" />,
      label: "Ofensiva",
      value: `${result.current_streak} ${result.current_streak === 1 ? "dia" : "dias"}`,
    },
  ];

  const messages = [
    result.perfect && "Perfeito! Você ganhou um bônus de XP.",
    result.streak_increased && `Ofensiva de ${result.current_streak} ${result.current_streak === 1 ? "dia" : "dias"}!`,
    result.goal_reached_now && "Meta diária batida!",
    result.leveled_up && `Você subiu para o nível ${result.level}!`,
    !result.first_completion && "Lição revisada. O XP só é concedido na primeira conclusão.",
  ].filter((m): m is string => typeof m === "string");

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-6 px-4 text-center">
      <Trophy size={72} className="text-amber-500" aria-hidden="true" />
      <h1 className="text-3xl font-extrabold">Lição concluída!</h1>

      <div className="grid w-full grid-cols-3 gap-3">
        {cards.map((card) => (
          <div key={card.label} className="rounded-2xl border-2 border-stone-200 bg-white p-3 dark:border-stone-800 dark:bg-stone-900">
            <div className="flex justify-center">{card.icon}</div>
            <p className="mt-1 text-xl font-extrabold">{card.value}</p>
            <p className="text-xs text-stone-500 dark:text-stone-400">{card.label}</p>
          </div>
        ))}
      </div>

      {messages.length > 0 && (
        <ul className="w-full space-y-2">
          {messages.map((message) => (
            <li key={message} className="rounded-xl bg-emerald-100 px-4 py-2 font-semibold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200">
              {message}
            </li>
          ))}
        </ul>
      )}

      <div className="w-full">
        <div className="mb-1 flex justify-between text-sm font-bold">
          <span>Meta de hoje</span>
          <span>
            {Math.min(result.xp_today, result.daily_goal_xp)}/{result.daily_goal_xp} XP
          </span>
        </div>
        <ProgressBar value={goalPercent} label="Meta diária de XP" color="bg-yellow-500" />
      </div>

      <div className="flex w-full flex-col gap-3">
        {result.next_lesson_id !== null && (
          <button type="button" onClick={() => onNext(result.next_lesson_id!)} className={`${BIG_BUTTON} ${GREEN}`}>
            Próxima lição
          </button>
        )}
        <button
          type="button"
          onClick={onBack}
          className="rounded-2xl border-2 border-b-4 border-stone-300 px-4 py-3 font-extrabold uppercase tracking-wide text-stone-600 transition active:translate-y-0.5 dark:border-stone-700 dark:text-stone-300"
        >
          Voltar à trilha
        </button>
      </div>
    </div>
  );
}