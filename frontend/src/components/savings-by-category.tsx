"use client";

import { ChartBar } from "lucide-react";
import { useLanguage } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";

type CategorySaving = {
  category: string;
  amount: number;
};

export function SavingsByCategory({ data }: { data: CategorySaving[] }) {
  const { t } = useLanguage();
  const max = Math.max(0, ...data.map((item) => item.amount));

  return (
    <div className="panel h-full min-w-0">
      <h2 className="panel-heading">
        <span className="icon-box shrink-0" aria-hidden="true">
          <ChartBar size={18} strokeWidth={1.7} />
        </span>
        <span className="min-w-0 [overflow-wrap:anywhere]">{t("savings_by_category_title")}</span>
      </h2>
      <p className="muted-label mt-4">{t("stat_savings")}</p>
      {data.length === 0 ? (
        <p className="mt-6 rounded-xl border border-dashed border-[color:var(--border-hairline)] bg-[color:var(--surface-2)] px-4 py-8 text-center text-sm leading-relaxed text-[color:var(--text-secondary)]">
          {t("no_recommendations")}
        </p>
      ) : (
        <ul className="mt-6 flex flex-col gap-6">
          {data.map((item, index) => (
            <li key={item.category} className="min-w-0">
              <div className="mb-2.5 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                <span className="min-w-0 text-sm leading-relaxed text-[color:var(--text-secondary)] [overflow-wrap:anywhere]">
                  {item.category}
                </span>
                <span className="text-sm font-semibold tabular-nums text-[color:var(--foreground)] [overflow-wrap:anywhere]">
                  {formatUsd(item.amount)}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-[color:var(--gridline)]" aria-hidden="true">
                <div
                  className="h-full rounded-full bg-[color:var(--accent)] motion-safe:transition-[width] motion-safe:duration-300"
                  style={{
                    width: `${max > 0 ? Math.min(100, Math.max(0, (item.amount / max) * 100)) : 0}%`,
                    opacity: Math.max(0.45, 1 - index * 0.13),
                  }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
