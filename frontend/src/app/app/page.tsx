"use client";

import { useCallback, useEffect, useState } from "react";
import { ArrowUpRight, Cloud, Layers3, LayoutDashboard, LoaderCircle, LogOut, RefreshCw, ShieldCheck, SlidersHorizontal, Sparkles, TrendingDown, Wallet } from "lucide-react";
import { Brand } from "@/components/brand";
import { BackendStatus } from "@/components/backend-status";
import { LanguageSwitcher } from "@/components/language-switcher";
import { LoginForm } from "@/components/login-form";
import { ConnectAwsForm } from "@/components/connect-aws-form";
import { StatTile } from "@/components/stat-tile";
import { SavingsByCategory } from "@/components/savings-by-category";
import { TopRecommendations } from "@/components/top-recommendations";
import { SavingsSimulator } from "@/components/savings-simulator";
import { useLanguage, type TranslationKey } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";
import { fetchDashboardSummary, disconnectAwsAccount, type DashboardSummary } from "@/lib/api";
import { AuthRequiredError, logout, verifyToken } from "@/lib/auth";

// Placeholder data shown until an AWS account is connected.
const PLACEHOLDER_SPEND = 17_840;
const PLACEHOLDER_SAVINGS = 3_240;
const PLACEHOLDER_SAVINGS_PERCENT = 18.2;
const PLACEHOLDER_RECOMMENDATIONS_COUNT = 34;

const CATEGORY_LABEL_KEYS: Record<string, TranslationKey> = {
  RIGHTSIZING: "rec_category_rightsizing",
  UNATTACHED_VOLUME: "rec_category_unattached_volume",
  NON_PROD_SCHEDULING: "rec_category_non_prod_scheduling",
  STOPPED_INSTANCE_STORAGE: "rec_category_stopped_instance_storage",
  ORPHANED_SNAPSHOT: "rec_category_orphaned_snapshot",
};

export default function DashboardPage() {
  const { t } = useLanguage();
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      const ok = await verifyToken();
      if (!cancelled) {
        setIsAuthenticated(ok);
        setAuthChecked(true);
      }
    }

    check();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!authChecked) {
    return <main className="dashboard-loading"><Brand /><p role="status" className="flex items-center gap-2"><LoaderCircle size={15} className="spin" />{t("loading_text")}</p></main>;
  }

  if (!isAuthenticated) {
    return <LoginForm onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  return (
    <Dashboard
      onLoggedOut={() => {
        logout();
        setIsAuthenticated(false);
      }}
    />
  );
}

