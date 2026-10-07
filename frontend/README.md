# Cloudheo — Frontend

Next.js dashboard for Cloudheo: AWS spend overview, potential savings, and
recommendations. Currently renders placeholder data — not yet wired to the
backend's real AWS/FinOps endpoints.

## Stack

- **Next.js 16** (App Router, Turbopack)
- **TypeScript**
- **Tailwind CSS v4**

## Structure

```
src/
├── app/
│   ├── layout.tsx        Root layout, fonts, wraps the app in LanguageProvider
│   ├── page.tsx           Dashboard page
│   └── globals.css        Design tokens (colors, light/dark mode) + Tailwind import
├── components/
│   ├── backend-status.tsx    Live API connectivity indicator (polls GET /health)
│   ├── language-switcher.tsx EN/FR toggle
│   ├── stat-tile.tsx          Stat card (label, value, optional delta)
│   ├── risk-badge.tsx          LOW/MEDIUM/HIGH risk pill
│   ├── savings-by-category.tsx Horizontal bar list
│   └── top-recommendations.tsx Recommendation list
└── lib/
    └── i18n.tsx            Translation dictionary + React context (see below)
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
