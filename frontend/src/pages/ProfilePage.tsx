import { LogOut } from "lucide-react";

import { useAuth } from "../auth/AuthContext";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const stats = [
    { label: "Nível", value: user.level },
    { label: "XP total", value: user.xp_total },
    { label: "Ofensiva atual", value: `${user.current_streak} dias` },
    { label: "Maior ofensiva", value: `${user.longest_streak} dias` },
    { label: "Meta diária", value: `${user.daily_goal_xp} XP` },
  ];

  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500 text-3xl font-extrabold text-white">
          {user.display_name.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-extrabold">{user.display_name}</h1>
          <p className="text-stone-500 dark:text-stone-400">{user.email}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-2xl border-2 border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900">
            <p className="text-sm text-stone-500 dark:text-stone-400">{stat.label}</p>
            <p className="text-xl font-extrabold">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-2xl border-2 border-stone-200 bg-white p-4 dark:border-stone-800 dark:bg-stone-900">
        <p className="text-sm text-stone-500 dark:text-stone-400">Instrumento</p>
        <p className="font-bold">Flauta doce soprano barroca</p>
      </div>

      <button
        type="button"
        onClick={logout}
        className="mt-8 flex w-full items-center justify-center gap-2 rounded-2xl border-2 border-b-4 border-red-400 px-4 py-3 font-extrabold uppercase tracking-wide text-red-600 transition active:translate-y-0.5 dark:text-red-400"
      >
        <LogOut size={20} aria-hidden="true" /> Sair
      </button>
    </div>
  );
}
