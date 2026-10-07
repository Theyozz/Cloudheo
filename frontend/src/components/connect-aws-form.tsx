"use client";

import { useState } from "react";
import { useLanguage } from "@/lib/i18n";
import { connectAwsAccount } from "@/lib/api";

export function ConnectAwsForm({ onConnected, onCancel }: { onConnected: () => void; onCancel: () => void }) {
  const { t } = useLanguage();
  const [roleArn, setRoleArn] = useState("");
  const [externalId, setExternalId] = useState("");
  const [region, setRegion] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await connectAwsAccount({
        role_arn: roleArn.trim(),
        external_id: externalId.trim() || undefined,
        region: region.trim() || undefined,
      });
      onConnected();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  const inputClass =
    "w-full rounded-md border border-[color:var(--border-hairline)] bg-[color:var(--background)] px-3 py-2 text-sm outline-none focus:border-[color:var(--accent)]";

  return (
    <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3">
      <div>
        <label htmlFor="role_arn" className="mb-1 block text-xs text-[color:var(--text-secondary)]">
          {t("connect_form_role_arn_label")}
        </label>
        <input
          id="role_arn"
          type="text"
          required
          value={roleArn}
          onChange={(e) => setRoleArn(e.target.value)}
          placeholder="arn:aws:iam::123456789012:role/CloudheoReadOnlyRole"
          className={inputClass}
        />
      </div>

      <button
        type="button"
        onClick={() => setShowAdvanced((v) => !v)}
        className="self-start text-xs text-[color:var(--text-muted)] hover:text-[color:var(--text-secondary)]"
      >
        {showAdvanced ? "▾" : "▸"} {t("connect_form_advanced")}
      </button>

      {showAdvanced && (
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="flex-1">
            <label htmlFor="external_id" className="mb-1 block text-xs text-[color:var(--text-secondary)]">
              {t("connect_form_external_id_label")}
            </label>
            <input
              id="external_id"
              type="text"
              value={externalId}
              onChange={(e) => setExternalId(e.target.value)}
              className={inputClass}
            />
          </div>
          <div className="flex-1">
            <label htmlFor="region" className="mb-1 block text-xs text-[color:var(--text-secondary)]">
              {t("connect_form_region_label")}
            </label>
            <input
              id="region"
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="eu-west-1"
              className={inputClass}
            />
          </div>
        </div>
      )}

      {error && <p className="text-sm" style={{ color: "var(--status-critical)" }}>{error}</p>}

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={submitting || !roleArn.trim()}
          className="rounded-md bg-[color:var(--foreground)] px-4 py-2 text-sm font-medium text-[color:var(--background)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? t("connect_form_connecting") : t("connect_form_submit")}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="text-sm text-[color:var(--text-secondary)] hover:text-[color:var(--foreground)]"
        >
          {t("connect_form_cancel")}
        </button>
      </div>
    </form>
  );
}
