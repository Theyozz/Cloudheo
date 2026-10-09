"use client";

import { useLayoutEffect, useSyncExternalStore } from "react";
import { Moon, Sun } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

type Theme = "system" | "light" | "dark";

// One preference for the whole app (landing, dashboard, auth pages) — not
// scoped to whichever page the user happened to set it from.
const STORAGE_KEY = "cloudheo-theme";
const CHANGE_EVENT = "cloudheo-theme-change";
let fallbackTheme: Theme | null = null;

function isTheme(value: unknown): value is Theme {
  return value === "system" || value === "light" || value === "dark";
}

function getSnapshot(): Theme {
  if (fallbackTheme !== null) return fallbackTheme;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isTheme(stored) ? stored : "dark";
  } catch {
    return "dark";
  }
}

function getServerSnapshot(): Theme {
  return "dark";
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

/** Keeps <html data-theme> in sync with the stored preference. Mounted once
 * in the root layout (not a specific page) so a choice made anywhere
 * applies on every page, including ones visited later in the same session. */
export function ThemeSync() {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  useLayoutEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return null;
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

/** Reads the same global preference directly — no provider/context needed,
 * so this can be dropped into any page's header. */
export function ThemeSwitcher() {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
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
