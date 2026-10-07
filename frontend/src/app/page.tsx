"use client";

import { useCallback, useEffect, useState } from "react";
import { BackendStatus } from "@/components/backend-status";
import { LanguageSwitcher } from "@/components/language-switcher";
import { ConnectAwsForm } from "@/components/connect-aws-form";
import { StatTile } from "@/components/stat-tile";
import { SavingsByCategory } from "@/components/savings-by-category";
import { TopRecommendations } from "@/components/top-recommendations";
import { SavingsSimulator } from "@/components/savings-simulator";
import { useLanguage, type TranslationKey } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";
import { fetchDashboardSummary, disconnectAwsAccount, type DashboardSummary } from "@/lib/api";

// Placeholder data shown until an AWS account is connected.
const PLACEHOLDER_SPEND = 17_840;
const PLACEHOLDER_SAVINGS = 3_240;
const PLACEHOLDER_SAVINGS_PERCENT = 18.2;
const PLACEHOLDER_RECOMMENDATIONS_COUNT = 34;

const CATEGORY_LABEL_KEYS: Record<string, TranslationKey> = {
  RIGHTSIZING: "rec_category_rightsizing",
  UNATTACHED_VOLUME: "rec_category_unattached_volume",
};

export default function DashboardPage() {
  const { t } = useLanguage();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [showConnectForm, setShowConnectForm] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const reload = useCallback(() => {
    setLoading(true);
    fetchDashboardSummary()
      .then((data) => {
        setSummary(data);
        setSelectedIds(new Set());
      })
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchDashboardSummary();
        if (!cancelled) {
          setSummary(data);
          setSelectedIds(new Set());
        }
      } catch {
        if (!cancelled) setSummary(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  function toggleSelected(resourceId: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(resourceId)) next.delete(resourceId);
      else next.add(resourceId);
      return next;
    });
  }

  function categoryLabel(code: string) {
    const key = CATEGORY_LABEL_KEYS[code];
    return key ? t(key) : code;
  }

  async function handleDisconnect() {
    await disconnectAwsAccount();
    reload();
  }

  const isConnected = summary?.connected ?? false;

  const placeholderSavingsByCategory = [
    { category: "EC2", amount: 820 },
    { category: "RDS", amount: 630 },
    { category: t("category_non_production"), amount: 540 },
    { category: "EBS", amount: 210 },
  ];

  const placeholderTopRecommendations = [
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

  const spend = isConnected ? summary!.monthly_spend : PLACEHOLDER_SPEND;
  const savings = isConnected ? summary!.potential_savings : PLACEHOLDER_SAVINGS;
  const savingsPercent = isConnected ? summary!.savings_percent : PLACEHOLDER_SAVINGS_PERCENT;
  const recommendationsCount = isConnected
    ? summary!.recommendations_count
    : PLACEHOLDER_RECOMMENDATIONS_COUNT;

  const savingsByCategory = isConnected ? summary!.savings_by_category : placeholderSavingsByCategory;

  const topRecommendations = isConnected
    ? summary!.top_recommendations.map((rec) => ({
        resourceId: rec.resource_id,
        resourceType: rec.resource_type,
        category: categoryLabel(rec.category),
        monthlySaving: rec.estimated_savings,
        risk: rec.risk,
        confidence: rec.confidence,
      }))
    : placeholderTopRecommendations;

  const selectedSavings = topRecommendations
    .filter((rec) => selectedIds.has(rec.resourceId))
    .reduce((sum, rec) => sum + rec.monthlySaving, 0);

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
          {!loading && (
            <span className="shrink-0 rounded-full border border-[color:var(--border-hairline)] px-3 py-1 text-xs text-[color:var(--text-muted)]">
              {isConnected
                ? t("connected_badge", { account: summary!.aws_account_id ?? "" })
                : t("sample_data_badge")}
            </span>
          )}
        </div>

        {/* AWS connection */}
        <section className="mt-6 rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <h2 className="text-sm font-medium">{t("connect_aws_title")}</h2>
              <p className="mt-1 max-w-xl text-sm text-[color:var(--text-secondary)]">
                {t("connect_aws_description")}
              </p>
              {!isConnected && showConnectForm && (
                <ConnectAwsForm
                  onConnected={() => {
                    setShowConnectForm(false);
                    reload();
                  }}
                  onCancel={() => setShowConnectForm(false)}
                />
              )}
            </div>
            {isConnected ? (
              <button
                type="button"
                onClick={handleDisconnect}
                className="shrink-0 rounded-md border border-[color:var(--border-hairline)] px-4 py-2 text-sm font-medium text-[color:var(--text-secondary)] hover:text-[color:var(--foreground)]"
              >
                {t("disconnect_button")}
              </button>
            ) : (
              !showConnectForm && (
                <button
                  type="button"
                  onClick={() => setShowConnectForm(true)}
                  className="shrink-0 rounded-md bg-[color:var(--foreground)] px-4 py-2 text-sm font-medium text-[color:var(--background)]"
                >
                  {t("connect_aws_button")}
                </button>
              )
            )}
          </div>
        </section>

        {/* Stat tiles */}
        <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatTile label={t("stat_spend")} value={formatUsd(spend)} />
          <StatTile
            label={t("stat_savings")}
            value={formatUsd(savings)}
            delta={{
              text: t("stat_savings_delta", { percent: savingsPercent }),
              direction: "down",
              isGood: true,
            }}
          />
          <StatTile label={t("stat_recommendations")} value={String(recommendationsCount)} />
        </section>

        {/* Breakdown */}
        <section className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <SavingsByCategory data={savingsByCategory} />
          <TopRecommendations data={topRecommendations} selectedIds={selectedIds} onToggle={toggleSelected} />
        </section>

        {/* Simulator */}
        <section className="mt-6">
          <SavingsSimulator currentSpend={spend} selectedSavings={selectedSavings} selectedCount={selectedIds.size} />
        </section>
      </main>

      <footer className="border-t border-[color:var(--border-hairline)] py-4">
        <p className="mx-auto max-w-6xl px-6 text-xs text-[color:var(--text-muted)]">{t("footer")}</p>
      </footer>
    </div>
  );
}
