"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "@/lib/i18n";
import { getAuthStatus, login, register } from "@/lib/auth";

export function LoginForm({ onAuthenticated }: { onAuthenticated: () => void }) {
  const { t } = useLanguage();
  const [mode, setMode] = useState<"loading" | "login" | "register">("loading");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function checkStatus() {
      try {
        const status = await getAuthStatus();
        if (!cancelled) setMode(status.registered ? "login" : "register");
      } catch {
        if (!cancelled) setMode("login");
      }
    }

    checkStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (mode === "register") {
        await register(email, password);
      } else {
        await login(email, password);
      }
      onAuthenticated();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  const inputClass =
    "w-full rounded-md border border-[color:var(--border-hairline)] bg-[color:var(--background)] px-3 py-2 text-sm outline-none focus:border-[color:var(--accent)]";

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-6">
        <div className="mb-6 flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-[color:var(--foreground)] text-sm font-semibold text-[color:var(--background)]">
            C
          </span>
          <span className="text-base font-semibold tracking-tight">Cloudheo</span>
        </div>

        {mode === "loading" ? (
          <p className="text-sm text-[color:var(--text-muted)]">{t("auth_checking")}</p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <h1 className="text-lg font-semibold tracking-tight">
                {mode === "register" ? t("auth_register_title") : t("auth_login_title")}
              </h1>
              {mode === "register" && (
                <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{t("auth_register_subtitle")}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="mb-1 block text-xs text-[color:var(--text-secondary)]">
                {t("auth_email_label")}
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputClass}
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1 block text-xs text-[color:var(--text-secondary)]">
                {t("auth_password_label")}
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={mode === "register" ? 8 : undefined}
                  autoComplete={mode === "register" ? "new-password" : "current-password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`${inputClass} pr-9`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? t("auth_hide_password") : t("auth_show_password")}
                  aria-pressed={showPassword}
                  className="absolute inset-y-0 right-0 flex w-9 items-center justify-center text-[color:var(--text-muted)] hover:text-[color:var(--text-secondary)]"
                >
                  {showPassword ? (
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                      <path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                      <line x1="2" y1="2" x2="22" y2="22" />
                    </svg>
                  ) : (
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {error && (
              <p className="text-sm" style={{ color: "var(--status-critical)" }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="rounded-md bg-[color:var(--foreground)] px-4 py-2 text-sm font-medium text-[color:var(--background)] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting
                ? t("auth_submitting")
                : mode === "register"
                  ? t("auth_submit_register")
                  : t("auth_submit_login")}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
