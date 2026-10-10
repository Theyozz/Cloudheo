"use client";

import { useCallback, useEffect, useState } from "react";
import { ArrowUpRight, Cloud, Layers3, LayoutDashboard, LoaderCircle, LogOut, RefreshCw, ShieldCheck, SlidersHorizontal, Sparkles, TrendingDown, Wallet } from "lucide-react";
import { Brand } from "@/components/brand";
import { LanguageSwitcher } from "@/components/language-switcher";
import { ThemeSwitcher } from "@/components/theme";
import { LoginForm } from "@/components/login-form";
import { ConnectAwsForm } from "@/components/connect-aws-form";
import { StatTile } from "@/components/stat-tile";
import { SavingsByCategory } from "@/components/savings-by-category";
import { TopRecommendations } from "@/components/top-recommendations";
import { SavingsSimulator } from "@/components/savings-simulator";
import { useLanguage, type TranslationKey } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";
import { fetchDashboardSummary, disconnectAwsAccount, type DashboardSummary } from "@/lib/api";
import { AuthRequiredError, getCurrentUser, logout } from "@/lib/auth";

const CATEGORY_LABEL_KEYS: Record<string, TranslationKey> = {
  RIGHTSIZING: "rec_category_rightsizing",
  UNATTACHED_VOLUME: "rec_category_unattached_volume",
  NON_PROD_SCHEDULING: "rec_category_non_prod_scheduling",
  STOPPED_INSTANCE_STORAGE: "rec_category_stopped_instance_storage",
  ORPHANED_SNAPSHOT: "rec_category_orphaned_snapshot",
  UNUSED_ELASTIC_IP: "rec_category_unused_elastic_ip",
  GP3_MIGRATION: "rec_category_gp3_migration",
  SAVINGS_PLAN_COVERAGE_GAP: "rec_category_savings_plan_coverage_gap",
};

export default function DashboardPage() {
  const { t } = useLanguage();
  const [authChecked, setAuthChecked] = useState(false);
  const [organizationName, setOrganizationName] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      const user = await getCurrentUser();
      if (!cancelled) {
        setOrganizationName(user?.organizationName ?? null);
        setAuthChecked(true);
      }
    }

    check();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleAuthenticated() {
    const user = await getCurrentUser();
    setOrganizationName(user?.organizationName ?? null);
  }

  if (!authChecked) {
    return <main className="dashboard-loading"><Brand /><p role="status" className="flex items-center gap-2"><LoaderCircle size={15} className="spin" />{t("loading_text")}</p></main>;
  }

  if (!organizationName) {
    return <LoginForm onAuthenticated={handleAuthenticated} />;
  }

  return (
    <Dashboard
      organizationName={organizationName}
      onLoggedOut={() => {
        logout();
        setOrganizationName(null);
      }}
    />
  );
}

function Dashboard({ organizationName, onLoggedOut }: { organizationName: string; onLoggedOut: () => void }) {
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

  const spend = isConnected ? summary!.monthly_spend : null;
  const savings = isConnected ? summary!.potential_savings : null;
  const savingsPercent = isConnected ? summary!.savings_percent : null;
  const recommendationsCount = isConnected ? summary!.recommendations_count : null;

  const savingsByCategory = isConnected ? summary!.savings_by_category : [];

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
    : [];

  const selectedSavings = topRecommendations
    .filter((rec) => selectedIds.has(rec.resourceId))
    .reduce((sum, rec) => sum + rec.monthlySaving, 0);

  return (
    <div className="dashboard-page">
      <a href="#overview" className="skip-link">{t("skip_to_content")}</a>
      <header className="dashboard-header">
        <div className="site-container header-inner">
          <div className="dashboard-brand-group">
            <Brand />
            <p className="dashboard-org" title={organizationName}>
              <span className="dashboard-org-name">{organizationName}</span>
              <span className="dashboard-org-label">{t("dashboard_workspace_label")}</span>
            </p>
          </div>
          <div className="dashboard-header-actions">
            <ThemeSwitcher />
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
              {loading ? t("loading_text") : isConnected ? t("connected_badge", { account: summary!.aws_account_id ?? "" }) : t("dashboard_not_connected_badge")}
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
                <h2>{isConnected ? t("dashboard_connection_active") : showConnectForm ? t("connect_aws_title") : t("dashboard_empty_title")}</h2>
                <p>{isConnected || showConnectForm ? t("connect_aws_description") : t("dashboard_empty_description")}</p>
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
          <StatTile label={t("stat_spend")} value={loading || spend === null ? "—" : formatUsd(spend)} icon={Wallet} />
          <StatTile
            label={t("stat_savings")}
            value={loading || savings === null ? "—" : formatUsd(savings)}
            icon={TrendingDown}
            delta={loading || savings === null ? undefined : {
              text: t("stat_savings_delta", { percent: savingsPercent ?? 0 }),
              direction: "down",
              isGood: true,
            }}
          />
          <StatTile label={t("stat_recommendations")} value={loading || recommendationsCount === null ? "—" : String(recommendationsCount)} icon={Layers3} />
        </section>

        {/* Breakdown */}
        <section id="optimizations" className="dashboard-breakdown">
          <SavingsByCategory data={savingsByCategory} />
          <TopRecommendations data={topRecommendations} selectedIds={selectedIds} onToggle={toggleSelected} />
        </section>

        {/* Simulator — only meaningful once there's something real to simulate */}
        {isConnected && (
          <section id="simulator" className="dashboard-simulator">
            <SavingsSimulator currentSpend={spend ?? 0} selectedSavings={selectedSavings} selectedCount={selectedIds.size} />
          </section>
        )}
      </main>

      <footer className="site-footer">
        <div className="site-container footer-inner"><p>{t("landing_footer_note")}</p><span className="flex items-center gap-2"><ShieldCheck size={12} />{t("footer")}</span></div>
      </footer>
    </div>
  );
}
