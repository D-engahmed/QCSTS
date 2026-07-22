# QC_System# CQSTS — QC Stability Tracking System

> On-premises backend for pharmaceutical stability testing. GxP-compliant, ALCOA+ aligned, built with Django REST Framework.

---

## What is CQSTS?

Pharmaceutical companies must prove that every drug batch remains effective and safe over time. This process — called **stability testing** — is required by law (ICH Q1A(R2)).

CQSTS automates the entire workflow:

```
Product → Monograph → Batch → Auto-Generated Test Schedule → Results → Reports
```

When a batch is registered, the system automatically generates the full testing schedule. Analysts submit results with electronic signatures. QA managers review and approve. Everything is tracked, timestamped, and immutable.

---

## Key Features

- **Auto-generated test schedules** — ICH Q1A(R2) timepoints created automatically on batch registration
- **Electronic signature** — analysts re-authenticate at the moment of result submission
- **Role-based access** — admin, qa_manager, supervisor, analyst — permissions configurable per role
- **Full audit trail** — every change tracked with who, what, when, old value, new value
- **ALCOA+ compliance** — Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available
- **On-premises** — no internet dependency, all data stays on the company server
- **No direct DB edits** — all changes go through the API; audit table protected at DB level

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 + Django REST Framework 3.14 |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL 15 |
| Cache / Queue broker | Redis 7 |
| Task queue | Celery + Celery Beat |
| API docs | drf-spectacular (Swagger UI) |
| Testing | pytest + pytest-django + factory-boy + freezegun |
| Deployment | Docker + docker-compose + Nginx + Gunicorn |

---

## Project Structure

```
CQSTS/
├── config/
│   ├── settings/
│   │   ├── base.py          # shared settings
│   │   ├── production.py    # production overrides
│   │   └── test.py          # test overrides (SQLite in-memory)
│   ├── urls.py              # main URL router
│   ├── celery.py            # Celery + Beat schedule
│   └── wsgi.py
│
├── apps/
│   ├── accounts/            # users, roles, JWT auth
│   ├── audit/               # immutable audit trail
│   ├── products/            # products + monographs
│   ├── batches/             # batch registration
│   ├── schedule/            # auto-generated test points
│   ├── results/             # test result submission
│   ├── chamber/             # sample storage + pulls
│   └── reports/             # dashboard + exports
│
├── services/
│   ├── schedule_engine.py   # generates ICH test points
│   ├── signature_service.py # electronic signature logic
│   ├── audit_service.py     # writes audit log entries
│   └── outcome_evaluator.py # pass/fail calculation
│
├── core/
│   ├── models.py            # BaseModel (UUID, timestamps, soft delete)
│   ├── exceptions.py        # custom exceptions + global handler
│   ├── permissions.py       # role-based permission classes
│   └── responses.py         # standard API response envelope
│
├── constants/
│   ├── stability.py         # ICH timepoints, study types, storage conditions
│   └── permissions.py       # permission code constants
│
├── requirements/
│   ├── base.txt
│   ├── production.txt
│   └── test.txt
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── logs/
├── manage.py
├── pytest.ini
└── .env.example
```

---

## Roles & Permissions

| Role | Description |
|---|---|
| `admin` | Full access. Creates user accounts, manages system configuration. |
| `qa_manager` | Approves monographs, views full audit trail, exports reports. |
| `supervisor` | Counter-signs test results, oversees batches. |
| `analyst` | Submits test results with electronic signature, records sample pulls. |

Permissions per role are **configurable by the admin** — not hardcoded. The admin assigns which actions each role can perform from within the system.

---

## API Endpoints

All endpoints return a standard envelope:

```json
{
  "success": true,
  "data": { },
  "errors": null
}
```

### Auth — `/api/v1/auth/`

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| POST | `login/` | Get JWT tokens | Public |
| POST | `logout/` | Blacklist refresh token | Authenticated |
| GET | `me/` | Current user profile | Authenticated |
| GET | `users/` | List all users | Admin |
| POST | `users/` | Create user | Admin |
| GET | `users/<id>/` | User detail | Admin |
| PATCH | `users/<id>/` | Update user | Admin |
| DELETE | `users/<id>/` | Deactivate user | Admin |
| POST | `change-password/` | Change own password | Authenticated |

### Audit — `/api/v1/audit/`

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| GET | `/` | Full audit trail (filterable) | QA Manager + |
| GET | `<id>/` | Single audit entry | QA Manager + |

---

## Stability Study Types

| Study Type | Storage Condition | Test Months |
|---|---|---|
| Long Study | 25°C / 60% RH | 0, 3, 6, 9, 12, 18, 24, 36 |
| Accelerated Study | 40°C / 75% RH | 0, 3, 6 |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker Desktop (recommended) or PostgreSQL + Redis installed locally

### 1. Clone and set up environment

```bash
git clone https://github.com/MedixAI/CQSTS.git
cd CQSTS
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements/test.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

Required `.env` variables:

```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@localhost:5432/cqsts_db
REDIS_URL=redis://127.0.0.1:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
CELERY_BEAT_TIMEZONE=Africa/Cairo
```

### 3. Run migrations and create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the development server

```bash
python manage.py runserver
```

API docs available at: `http://localhost:8000/api/docs/`

### 5. Run tests

```bash
pytest
```

---

## Data Integrity — ALCOA+ Compliance

| Principle | Implementation |
|---|---|
| **Attributable** | Every record has `created_by` FK. Every audit entry has `performed_by`. |
| **Legible** | All data stored as structured fields, never free text blobs. |
| **Contemporaneous** | `created_at` and `updated_at` set server-side via `auto_now_add` / `auto_now`. |
| **Original** | `specification_snapshot` copied at time of result submission. |
| **Accurate** | Electronic signature required for result submission. |
| **Complete** | All test points must have results before batch is marked complete. |
| **Consistent** | UTC timezone enforced system-wide. |
| **Enduring** | Soft delete only — no record is ever hard deleted. |
| **Available** | Full audit trail queryable by QA managers at any time. |

---

## Git Branch Strategy

```
main                  ← stable releases only
└── dev_back_end      ← integration branch
    ├── feat/accounts
    ├── feat/products
    ├── feat/batches
    └── ...
```

Commit message format: `type(scope): description`

Types: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`

---

## License

Proprietary — MedixAI. All rights reserved.