import { useQuery } from "@tanstack/react-query";

import { api } from "./api";
import type { LessonDetail, Note, Section } from "./types";

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