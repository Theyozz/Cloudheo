"use client";

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
    <div className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-medium text-[color:var(--text-secondary)]">{t("simulator_title")}</h2>
        <span className="text-xs text-[color:var(--text-muted)]">{t("simulator_selected", { count: selectedCount })}</span>
      </div>
      <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <p className="text-xs text-[color:var(--text-secondary)]">{t("simulator_current_spend")}</p>
          <p className="mt-1 text-xl font-semibold tracking-tight">{formatUsd(currentSpend)}</p>
        </div>
        <div>
          <p className="text-xs text-[color:var(--text-secondary)]">{t("simulator_estimated_savings")}</p>
          <p className="mt-1 text-xl font-semibold tracking-tight" style={{ color: "var(--status-good)" }}>
            -{formatUsd(selectedSavings)}
          </p>
        </div>
        <div>
          <p className="text-xs text-[color:var(--text-secondary)]">{t("simulator_new_spend")}</p>
          <p className="mt-1 text-xl font-semibold tracking-tight">{formatUsd(newSpend)}</p>
        </div>
      </div>
    </div>
  );
}
