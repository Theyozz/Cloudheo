"use client";

import { useState } from "react";
import { ArrowRight, MailCheck } from "lucide-react";
import { useLanguage, type TranslationKey } from "@/lib/i18n";
import { requestAudit, type MonthlySpendRange } from "@/lib/api";

const SPEND_RANGES: { value: MonthlySpendRange; labelKey: TranslationKey }[] = [
  { value: "under_10k", labelKey: "audit_form_spend_under_10k" },
  { value: "10k_50k", labelKey: "audit_form_spend_10k_50k" },
  { value: "50k_200k", labelKey: "audit_form_spend_50k_200k" },
  { value: "over_200k", labelKey: "audit_form_spend_over_200k" },
];

export function AuditLeadForm() {
  const { t } = useLanguage();
  const [name, setName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [workEmail, setWorkEmail] = useState("");
  const [spendRange, setSpendRange] = useState<MonthlySpendRange | "">("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!spendRange) return;
    setSubmitting(true);
    setError(null);
    try {
      await requestAudit({
        name: name.trim(),
        company_name: companyName.trim(),
        work_email: workEmail.trim(),
        monthly_spend_range: spendRange,
        message: message.trim() || undefined,
      });
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  const inputClass = "field-input";

  if (sent) {
    return (
      <div className="mt-8 flex w-full max-w-[480px] flex-col items-center gap-3 rounded-2xl border border-[color:var(--border-hairline)] bg-[color:var(--surface-1)] p-8 text-center">
        <MailCheck size={22} strokeWidth={1.5} className="text-[color:var(--accent)]" aria-hidden="true" />
        <h3 className="text-base font-semibold">{t("audit_form_success_title")}</h3>
        <p className="text-sm leading-relaxed text-[color:var(--text-secondary)]">{t("audit_form_success_body")}</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} aria-busy={submitting} className="mt-8 flex w-full max-w-[480px] flex-col gap-4 text-left">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="audit-name" className="field-label">{t("audit_form_name_label")}</label>
          <input id="audit-name" type="text" required autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} className={inputClass} />
        </div>
        <div>
          <label htmlFor="audit-company" className="field-label">{t("audit_form_company_label")}</label>
          <input id="audit-company" type="text" required autoComplete="organization" value={companyName} onChange={(e) => setCompanyName(e.target.value)} className={inputClass} />
        </div>
      </div>

      <div>
        <label htmlFor="audit-email" className="field-label">{t("audit_form_email_label")}</label>
        <input
          id="audit-email"
          type="email"
          required
          autoComplete="email"
          placeholder="you@company.com"
          value={workEmail}
          onChange={(e) => setWorkEmail(e.target.value)}
          className={inputClass}
        />
      </div>

      <div>
        <label htmlFor="audit-spend" className="field-label">{t("audit_form_spend_label")}</label>
        <select
          id="audit-spend"
          required
          value={spendRange}
          onChange={(e) => setSpendRange(e.target.value as MonthlySpendRange)}
          className={inputClass}
        >
          <option value="" disabled>{t("audit_form_spend_placeholder")}</option>
          {SPEND_RANGES.map((range) => (
            <option key={range.value} value={range.value}>{t(range.labelKey)}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="audit-message" className="field-label">{t("audit_form_message_label")}</label>
        <textarea
          id="audit-message"
          rows={3}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className={`${inputClass} resize-none`}
        />
      </div>

      {error && (
        <p role="alert" className="text-sm" style={{ color: "var(--status-critical)" }}>
          {error}
        </p>
      )}

      <button type="submit" disabled={submitting} className="button button-primary w-full">
        {submitting ? t("audit_form_submitting") : t("audit_form_submit")}
        <ArrowRight size={15} aria-hidden="true" />
      </button>
    </form>
  );
}
