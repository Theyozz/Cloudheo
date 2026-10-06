"use client";

import { useLanguage } from "@/lib/i18n";

type Risk = "LOW" | "MEDIUM" | "HIGH";

const RISK_COLOR: Record<Risk, string> = {
  LOW: "var(--status-good)",
  MEDIUM: "var(--status-warning)",
  HIGH: "var(--status-critical)",
};

const RISK_LABEL_KEY = {
  LOW: "risk_low",
  MEDIUM: "risk_medium",
  HIGH: "risk_high",
} as const;

export function RiskBadge({ risk }: { risk: Risk }) {
  const { t } = useLanguage();

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-[color:var(--border-hairline)] px-2.5 py-1 text-xs font-medium text-[color:var(--text-secondary)]">
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: RISK_COLOR[risk] }}
        aria-hidden
      />
      {t(RISK_LABEL_KEY[risk])}
    </span>
  );
}
