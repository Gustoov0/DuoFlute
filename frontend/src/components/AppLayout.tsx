import { NavLink, Outlet } from "react-router";
import {
  BookOpen,
  BarChart3,
  Dumbbell,
  Music,
  User as UserIcon,
  Users,
  type LucideIcon,
} from "lucide-react";

const ITEMS: { to: string; label: string; icon: LucideIcon; end?: boolean }[] = [
  { to: "/", label: "Aprender", icon: BookOpen, end: true },
  { to: "/praticar", label: "Praticar", icon: Dumbbell },
  { to: "/musicas", label: "Músicas", icon: Music },
  { to: "/progresso", label: "Progresso", icon: BarChart3 },
  { to: "/comunidade", label: "Comunidade", icon: Users },
  { to: "/perfil", label: "Perfil", icon: UserIcon },
];

export default function AppLayout() {
  return (
    <div className="min-h-screen">
      {/* Menu lateral (telas grandes) */}
      <aside className="fixed inset-y-0 left-0 hidden w-56 flex-col border-r border-stone-200 bg-white p-4 md:flex dark:border-stone-800 dark:bg-stone-900">
        <div className="mb-6 flex items-center gap-2 px-2 text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
          <Music aria-hidden="true" /> DuoFlute
        </div>
        <nav className="flex flex-col gap-1">
          {ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 font-semibold ${
                  isActive
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                    : "text-stone-600 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"
                }`
              }
            >
              <Icon size={22} aria-hidden="true" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Conteúdo da página */}
      <main className="mx-auto max-w-xl px-4 pb-28 pt-6 md:ml-56 md:max-w-2xl md:pb-10">
        <Outlet />
      </main>

      {/* Menu inferior (celular) */}
      <nav className="fixed inset-x-0 bottom-0 z-10 flex border-t border-stone-200 bg-white md:hidden dark:border-stone-800 dark:bg-stone-900">
        {ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center gap-0.5 py-2 text-[11px] font-semibold ${
                isActive
                  ? "text-emerald-600 dark:text-emerald-400"
                  : "text-stone-500 dark:text-stone-400"
              }`
            }
          >
            <Icon size={22} aria-hidden="true" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
