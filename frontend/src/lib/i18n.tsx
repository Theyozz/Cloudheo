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
    rec_category_stopped_instance_storage: "Stopped instance storage",
    rec_category_orphaned_snapshot: "Orphaned snapshot",
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
    auth_login_title: "Sign in to Cloudheo",
    auth_register_title: "Create your admin account",
    auth_register_subtitle: "One-time setup — this creates the only admin account for this instance.",
    auth_email_label: "Email",
    auth_password_label: "Password",
    auth_submit_login: "Sign in",
    auth_submit_register: "Create account",
    auth_submitting: "Please wait…",
    auth_logout: "Log out",
    auth_checking: "Checking session…",
    auth_show_password: "Show password",
    auth_hide_password: "Hide password",
    explain_button: "Explain",
    explain_loading: "Explaining…",
    explain_error: "Couldn't generate an explanation.",

    // Landing page
    landing_nav_how: "How it works",
    landing_nav_security: "Security",
    landing_nav_login: "Sign in",
    landing_hero_title: "Cloudheo detects, explains and eliminates unnecessary AWS spend.",
    landing_hero_subtitle:
      "A FinOps tool for small and mid-size teams without a dedicated cloud cost function. Connect a read-only AWS role and get a clear picture of what you're wasting — in minutes, not a consulting engagement.",
    landing_cta_primary: "Request a free AWS audit",
    landing_cta_secondary: "See how it works",
    landing_loop_title: "How Cloudheo works",
    landing_loop_subtitle:
      "Every number is computed by deterministic rules, not guessed by an AI — the explanations just make them easy to read.",
    landing_step_detect_title: "Detect",
    landing_step_detect_desc: "Scan your AWS account (read-only) for cost and usage data.",
    landing_step_explain_title: "Explain",
    landing_step_explain_desc:
      "A rule-based engine finds concrete waste — oversized instances, unattached volumes, idle non-prod resources — with every figure traceable back to the source data.",
    landing_step_simulate_title: "Simulate",
    landing_step_simulate_desc: "Pick optimizations and preview their combined impact on your bill before doing anything.",
    landing_step_approve_title: "Approve",
    landing_step_approve_desc: "Review and approve changes with a human in the loop.",
    landing_step_fix_title: "Fix",
    landing_step_fix_desc: "Cloudheo applies the approved, low-risk change for you.",
    landing_step_verify_title: "Verify",
    landing_step_verify_desc: "Confirm the expected savings actually showed up on the bill.",
    landing_step_soon: "Coming soon",
    landing_audience_title: "Built for teams without a dedicated FinOps function",
    landing_audience_body:
      "SMEs and mid-market companies, mostly on AWS, with €5k–50k in monthly cloud spend and a small technical team — not a platform or cost-optimization specialist on staff.",
    landing_security_title: "Read-only, always — for now",
    landing_security_body:
      "Cloudheo connects via AWS STS AssumeRole with short-lived, temporary credentials — never your permanent keys. No Delete, Terminate, Modify, or Update permission is ever requested. Nothing changes in your AWS account without your explicit approval.",
    landing_final_cta_title: "See what you're actually spending on — for free.",
    landing_footer: "Cloudheo — read-only MVP",
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
    rec_category_stopped_instance_storage: "Stockage d'instance arrêtée",
    rec_category_orphaned_snapshot: "Snapshot orphelin",
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
    auth_login_title: "Connexion à Cloudheo",
    auth_register_title: "Crée ton compte admin",
    auth_register_subtitle: "Configuration unique — ceci crée le seul compte admin de cette instance.",
    auth_email_label: "Email",
    auth_password_label: "Mot de passe",
    auth_submit_login: "Se connecter",
    auth_submit_register: "Créer le compte",
    auth_submitting: "Patiente…",
    auth_logout: "Déconnexion",
    auth_checking: "Vérification de la session…",
    auth_show_password: "Afficher le mot de passe",
    auth_hide_password: "Masquer le mot de passe",
    explain_button: "Expliquer",
    explain_loading: "Explication…",
    explain_error: "Impossible de générer une explication.",

    // Landing page
    landing_nav_how: "Fonctionnement",
    landing_nav_security: "Sécurité",
    landing_nav_login: "Se connecter",
    landing_hero_title: "Cloudheo détecte, explique et élimine les dépenses cloud inutiles.",
    landing_hero_subtitle:
      "Un outil FinOps pour les petites et moyennes équipes sans fonction dédiée aux coûts cloud. Connectez un rôle AWS en lecture seule et obtenez une image claire de ce que vous gaspillez — en quelques minutes, pas en mission de conseil.",
    landing_cta_primary: "Demander un audit AWS gratuit",
    landing_cta_secondary: "Voir comment ça marche",
    landing_loop_title: "Comment fonctionne Cloudheo",
    landing_loop_subtitle:
      "Chaque chiffre est calculé par des règles déterministes, jamais deviné par une IA — les explications ne font que les rendre lisibles.",
    landing_step_detect_title: "Détecter",
    landing_step_detect_desc: "Analyse de votre compte AWS (lecture seule) : coûts et utilisation.",
    landing_step_explain_title: "Expliquer",
    landing_step_explain_desc:
      "Un moteur à base de règles trouve du gaspillage concret — instances surdimensionnées, volumes non attachés, ressources hors-prod inactives — avec chaque chiffre traçable jusqu'à la donnée source.",
    landing_step_simulate_title: "Simuler",
    landing_step_simulate_desc: "Sélectionnez des optimisations et prévisualisez leur impact combiné sur votre facture avant d'agir.",
    landing_step_approve_title: "Approuver",
    landing_step_approve_desc: "Validez les changements avec un humain dans la boucle.",
    landing_step_fix_title: "Corriger",
    landing_step_fix_desc: "Cloudheo applique pour vous le changement approuvé, à faible risque.",
    landing_step_verify_title: "Vérifier",
    landing_step_verify_desc: "Confirme que l'économie attendue s'est bien reflétée sur la facture.",
    landing_step_soon: "Bientôt disponible",
    landing_audience_title: "Conçu pour les équipes sans fonction FinOps dédiée",
    landing_audience_body:
      "PME et ETI, majoritairement sur AWS, avec 5k–50k€ de dépenses cloud mensuelles et une petite équipe technique — pas de spécialiste de l'optimisation des coûts en interne.",
    landing_security_title: "Lecture seule, toujours — pour l'instant",
    landing_security_body:
      "Cloudheo se connecte via AWS STS AssumeRole, avec des identifiants temporaires et de courte durée — jamais vos clés permanentes. Aucune permission Delete, Terminate, Modify ou Update n'est jamais demandée. Rien ne change dans votre compte AWS sans votre accord explicite.",
    landing_final_cta_title: "Découvrez gratuitement ce sur quoi vous dépensez vraiment.",
    landing_footer: "Cloudheo — MVP en lecture seule",
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
