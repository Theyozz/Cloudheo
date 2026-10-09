"use client";

import { useId, useState } from "react";
import { ArrowDownRight, ArrowUpRight, Check, ChevronDown, Cloud, Database, HardDrive, LayoutDashboard, Server, ShieldCheck, Sparkles } from "lucide-react";
import { LocalizedText, useLanguage, type TranslationKey } from "@/lib/i18n";

const OPPORTUNITIES = [
  { id: "ec2", icon: Server, name: "EC2", key: "rec_category_rightsizing" as TranslationKey, amount: 820 },
  { id: "rds", icon: Database, name: "RDS", key: "rec_category_non_prod_scheduling" as TranslationKey, amount: 630 },
  { id: "ebs", icon: HardDrive, name: "EBS", key: "rec_category_unattached_volume" as TranslationKey, amount: 210 },
];

export function ProductPreview() {
  const { t, lang } = useLanguage();
  const gradientId = useId();
  const [selected, setSelected] = useState(() => new Set(OPPORTUNITIES.map((item) => item.id)));
  const savings = OPPORTUNITIES.filter((item) => selected.has(item.id)).reduce((total, item) => total + item.amount, 0);
  const money = (value: number) => new Intl.NumberFormat(lang === "fr" ? "fr-FR" : "en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

  function toggle(id: string) {
    setSelected((previous) => {
      const next = new Set(previous);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="preview-scene">
      <div className="preview-halo" aria-hidden="true" />
      <div className="product-preview">
        <div className="preview-topbar">
          <div className="flex items-center gap-2.5"><span className="preview-cloud"><Cloud size={16} /></span><span>acme / <strong><LocalizedText id="preview_workspace" /></strong><ChevronDown size={11} className="ml-1 inline" /></span></div>
          <span className="preview-demo-label"><span /><LocalizedText id="preview_demo" /></span>
        </div>
        <div className="preview-content">
          <div className="preview-heading"><span><LayoutDashboard size={13} /><LocalizedText id="nav_dashboard" /></span><span>AWS</span></div>
          <div className="preview-metrics">
            <div><p><LocalizedText id="stat_spend" /></p><strong>{money(17840)}</strong><span className="preview-period"><LocalizedText id="preview_period" /></span></div>
            <div className="preview-savings"><p><LocalizedText id="stat_savings" /></p><strong>{money(savings)}<ArrowDownRight size={22} /></strong><span><LocalizedText id="preview_identified" /></span></div>
          </div>
          <div className="preview-chart" role="img" aria-label={t("preview_chart_label")}>
            <div className="chart-grid" aria-hidden="true"><span>$20k</span><span>$15k</span><span>$10k</span></div>
            <svg viewBox="0 0 400 120" preserveAspectRatio="none" aria-hidden="true">
              <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--accent)" stopOpacity="0.16" /><stop offset="100%" stopColor="var(--accent)" stopOpacity="0" /></linearGradient></defs>
              <path d="M0 41 C20 43 24 21 45 28 S78 44 98 34 S123 45 143 33 S168 39 185 31 S212 46 230 35 S257 30 277 24 S299 34 320 22 S349 23 367 14 S389 22 400 14" fill="none" stroke="var(--text-muted)" strokeWidth="1.5" strokeDasharray="4 5" />
              <path d="M0 41 C20 43 24 21 45 28 S78 44 98 34 S123 45 143 38 S168 53 185 49 S212 72 230 65 S257 74 277 71 S299 91 320 83 S349 92 367 89 S389 97 400 94 L400 120 L0 120Z" fill={`url(#${gradientId})`} />
              <path d="M0 41 C20 43 24 21 45 28 S78 44 98 34 S123 45 143 38 S168 53 185 49 S212 72 230 65 S257 74 277 71 S299 91 320 83 S349 92 367 89 S389 97 400 94" fill="none" stroke="var(--accent)" strokeWidth="2.5" />
            </svg>
            <div className="chart-caption"><span><LocalizedText id="preview_illustration" /></span><span><i /><LocalizedText id="preview_optimized" /></span></div>
          </div>
          <div className="preview-list-heading"><span><Sparkles size={13} /><LocalizedText id="preview_opportunities" /></span><span>03</span></div>
          <div className="preview-opportunities">
            {OPPORTUNITIES.map((item) => (
              <label key={item.id} className={`preview-opportunity${selected.has(item.id) ? " is-selected" : ""}`}>
                <input type="checkbox" checked={selected.has(item.id)} onChange={() => toggle(item.id)} aria-label={`${item.name} · ${t(item.key)}`} />
                <span className="preview-service-icon"><item.icon size={15} strokeWidth={1.6} /></span>
                <span className="preview-resource"><strong>{item.name}</strong><span><LocalizedText id={item.key} /></span></span>
                <span className="preview-amount">−{money(item.amount)}<ArrowUpRight size={12} /></span>
              </label>
            ))}
          </div>
          <div className="preview-bottom"><ShieldCheck size={13} /><span><LocalizedText id="preview_safe" /></span><Check size={13} className="ml-auto" /></div>
        </div>
      </div>
      <div className="preview-floating-note"><span className="floating-check"><Check size={16} /></span><div><strong><LocalizedText id="preview_in_control" /></strong><span><LocalizedText id="preview_try" /></span></div></div>
      <p className="preview-disclaimer" role="status" aria-live="polite">{t("preview_selection", { amount: money(savings) })}</p>
    </div>
  );
}