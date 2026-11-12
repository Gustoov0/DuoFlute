import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { Music } from "lucide-react";

import { useAuth } from "../auth/AuthContext";

const INPUT =
  "w-full rounded-xl border-2 border-stone-300 bg-white px-4 py-3 outline-none focus:border-emerald-500 dark:border-stone-700 dark:bg-stone-900";

export default function LoginPage() {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Depois do login, o usuário é carregado e seguimos para a trilha
  useEffect(() => {
    if (user) navigate("/", { replace: true });
  }, [user, navigate]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "register") await register(email, password, name);
      else await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro inesperado.");
    } finally {
      setBusy(false);
    }
  }

  const isRegister = mode === "register";

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2 text-emerald-600 dark:text-emerald-400">
          <Music size={48} aria-hidden="true" />
          <h1 className="text-4xl font-extrabold">DuoFlute</h1>
          <p className="text-center text-stone-600 dark:text-stone-300">
            Aprenda flauta doce em lições curtas e interativas.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <h2 className="text-xl font-bold">{isRegister ? "Criar conta" : "Entrar"}</h2>

          {isRegister && (
            <input
              className={INPUT}
              placeholder="Como quer ser chamado?"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={100}
              required
            />
          )}
          <input
            className={INPUT}
            type="email"
            placeholder="E-mail"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className={INPUT}
            type="password"
            placeholder={isRegister ? "Senha (mínimo 8 caracteres)" : "Senha"}
            autoComplete={isRegister ? "new-password" : "current-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={isRegister ? 8 : undefined}
            required
          />

          {error && (
            <p role="alert" className="rounded-xl bg-red-100 px-4 py-3 text-sm font-semibold text-red-800 dark:bg-red-950 dark:text-red-200">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="rounded-2xl border-b-4 border-emerald-700 bg-emerald-500 px-4 py-3 font-extrabold uppercase tracking-wide text-white transition active:translate-y-0.5 active:border-b-0 disabled:opacity-60"
          >
            {busy ? "Aguarde..." : isRegister ? "Criar conta" : "Entrar"}
          </button>
        </form>

        <button
          type="button"
          onClick={() => {
            setMode(isRegister ? "login" : "register");
            setError(null);
          }}
          className="mt-4 w-full text-center font-semibold text-sky-600 dark:text-sky-400"
        >
          {isRegister ? "Já tenho conta" : "Ainda não tenho conta"}
        </button>
      </div>
    </div>
  );
}
