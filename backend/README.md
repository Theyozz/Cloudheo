# Cloudheo — Backend

FastAPI backend: AWS data ingestion (via STS AssumeRole), the FinOps rules
engine (not built yet), and the REST API consumed by the Next.js frontend.

## Stack

- **FastAPI** + **Pydantic v2** — API layer and validation
- **SQLAlchemy** + **Alembic** — ORM and migrations
- **PostgreSQL** — database
- **boto3** — AWS SDK (STS, Cost Explorer, EC2, RDS, CloudWatch, ELB)
- **pytest** + **moto** — tests, with AWS calls mocked (no real AWS account needed to run the suite)

## Structure

```
app/
├── main.py            FastAPI app, CORS, router registration
├── api/                Route handlers (one file per resource)
│   ├── health.py        GET /health
│   └── aws.py            POST /aws/test-connection, POST /aws/costs
├── core/
│   ├── config.py         Settings (env vars via pydantic-settings)
│   └── db.py              SQLAlchemy engine/session, declarative Base
├── models/              SQLAlchemy models (empty — Sprint 3)
├── schemas/              Pydantic request/response schemas
└── services/
    ├── aws/               AWS integrations
    │   ├── sts.py           AssumeRole, temporary credentials, caller identity
    │   └── cost_explorer.py  Cost and usage by service
    ├── finops/            FinOps rules engine (not started)
    └── ai/                 AI explanation service (not started)
alembic/                 Migrations
tests/                   pytest suite, mirrors app/ structure
scripts/                 One-off dev utilities (e.g. check_aws_identity.py)
```

Empty directories (`models/`, `services/finops/`, `services/ai/`) are
placeholders for work that hasn't started yet — they're kept because the repo
structure is intentional, but no dead files live inside them.

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
account are required to run the suite.

## API

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness check |
| `POST /aws/test-connection` | Assumes a customer's `CloudheoReadOnlyRole` and confirms the trust relationship works, with no data access |
| `POST /aws/costs` | Assumes the role and returns total spend + spend by AWS service over a date range (defaults to the last 30 days) |

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
