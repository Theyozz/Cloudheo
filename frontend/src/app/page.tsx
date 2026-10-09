"use client";

import Link from "next/link";
import {
  Archive,
  ArrowDown,
  ArrowUpRight,
  Calculator,
  Check,
  CheckCheck,
  ChevronDown,
  CircleCheck,
  Cloud,
  Database,
  Eye,
  Gauge,
  HardDrive,
  KeyRound,
  Moon,
  PlugZap,
  PowerOff,
  ScanLine,
  Server,
  ShieldCheck,
  SlidersHorizontal,
  UserCheck,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import { Brand } from "@/components/brand";
import { CloudOrbit } from "@/components/cloud-orbit";
import { ProductPreview } from "@/components/product-preview";
import { LanguageSwitcher } from "@/components/language-switcher";
import { LandingTheme, ThemeSwitcher } from "@/components/landing-theme";
import { LocalizedText, type TranslationKey } from "@/lib/i18n";

const CONTACT_EMAIL = "theomaurin875@gmail.com";
const CONTACT_SUBJECT = encodeURIComponent("Free AWS audit — Cloudheo");
const MAILTO = `mailto:${CONTACT_EMAIL}?subject=${CONTACT_SUBJECT}`;

type ContentItem = {
  titleKey: TranslationKey;
  descKey: TranslationKey;
  icon: LucideIcon;
};

const SERVICES: { name: string; icon: LucideIcon }[] = [
  { name: "Amazon EC2", icon: Server },
  { name: "Amazon RDS", icon: Database },
  { name: "Amazon EBS", icon: HardDrive },
  { name: "EBS Snapshots", icon: Archive },
];

const FINDINGS: (ContentItem & { services: string })[] = [
  { titleKey: "landing_finding_rightsizing_title", descKey: "landing_finding_rightsizing_desc", icon: Gauge, services: "EC2 · RDS" },
  { titleKey: "landing_finding_nonprod_title", descKey: "landing_finding_nonprod_desc", icon: Moon, services: "EC2 · RDS" },
  { titleKey: "landing_finding_unattached_title", descKey: "landing_finding_unattached_desc", icon: HardDrive, services: "EBS" },
  { titleKey: "landing_finding_stopped_title", descKey: "landing_finding_stopped_desc", icon: PowerOff, services: "EC2 · EBS" },
  { titleKey: "landing_finding_snapshot_title", descKey: "landing_finding_snapshot_desc", icon: Archive, services: "EBS" },
];

const STEPS: ContentItem[] = [
  { titleKey: "landing_step_connect_title", descKey: "landing_step_connect_desc", icon: PlugZap },
  { titleKey: "landing_step_analyze_title", descKey: "landing_step_analyze_desc", icon: ScanLine },
  { titleKey: "landing_step_decide_title", descKey: "landing_step_decide_desc", icon: SlidersHorizontal },
];

const ROADMAP: ContentItem[] = [
  { titleKey: "landing_step_approve_title", descKey: "landing_step_approve_desc", icon: CheckCheck },
  { titleKey: "landing_step_fix_title", descKey: "landing_step_fix_desc", icon: Workflow },
  { titleKey: "landing_step_verify_title", descKey: "landing_step_verify_desc", icon: CircleCheck },
];

const AUDIENCE_STATS: { valueKey: TranslationKey; labelKey: TranslationKey }[] = [
  { valueKey: "landing_audience_stat_size_value", labelKey: "landing_audience_stat_size_label" },
  { valueKey: "landing_audience_stat_spend_value", labelKey: "landing_audience_stat_spend_label" },
  { valueKey: "landing_audience_stat_cloud_value", labelKey: "landing_audience_stat_cloud_label" },
  { valueKey: "landing_audience_stat_team_value", labelKey: "landing_audience_stat_team_label" },
];

const SECURITY_PRINCIPLES: ContentItem[] = [
  { titleKey: "landing_security_principle_readonly_title", descKey: "landing_security_principle_readonly_desc", icon: Eye },
  { titleKey: "landing_security_principle_credentials_title", descKey: "landing_security_principle_credentials_desc", icon: KeyRound },
  { titleKey: "landing_security_principle_revocable_title", descKey: "landing_security_principle_revocable_desc", icon: PowerOff },
  { titleKey: "landing_security_principle_consent_title", descKey: "landing_security_principle_consent_desc", icon: UserCheck },
];

const FAQ: { questionKey: TranslationKey; answerKey: TranslationKey }[] = [
  { questionKey: "landing_faq_audit_q", answerKey: "landing_faq_audit_a" },
  { questionKey: "landing_faq_changes_q", answerKey: "landing_faq_changes_a" },
  { questionKey: "landing_faq_services_q", answerKey: "landing_faq_services_a" },
  { questionKey: "landing_faq_ai_q", answerKey: "landing_faq_ai_a" },
];

function PrimaryButton({ children }: { children: React.ReactNode }) {
  return (
    <a href={MAILTO} className="button button-primary">
      {children}<ArrowUpRight size={16} aria-hidden="true" />
    </a>
  );
}

export default function LandingPage() {
  return (
    <LandingTheme>
      <a href="#main-content" className="skip-link"><LocalizedText id="skip_to_content" /></a>
      <header className="site-header">
        <div className="site-container header-inner">
          <Brand />
          <nav className="desktop-nav">
            <a href="#findings"><LocalizedText id="landing_nav_findings" /></a>
            <a href="#how"><LocalizedText id="landing_nav_how" /></a>
            <a href="#security"><LocalizedText id="landing_nav_security" /></a>
            <a href="#faq"><LocalizedText id="landing_nav_faq" /></a>
          </nav>
          <div className="header-actions">
            <ThemeSwitcher />
            <LanguageSwitcher />
            <Link href="/app" className="button button-small button-outline">
              <LocalizedText id="landing_nav_login" /><ArrowUpRight size={14} aria-hidden="true" />
            </Link>
          </div>
        </div>
      </header>

      <main id="main-content">
        <section className="hero-section site-container">
          <div className="hero-copy">
            <p className="eyebrow"><span className="status-dot" /><LocalizedText id="landing_eyebrow" /></p>
            <h1><LocalizedText id="landing_hero_line" accentId="landing_hero_accent" /></h1>
            <p className="hero-description"><LocalizedText id="landing_hero_description" /></p>
            <div className="hero-actions">
              <PrimaryButton><LocalizedText id="landing_cta_primary" /></PrimaryButton>
              <a href="#findings" className="text-link"><LocalizedText id="landing_cta_secondary" /><ArrowDown size={15} aria-hidden="true" /></a>
            </div>
            <div className="hero-trust">
              <span><ShieldCheck size={14} aria-hidden="true" /><LocalizedText id="landing_trust_readonly" /></span>
              <span><KeyRound size={14} aria-hidden="true" /><LocalizedText id="landing_trust_keys" /></span>
              <span><Check size={14} aria-hidden="true" /><LocalizedText id="landing_trust_free" /></span>
            </div>
          </div>
          <ProductPreview />
        </section>

        <div className="service-strip site-container">
          <p><LocalizedText id="landing_services" /></p>
          <div>{SERVICES.map(({ name, icon: Icon }) => <span key={name}><Icon size={22} strokeWidth={1.4} aria-hidden="true" />{name}</span>)}</div>
        </div>

        <section id="findings" className="site-container section-space">
          <div className="section-heading-row">
            <div><p className="eyebrow"><LocalizedText id="landing_findings_eyebrow" /></p><h2 className="section-title"><LocalizedText id="landing_findings_title" /></h2></div>
            <p className="section-description"><LocalizedText id="landing_findings_description" /></p>
          </div>
          <div className="findings-grid">
            {FINDINGS.map(({ titleKey, descKey, icon: Icon, services }) => (
              <article key={titleKey} className="finding-card">
                <div className="finding-card-top">
                  <span className="icon-box" aria-hidden="true"><Icon size={18} strokeWidth={1.6} /></span>
                  <span className="mono-label finding-services">{services}</span>
                </div>
                <h3><LocalizedText id={titleKey} /></h3>
                <p><LocalizedText id={descKey} /></p>
              </article>
            ))}
            <article className="finding-card finding-note">
              <span className="icon-box" aria-hidden="true"><Calculator size={18} strokeWidth={1.6} /></span>
              <h3><LocalizedText id="landing_finding_note_title" /></h3>
              <p><LocalizedText id="landing_finding_note_desc" /></p>
            </article>
          </div>
        </section>

        <section id="how" className="workflow-section section-space">
          <div className="site-container">
            <div className="section-heading-row">
              <div><p className="eyebrow"><LocalizedText id="landing_how_eyebrow" /></p><h2 className="section-title"><LocalizedText id="landing_how_title" /></h2></div>
              <p className="section-description"><LocalizedText id="landing_how_description" /></p>
            </div>
            <ol className="workflow-grid">
              {STEPS.map(({ titleKey, descKey, icon: Icon }, i) => (
                <li key={titleKey} className="workflow-card">
                  <div className="workflow-card-top"><span className="workflow-icon" aria-hidden="true"><Icon size={23} strokeWidth={1.5} /></span><span className="step-number" aria-hidden="true">0{i + 1}</span></div>
                  <h3><LocalizedText id={titleKey} /></h3>
                  <p><LocalizedText id={descKey} /></p>
                </li>
              ))}
            </ol>
            <div className="roadmap">
              <div className="roadmap-label"><span className="mono-label"><LocalizedText id="landing_next" /></span><span className="soft-badge"><LocalizedText id="landing_step_soon" /></span></div>
              {ROADMAP.map(({ titleKey, descKey, icon: Icon }) => (
                <div className="roadmap-step" key={titleKey}><Icon size={17} aria-hidden="true" /><div><h3><LocalizedText id={titleKey} /></h3><p><LocalizedText id={descKey} /></p></div></div>
              ))}
            </div>
          </div>
        </section>

        <section className="audience-section site-container section-space">
          <div><p className="eyebrow"><LocalizedText id="landing_audience_eyebrow" /></p><h2 className="section-title"><LocalizedText id="landing_audience_heading" /></h2><p className="section-description"><LocalizedText id="landing_audience_description" /></p></div>
          <div className="audience-stats">
            {AUDIENCE_STATS.map((stat) => <div key={stat.valueKey}><p><LocalizedText id={stat.valueKey} /></p><span><LocalizedText id={stat.labelKey} /></span></div>)}
          </div>
        </section>

        <section id="security" className="security-section">
          <div className="site-container security-grid">
            <div className="security-intro">
              <p className="eyebrow"><LocalizedText id="landing_security_eyebrow" /></p>
              <h2 className="section-title"><LocalizedText id="landing_security_heading" /></h2>
              <p className="section-description"><LocalizedText id="landing_security_description" /></p>
              <CloudOrbit />
              <p className="security-signature"><ShieldCheck size={14} aria-hidden="true" /><LocalizedText id="landing_security_note" /></p>
            </div>
            <div className="security-principles">
              {SECURITY_PRINCIPLES.map(({ titleKey, descKey, icon: Icon }) => (
                <article key={titleKey} className="security-principle"><span className="security-icon" aria-hidden="true"><Icon size={19} strokeWidth={1.6} /></span><div><h3><LocalizedText id={titleKey} /></h3><p><LocalizedText id={descKey} /></p></div></article>
              ))}
            </div>
          </div>
        </section>

        <section id="faq" className="faq-section site-container section-space">
          <div><p className="eyebrow"><LocalizedText id="landing_faq_eyebrow" /></p><h2 className="section-title"><LocalizedText id="landing_faq_title" /></h2></div>
          <div className="faq-list">
            {FAQ.map(({ questionKey, answerKey }) => (
              <details key={questionKey} className="faq-item">
                <summary><LocalizedText id={questionKey} /><ChevronDown size={16} aria-hidden="true" /></summary>
                <p><LocalizedText id={answerKey} /></p>
              </details>
            ))}
          </div>
        </section>

        <section className="final-cta site-container section-space">
          <span className="cta-cloud" aria-hidden="true"><Cloud size={29} strokeWidth={1.4} /></span>
          <p className="eyebrow"><LocalizedText id="landing_final_eyebrow" /></p>
          <h2><LocalizedText id="landing_final_heading" /></h2>
          <p className="section-description"><LocalizedText id="landing_final_description" /></p>
          <PrimaryButton><LocalizedText id="landing_cta_primary" /></PrimaryButton>
          <span className="cta-reassurance"><ShieldCheck size={13} aria-hidden="true" /><LocalizedText id="landing_trust_readonly" /> · <LocalizedText id="landing_trust_keys" /></span>
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-container footer-inner"><Brand /><p><LocalizedText id="landing_footer_note" /></p><span><LocalizedText id="landing_footer" /></span></div>
      </footer>
    </LandingTheme>
  );
}
