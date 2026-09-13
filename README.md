# <center> QC Stability Tracking System v0.1.3 </center>
<center>

=======
<center> 
    
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Django](https://img.shields.io/badge/Django-4.2-092E20.svg)](https://www.djangoproject.com/)
[![GMP](https://img.shields.io/badge/GMP-Compliant-brightgreen.svg)](https://www.fda.gov/drugs/pharmaceutical-quality-resources/good-manufacturing-practice-gmp-resources)
[![21 CFR Part 11](https://img.shields.io/badge/21%20CFR%20Part%2011-Compliant-blue.svg)](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application)

</center>

> **Enterprise pharmaceutical quality control platform** for GMP stability studies, chamber inventory management, sample pull workflows with quantity confirmation, and 21 CFR Part 11 compliant test result entry with auto pass/fail calculation.

---

## Overview

QC Stability Tracking System (QCSTS) supports pharmaceutical stability studies with a structured, auditable workflow for batch lifecycle management, chamber placement, sample pull tracking, test entry, and result review.

```
Product → Monograph → Batch → Auto-Generated Test Schedule → Results → Reports
```

When a batch is registered, the system automatically generates the full ICH Q1A(R2) testing schedule. Analysts submit results with an electronic signature. QA managers review and approve. Everything is tracked, timestamped, and immutable.

## Key Features

- Batch creation and study scheduling based on incubation dates
- Chamber inventory management with unique shelf/rack/position validation
- Sample pull workflow with quantity confirmation and status tracking
- Test result entry with auto pass/fail evaluation against specification limits
- Electronic signature on every result submission, full audit trail
- **Batch Stability Report** — pick a product, see all its batches, pick a batch, see the full per-test-point results matrix (which timepoints are tested / pulled / pending, and each assay's value + pass/fail), with CSV and print export
- Role-based access: admin, qa_manager, supervisor, analyst

## Supported Stability Study Types

| Study Type | Time Points | Typical Conditions |
|------------|-------------|--------------------|
| Long-term | 0M, 3M, 6M, 9M, 12M, 18M, 24M, 36M | 25°C / 60% RH |
| Accelerated | 0M, 3M, 6M | 40°C / 75% RH |

## Architecture

```
QCSTS/                    ← repo root (this is where you `git clone` to)
├── QCSTS/                ← Django backend (REST API, models, auth, business logic)
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml   ← runs the ENTIRE stack, backend + frontend
│   ├── apps/              # accounts, products, batches, schedule, results, chamber, audit, reports
│   ├── services/          # schedule_engine, signature_service, audit_service, outcome_evaluator
│   ├── core/               # base model, custom exceptions, permissions, response envelope
│   └── .env.example
└── QCSTS_frontend/        ← React 19 + Vite frontend
```

⚠️ **Note the nested folder name** — the repo root and the Django project are both called `QCSTS`, so a clone looks like `.../QCSTS/QCSTS/...`. Every command below assumes you're standing in the **repo root** (the outer `QCSTS/`, containing both `QCSTS/` and `QCSTS_frontend/` as siblings) unless stated otherwise. This trips people up more than anything else in this project — if a `docker compose` command says *"no configuration file provided"* or *"cannot find the path specified,"* it's almost always because the current directory doesn't match the `-f` path used. Run `Get-Location` (PowerShell) / `pwd` (bash) if you're ever unsure.

---

## Quick Start (Docker — recommended)

This runs **everything** — Postgres, Redis, Django (gunicorn), Celery, Celery Beat, nginx, and the Vite dev server with hot reload — with one command.

### 1. Configure environment

```bash
cp QCSTS/.env.example QCSTS/.env
```

The defaults in `.env.example` work out of the box for local development (including `CORS_ALLOWED_ORIGINS=http://localhost:5173` for the frontend dev server). Change `DJANGO_SECRET_KEY` before deploying anywhere real.

### 2. Bring the stack up

```bash
docker compose -f QCSTS/docker/docker-compose.yml up -d --build
```

First run takes a few minutes (image builds + `npm install` inside the frontend container). `migrate` and `collectstatic` run automatically as part of the `web` container's startup — you don't need to run them by hand on a fresh setup.

| Service | URL |
|---|---|
| Frontend (hot reload) | http://localhost:5173 |
| API / nginx | http://localhost |
| API docs (Swagger) | http://localhost/api/docs/ |
| Django directly (bypasses nginx) | http://localhost:8000 |

### 3. Create an admin account

```bash
docker compose -f QCSTS/docker/docker-compose.yml exec web python manage.py createsuperuser
```

### Common commands

```bash
# Tail logs for one service
docker compose -f QCSTS/docker/docker-compose.yml logs -f web
docker compose -f QCSTS/docker/docker-compose.yml logs -f frontend

# Run a management command
docker compose -f QCSTS/docker/docker-compose.yml exec web python manage.py <command>

# After pulling backend code changes, rebuild
docker compose -f QCSTS/docker/docker-compose.yml up -d --build

# Frontend code changes hot-reload automatically — no rebuild needed
# (the frontend container bind-mounts QCSTS_frontend/, it isn't baked into an image)

# Stop everything
docker compose -f QCSTS/docker/docker-compose.yml down
```

---

## Manual Setup (without Docker)

<details>
<summary>Backend</summary>

```bash
cd QCSTS
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements/test.txt
cp .env.example .env
# Point DATABASE_URL / REDIS_URL at locally-running Postgres/Redis instead of
# the docker service names (db/redis) in .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
</details>

<details>
<summary>Frontend</summary>

```bash
cd QCSTS_frontend
npm install
npm run dev
```

By default the frontend calls `http://localhost/api/v1` (see `VITE_API_URL` in `src/services/api.js`) — set `VITE_API_URL=http://localhost:8000/api/v1` if you're running the backend with `manage.py runserver` directly instead of through nginx.
</details>

---

## Roles & Permissions

| Role | Description |
|---|---|
| `admin` | Full access. Creates user accounts, manages system configuration. |
| `qa_manager` | Approves monographs, views full audit trail, exports reports. |
| `supervisor` | Counter-signs test results, oversees batches. |
| `analyst` | Submits test results with electronic signature, records sample pulls. |
| `system` | Reserved for automated/service accounts. |

## Testing

```bash
# Backend — from QCSTS/, inside the venv or docker compose exec web
pytest

# Frontend build check — from QCSTS_frontend/
npm run build
```

---

## Documentation

- Full backend architecture, API endpoint reference, and ALCOA+ compliance notes: [`QCSTS/README.md`](QCSTS/README.md)
- API documentation: [`QCSTS/API_DOCUMENTATION.md`](QCSTS/API_DOCUMENTATION.md)

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `no configuration file provided: not found` | `docker compose` run without `-f`, or from the wrong directory | Always pass `-f QCSTS/docker/docker-compose.yml` (from repo root) or `-f docker/docker-compose.yml` (from inside `QCSTS/`) |
| `open .../docker-compose.yml: The system cannot find the path specified` | Same as above, path doesn't resolve from current directory | Run `Get-Location` first, then use the matching relative path |
| `Bind for 0.0.0.0:5432 failed: port is already allocated` | Something else on the host (local Postgres install, another compose project) already has port 5432 | `docker compose -f QCSTS/docker/docker-compose.yml down` fully before re-running `up`, or check `netstat -ano \| findstr :5432` (Windows) to find and stop the conflicting process |
| `git apply` fails with "patch does not apply" on files you haven't touched | Usually Windows line-ending (CRLF) conversion mangling the diff | Prefer copying files directly over `git apply` on Windows, or apply with `git apply --ignore-whitespace` |
| `Your models in app(s): 'X' have changes that are not yet reflected in a migration` | A model field changed without running `makemigrations` | `docker compose -f QCSTS/docker/docker-compose.yml exec web python manage.py makemigrations <app>`, then `migrate` |

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

Commit message format: `type(scope): description` — types: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`.

## Contribution

Contributions should follow existing application structure, maintain code quality, and preserve testing coverage. Use the current repository conventions for apps, serializers, views, and migration management.

## License

This project is provided under the license terms defined in [LICENSE.md](LICENSE.md).
