import { Play } from "lucide-react";

import { playNote, playSequence } from "../lib/audio";
import type {
  AnswerResult,
  ChoiceContent,
  Exercise,
  InfoContent,
  Note,
  PlayContent,
} from "../lib/types";
import AudioButton from "./AudioButton";
import FingeringDiagram from "./FingeringDiagram";
import StaffNote from "./StaffNote";

interface Props {
  exercise: Exercise;
  notes: Map<number, Note>;
  selected: string | null;
  onSelect: (id: string) => void;
  result: AnswerResult | null;
}

function contentOf<T>(exercise: Exercise): T {
  return exercise.content as unknown as T;
}

const OPTION_BASE =
  "w-full rounded-2xl border-2 border-b-4 p-4 text-left font-semibold transition active:translate-y-0.5 disabled:active:translate-y-0";
const OPTION_STYLES = {
  idle: "border-stone-300 bg-white hover:bg-stone-50 dark:border-stone-700 dark:bg-stone-900 dark:hover:bg-stone-800",
  selected: "border-sky-400 bg-sky-50 dark:bg-sky-950",
  correct: "border-emerald-500 bg-emerald-50 dark:bg-emerald-950",
  wrong: "border-red-500 bg-red-50 dark:bg-red-950",
} as const;

export default function ExerciseView({ exercise, notes, selected, onSelect, result }: Props) {
  function optionStyle(id: string): string {
    if (result) {
      if (id === result.correct_answer) return OPTION_STYLES.correct;
      if (id === selected) return OPTION_STYLES.wrong;
      return OPTION_STYLES.idle;
    }
    return selected === id ? OPTION_STYLES.selected : OPTION_STYLES.idle;
  }

  function playNotesById(ids: number[]) {
    ids.forEach((id) => {
      const note = notes.get(id);
      if (note) playNote(note.frequency_hz);
    });
  }

  // ---------- Cartão informativo ----------
  if (exercise.exercise_type === "informativo") {
    const c = contentOf<InfoContent>(exercise);
    const note = c.note_id ? notes.get(c.note_id) : undefined;
    return (
      <div className="flex flex-col items-center gap-6 text-center">
        <div>
          <h2 className="text-2xl font-extrabold">{c.title}</h2>
          <p className="mt-3 text-lg leading-relaxed text-stone-600 dark:text-stone-300">{c.text}</p>
        </div>

        {note && c.show === "nota_e_pauta" && (
          <>
            <StaffNote position={note.staff_position} />
            <AudioButton label={`Ouvir ${note.name_pt}`} onClick={() => playNote(note.frequency_hz)} />
          </>
        )}

        {note?.fingering && c.show === "digitacao" && (
          <>
            <FingeringDiagram holes={note.fingering.holes} size="lg" showLabels />
            <AudioButton label={`Ouvir ${note.name_pt}`} onClick={() => playNote(note.frequency_hz)} />
          </>
        )}
      </div>
    );
  }

  // ---------- Perguntas com alternativas ----------
  if (
    exercise.exercise_type === "multipla_escolha" ||
    exercise.exercise_type === "identificar_digitacao" ||
    exercise.exercise_type === "ouvir_e_reconhecer"
  ) {
    const c = contentOf<ChoiceContent>(exercise);
    const asDiagrams = exercise.exercise_type === "identificar_digitacao";

    return (
      <div className="flex flex-col gap-6">
        <h2 className="text-2xl font-extrabold">{c.prompt}</h2>

        {c.audio && (
          <div className="flex justify-center">
            <AudioButton label="Ouvir o som" onClick={() => playNotesById(c.audio!.note_ids)} />
          </div>
        )}

        <div className={asDiagrams ? "grid grid-cols-2 gap-3" : "flex flex-col gap-3"}>
          {c.options.map((option) => (
            <button
              key={option.id}
              type="button"
              disabled={!!result}
              onClick={() => onSelect(option.id)}
              className={`${OPTION_BASE} ${optionStyle(option.id)} ${asDiagrams ? "flex justify-center" : ""}`}
            >
              {asDiagrams && option.holes ? (
                <FingeringDiagram holes={option.holes} size="md" />
              ) : (
                option.label
              )}
            </button>
          ))}
        </div>
      </div>
    );
  }

  // ---------- Atividade de execução (o aluno toca) ----------
  const c = contentOf<PlayContent>(exercise);
  const items = c.sequence
    .map((step) => ({ note: notes.get(step.note_id), duration: step.duration }))
    .filter((item): item is { note: Note; duration: string } => !!item.note);
  const uniqueNotes = [...new Map(items.map((item) => [item.note.id, item.note])).values()];

  return (
    <div className="flex flex-col items-center gap-6 text-center">
      <h2 className="text-2xl font-extrabold">{c.prompt}</h2>

      {items.length > 0 && (
        <>
          <div className="flex flex-wrap justify-center gap-2">
            {items.map((item, i) => (
              <span key={i} className="rounded-xl bg-stone-200 px-3 py-1 text-sm font-bold dark:bg-stone-800">
                {item.note.name_pt}
                <span className="ml-1 font-normal opacity-60">{item.duration}</span>
              </span>
            ))}
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            {uniqueNotes.map((note) =>
              note.fingering ? (
                <div key={note.id} className="flex flex-col items-center gap-1">
                  <FingeringDiagram holes={note.fingering.holes} size="sm" />
                  <span className="text-xs font-semibold">{note.name_pt}</span>
                </div>
              ) : null,
            )}
          </div>

          <button
            type="button"
            onClick={() =>
              playSequence(
                items.map((item) => ({ frequency: item.note.frequency_hz, duration: item.duration })),
                c.bpm,
              )
            }
            className="inline-flex items-center gap-2 rounded-2xl border-2 border-b-4 border-sky-400 bg-sky-50 px-4 py-2 font-semibold text-sky-700 transition active:translate-y-0.5 dark:bg-sky-950 dark:text-sky-300"
          >
            <Play size={20} aria-hidden="true" />
            Ouvir referência
          </button>
        </>
      )}

      {c.checklist && (
        <ul className="list-inside list-disc text-left text-stone-600 dark:text-stone-300">
          {c.checklist.map((entry) => (
            <li key={entry}>{entry}</li>
          ))}
        </ul>
      )}

      <p className="text-sm text-stone-500 dark:text-stone-400">
        Toque na sua flauta e depois avalie como foi. A análise automática pelo microfone ainda não está disponível.
      </p>
    </div>
  );
}
