"use client";

import { BackendStatus } from "@/components/backend-status";
import { LanguageSwitcher } from "@/components/language-switcher";
import { StatTile } from "@/components/stat-tile";
import { SavingsByCategory } from "@/components/savings-by-category";
import { TopRecommendations } from "@/components/top-recommendations";
import { useLanguage } from "@/lib/i18n";

// Placeholder data — no AWS account is connected yet. This will be replaced
// by real data from Cost Explorer / EC2 / EBS / RDS once the AWS integration
// and FinOps engine are built (Sprint 2 & 3).
const SPEND_EUR = 17_840;
const SAVINGS_EUR = 3_240;
const SAVINGS_PERCENT = 18.2;
const RECOMMENDATIONS_COUNT = 34;

function formatEur(amount: number) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function DashboardPage() {
  const { t } = useLanguage();

  const savingsByCategory = [
    { category: "EC2", amount: 820 },
    { category: "RDS", amount: 630 },
    { category: t("category_non_production"), amount: 540 },
    { category: "EBS", amount: 210 },
  ];

  const topRecommendations = [
    {
      resourceId: "i-0abc123",
      resourceType: "EC2",
      category: t("rec_category_rightsizing"),
      monthlySaving: 79,
      risk: "LOW" as const,
      confidence: 0.94,
    },
    {
      resourceId: "db-staging-02",
      resourceType: "RDS",
      category: t("rec_category_non_prod_scheduling"),
      monthlySaving: 54,
      risk: "LOW" as const,
      confidence: 0.88,
    },
    {
      resourceId: "vol-0def456",
      resourceType: "EBS",
      category: t("rec_category_unattached_volume"),
      monthlySaving: 23,
      risk: "LOW" as const,
      confidence: 0.99,
    },
    {
      resourceId: "db-prod-reporting",
      resourceType: "RDS",
      category: t("rec_category_rightsizing"),
      monthlySaving: 61,
      risk: "MEDIUM" as const,
      confidence: 0.76,
    },
  ];

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
          <div className="flex items-center gap-4">
            <BackendStatus />
            <span className="text-[color:var(--border-hairline)]">|</span>
            <LanguageSwitcher />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{t("dashboard_title")}</h1>
            <p className="mt-1 text-sm text-[color:var(--text-secondary)]">{t("dashboard_subtitle")}</p>
          </div>
          <span className="shrink-0 rounded-full border border-[color:var(--border-hairline)] px-3 py-1 text-xs text-[color:var(--text-muted)]">
            {t("sample_data_badge")}
          </span>
        </div>

        {/* AWS connection */}
        <section className="mt-6 rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-sm font-medium">{t("connect_aws_title")}</h2>
              <p className="mt-1 max-w-xl text-sm text-[color:var(--text-secondary)]">
                {t("connect_aws_description")}
              </p>
            </div>
            <button
              type="button"
              disabled
              className="shrink-0 cursor-not-allowed rounded-md bg-[color:var(--foreground)] px-4 py-2 text-sm font-medium text-[color:var(--background)] opacity-50"
              title={t("connect_aws_tooltip")}
            >
              {t("connect_aws_button")}
            </button>
          </div>
        </section>

        {/* Stat tiles */}
        <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatTile label={t("stat_spend")} value={formatEur(SPEND_EUR)} />
          <StatTile
            label={t("stat_savings")}
            value={formatEur(SAVINGS_EUR)}
            delta={{
              text: t("stat_savings_delta", { percent: SAVINGS_PERCENT }),
              direction: "down",
              isGood: true,
            }}
          />
          <StatTile label={t("stat_recommendations")} value={String(RECOMMENDATIONS_COUNT)} />
        </section>

        {/* Breakdown */}
        <section className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <SavingsByCategory data={savingsByCategory} />
          <TopRecommendations data={topRecommendations} />
        </section>
      </main>

      <footer className="border-t border-[color:var(--border-hairline)] py-4">
        <p className="mx-auto max-w-6xl px-6 text-xs text-[color:var(--text-muted)]">{t("footer")}</p>
      </footer>
    </div>
  );
}
