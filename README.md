# Cloudheo

[![Backend](https://github.com/Theyozz/Cloudheo/actions/workflows/backend.yml/badge.svg)](https://github.com/Theyozz/Cloudheo/actions/workflows/backend.yml)
[![Frontend](https://github.com/Theyozz/Cloudheo/actions/workflows/frontend.yml/badge.svg)](https://github.com/Theyozz/Cloudheo/actions/workflows/frontend.yml)

**Cloudheo detects, explains and eliminates unnecessary AWS spend.**

A B2B FinOps / Cloud Cost Optimization SaaS, initially focused on AWS. Unlike a
pure cost dashboard, Cloudheo is built around a full loop:

```
Detect → Explain → Simulate → Approve → Fix → Verify
```

1. **Detect** — scan a customer's AWS account (read-only) for cost and usage data.
2. **Explain** — a deterministic, rule-based FinOps engine turns raw data into
   concrete optimization opportunities, with cost/savings figures that are always
   traceable back to the source data (no invented numbers).
3. **Simulate** — let the user pick optimizations and preview the combined impact
   on their monthly bill.
4. **Approve / Fix / Verify** — (future) apply approved, low-risk changes to AWS
   with human validation, then verify the expected savings actually materialized.

## Target customer

French-speaking SMEs/mid-market (France / Belgium / Switzerland), ~20–500
employees, mostly on AWS, €5k–50k/month cloud spend, no dedicated FinOps team.

## Status

Early MVP, **read-only only** — Cloudheo never modifies or deletes anything in a
connected AWS account. Current focus: Sprint 2 (AWS data ingestion).

| Sprint | Scope | Status |
|---|---|---|
| 1 — Foundation | Repo, Next.js, FastAPI, Postgres, local dev setup | ✅ Done |
| 2 — AWS | AssumeRole, Cost Explorer, EC2/EBS/RDS/CloudWatch | 🟡 In progress (AssumeRole + Cost Explorer live-tested; EC2/EBS/RDS/CloudWatch pending) |
| 3 — FinOps Engine | Resource/cost models, savings rules, recommendations | ⬜ Not started |
| 4 — Dashboard | Wire the UI to real data, savings simulator | ⬜ Not started (UI exists with placeholder data) |
| 5 — AI | Natural-language explanations, "Ask Cloudheo" | ⬜ Not started |
| 6 — Beta | Auth, audit logs, security hardening, first prospects | ⬜ Not started |

## Architecture

```
Next.js (frontend)
      │  REST
      ▼
FastAPI (backend)
      ├── AWS service      (STS AssumeRole, Cost Explorer, EC2/EBS/RDS, CloudWatch)
      ├── FinOps engine    (deterministic rules → recommendations)
      ├── AI service       (explanations only — never computes numbers)
      └── Recommendation service
               │
               ▼
          PostgreSQL
```

AWS access model — Cloudheo never stores a customer's permanent credentials:

```
Customer AWS account
      │  customer creates a read-only IAM role (CloudheoReadOnlyRole)
      │  that trusts Cloudheo's AWS account
      ▼
AWS STS AssumeRole
      │
      ▼
Short-lived, read-only credentials ──▶ Cost Explorer / EC2 / EBS / RDS / CloudWatch
```

## Repository structure

```
cloudheo/
├── frontend/         Next.js app (TypeScript, Tailwind) — see frontend/README.md
├── backend/          FastAPI app (Python) — see backend/README.md
├── infrastructure/   Docker / deployment config (not started yet)
├── .env.example      Reference env vars for local dev
└── .gitignore
```

Only what's actually implemented exists in the tree — no empty placeholder
files for unbuilt features.

## Quick start

Prerequisites: Node.js 20+, Python 3.11+, PostgreSQL running locally.

```bash
# 1. Database
createuser cloudheo --pwprompt   # password: cloudheo (or update backend/.env)
createdb cloudheo --owner=cloudheo

# 2. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # then fill in AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
alembic upgrade head
uvicorn app.main:app --reload

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000 — Backend: http://localhost:8000

See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md)
for details on each side.

## Security principles

- **Read-only, always (for now).** No `Delete*`, `Terminate*`, `Modify*`, or
  `Update*` permission is ever requested from a customer account in the MVP.
- **No stored customer credentials.** Access is via `sts:AssumeRole` with
  short-lived (1h) temporary credentials, never long-lived keys.
- **Deterministic financial calculations.** Savings estimates come from a
  rule-based FinOps engine, not an LLM. AI is only used to explain and
  contextualize numbers that were already computed.
- **Secrets stay in `.env` files**, which are git-ignored. Never commit real
  AWS keys, database passwords, or API tokens.
