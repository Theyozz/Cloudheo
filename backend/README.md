# Cloudheo — Backend

FastAPI backend: AWS data ingestion (via STS AssumeRole), a deterministic
FinOps rules engine, authentication, and the REST API consumed by the
Next.js frontend.

## Stack

- **FastAPI** + **Pydantic v2** — API layer and validation
- **SQLAlchemy** + **Alembic** — ORM and migrations
- **PostgreSQL** — database
- **boto3** — AWS SDK (STS, Cost Explorer, EC2, RDS, EBS, CloudWatch)
- **bcrypt** + **PyJWT** — password hashing and session tokens
- **slowapi** — rate limiting on `/auth/login` and `/auth/register`
- **pytest** + **moto** — tests, with AWS calls mocked (no real AWS account needed to run the suite)

## Structure

```
app/
├── main.py             FastAPI app, CORS, router registration
├── api/                 Route handlers (one file per resource)
│   ├── health.py          GET /health (public)
│   ├── auth.py             POST /auth/register, /login, GET /me
│   ├── audit.py             GET /audit-logs
│   ├── connect.py          POST/GET/DELETE /aws/connect (stored AWS account)
│   └── dashboard.py        GET /dashboard/summary (cost + recommendations, one call)
├── core/
│   ├── config.py           Settings (env vars via pydantic-settings)
│   ├── db.py                SQLAlchemy engine/session, declarative Base
│   ├── security.py          Password hashing, JWT encode/decode
│   └── deps.py               get_current_user FastAPI dependency
├── models/                SQLAlchemy models: Organization, User, AwsAccount, AuditLog
├── schemas/                Pydantic request/response schemas
└── services/
    ├── aws/                 AWS integrations
    │   ├── sts.py              AssumeRole, temporary credentials, caller identity
    │   ├── cost_explorer.py    Cost and usage by service
    │   ├── ec2.py / ebs.py / rds.py / snapshots.py   Resource inventories
    │   ├── cloudwatch.py       CPU utilization
    │   └── inventory.py        Combines the above into one scan
    ├── finops/               Deterministic rules engine
    │   ├── pricing.py           Static, documented-approximate pricing
    │   ├── environment.py       Non-production detection (tags/name)
    │   └── rules.py              The rules themselves
    ├── ai/                   AI explanation service
    │   ├── base.py              ExplanationProvider interface
    │   ├── claude_provider.py   Real implementation (Claude Haiku 5.5)
    │   └── stub_provider.py     No-network fake, used in tests
    └── audit.py              log_action() — records an AuditLog row, atomic with the action it describes
alembic/                  Migrations
tests/                    pytest suite, mirrors app/ structure
scripts/                  One-off dev utilities (e.g. check_aws_identity.py)
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `../.env.example` to `.env` in this directory and fill in:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Credentials for Cloudheo's own `cloudheo-backend` IAM user — used **only** to call `sts:AssumeRole` into customer accounts, never to access customer resources directly |
| `AWS_REGION` | Default region for the AssumeRole session |
| `CORS_ORIGINS` | Allowed frontend origin(s) |
| `JWT_SECRET_KEY` | Signs login sessions — generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. The in-code default is an obvious placeholder; the app **refuses to start** with it when `ENVIRONMENT` isn't `development` |
| `ANTHROPIC_API_KEY` | From `console.anthropic.com` (a developer account, separate from a claude.ai subscription) — powers `POST /ai/explain`. Billed pay-as-you-go by token, not a flat fee; Haiku calls for this feature cost a small fraction of a cent each |

### Database

```bash
createuser cloudheo --pwprompt
createdb cloudheo --owner=cloudheo
alembic upgrade head
```

### Run

```bash
uvicorn app.main:app --reload
```

### Test

```bash
pytest
```

All AWS calls in tests are mocked with `moto` — no real AWS credentials or
account are required to run the suite. The `client` fixture (see
`tests/conftest.py`) is pre-authenticated; use `unauthenticated_client` for
tests of the auth flow itself.

## Authentication & multi-tenancy

Multi-tenant: each `POST /auth/register` call creates a new `Organization`
plus its first user — registration is always open, since onboarding a new
customer means creating a new organization. MVP simplification: one user per
organization for now (no invitations/roles yet). Every connected AWS account
(`aws_accounts` row) belongs to exactly one organization and is scoped by it
on every read/write — one organization can never see another's connected
account or data. Everything except `GET /health` and `/auth/*` requires an
`Authorization: Bearer <token>` header (JWT, 24h expiry by default); the
frontend's login screen lets the user toggle between "sign in" and "create
an organization" rather than guessing which to show.

Known gap: there is no password-reset flow yet — a user who forgets their
password is locked out. Not blocking for an internal/first-customer pilot,
but needed before a self-serve audience.

All endpoints below that touch AWS or spend money per call are rate-limited
per IP via `slowapi` (`app/core/rate_limit.py`), in-memory (resets on
restart, not shared across multiple backend processes — revisit with a
shared store like Redis if Cloudheo ever runs more than one API process):

| Endpoint | Limit | Why |
|---|---|---|
| `POST /auth/login` | 10/minute | Password brute-forcing |
| `POST /auth/register` | 5/hour | Spam account creation (registration is always open) |
| `POST /aws/connect` | 20/hour | Each call performs a real AssumeRole against a customer AWS account |
| `GET /dashboard/summary` | 30/minute | Each call makes several live AWS API calls (Cost Explorer, EC2/RDS/EBS) |
| `POST /ai/explain` | 30/hour | Each call is a billed Claude API request |

## API

| Endpoint | Auth | Description |
|---|---|---|
| `GET /health` | — | Liveness check |
| `POST /auth/register` | — | Create a new organization and its first user |
| `POST /auth/login` | — | Returns a JWT access token |
| `GET /auth/me` | ✓ | Current user (includes `organization_id`) |
| `POST` / `GET` / `DELETE /aws/connect` | ✓ | Store, read or remove the current organization's connected AWS account |
| `GET /dashboard/summary` | ✓ | Cost + recommendations for the organization's connected account, in one call |
| `POST /ai/explain` | ✓ | Turns one recommendation's numbers into a plain-language explanation (Claude Haiku) |
| `GET /audit-logs` | ✓ | Most recent audit log entries for the organization (newest first, capped at 200) |

Every response also carries baseline security headers (`X-Content-Type-Options:
nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`),
set in `app/main.py`.

### Removed: ad-hoc AWS scan endpoints

`POST /aws/test-connection`, `POST /aws/costs`, `POST /aws/resources`, and
`POST /finops/recommendations` existed from an earlier sprint, before AWS
accounts were stored per organization. They accepted a `role_arn` directly
from the request body with no check that it belonged to the caller's own
organization — since Cloudheo's `cloudheo-backend` IAM user can assume
*any* role named `CloudheoReadOnlyRole` in *any* AWS account, any
authenticated user (from any organization) could have read another
organization's AWS cost and resource data by passing that organization's
role ARN. Unused by the frontend (the real flow is `/aws/connect` +
`/dashboard/summary`, both scoped by `organization_id`), so removed rather
than patched — the underlying service functions (`app/services/aws/*`,
`app/services/finops/rules.py`) are unaffected, since `dashboard.py` already
called them directly.

## Audit logs

Every sensitive action is recorded to `audit_logs`, scoped by organization,
in the same database transaction as the action itself (`app/services/audit.py`):
registering, logging in, connecting an AWS account, and disconnecting one.
Routine reads (dashboard views, recommendation scans) are not logged — the
goal is "who did this, and when" for actions that matter, not a full request
log. No UI yet; `GET /audit-logs` is the only way to read them today.

## FinOps rules engine

Deterministic, not AI — every number is traceable back to AWS data
(`app/services/finops/rules.py`):

| Category | Resource | Risk |
|---|---|---|
| `RIGHTSIZING` | EC2, RDS | LOW |
| `UNATTACHED_VOLUME` | EBS | LOW |
| `STOPPED_INSTANCE_STORAGE` | EC2 | HIGH (suggested action is destructive) |
| `ORPHANED_SNAPSHOT` | EBS | LOW |
| `NON_PROD_SCHEDULING` | EC2, RDS | MEDIUM (changes behavior, needs validation) |

Pricing is a static, documented approximation (`app/services/finops/pricing.py`)
— swap for the AWS Pricing API once cent-level accuracy matters.

## AI explanation service

Narrates a recommendation's already-computed numbers in plain language — it
never calculates or invents a figure itself (`app/services/ai/`). Provider
is swappable behind `ExplanationProvider`; the only implementation today is
Claude Haiku 5.5, chosen because this is short, factual text generation, not
a task that needs a larger model. Bundled into the Cloudheo subscription
(not bring-your-own-key) — the target customer (SMEs with no dedicated
FinOps/technical team) shouldn't need their own LLM API account, and the
per-call cost is negligible (a small fraction of a cent on Haiku pricing).

Tests use `StubExplanationProvider` (no network call) via a FastAPI
dependency override — same pattern as mocking AWS with `moto`, for the same
reasons: speed, determinism, and no required API key to run `pytest`.

## AWS access model

Cloudheo's own AWS account has one IAM user, `cloudheo-backend`, whose only
permission is `sts:AssumeRole`, restricted to roles named `CloudheoReadOnlyRole`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/CloudheoReadOnlyRole"
    }
  ]
}
```

Every customer creates a role with that exact name in their own account, trusting
Cloudheo's account ID, with a strictly read-only permission set (Cost Explorer,
`Describe*` on EC2/RDS/ELB, CloudWatch `Get*`/`List*` — no `Delete`, `Terminate`,
`Modify`, or `Update` action is ever requested).

## Security audit (2026-10-09)

Fixed:
- Removed the cross-tenant AWS data leak described above (ad-hoc scan endpoints).
- `JWT_SECRET_KEY` can no longer be left at its insecure default outside of `ENVIRONMENT=development`.
- Rate limiting extended from login/register to every endpoint that costs money or touches a customer's AWS account per call (table above).
- Added `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` headers to every response.
- Bumped `pyjwt` and `python-dotenv` to patch known CVEs (`pip-audit` was clean for both afterwards).

Deferred (flagged, not fixed — each needs dedicated attention, not a drive-by change):
- **`fastapi`/`starlette` have known CVEs patched only in versions far ahead of what's pinned** (`fastapi` 0.115.6 hard-pins `starlette<0.42`; the fixes are in `starlette>=0.47`). Fixing requires a `fastapi` major-version upgrade with its own regression testing — tracked, not done in this pass.
- **No password-reset flow** (see Authentication section above) — a credential-recovery gap, not an exploit path, but blocking for a self-serve audience.
- **No audit-log UI** — already a known, deliberate scope cut (see Audit logs section).
- Email enumeration on `POST /auth/register` (409 reveals an email is already registered) — a conscious, common tradeoff for UX, not treated as a finding worth obscuring.
