"use client";

import { useLanguage, type Lang } from "@/lib/i18n";

const OPTIONS: Lang[] = ["en", "fr"];

export function LanguageSwitcher() {
  const { lang, setLang } = useLanguage();

  return (
    <div className="language-switcher" data-language={lang} role="group" aria-label={lang === "fr" ? "Langue" : "Language"}>
      {OPTIONS.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setLang(option)}
            aria-pressed={lang === option}
            aria-label={option === "fr" ? "Français" : "English"}
            lang={option}
          >
            {option.toUpperCase()}
          </button>
      ))}
    </div>
  );
}
