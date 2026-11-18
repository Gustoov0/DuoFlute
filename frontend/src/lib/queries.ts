import { useQuery } from "@tanstack/react-query";

import { api } from "./api";
import type {
  LessonDetail,
  LessonProgress,
  Note,
  ProgressSummary,
  Section,
  WeeklyRanking,
} from "./types";

export function usePath() {
  return useQuery({
    queryKey: ["path"],
    queryFn: () => api<Section[]>("/learning/path"),
  });
}

export function useLesson(id: number) {
  return useQuery({
    queryKey: ["lesson", id],
    queryFn: () => api<LessonDetail>(`/learning/lessons/${id}`),
    enabled: Number.isFinite(id),
  });
}

/** Notas indexadas por id (usadas para tocar sons e desenhar digitações). */
export function useNotes() {
  return useQuery({
    queryKey: ["notes"],
    queryFn: () => api<Note[]>("/learning/notes"),
    staleTime: Infinity,
    select: (list) => new Map(list.map((note) => [note.id, note] as const)),
  });
}

/** XP, nível, ofensiva e meta diária. */
export function useSummary() {
  return useQuery({
    queryKey: ["summary"],
    queryFn: () => api<ProgressSummary>("/progress/summary"),
  });
}

/** Estado de cada lição (concluída, disponível, bloqueada), indexado pelo id da lição. */
export function useLessonStatuses() {
  return useQuery({
    queryKey: ["lessonStatuses"],
    queryFn: () => api<LessonProgress[]>("/progress/lessons"),
    select: (list) => new Map(list.map((item) => [item.lesson_id, item] as const)),
  });
}

/** Ranking semanal de XP. Atualiza sozinho a cada 15 segundos. */
export function useWeeklyRanking() {
  return useQuery({
    queryKey: ["ranking", "weekly"],
    queryFn: () => api<WeeklyRanking>("/ranking/weekly?limit=10"),
    refetchInterval: 15_000,
  });
}