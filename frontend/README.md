# Cloudheo — Frontend

Next.js app for Cloudheo: a public landing page plus the authenticated
dashboard (AWS spend, potential savings, recommendations, savings simulator).

## Routes

| Route | Public? | Content |
|---|---|---|
| `/` | Yes | Landing page — pitch, how it works, security, contact CTA |
| `/app` | Login required | Dashboard — login/register gate, then the real app |
| `/reset-password` | Yes | Set a new password from a forgot-password email link (`?token=...`) |

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
│   ├── reset-password/page.tsx  Set a new password from an emailed token
│   └── globals.css        Design tokens (colors, light/dark mode) + Tailwind import
├── components/
│   ├── language-switcher.tsx  EN/FR toggle
│   ├── login-form.tsx          Sign in / create organization / forgot password, with a show/hide password toggle
│   ├── reset-password-form.tsx New password + confirm, from a forgot-password email link
│   ├── connect-aws-form.tsx    Role ARN (+ external ID / region) to connect an AWS account
│   ├── stat-tile.tsx           Stat card (label, value, optional delta)
│   ├── risk-badge.tsx          LOW/MEDIUM/HIGH risk pill
│   ├── savings-by-category.tsx Horizontal bar list
│   ├── top-recommendations.tsx Recommendation list, selectable, with an on-demand "Explain" (AI) per row
│   └── savings-simulator.tsx   Live total for the currently selected recommendations
└── lib/
    ├── i18n.tsx            Translation dictionary + React context (see below)
    ├── auth.ts              Token storage, login/register/logout/forgot-reset password, authFetch() wrapper
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
backend is multi-tenant — registration is always open and creates a new
organization — so `LoginForm` has an explicit "sign in" / "create an
organization" toggle rather than guessing which to show; register mode adds
an organization name field. Every protected API call goes through
`authFetch()`, which attaches the bearer token and throws `AuthRequiredError`
on a 401 so the dashboard can drop back to the login screen (expired
session) without a special case at every call site.

`LoginForm` has a third mode, "forgot password": just an email field, always
shows the same "check your email" confirmation regardless of whether that
email has an account (the backend is deliberately silent about this too —
see the backend README). The emailed link opens the public `/reset-password`
page (`reset-password-form.tsx`), which reads `?token=` from the URL, asks
for a new password twice, and submits it. A successful reset signs the user
out of every other session as well — expect to have to log back in anywhere
else you were signed in.

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
