import { Navigate, Route, Routes } from "react-router";

import RequireAuth from "./auth/RequireAuth";
import AppLayout from "./components/AppLayout";
import LoginPage from "./pages/LoginPage";
import LearnPage from "./pages/LearnPage";
import LessonPage from "./pages/LessonPage";
import ProfilePage from "./pages/ProfilePage";
import ComingSoonPage from "./pages/ComingSoonPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Tudo aqui dentro exige login */}
      <Route element={<RequireAuth />}>
        {/* Telas com menu de navegação */}
        <Route element={<AppLayout />}>
          <Route index element={<LearnPage />} />
          <Route
            path="praticar"
            element={<ComingSoonPage title="Praticar" text="Treino de notas, ritmo com metrônomo e ferramentas musicais." />}
          />
          <Route
            path="musicas"
            element={<ComingSoonPage title="Músicas" text="Repertório com partituras e desafios de execução." />}
          />
          <Route
            path="progresso"
            element={<ComingSoonPage title="Progresso" text="XP, ofensivas, estatísticas e conquistas." />}
          />
          <Route
            path="comunidade"
            element={<ComingSoonPage title="Comunidade" text="Publicações, curtidas e comentários dos alunos." />}
          />
          <Route path="perfil" element={<ProfilePage />} />
        </Route>

        {/* Lição em tela cheia, sem menu */}
        <Route path="licao/:lessonId" element={<LessonPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
