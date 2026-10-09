"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, LockKeyhole, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";
import { CloudOrbit } from "@/components/cloud-orbit";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useLanguage } from "@/lib/i18n";
import { login, register } from "@/lib/auth";

export function LoginForm({ onAuthenticated }: { onAuthenticated: () => void }) {
  const { t } = useLanguage();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [organizationName, setOrganizationName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (mode === "register") {
        await register(organizationName, email, password);
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

  function toggleMode() {
    setError(null);
    setMode((m) => (m === "register" ? "login" : "register"));
  }

  const inputClass = "field-input";

  return (
    <main className="auth-layout">
      <aside className="auth-story">
        <Brand inverse />
        <div className="auth-story-content">
          <p className="eyebrow">{t("auth_eyebrow")}</p>
          <h2>{t("auth_heading")}</h2>
          <p className="section-description">{t("auth_description")}</p>
          <CloudOrbit />
        </div>
        <p className="auth-story-footer"><ShieldCheck size={13} />{t("landing_trust_readonly")}<span className="mx-2">·</span>{t("landing_trust_keys")}</p>
      </aside>
      <div className="auth-form-side">
        <div className="auth-topbar"><Link href="/" className="text-link"><ArrowLeft size={14} />{t("auth_back")}</Link><LanguageSwitcher /></div>
        <div className="auth-form-container">
          <div className="auth-mobile-brand"><Brand /></div>
          <div className="auth-form-icon" aria-hidden="true"><LockKeyhole size={20} strokeWidth={1.5} /></div>

        <form onSubmit={handleSubmit} aria-busy={submitting}>
          <div>
            <h1>
              {mode === "register" ? t("auth_register_title") : t("auth_login_title")}
            </h1>
            <p className="auth-subtitle">{mode === "register" ? t("auth_register_subtitle") : t("auth_login_subtitle")}</p>
          </div>

          {mode === "register" && (
            <div>
              <label htmlFor="organizationName" className="field-label">
                {t("auth_org_name_label")}
              </label>
              <input
                id="organizationName"
                type="text"
                required
                autoComplete="organization"
                value={organizationName}
                onChange={(e) => setOrganizationName(e.target.value)}
                className={inputClass}
              />
            </div>
          )}

          <div>
            <label htmlFor="email" className="field-label">
              {t("auth_email_label")}
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputClass}
            />
          </div>

          <div>
            <label htmlFor="password" className="field-label">
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
            <p role="alert" className="text-sm" style={{ color: "var(--status-critical)" }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="button button-primary mt-1 w-full"
          >
            {submitting
              ? t("auth_submitting")
              : mode === "register"
                ? t("auth_submit_register")
                : t("auth_submit_login")}
              <ArrowRight size={15} aria-hidden="true" />
          </button>

          <button
            type="button"
            onClick={toggleMode}
            disabled={submitting}
            className="auth-switch"
          >
            {mode === "register" ? t("auth_toggle_to_login") : t("auth_toggle_to_register")}
          </button>
        </form>
        </div>
        <p className="auth-privacy"><ShieldCheck size={13} />{t("auth_secure")}</p>
      </div>
    </main>
  );
}
