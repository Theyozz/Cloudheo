"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "@/lib/i18n";

type Status = "checking" | "online" | "offline";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function BackendStatus() {
  const { t } = useLanguage();
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
        if (!cancelled) setStatus(res.ok ? "online" : "offline");
      } catch {
        if (!cancelled) setStatus("offline");
      }
    }

    check();
    const interval = setInterval(check, 15000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const dotColor =
    status === "online"
      ? "var(--status-good)"
      : status === "offline"
        ? "var(--status-critical)"
        : "var(--text-muted)";

  const label =
    status === "online" ? t("api_connected") : status === "offline" ? t("api_unreachable") : t("api_checking");

  return (
    <div className="flex items-center gap-2 text-sm text-[color:var(--text-secondary)]">
      <span
        className="h-2 w-2 rounded-full"
        style={{ backgroundColor: dotColor }}
        aria-hidden
      />
      <span>{label}</span>
    </div>
  );
}
