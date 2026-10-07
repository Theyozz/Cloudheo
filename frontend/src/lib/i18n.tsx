"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type Lang = "en" | "fr";

const STORAGE_KEY = "cloudheo-lang";

const translations = {
  en: {
    nav_dashboard: "Dashboard",
    api_connected: "API connected",
    api_unreachable: "API unreachable",
    api_checking: "Checking API…",
    dashboard_title: "Dashboard",
    dashboard_subtitle: "Overview of your AWS spend and optimization opportunities.",
    sample_data_badge: "Sample data · AWS not connected",
    connect_aws_title: "Connect your AWS account",
    connect_aws_description:
      "Cloudheo analyzes your account using a read-only IAM role via AWS STS AssumeRole. No permanent credentials are requested and no destructive permissions are ever used.",
    connect_aws_button: "Connect AWS account",
    connect_aws_tooltip: "AWS integration is coming soon",
    stat_spend: "AWS spend / month",
    stat_savings: "Potential savings / month",
    stat_savings_delta: "{percent}% of spend",
    stat_recommendations: "Recommendations",
    savings_by_category_title: "Potential savings by category",
    top_recommendations_title: "Top recommendations",
    confidence_label: "{percent}% confidence",
    risk_low: "Low risk",
    risk_medium: "Medium risk",
    risk_high: "High risk",
    footer: "Cloudheo — read-only MVP",
    category_non_production: "Non-production",
    rec_category_rightsizing: "Rightsizing",
    rec_category_non_prod_scheduling: "Non-production scheduling",
    rec_category_unattached_volume: "Unattached volume",
    connected_badge: "Connected · AWS account {account}",
    disconnect_button: "Disconnect",
    connect_form_role_arn_label: "Read-only role ARN",
    connect_form_advanced: "Advanced options",
    connect_form_external_id_label: "External ID (optional)",
    connect_form_region_label: "Restrict to a single region (optional)",
    connect_form_submit: "Validate & connect",
    connect_form_cancel: "Cancel",
    connect_form_connecting: "Connecting…",
    loading_text: "Loading…",
    no_recommendations: "No recommendations yet.",
    simulator_title: "Savings simulator",
    simulator_selected: "{count} selected",
    simulator_current_spend: "Current spend",
    simulator_estimated_savings: "Estimated savings",
    simulator_new_spend: "New estimated spend",
  },
  fr: {
    nav_dashboard: "Tableau de bord",
    api_connected: "API connectée",
    api_unreachable: "API injoignable",
    api_checking: "Vérification de l'API…",
    dashboard_title: "Tableau de bord",
    dashboard_subtitle: "Vue d'ensemble de vos dépenses AWS et des opportunités d'optimisation.",
    sample_data_badge: "Données d'exemple · AWS non connecté",
    connect_aws_title: "Connectez votre compte AWS",
    connect_aws_description:
      "Cloudheo analyse votre compte via un rôle IAM en lecture seule, grâce à AWS STS AssumeRole. Aucun identifiant permanent n'est demandé et aucune permission destructrice n'est jamais utilisée.",
    connect_aws_button: "Connecter un compte AWS",
    connect_aws_tooltip: "L'intégration AWS arrive bientôt",
    stat_spend: "Dépenses AWS / mois",
    stat_savings: "Économies potentielles / mois",
    stat_savings_delta: "{percent}% des dépenses",
    stat_recommendations: "Recommandations",
    savings_by_category_title: "Économies potentielles par catégorie",
    top_recommendations_title: "Meilleures recommandations",
    confidence_label: "{percent}% de confiance",
    risk_low: "Risque faible",
    risk_medium: "Risque moyen",
    risk_high: "Risque élevé",
    footer: "Cloudheo — MVP en lecture seule",
    category_non_production: "Hors production",
    rec_category_rightsizing: "Redimensionnement",
    rec_category_non_prod_scheduling: "Planification hors production",
    rec_category_unattached_volume: "Volume non attaché",
    connected_badge: "Connecté · compte AWS {account}",
    disconnect_button: "Déconnecter",
    connect_form_role_arn_label: "ARN du rôle en lecture seule",
    connect_form_advanced: "Options avancées",
    connect_form_external_id_label: "External ID (optionnel)",
    connect_form_region_label: "Restreindre à une seule région (optionnel)",
    connect_form_submit: "Valider et connecter",
    connect_form_cancel: "Annuler",
    connect_form_connecting: "Connexion…",
    loading_text: "Chargement…",
    no_recommendations: "Aucune recommandation pour l'instant.",
    simulator_title: "Simulateur d'économies",
    simulator_selected: "{count} sélectionnée(s)",
    simulator_current_spend: "Dépense actuelle",
    simulator_estimated_savings: "Économies estimées",
    simulator_new_spend: "Nouvelle dépense estimée",
  },
} as const;

export type TranslationKey = keyof (typeof translations)["en"];

type LanguageContextValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: TranslationKey, vars?: Record<string, string | number>) => string;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  // Always render "en" during SSR/first paint so server and client markup
  // match, then sync from localStorage (an external system) once mounted.
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "en" || stored === "fr") {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- syncing initial state from localStorage, an external system, on mount
      setLangState(stored);
    }
  }, []);

  function setLang(next: Lang) {
    setLangState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }

  function t(key: TranslationKey, vars?: Record<string, string | number>) {
    let str: string = translations[lang][key];
    if (vars) {
      for (const [name, value] of Object.entries(vars)) {
        str = str.replace(`{${name}}`, String(value));
      }
    }
    return str;
  }

  return <LanguageContext.Provider value={{ lang, setLang, t }}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}
