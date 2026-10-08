"use client";

import Link from "next/link";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useLanguage, type TranslationKey } from "@/lib/i18n";

const CONTACT_EMAIL = "theomaurin875@gmail.com";
const CONTACT_SUBJECT = encodeURIComponent("Free AWS audit — Cloudheo");
const MAILTO = `mailto:${CONTACT_EMAIL}?subject=${CONTACT_SUBJECT}`;

type Step = {
  titleKey: TranslationKey;
  descKey: TranslationKey;
  live: boolean;
};

const STEPS: Step[] = [
  { titleKey: "landing_step_detect_title", descKey: "landing_step_detect_desc", live: true },
  { titleKey: "landing_step_explain_title", descKey: "landing_step_explain_desc", live: true },
  { titleKey: "landing_step_simulate_title", descKey: "landing_step_simulate_desc", live: true },
  { titleKey: "landing_step_approve_title", descKey: "landing_step_approve_desc", live: false },
  { titleKey: "landing_step_fix_title", descKey: "landing_step_fix_desc", live: false },
  { titleKey: "landing_step_verify_title", descKey: "landing_step_verify_desc", live: false },
];

function PrimaryButton({ children }: { children: React.ReactNode }) {
  return (
    <a
      href={MAILTO}
      className="inline-flex items-center justify-center rounded-md bg-[color:var(--foreground)] px-5 py-2.5 text-sm font-medium text-[color:var(--background)] hover:opacity-90"
    >
      {children}
    </a>
  );
}

export default function LandingPage() {
  const { t } = useLanguage();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-[color:var(--border-hairline)]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-[color:var(--foreground)] text-sm font-semibold text-[color:var(--background)]">
              C
            </span>
            <span className="text-base font-semibold tracking-tight">Cloudheo</span>
          </div>
          <nav className="hidden items-center gap-6 text-sm text-[color:var(--text-secondary)] sm:flex">
            <a href="#how" className="hover:text-[color:var(--foreground)]">
              {t("landing_nav_how")}
            </a>
            <a href="#security" className="hover:text-[color:var(--foreground)]">
              {t("landing_nav_security")}
            </a>
          </nav>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <span className="text-[color:var(--border-hairline)]">|</span>
            <Link href="/app" className="text-sm text-[color:var(--text-secondary)] hover:text-[color:var(--foreground)]">
              {t("landing_nav_login")}
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero */}
        <section className="mx-auto max-w-4xl px-6 py-20 text-center sm:py-28">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-5xl">{t("landing_hero_title")}</h1>
          <p className="mx-auto mt-5 max-w-2xl text-base text-[color:var(--text-secondary)] sm:text-lg">
            {t("landing_hero_subtitle")}
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <PrimaryButton>{t("landing_cta_primary")}</PrimaryButton>
            <a href="#how" className="text-sm text-[color:var(--text-secondary)] hover:text-[color:var(--foreground)]">
              {t("landing_cta_secondary")} ↓
            </a>
          </div>
        </section>

        {/* Loop */}
        <section id="how" className="border-t border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] py-16">
          <div className="mx-auto max-w-6xl px-6">
            <h2 className="text-2xl font-semibold tracking-tight">{t("landing_loop_title")}</h2>
            <p className="mt-2 max-w-2xl text-sm text-[color:var(--text-secondary)]">{t("landing_loop_subtitle")}</p>
            <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {STEPS.map((step, i) => (
                <div
                  key={step.titleKey}
                  className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--background)] p-5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-[color:var(--text-muted)]">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    {!step.live && (
                      <span className="rounded-full border border-[color:var(--border-hairline)] px-2 py-0.5 text-[10px] text-[color:var(--text-muted)]">
                        {t("landing_step_soon")}
                      </span>
                    )}
                  </div>
                  <h3 className="mt-3 text-sm font-semibold">{t(step.titleKey)}</h3>
                  <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{t(step.descKey)}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Audience */}
        <section className="mx-auto max-w-4xl px-6 py-16 text-center">
          <h2 className="text-2xl font-semibold tracking-tight">{t("landing_audience_title")}</h2>
          <p className="mx-auto mt-3 max-w-2xl text-sm text-[color:var(--text-secondary)]">
            {t("landing_audience_body")}
          </p>
        </section>

        {/* Security */}
        <section
          id="security"
          className="border-t border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] py-16"
        >
          <div className="mx-auto max-w-3xl px-6 text-center">
            <h2 className="text-2xl font-semibold tracking-tight">{t("landing_security_title")}</h2>
            <p className="mt-3 text-sm text-[color:var(--text-secondary)]">{t("landing_security_body")}</p>
          </div>
        </section>

        {/* Final CTA */}
        <section className="mx-auto max-w-3xl px-6 py-20 text-center">
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t("landing_final_cta_title")}</h2>
          <div className="mt-6">
            <PrimaryButton>{t("landing_cta_primary")}</PrimaryButton>
          </div>
        </section>
      </main>

      <footer className="border-t border-[color:var(--border-hairline)] py-4">
        <p className="mx-auto max-w-6xl px-6 text-xs text-[color:var(--text-muted)]">{t("landing_footer")}</p>
      </footer>
    </div>
  );
}
