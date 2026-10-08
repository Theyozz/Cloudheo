# Cloudheo — Frontend

Next.js app for Cloudheo: a public landing page plus the authenticated
dashboard (AWS spend, potential savings, recommendations, savings simulator).

## Routes

| Route | Public? | Content |
|---|---|---|
| `/` | Yes | Landing page — pitch, how it works, security, contact CTA |
| `/app` | Login required | Dashboard — login/register gate, then the real app |

## Stack

- **Next.js 16** (App Router, Turbopack)
- **TypeScript**
- **Tailwind CSS v4**

## Structure

```
src/
├── app/
│   ├── layout.tsx        Root layout, fonts, wraps the app in LanguageProvider
│   ├── page.tsx            Landing page (public)
│   ├── app/page.tsx        Dashboard — auth gate (login/register) then the app
│   └── globals.css        Design tokens (colors, light/dark mode) + Tailwind import
├── components/
│   ├── backend-status.tsx     Live API connectivity indicator (polls GET /health)
│   ├── language-switcher.tsx  EN/FR toggle
│   ├── login-form.tsx          Register (first run only) / sign in, with a show/hide password toggle
│   ├── connect-aws-form.tsx    Role ARN (+ external ID / region) to connect an AWS account
│   ├── stat-tile.tsx           Stat card (label, value, optional delta)
│   ├── risk-badge.tsx          LOW/MEDIUM/HIGH risk pill
│   ├── savings-by-category.tsx Horizontal bar list
│   ├── top-recommendations.tsx Recommendation list, selectable, with an on-demand "Explain" (AI) per row
│   └── savings-simulator.tsx   Live total for the currently selected recommendations
└── lib/
    ├── i18n.tsx            Translation dictionary + React context (see below)
    ├── auth.ts              Token storage, login/register/logout, authFetch() wrapper
    ├── api.ts                Typed calls to the dashboard/AWS/AI endpoints
    └── format.ts             Shared USD currency formatting
```

## Setup

```bash
npm install
```

Set `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`) if the backend
runs somewhere other than localhost — see the root `.env.example`.

## Scripts

```bash
npm run dev     # dev server (Turbopack)
npm run build   # production build
npm run lint    # ESLint
```

## Authentication

`/app` is gated: on mount it calls `GET /auth/me` with the token in
`localStorage` (`lib/auth.ts`) and shows `LoginForm` if that fails. The
backend is single-admin — registration only works once — so the form shows
"create admin account" or "sign in" based on `GET /auth/status`. Every
protected API call goes through `authFetch()`, which attaches the bearer
token and throws `AuthRequiredError` on a 401 so the dashboard can drop back
to the login screen (expired session) without a special case at every call site.

## Internationalization

Language support is a small custom context in `src/lib/i18n.tsx` — no external
i18n library. The preference is stored in `localStorage` and defaults to
English on first visit and during server rendering (to avoid a hydration
mismatch), then syncs to the stored value once mounted.

To add a string: add the key to **both** the `en` and `fr` objects in
`translations`, then call `t("your_key")` from any client component via
`useLanguage()`. To add a language: add a new top-level key to `translations`
with the same shape, and add it to `OPTIONS` in `language-switcher.tsx`.

## Design

Sober, data-oriented B2B look — no gradients, no decorative animation. Colors
are defined as CSS custom properties in `globals.css` (light/dark aware) and
referenced by role (`--accent`, `--status-good`, `--text-secondary`, ...)
rather than raw hex values in components. Status colors (risk levels, API
connectivity) always pair a colored dot/indicator with a text label — never
color alone.
