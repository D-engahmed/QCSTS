# QC Stability Tracking System (QCSTS)

**Multi-tenant pharmaceutical quality and stability management platform**

[![Django](https://img.shields.io/badge/Django-4.2-092E20.svg)](https://www.djangoproject.com/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/) [![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/) [![Redis](https://img.shields.io/badge/Redis-7+-DC382D.svg)](https://redis.io/)

> QCSTS is a SaaS-oriented quality and stability platform for pharmaceutical organizations. It is engineered around controlled workflows, organization/site isolation, role-based authorization, auditability, electronic-signature workflows, reporting, quality investigations, and subscription billing.

> **Regulatory positioning:** QCSTS is designed for GxP-regulated environments and is being developed toward a validation-ready architecture. The project does **not** claim GMP, 21 CFR Part 11, or other regulatory certification merely because a feature exists. Customer validation, procedures, configuration, qualification, and regulatory assessment remain separate activities.

## 1. What QCSTS is

QCSTS manages the lifecycle of pharmaceutical quality and stability data from controlled study setup through execution, review, reporting, and audit.

~~~text
Organization
    ↓
Site
    ↓
Product / Monograph / Batch
    ↓
Stability Study
    ↓
Protocol → Protocol Version
    ↓
Specification
    ↓
Timepoint → Sample Pull → Test Result
    ↓
Review → Approval → Electronic Signature → Lock
    ↓
Report / Export
~~~

Quality investigations extend the lifecycle:

~~~text
Result / Event → OOS / OOT / Deviation → Investigation → CAPA → Closure
~~~

Commercial lifecycle:

~~~text
Plan → Entitlements → Usage → Subscription → Invoice → Payment → Verified Webhook → Subscription State
~~~

## 2. Security architecture

QCSTS treats the backend as the authorization authority.

~~~text
Authenticated User
        ↓
Active Membership
        ↓
Organization
        ↓
Site Scope
        ↓
Explicit Permission
        ↓
Object Authorization
        ↓
State Transition
~~~

Security rules:

- Authentication is not authorization.
- Organization ownership is derived server-side where applicable.
- Client-supplied organization identifiers are not trusted as an authorization boundary.
- Tenant-scoped querysets are required for tenant resources.
- Critical endpoints must declare explicit authorization policy.
- Legacy user-role fields must not become an independent source of authority.
- Cross-tenant access and privilege escalation are release-blocking defects.

## 3. Core capabilities

### Organization and access control
- Multi-organization architecture
- Site-aware access
- Membership-based organization access
- Organization-scoped roles and permissions
- Explicit endpoint authorization
- Tenant isolation
- Cross-tenant security regression coverage

### Stability management
- Stability studies
- Controlled protocols and protocol versions
- Specification/version binding
- Stability timepoints
- Batch enrollment
- Sample pulls
- Test results and traceability
- Controlled review and approval
- Locking and electronic-signature workflow

### Quality workflows
- OOS investigations
- OOT investigations
- Deviations
- CAPA
- Change Control
- Evidence and controlled records
- Audit trail coverage

### Reporting
- Stability reports
- Controlled exports
- Authorization-aware report generation
- Report provenance and version context

### Commercial platform
- Plans
- Entitlements
- Usage metering
- Subscriptions
- Invoices
- Paymob integration
- Idempotent payment webhook processing

### Operations
- PostgreSQL
- Redis
- Celery workers and Beat
- Django/Gunicorn
- Nginx/reverse proxy
- Docker-based deployment
- Production health/readiness checks
- Logging and observability
- Backup and restore procedures
- CI/CD release gates
- Immutable commit-SHA container images through GHCR

## 4. Repository architecture

~~~text
QCSTS/
├── QCSTS/                  # Django backend / project
│   ├── apps/               # domain applications
│   ├── core/               # shared platform/security primitives
│   ├── services/           # business/application services
│   ├── docker/             # container orchestration
│   └── .env.example
├── QCSTS_frontend/         # active frontend application
├── frontend/               # frontend-related repository assets
├── docs/                   # engineering and release documentation
├── LICENSE.md
└── README.md
~~~

The repository contains both `QCSTS_frontend/` and `frontend/`. **QCSTS_frontend/** is the active application used by the current production-oriented stack. **frontend/** is not part of the current production deployment; treat it as inactive/experimental until it is explicitly promoted and integrated.

## 5. Quick start — Docker

From the repository root:

~~~bash
cp QCSTS/.env.example QCSTS/.env
docker compose -f QCSTS/docker/docker-compose.yml up -d --build
~~~

Typical local endpoints:

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API / Nginx | http://localhost |
| API docs | http://localhost/api/docs/ |
| Django direct | http://localhost:8000 |

Create a local administrator:

~~~bash
docker compose -f QCSTS/docker/docker-compose.yml exec web python manage.py createsuperuser
~~~

Useful commands:

~~~bash
docker compose -f QCSTS/docker/docker-compose.yml logs -f web
docker compose -f QCSTS/docker/docker-compose.yml logs -f frontend
docker compose -f QCSTS/docker/docker-compose.yml exec web python manage.py <command>
docker compose -f QCSTS/docker/docker-compose.yml down
~~~

Never use development secrets in a real deployment.

## 6. Production deployment

Use the dedicated production stack rather than the local-development Compose file:

~~~bash
cp QCSTS/.env.production.example QCSTS/.env
# replace every placeholder, including the real public host and TLS certificate files
mkdir -p QCSTS/docker/certs
# place fullchain.pem and privkey.pem in QCSTS/docker/certs/
docker compose -f QCSTS/docker/docker-compose.production.yml up -d --build
~~~

The production stack is designed to run the production Django settings, keep PostgreSQL and Redis off the public host interface, require non-default credentials, and terminate HTTPS at Nginx.

The release path includes:

1. Migration execution.
2. Static-asset collection.
3. Application health/readiness checks.
4. Gunicorn startup.
5. Celery worker and Beat startup.
6. Next.js production frontend.
7. Nginx reverse proxy.
8. PostgreSQL and authenticated Redis.
9. Production image builds.

Before release, run migrations and the full security/integration test gates against a production-like PostgreSQL environment. A clean container start is not evidence that the migration graph is synchronized.

## 7. Manual backend setup

~~~bash
cd QCSTS
python -m venv venv

# Windows
venv\\Scripts\\activate

# macOS/Linux
# source venv/bin/activate

pip install -r requirements/test.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
~~~

Configure `DATABASE_URL` and `REDIS_URL` for the local PostgreSQL and Redis services.

## 8. Frontend development

~~~bash
cd QCSTS_frontend
npm install
npm run dev
npm run build
~~~

The current stability UI is API-backed rather than relying on hardcoded demonstration study data.

## 9. Testing

~~~bash
python manage.py check
python manage.py makemigrations --check
pytest
~~~

Frontend build:

~~~bash
npm run build
~~~

Security-sensitive changes require negative tests, not only happy-path tests. At minimum, cover cross-organization reads/updates/deletes, organization spoofing, site boundary violations, missing permissions, privilege escalation, inactive memberships, unauthorized file/report access, and duplicate or invalid payment events.

## 10. CI/CD and release gates

The production CI/CD gate has been hardened around **Python 3.12** and **Node 20**.

Current CI controls include:

- Dependency installation and pip caching.
- `pip check`.
- Django deployment checks.
- Migration drift detection.
- Real PostgreSQL migrations in CI.
- Backend tests against PostgreSQL rather than silently relying on SQLite.
- Coverage artifact collection with a **90% coverage floor**.
- Frontend type checking.
- Frontend production build.
- Backend and frontend Docker builds.
- Least-privilege GitHub Actions permissions.
- Concurrency cancellation for superseded runs.
- Successful `main` builds publish immutable commit-SHA images to GHCR.

### Production release gates

These gates are evidence-based. A merged PR or existing model is not, by itself, evidence that a production requirement is complete.

| Gate | Scope | Status |
|---|---|---|
| Tenant isolation | Organization/site scoping and ownership boundaries | Implemented / hardened |
| Endpoint authorization | Explicit backend RBAC and object authorization | Implemented / hardened |
| Security regression | Cross-tenant and privilege-escalation protections | Implemented / hardened |
| Stability core | Study, protocol, version, specification | Implemented |
| Stability execution | Enrollment, timepoints, sample lifecycle | Implemented |
| Controlled results | QA approval, controlled records, result locking | Implemented |
| Quality investigations | OOS, OOT, Deviation, CAPA, Change Control | Implemented |
| Audit integrity | Django + PostgreSQL audit immutability | Implemented |
| Reporting | Reports, exports, authorization-aware access | Implemented |
| Billing | Plans, entitlements, usage, subscriptions, invoices | Remaining validation/enforcement |
| Payments | Paymob + verified idempotent webhooks | Remaining validation |
| Production infrastructure | Docker, Nginx, PostgreSQL, Redis, workers, frontend | Implemented |
| CI/CD | Tests, migrations, builds, release gates, GHCR images | Implemented / hardened |
| Backup / DR | Restore verification and RPO/RTO evidence | Remaining |
| E2E release evidence | Full workflow/security regression evidence | Remaining |
| Validation / UAT | Customer-specific validation and pilot evidence | Remaining |

## 11. Wave 3 — production completion and CI/CD hardening

**Wave 3 was completed on 20 September 2026.**

The wave focused on closing the gap between feature implementation and actual release engineering.

### Backend and data integrity
- Tenant-owned foreign-key validation remains structural.
- Chamber locations are database-unique within a tenant.
- Sample pulls lock the batch row and re-check inventory transactionally.
- Monograph approval cannot be performed through ordinary CRUD input.
- Monograph approval requires signature re-authentication and a reason.
- Stability APIs expose controlled protocols, versions, specifications, studies, enrollments, timepoints, and samples.
- Stability lifecycle transitions are server-controlled and audit/signature backed.
- QA approval creates and locks a `ControlledRecord` for results.
- Uncontrolled correction of locked results is rejected.
- OOS/OOT/Deviation/CAPA/Change Control use controlled lifecycle transitions.
- `AuditLog` immutability is enforced in Django and at PostgreSQL trigger level.

### Frontend integration
- Stability Studies list is API-backed.
- Study creation submits through the tenant-scoped stability API.
- Study detail loads real study, timepoint, sample, and enrolled-batch data.
- Frontend endpoint definitions cover stability master data.
- Study navigation uses stable study UUIDs.
- Duplicate stability endpoint aliases were removed.

### Production engineering
- Production Docker runtime was added for the frontend.
- Production Compose includes PostgreSQL, authenticated Redis, migration/collectstatic release gating, Gunicorn, Celery, Celery Beat, Next.js, and Nginx.
- Development Compose frontend mounting was corrected.
- Production reverse proxy configuration was added.
- CI uses PostgreSQL for backend integration testing.
- CI validates migration synchronization instead of assuming migrations are correct.
- Production images are published immutably by commit SHA.
- GitHub Actions token permissions were minimized.

## 12. Production readiness model

~~~text
Code implemented
      ↓
Unit/API tests
      ↓
Security tests
      ↓
Integration tests
      ↓
End-to-end workflow
      ↓
Operational tests
      ↓
Backup restore verification
      ↓
Deployment verification
      ↓
Requirements / validation evidence
      ↓
Controlled pilot
      ↓
Production release
~~~

**Current state:** QCSTS is in **advanced pre-production / pilot preparation**, not a certified production regulated system.

The remaining release-critical evidence includes billing enforcement, payment verification, backup/restore and disaster-recovery evidence, broader end-to-end/security regression coverage, external deployment/TLS infrastructure, and customer-specific validation/UAT.

## 13. Critical data integrity workflow

~~~text
Draft → Review → Approve → Sign → Lock
~~~

After controlled locking/signature, ordinary mutation must not silently change the historical record. Changes should use the appropriate controlled amendment/version mechanism and generate the required audit evidence.

Electronic signatures must identify the signer and signing event. Authentication credentials alone are not a complete electronic-signature and audit workflow.

## 14. Auditability

Critical events should provide enough evidence to answer:

~~~text
WHO
WHAT
WHEN
WHERE
WHICH OBJECT
WHAT CHANGED
WHY / REASON WHEN REQUIRED
~~~

Audit records are security-sensitive data and must not be editable or deletable by ordinary application users.

## 15. Regulatory positioning

QCSTS is designed with regulated pharmaceutical environments in mind, including controlled records, auditability, access control, electronic signatures, data integrity, and validation evidence.

However:

- QCSTS is not automatically GMP compliant because it implements GMP-related workflows.
- QCSTS is not automatically 21 CFR Part 11 compliant because it has electronic signatures.
- Regulatory compliance depends on the complete computerized-system lifecycle, configuration, procedures, validation/qualification evidence, supplier controls, security, operations, and intended use.
- Customer-specific validation remains required.
- Product documentation must not claim regulatory certification unless such certification has actually been obtained.

Preferred positioning:

> **Designed for GxP-regulated environments with a validation-ready architecture.**

## 16. Contributor security rules

Before opening a production PR:

1. Derive authorization from trusted membership/permission context.
2. Scope querysets to the tenant.
3. Enforce object-level authorization.
4. Prevent ownership spoofing.
5. Declare explicit permissions for sensitive operations.
6. Validate state transitions server-side.
7. Generate audit evidence for critical changes.
8. Add negative security tests.
9. Never commit secrets.
10. Fix security failures in implementation rather than weakening tests.

## 17. Documentation

- Backend architecture and API documentation: `QCSTS/README.md`
- API documentation: `QCSTS/API_DOCUMENTATION.md`
- Engineering documentation: `docs/`
- Production release gates: `docs/release-gates/`

## 18. Project status

QCSTS has moved beyond basic feature development into **production hardening and controlled release engineering**.

The current objective is to prove—not merely assume—that:

- tenant boundaries hold;
- permissions are enforced server-side;
- critical quality records are controlled;
- stability workflows are traceable;
- audit evidence is immutable;
- billing/payment state is authoritative;
- infrastructure is recoverable;
- CI/CD prevents unsafe releases; and
- regulatory positioning matches the evidence actually available.

Wave 3 materially advances the production foundation, but the remaining evidence listed above is still required before describing QCSTS as a production-ready regulated system.

## License

This project is provided under the terms defined in LICENSE.md.
