"use client";

import { createContext, useContext, useLayoutEffect, useSyncExternalStore, type ReactNode } from "react";
import { Moon, Sun } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

type Theme = "system" | "light" | "dark";

// Scoped to the landing experiment; the application keeps its existing theme.
const STORAGE_KEY = "cloudheo-landing-theme";
const CHANGE_EVENT = "cloudheo-landing-theme-change";
let fallbackTheme: Theme | null = null;

function isTheme(value: unknown): value is Theme {
  return value === "system" || value === "light" || value === "dark";
}

function getSnapshot(): Theme {
  if (fallbackTheme !== null) return fallbackTheme;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isTheme(stored) ? stored : "system";
  } catch {
    return "system";
  }
}

function getServerSnapshot(): Theme {
  return "system";
}

function subscribe(onChange: () => void) {
  function onStorage(event: StorageEvent) {
    if (event.key === STORAGE_KEY || event.key === null) {
      fallbackTheme = null;
      onChange();
    }
  }

  window.addEventListener("storage", onStorage);
  window.addEventListener(CHANGE_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onStorage);
    window.removeEventListener(CHANGE_EVENT, onChange);
  };
}

function setTheme(theme: Theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
    fallbackTheme = null;
  } catch {
    // Switching still works when browser storage is unavailable.
    fallbackTheme = theme;
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

const ThemeContext = createContext<Theme>("system");

export function LandingTheme({ children }: { children: ReactNode }) {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  useLayoutEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-landing-theme", theme);
    // Next.js retains hidden pages with Activity. Its effect cleanup prevents
    // the landing's browser canvas and scrollbar theme from leaking into /app.
    return () => root.removeAttribute("data-landing-theme");
  }, [theme]);

  return (
    <ThemeContext.Provider value={theme}>
      <div className="landing-page" data-theme={theme}>{children}</div>
    </ThemeContext.Provider>
  );
}

function subscribeToSystemTheme(onChange: () => void) {
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}

function getSystemDark() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function getServerSystemDark() {
  return false;
}

export function ThemeSwitcher() {
  const theme = useContext(ThemeContext);
  const { t } = useLanguage();
  const systemDark = useSyncExternalStore(subscribeToSystemTheme, getSystemDark, getServerSystemDark);
  const isDark = theme === "dark" || (theme === "system" && systemDark);

  return (
    <div className="theme-switcher">
      <button
        type="button"
        role="switch"
        className="theme-toggle"
        aria-label={t("theme_dark_mode")}
        aria-checked={isDark}
        title={t(isDark ? "theme_switch_light" : "theme_switch_dark")}
        onClick={() => setTheme(isDark ? "light" : "dark")}
      >
        <Sun size={15} strokeWidth={1.7} aria-hidden="true" />
        <Moon size={15} strokeWidth={1.7} aria-hidden="true" />
      </button>
    </div>
  );
}