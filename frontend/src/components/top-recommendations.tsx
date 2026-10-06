"use client";

import { useLanguage } from "@/lib/i18n";
import { RiskBadge } from "./risk-badge";

type Recommendation = {
  resourceId: string;
  resourceType: string;
  category: string;
  monthlySaving: number;
  risk: "LOW" | "MEDIUM" | "HIGH";
  confidence: number;
};

function formatEur(amount: number) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function TopRecommendations({ data }: { data: Recommendation[] }) {
  const { t } = useLanguage();

  return (
    <div className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
      <h2 className="text-sm font-medium text-[color:var(--text-secondary)]">
        {t("top_recommendations_title")}
      </h2>
      <ul className="mt-4 flex flex-col divide-y divide-[color:var(--border-hairline)]">
        {data.map((rec) => (
          <li key={rec.resourceId} className="flex items-center justify-between gap-4 py-3 first:pt-1 last:pb-1">
            <div>
              <p className="text-sm font-medium">
                {rec.resourceType} · {rec.resourceId}
              </p>
              <p className="text-xs text-[color:var(--text-muted)]">
                {rec.category} · {t("confidence_label", { percent: Math.round(rec.confidence * 100) })}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium tabular-nums" style={{ color: "var(--status-good)" }}>
                -{formatEur(rec.monthlySaving)}/mo
              </span>
              <RiskBadge risk={rec.risk} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
