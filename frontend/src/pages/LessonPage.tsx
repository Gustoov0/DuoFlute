import { useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router";
import { useMutation } from "@tanstack/react-query";
import { Trophy, X } from "lucide-react";

import ExerciseView from "../components/ExerciseView";
import Spinner from "../components/Spinner";
import { api } from "../lib/api";
import { useLesson, useNotes } from "../lib/queries";
import type { AnswerResult } from "../lib/types";

// Tipos de exercício que o servidor corrige automaticamente
const GRADED = new Set(["multipla_escolha", "identificar_digitacao", "ouvir_e_reconhecer"]);

const BIG_BUTTON =
  "w-full rounded-2xl border-b-4 px-4 py-3 font-extrabold uppercase tracking-wide text-white transition active:translate-y-0.5 active:border-b-0 disabled:opacity-50";

export default function LessonPage() {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const lesson = useLesson(Number(lessonId));
  const notesQuery = useNotes();

  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [finished, setFinished] = useState(false);

  // Envia a resposta ao servidor, que confere com o gabarito
  const check = useMutation({
    mutationFn: (v: { exerciseId: number; answer: string }) =>
      api<AnswerResult>(`/learning/exercises/${v.exerciseId}/answer`, {
        method: "POST",
        body: { answer: v.answer },
      }),
    onSuccess: (data) => {
      setResult(data);
      if (data.correct) setCorrectCount((n) => n + 1);
    },
  });

  const backToPath = () => navigate("/");

  if (lesson.isPending || notesQuery.isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const notes = notesQuery.data;
  const exercises = lesson.data?.exercises ?? [];
  const exercise = exercises[index];

  if (lesson.isError || !notes || !exercise) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="font-semibold">Não foi possível abrir esta lição.</p>
        <button type="button" onClick={backToPath} className={`${BIG_BUTTON} max-w-xs border-emerald-700 bg-emerald-500`}>
          Voltar à trilha
        </button>
      </div>
    );
  }

  const gradedTotal = exercises.filter((e) => GRADED.has(e.exercise_type)).length;
  const isGraded = GRADED.has(exercise.exercise_type);

  function next() {
    setSelected(null);
    setResult(null);
    check.reset();
    if (index + 1 >= exercises.length) setFinished(true);
    else setIndex(index + 1);
  }

  // ---------- Tela final ----------
  if (finished) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-4 text-center">
        <Trophy size={72} className="text-amber-500" aria-hidden="true" />
        <h1 className="text-3xl font-extrabold">Lição concluída!</h1>
        {gradedTotal > 0 && (
          <p className="text-xl">
            Você acertou <strong>{correctCount}</strong> de <strong>{gradedTotal}</strong> perguntas.
          </p>
        )}
        <p className="text-sm text-stone-500 dark:text-stone-400">
          O registro de XP e progresso será ativado no próximo passo do projeto.
        </p>
        <button type="button" onClick={backToPath} className={`${BIG_BUTTON} max-w-xs border-emerald-700 bg-emerald-500`}>
          Voltar à trilha
        </button>
      </div>
    );
  }

  // ---------- Botões da barra inferior ----------
  let actions: ReactNode;
  if (!isGraded && exercise.exercise_type === "executar") {
    actions = (
      <div className="flex gap-3">
        <button type="button" onClick={next} className={`${BIG_BUTTON} border-stone-500 bg-stone-400`}>
          Preciso treinar
        </button>
        <button type="button" onClick={next} className={`${BIG_BUTTON} border-emerald-700 bg-emerald-500`}>
          Consegui!
        </button>
      </div>
    );
  } else if (!isGraded) {
    actions = (
      <button type="button" onClick={next} className={`${BIG_BUTTON} border-emerald-700 bg-emerald-500`}>
        Continuar
      </button>
    );
  } else if (!result) {
    actions = (
      <button
        type="button"
        disabled={!selected || check.isPending}
        onClick={() => selected && check.mutate({ exerciseId: exercise.id, answer: selected })}
        className={`${BIG_BUTTON} border-emerald-700 bg-emerald-500`}
      >
        Verificar
      </button>
    );
  } else {
    actions = (
      <button
        type="button"
        onClick={next}
        className={`${BIG_BUTTON} ${result.correct ? "border-emerald-700 bg-emerald-500" : "border-red-700 bg-red-500"}`}
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
        <div className="h-4 flex-1 overflow-hidden rounded-full bg-stone-200 dark:bg-stone-800">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all"
            style={{ width: `${(index / exercises.length) * 100}%` }}
          />
        </div>
      </header>

      {/* Exercício */}
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-6">
        <ExerciseView
          exercise={exercise}
          notes={notes}
          selected={selected}
          onSelect={setSelected}
          result={result}
        />
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
