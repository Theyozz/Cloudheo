"use client";

import { ArrowDownRight, SlidersHorizontal, TrendingDown, Wallet } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";

export function SavingsSimulator({
  currentSpend,
  selectedSavings,
  selectedCount,
}: {
  currentSpend: number;
  selectedSavings: number;
  selectedCount: number;
}) {
  const { t } = useLanguage();
  const newSpend = Math.max(0, currentSpend - selectedSavings);

  return (
    <div className="panel simulator-panel min-w-0 text-[color:var(--foreground)]">
      <div className="grid min-w-0 gap-8 xl:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] xl:items-center">
        <div className="min-w-0">
          <h2 className="panel-heading">
            <span className="icon-box shrink-0" aria-hidden="true">
              <SlidersHorizontal size={18} strokeWidth={1.7} />
            </span>
            <span className="min-w-0 [overflow-wrap:anywhere]">{t("simulator_title")}</span>
          </h2>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-[color:var(--text-secondary)]">
            {t("landing_step_simulate_desc")}
          </p>
          <span className="soft-badge mt-4 inline-flex max-w-full items-center gap-1.5">
            <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[color:var(--status-good)]" aria-hidden="true" />
            <span className="whitespace-normal">{t("simulator_selected", { count: selectedCount })}</span>
          </span>
        </div>
        <dl className="grid min-w-0 grid-cols-1 gap-6 border-t border-[color:var(--gridline)] pt-6 sm:grid-cols-3 xl:border-t-0 xl:border-l xl:pt-0 xl:pl-8">
          <div className="min-w-0">
            <dt className="muted-label flex items-start gap-2 leading-relaxed">
              <Wallet size={15} className="mt-0.5 shrink-0" aria-hidden="true" />
              {t("simulator_current_spend")}
            </dt>
            <dd className="mt-3 text-3xl font-medium tracking-[-0.04em] tabular-nums [overflow-wrap:anywhere]">
              {formatUsd(currentSpend)}
            </dd>
          </div>
          <div className="min-w-0">
            <dt className="muted-label flex items-start gap-2 leading-relaxed">
              <TrendingDown size={15} className="mt-0.5 shrink-0" aria-hidden="true" />
              {t("simulator_estimated_savings")}
            </dt>
            <dd className="mt-3 text-3xl font-medium tracking-[-0.04em] tabular-nums text-[color:var(--status-good)] [overflow-wrap:anywhere]">
              -{formatUsd(selectedSavings)}
            </dd>
          </div>
          <div className="min-w-0">
            <dt className="muted-label flex items-start gap-2 leading-relaxed">
              <ArrowDownRight size={15} className="mt-0.5 shrink-0" aria-hidden="true" />
              {t("simulator_new_spend")}
            </dt>
            <dd className="mt-3 text-3xl font-semibold tracking-[-0.04em] tabular-nums [overflow-wrap:anywhere]">
              {formatUsd(newSpend)}
            </dd>
          </div>
        </dl>
      </div>
      <p role="status" aria-live="polite" aria-atomic="true" className="sr-only">
        {t("simulator_selected", { count: selectedCount })}. {t("simulator_estimated_savings")}: {formatUsd(selectedSavings)}. {t("simulator_new_spend")}: {formatUsd(newSpend)}.
      </p>
    </div>
  );
}
