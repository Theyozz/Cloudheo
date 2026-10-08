"use client";

import { useState } from "react";
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
    <div className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
      <h2 className="text-sm font-medium text-[color:var(--text-secondary)]">
        {t("top_recommendations_title")}
      </h2>
      {data.length === 0 && <p className="mt-4 text-sm text-[color:var(--text-muted)]">{t("no_recommendations")}</p>}
      <ul className="mt-4 flex flex-col divide-y divide-[color:var(--border-hairline)]">
        {data.map((rec) => {
          const explanation = explanations[rec.resourceId];
          return (
            <li key={rec.resourceId} className="flex flex-col gap-2 py-3 first:pt-1 last:pb-1">
              <div className="flex items-center justify-between gap-4">
                <label className="flex min-w-0 flex-1 cursor-pointer items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(rec.resourceId)}
                    onChange={() => onToggle(rec.resourceId)}
                    className="mt-1 h-4 w-4 shrink-0 accent-[color:var(--accent)]"
                  />
                  <span className="min-w-0">
                    <p className="text-sm font-medium">
                      {rec.resourceType} · {rec.resourceId}
                    </p>
                    <p className="text-xs text-[color:var(--text-muted)]">
                      {rec.category} · {t("confidence_label", { percent: Math.round(rec.confidence * 100) })}
                    </p>
                  </span>
                </label>
                <div className="flex shrink-0 items-center gap-3">
                  <span className="text-sm font-medium tabular-nums" style={{ color: "var(--status-good)" }}>
                    -{formatUsd(rec.monthlySaving)}/mo
                  </span>
                  <RiskBadge risk={rec.risk} />
                </div>
              </div>

              {rec.explainPayload && (
                <div className="ml-7">
                  {!explanation && (
                    <button
                      type="button"
                      onClick={() => handleExplain(rec)}
                      className="text-xs text-[color:var(--accent)] hover:underline"
                    >
                      ✨ {t("explain_button")}
                    </button>
                  )}
                  {explanation?.status === "loading" && (
                    <p className="text-xs text-[color:var(--text-muted)]">{t("explain_loading")}</p>
                  )}
                  {explanation?.status === "error" && (
                    <p className="text-xs" style={{ color: "var(--status-critical)" }}>
                      {t("explain_error")}
                    </p>
                  )}
                  {explanation?.status === "done" && (
                    <p className="max-w-xl text-xs text-[color:var(--text-secondary)]">{explanation.text}</p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
