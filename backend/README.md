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
- **pytest** + **moto** — tests, with AWS calls mocked (no real AWS account needed to run the suite)

## Structure

```
app/
├── main.py             FastAPI app, CORS, router registration
├── api/                 Route handlers (one file per resource)
│   ├── health.py          GET /health (public)
│   ├── auth.py             POST /auth/register, /login, GET /me, /status
│   ├── aws.py              POST /aws/test-connection, POST /aws/costs
│   ├── connect.py          POST/GET/DELETE /aws/connect (stored AWS account)
│   ├── resources.py        POST /aws/resources (EC2/EBS/RDS/snapshots)
│   ├── finops.py           POST /finops/recommendations
│   └── dashboard.py        GET /dashboard/summary (cost + recommendations, one call)
├── core/
│   ├── config.py           Settings (env vars via pydantic-settings)
│   ├── db.py                SQLAlchemy engine/session, declarative Base
│   ├── security.py          Password hashing, JWT encode/decode
│   └── deps.py               get_current_user FastAPI dependency
├── models/                SQLAlchemy models: User, AwsAccount
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
    └── ai/                   AI explanation service (not started — Sprint 5)
alembic/                  Migrations
tests/                    pytest suite, mirrors app/ structure
scripts/                  One-off dev utilities (e.g. check_aws_identity.py)
```

`services/ai/` is currently empty — a placeholder for work that hasn't
started yet, kept because the structure is intentional, but with no dead
files inside it.

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
| `JWT_SECRET_KEY` | Signs login sessions — generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. The in-code default is an obvious placeholder, fine for local dev only |

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

## Authentication

Single-admin MVP, not multi-tenant yet: `POST /auth/register` only succeeds
once — the first account created becomes the only account, and the endpoint
is closed afterwards (`403`). Everything except `GET /health` and the
`/auth/*` endpoints requires a `Authorization: Bearer <token>` header
(JWT, 24h expiry by default). The frontend's login screen shows "create
admin account" or "sign in" based on `GET /auth/status`.

## API

| Endpoint | Auth | Description |
|---|---|---|
| `GET /health` | — | Liveness check |
| `GET /auth/status` | — | Whether an admin account already exists |
| `POST /auth/register` | — | Create the (single) admin account; closed after first use |
| `POST /auth/login` | — | Returns a JWT access token |
| `GET /auth/me` | ✓ | Current user |
| `POST /aws/test-connection` | ✓ | Assumes a customer's `CloudheoReadOnlyRole` and confirms the trust relationship, with no data access |
| `POST /aws/costs` | ✓ | Total spend + spend by AWS service over a date range (defaults to the last 30 days) |
| `POST /aws/resources` | ✓ | EC2/EBS/RDS/snapshot inventory, enriched with CloudWatch CPU |
| `POST /finops/recommendations` | ✓ | Runs the rules engine over a fresh scan |
| `POST` / `GET` / `DELETE /aws/connect` | ✓ | Store, read or remove the currently connected AWS account |
| `GET /dashboard/summary` | ✓ | Cost + recommendations for the connected account, in one call |

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
