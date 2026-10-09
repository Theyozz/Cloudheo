"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, ArrowRight, KeyRound, ShieldCheck } from "lucide-react";
import { Brand } from "@/components/brand";
import { CloudOrbit } from "@/components/cloud-orbit";
import { LanguageSwitcher } from "@/components/language-switcher";
import { ThemeSwitcher } from "@/components/theme";
import { useLanguage } from "@/lib/i18n";
import { resetPassword } from "@/lib/auth";

export function ResetPasswordForm() {
  const { t } = useLanguage();
  const token = useSearchParams().get("token");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError(t("auth_reset_mismatch"));
      return;
    }

    setSubmitting(true);
    try {
      await resetPassword(token ?? "", password);
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
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
        <div className="auth-topbar"><Link href="/" className="text-link"><ArrowLeft size={14} />{t("auth_back")}</Link><div className="auth-topbar-actions"><ThemeSwitcher /><LanguageSwitcher /></div></div>
        <div className="auth-form-container">
          <div className="auth-mobile-brand"><Brand /></div>
          <div className="auth-form-icon" aria-hidden="true"><KeyRound size={20} strokeWidth={1.5} /></div>

          {!token ? (
            <>
              <h1>{t("auth_reset_invalid_token_title")}</h1>
              <p className="auth-subtitle">{t("auth_reset_invalid_token_body")}</p>
              <Link href="/app" className="button button-primary mt-1 w-full">
                {t("auth_reset_request_new_link")}<ArrowRight size={15} aria-hidden="true" />
              </Link>
            </>
          ) : done ? (
            <>
              <h1>{t("auth_reset_success_title")}</h1>
              <p className="auth-subtitle">{t("auth_reset_success_body")}</p>
              <Link href="/app" className="button button-primary mt-1 w-full">
                {t("auth_reset_go_to_login")}<ArrowRight size={15} aria-hidden="true" />
              </Link>
            </>
          ) : (
            <form onSubmit={handleSubmit} aria-busy={submitting}>
              <div>
                <h1>{t("auth_reset_title")}</h1>
                <p className="auth-subtitle">{t("auth_reset_subtitle")}</p>
              </div>

              <div>
                <label htmlFor="newPassword" className="field-label">
                  {t("auth_reset_new_password_label")}
                </label>
                <input
                  id="newPassword"
                  type="password"
                  required
                  minLength={8}
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="field-label">
                  {t("auth_reset_confirm_password_label")}
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  required
                  minLength={8}
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={inputClass}
                />
              </div>

              {error && (
                <p role="alert" className="text-sm" style={{ color: "var(--status-critical)" }}>
                  {error}
                </p>
              )}

              <button type="submit" disabled={submitting} className="button button-primary mt-1 w-full">
                {submitting ? t("auth_submitting") : t("auth_reset_submit")}
                <ArrowRight size={15} aria-hidden="true" />
              </button>
            </form>
          )}
        </div>
        <p className="auth-privacy"><ShieldCheck size={13} />{t("auth_secure")}</p>
      </div>
    </main>
  );
}
