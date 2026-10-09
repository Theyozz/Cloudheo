"use client";

import { ShieldAlert, ShieldCheck, TriangleAlert, type LucideIcon } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

type Risk = "LOW" | "MEDIUM" | "HIGH";

const RISK_COLOR: Record<Risk, string> = {
  LOW: "var(--status-good)",
  MEDIUM: "var(--status-warning, #8f642f)",
  HIGH: "var(--status-critical, #a34d43)",
};

const RISK_ICON: Record<Risk, LucideIcon> = {
  LOW: ShieldCheck,
  MEDIUM: ShieldAlert,
  HIGH: TriangleAlert,
};

const RISK_LABEL_KEY = {
  LOW: "risk_low",
  MEDIUM: "risk_medium",
  HIGH: "risk_high",
} as const;

export function RiskBadge({ risk }: { risk: Risk }) {
  const { t } = useLanguage();
  const Icon = RISK_ICON[risk];

  return (
    <span
      className={`${risk === "LOW" ? "good-badge" : "soft-badge"} inline-flex items-center gap-1.5 whitespace-nowrap`}
      style={{
        color: RISK_COLOR[risk],
        backgroundColor: `color-mix(in srgb, ${RISK_COLOR[risk]} 9%, var(--surface-1))`,
        borderColor: `color-mix(in srgb, ${RISK_COLOR[risk]} 20%, var(--border-hairline))`,
      }}
    >
      <Icon size={13} strokeWidth={1.8} className="shrink-0" aria-hidden="true" />
      {t(RISK_LABEL_KEY[risk])}
    </span>
  );
}
