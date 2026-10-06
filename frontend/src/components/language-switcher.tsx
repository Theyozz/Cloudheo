"use client";

import { useLanguage, type Lang } from "@/lib/i18n";

const OPTIONS: Lang[] = ["en", "fr"];

export function LanguageSwitcher() {
  const { lang, setLang } = useLanguage();

  return (
    <div className="flex items-center gap-1 text-sm">
      {OPTIONS.map((option, index) => (
        <span key={option} className="flex items-center gap-1">
          {index > 0 && <span className="text-[color:var(--text-muted)]">/</span>}
          <button
            type="button"
            onClick={() => setLang(option)}
            aria-pressed={lang === option}
            className={
              lang === option
                ? "font-medium text-[color:var(--foreground)]"
                : "text-[color:var(--text-muted)] hover:text-[color:var(--text-secondary)]"
            }
          >
            {option.toUpperCase()}
          </button>
        </span>
      ))}
    </div>
  );
}
