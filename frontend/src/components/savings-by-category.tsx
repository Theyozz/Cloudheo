"use client";

import { useLanguage } from "@/lib/i18n";
import { formatUsd } from "@/lib/format";

type CategorySaving = {
  category: string;
  amount: number;
};

export function SavingsByCategory({ data }: { data: CategorySaving[] }) {
  const { t } = useLanguage();

  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
        <h2 className="text-sm font-medium text-[color:var(--text-secondary)]">
          {t("savings_by_category_title")}
        </h2>
        <p className="mt-5 text-sm text-[color:var(--text-muted)]">{t("no_recommendations")}</p>
      </div>
    );
  }

  const max = Math.max(...data.map((d) => d.amount));

  return (
    <div className="rounded-lg border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-5">
      <h2 className="text-sm font-medium text-[color:var(--text-secondary)]">
        {t("savings_by_category_title")}
      </h2>
      <ul className="mt-5 flex flex-col gap-4">
        {data.map((item) => (
          <li key={item.category} className="flex items-center gap-4">
            <span className="w-32 shrink-0 text-sm text-[color:var(--text-secondary)]">
              {item.category}
            </span>
            <span className="relative h-3 flex-1 overflow-hidden rounded-full bg-[color:var(--gridline)]">
              <span
                className="absolute inset-y-0 left-0 rounded-full"
                style={{
                  width: `${(item.amount / max) * 100}%`,
                  backgroundColor: "var(--accent)",
                }}
              />
            </span>
            <span className="w-20 shrink-0 text-right text-sm font-medium tabular-nums">
              {formatUsd(item.amount)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