function Dashboard({ onLoggedOut }: { onLoggedOut: () => void }) {
  const { t } = useLanguage();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [disconnectError, setDisconnectError] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState(false);
  const [showConnectForm, setShowConnectForm] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const reload = useCallback(() => {
    setLoading(true);
    setLoadError(false);
    setDisconnectError(null);
    fetchDashboardSummary()
      .then((data) => {
        setSummary(data);
        setSelectedIds(new Set());
      })
      .catch((err) => {
        if (err instanceof AuthRequiredError) {
          onLoggedOut();
          return;
        }
        setLoadError(true);
        setSummary(null);
        setSelectedIds(new Set());
      })
      .finally(() => setLoading(false));
  }, [onLoggedOut]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchDashboardSummary();
        if (!cancelled) {
          setSummary(data);
          setSelectedIds(new Set());
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof AuthRequiredError) {
          onLoggedOut();
          return;
        }
        setLoadError(true);
        setSummary(null);
        setSelectedIds(new Set());
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [onLoggedOut]);

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
    setDisconnecting(true);
    setDisconnectError(null);
    try {
      await disconnectAwsAccount();
      reload();
    } catch (err) {
      if (err instanceof AuthRequiredError) onLoggedOut();
      else setDisconnectError(err instanceof Error ? err.message : String(err));
    } finally {
      setDisconnecting(false);
    }
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
      explainPayload: null,
    },
    {
      resourceId: "db-staging-02",
      resourceType: "RDS",
      category: t("rec_category_non_prod_scheduling"),
      monthlySaving: 54,
      risk: "LOW" as const,
      confidence: 0.88,
      explainPayload: null,
    },
    {
      resourceId: "vol-0def456",
      resourceType: "EBS",
      category: t("rec_category_unattached_volume"),
      monthlySaving: 23,
      risk: "LOW" as const,
      confidence: 0.99,
      explainPayload: null,
    },
    {
      resourceId: "db-prod-reporting",
      resourceType: "RDS",
      category: t("rec_category_rightsizing"),
      monthlySaving: 61,
      risk: "MEDIUM" as const,
      confidence: 0.76,
      explainPayload: null,
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
        explainPayload: rec,
      }))
    : placeholderTopRecommendations;

  const selectedSavings = topRecommendations
    .filter((rec) => selectedIds.has(rec.resourceId))
    .reduce((sum, rec) => sum + rec.monthlySaving, 0);

  return (
    <div className="dashboard-page">
      <a href="#overview" className="skip-link">{t("skip_to_content")}</a>
      <header className="dashboard-header">
        <div className="site-container header-inner">
          <Brand />
          <div className="dashboard-header-actions">
            <div className="dashboard-api-status"><BackendStatus /></div>
            <LanguageSwitcher />
            <button
              type="button"
              onClick={onLoggedOut}
              className="text-link dashboard-logout"
              aria-label={t("auth_logout")}
            >
              <LogOut size={14} /><span>{t("auth_logout")}</span>
            </button>
          </div>
        </div>
        <nav className="site-container dashboard-nav" aria-label={t("nav_dashboard")}>
          <div className="dashboard-nav-links">
            <a href="#overview"><LayoutDashboard size={15} />{t("dashboard_overview")}</a>
            <a href="#optimizations"><Sparkles size={15} />{t("dashboard_optimizations")}</a>
            <a href="#simulator"><SlidersHorizontal size={15} />{t("dashboard_simulator")}</a>
          </div>
          <span><ShieldCheck size={13} />{t("dashboard_readonly")}</span>
        </nav>
      </header>

      <main id="overview" className="site-container dashboard-main" aria-busy={loading}>
        <div className="dashboard-heading">
          <div>
            <p className="eyebrow">{t("dashboard_eyebrow")}</p>
            <h1>{t("dashboard_title")}</h1>
            <p>{t("dashboard_subtitle")}</p>
          </div>
          <div className="dashboard-heading-actions">
            <span className={isConnected ? "good-badge" : "soft-badge"} role="status">
              {loading ? t("loading_text") : isConnected ? t("connected_badge", { account: summary!.aws_account_id ?? "" }) : t("sample_data_badge")}
            </span>
            <button type="button" onClick={reload} disabled={loading || disconnecting} className="refresh-button" aria-label={t("dashboard_refresh")} title={t("dashboard_refresh")}><RefreshCw size={14} className={loading ? "spin" : undefined} /></button>
          </div>
        </div>
        {loadError && <p role="alert" className="error-notice">{t("dashboard_load_error")}</p>}
        {disconnectError && <p role="alert" className="error-notice">{disconnectError}</p>}

        {/* AWS connection */}
        <section className="connection-panel">
          <span className="icon-box"><Cloud size={20} strokeWidth={1.5} /></span>
          <div className="connection-content">
            <div className="connection-row">
              <div className="connection-copy">
                <h2>{isConnected ? t("dashboard_connection_active") : showConnectForm ? t("connect_aws_title") : t("dashboard_sample_title")}</h2>
                <p>{isConnected || showConnectForm ? t("connect_aws_description") : t("dashboard_sample_description")}</p>
              </div>
              {isConnected ? (
                <button type="button" onClick={handleDisconnect} disabled={disconnecting || loading} className="button button-outline button-small">
                  {disconnecting ? <LoaderCircle size={14} className="spin" /> : null}{t("disconnect_button")}
                </button>
              ) : !showConnectForm && (
                <button type="button" onClick={() => setShowConnectForm(true)} disabled={loading} className="button button-primary button-small">{t("connect_aws_button")}<ArrowUpRight size={14} /></button>
              )}
            </div>
            {!isConnected && showConnectForm && (
              <ConnectAwsForm onConnected={() => { setShowConnectForm(false); reload(); }} onCancel={() => setShowConnectForm(false)} />
            )}
          </div>
        </section>

        {/* Stat tiles */}
        <section className="dashboard-stats">
          <StatTile label={t("stat_spend")} value={loading ? "—" : formatUsd(spend)} icon={Wallet} />
          <StatTile
            label={t("stat_savings")}
            value={loading ? "—" : formatUsd(savings)}
            icon={TrendingDown}
            delta={loading ? undefined : {
              text: t("stat_savings_delta", { percent: savingsPercent }),
              direction: "down",
              isGood: true,
            }}
          />
          <StatTile label={t("stat_recommendations")} value={loading ? "—" : String(recommendationsCount)} icon={Layers3} />
        </section>

        {/* Breakdown */}
        <section id="optimizations" className="dashboard-breakdown">
          <SavingsByCategory data={savingsByCategory} />
          <TopRecommendations data={topRecommendations} selectedIds={selectedIds} onToggle={toggleSelected} />
        </section>

        {/* Simulator */}
        <section id="simulator" className="dashboard-simulator">
          <SavingsSimulator currentSpend={spend} selectedSavings={selectedSavings} selectedCount={selectedIds.size} />
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-container footer-inner"><p>{t("landing_footer_note")}</p><span className="flex items-center gap-2"><ShieldCheck size={12} />{t("footer")}</span></div>
      </footer>
    </div>
  );
}
