// Tipos que espelham o que a API devolve.

export interface User {
  id: number;
  email: string;
  display_name: string;
  avatar_url: string | null;
  role: string;
  daily_goal_xp: number;
  xp_total: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  profile_public: boolean;
  created_at: string;
}

/** 0 = aberto, 1 = fechado, 2 = meio furo. Chaves: thumb, h1 ... h7 */
export type Holes = Record<string, number>;

export interface Note {
  id: number;
  name_pt: string;
  scientific_name: string;
  frequency_hz: number;
  staff_position: number;
  introduced_in_unit_id: number | null;
  fingering: { holes: Holes } | null;
}

export interface LessonSummary {
  id: number;
  title: string;
  lesson_type: string;
  position: number;
  xp_reward: number;
  is_essential: boolean;
}

export interface Unit {
  id: number;
  title: string;
  objective: string | null;
  position: number;
  lessons: LessonSummary[];
}

export interface Section {
  id: number;
  title: string;
  description: string | null;
  position: number;
  units: Unit[];
}

export type ExerciseType =
  | "informativo"
  | "multipla_escolha"
  | "identificar_digitacao"
  | "ouvir_e_reconhecer"
  | "executar";

export interface Exercise {
  id: number;
  exercise_type: ExerciseType;
  position: number;
  difficulty: number;
  content: Record<string, unknown>;
}

export interface LessonDetail extends LessonSummary {
  unit_id: number;
  exercises: Exercise[];
}

export interface AnswerResult {
  correct: boolean;
  correct_answer: string;
}

// Formatos do campo "content" de cada tipo de exercício
export interface InfoContent {
  title: string;
  text: string;
  note_id?: number;
  show?: "nota_e_pauta" | "digitacao";
}

export interface ChoiceOption {
  id: string;
  label?: string;
  holes?: Holes;
}

export interface ChoiceContent {
  prompt: string;
  options: ChoiceOption[];
  audio?: { note_ids: number[] };
}

export interface PlayContent {
  prompt: string;
  assessment: string;
  bpm: number;
  sequence: { note_id: number; duration: string }[];
  checklist?: string[];
}

// ---------- Progresso e gamificação ----------
export interface ProgressSummary {
  xp_total: number;
  level: number;
  xp_into_level: number;
  xp_per_level: number;
  current_streak: number;
  longest_streak: number;
  daily_goal_xp: number;
  xp_today: number;
  goal_met_today: boolean;
  active_today: boolean;
}

export type LessonStatus = "concluida" | "disponivel" | "bloqueada";

export interface LessonProgress {
  lesson_id: number;
  status: LessonStatus;
  best_score: number | null;
  attempts: number | null;
  completed_at: string | null;
}

export interface LessonResult {
  xp_earned: number;
  first_completion: boolean;
  perfect: boolean;
  score: number;
  correct: number;
  total: number;
  xp_total: number;
  level: number;
  leveled_up: boolean;
  current_streak: number;
  streak_increased: boolean;
  xp_today: number;
  daily_goal_xp: number;
  goal_reached_now: boolean;
  next_lesson_id: number | null;
}

// ---------- Ranking ----------
export interface RankingEntry {
  rank: number;
  user_id: number;
  display_name: string;
  xp: number;
  is_me: boolean;
}

export interface WeeklyRanking {
  week_start: string;
  week_end: string;
  source: "redis" | "database";
  entries: RankingEntry[];
  me: { rank: number; xp: number } | null;
}