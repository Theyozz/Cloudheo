"use client";

import { useState } from "react";
import { Box, CircleAlert, Database, HardDrive, ListChecks, LoaderCircle, Server, Sparkles, type LucideIcon } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";
import { explainRecommendation, type ApiRecommendation } from "@/lib/api";
import { RiskBadge } from "./risk-badge";

type Recommendation = {
  resourceId: string;
  resourceType: string;
  category: string;
  monthlySaving: number;
  risk: "LOW" | "MEDIUM" | "HIGH";
  confidence: number;
  // The raw API shape, needed to call /ai/explain. Null for placeholder
  // rows (not connected to a real AWS account) — hides the Explain button
  // rather than spending a real LLM call narrating fake numbers.
  explainPayload: ApiRecommendation | null;
};

type TopRecommendationsProps = {
  data: Recommendation[];
  selectedIds: Set<string>;
  onToggle: (resourceId: string) => void;
};

type ExplanationState = { status: "loading" | "done" | "error"; text?: string };

const RESOURCE_ICONS: Record<string, LucideIcon> = {
  EC2: Server,
  EBS: HardDrive,
  RDS: Database,
};

export function TopRecommendations({ data, selectedIds, onToggle }: TopRecommendationsProps) {
  const { t } = useLanguage();
  const [explanations, setExplanations] = useState<Record<string, ExplanationState>>({});

  async function handleExplain(rec: Recommendation) {
    if (!rec.explainPayload) return;
    setExplanations((prev) => ({ ...prev, [rec.resourceId]: { status: "loading" } }));
    try {
      const text = await explainRecommendation(rec.explainPayload);
      setExplanations((prev) => ({ ...prev, [rec.resourceId]: { status: "done", text } }));
    } catch {
      setExplanations((prev) => ({ ...prev, [rec.resourceId]: { status: "error" } }));
    }
  }

  return (
    <div className="panel h-full min-w-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="panel-heading min-w-0">
          <span className="icon-box shrink-0" aria-hidden="true">
            <ListChecks size={18} strokeWidth={1.7} />
          </span>
          <span className="min-w-0 [overflow-wrap:anywhere]">{t("top_recommendations_title")}</span>
        </h2>
        <span className="soft-badge tabular-nums">
          <span className="sr-only">{t("stat_recommendations")}: </span>
          {data.length}
        </span>
      </div>
      <p className="muted-label mt-4">{t("stat_savings")}</p>
      {data.length === 0 && (
        <p className="mt-6 rounded-xl border border-dashed border-[color:var(--border-hairline)] bg-[color:var(--surface-2)] px-4 py-8 text-center text-sm leading-relaxed text-[color:var(--text-secondary)]">
          {t("no_recommendations")}
        </p>
      )}
      <ul className="mt-5 flex min-w-0 flex-col gap-3">
        {data.map((rec) => {
          const explanation = explanations[rec.resourceId];
          const selected = selectedIds.has(rec.resourceId);
          const ResourceIcon = RESOURCE_ICONS[rec.resourceType] ?? Box;
          return (
            <li
              key={rec.resourceId}
              className="min-w-0 rounded-xl border border-[color:var(--border-hairline)] p-4 motion-safe:transition-colors"
              style={selected ? {
                backgroundColor: "var(--accent-soft)",
                borderColor: "color-mix(in srgb, var(--accent) 35%, var(--border-hairline))",
              } : undefined}
            >
              <label className="flex min-w-0 cursor-pointer items-start gap-3">
                <input
                  type="checkbox"
                  checked={selected}
                  onChange={() => onToggle(rec.resourceId)}
                  className="mt-1.5 h-4 w-4 shrink-0 cursor-pointer accent-[color:var(--accent)] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[color:var(--accent)]"
                />
                <span className="block min-w-0 flex-1">
                  <span className="flex flex-wrap items-center justify-between gap-2">
                    <span className="flex min-w-0 items-center gap-2 text-[color:var(--text-secondary)]">
                      <ResourceIcon size={15} strokeWidth={1.7} className="shrink-0" aria-hidden="true" />
                      <span className="mono-label min-w-0 [overflow-wrap:anywhere]">{rec.resourceType}</span>
                    </span>
                    <RiskBadge risk={rec.risk} />
                  </span>
                  <span className="mt-2 block font-mono text-[13px] leading-relaxed font-medium text-[color:var(--foreground)] [overflow-wrap:anywhere]">
                    {rec.resourceId}
                  </span>
                  <span className="muted-label mt-1 block leading-relaxed [overflow-wrap:anywhere]">
                    {rec.category}
                  </span>
                  <span className="mt-3 flex flex-wrap items-baseline justify-between gap-x-3 gap-y-2">
                    <span className="muted-label [overflow-wrap:anywhere]">
                      {t("confidence_label", { percent: Math.round(rec.confidence * 100) })}
                    </span>
                    <span className="text-base font-semibold tracking-tight tabular-nums text-[color:var(--status-good)] [overflow-wrap:anywhere]">
                      <span className="sr-only">{t("stat_savings")}: </span>
                      -{formatUsd(rec.monthlySaving)}
                    </span>
                  </span>
                </span>
              </label>

              {rec.explainPayload && (
                <div className="mt-3 ml-7 min-w-0">
                  {!explanation && (
                    <button
                      type="button"
                      onClick={() => handleExplain(rec)}
                      className="inline-flex min-h-9 max-w-full cursor-pointer items-center gap-1.5 rounded-lg border border-[color:var(--border-hairline)] px-3 py-1.5 text-xs font-medium text-[color:var(--accent)] hover:bg-[color:var(--surface-2)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)] motion-safe:transition-colors"
                    >
                      <Sparkles size={13} className="shrink-0" aria-hidden="true" />
                      {t("explain_button")}
                      <span className="sr-only">: {rec.resourceId}</span>
                    </button>
                  )}
                  <div aria-live="polite" aria-atomic="true">
                    {explanation?.status === "loading" && (
                      <p className="flex items-center gap-2 text-xs text-[color:var(--text-secondary)]">
                        <LoaderCircle size={14} className="shrink-0 motion-safe:animate-spin" aria-hidden="true" />
                        {t("explain_loading")}
                      </p>
                    )}
                    {explanation?.status === "error" && (
                      <p className="flex items-start gap-2 text-xs leading-relaxed" style={{ color: "var(--status-critical, #a34d43)" }}>
                        <CircleAlert size={14} className="mt-0.5 shrink-0" aria-hidden="true" />
                        {t("explain_error")}
                      </p>
                    )}
                    {explanation?.status === "done" && (
                      <p className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-2)] p-3 text-sm leading-relaxed whitespace-pre-line text-[color:var(--text-secondary)] [overflow-wrap:anywhere]">
                        {explanation.text}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
