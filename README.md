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
- Protocols and protocol versions
- Specification/version binding
- Stability timepoints
- Sample pulls
- Test results and traceability
- Controlled review and approval
- Locking and electronic-signature workflow

### Quality workflows
- OOS investigations
- OOT investigations
- Deviations
- CAPA
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

## 4. Repository architecture

~~~text
QCSTS/
├── QCSTS/                  # Django backend / project
│   ├── apps/               # domain applications
│   ├── core/               # shared platform/security primitives
│   ├── services/           # business/application services
│   ├── docker/             # container orchestration
│   └── .env.example
├── QCSTS_frontend/         # React/Vite frontend
├── frontend/               # frontend-related repository assets
├── docs/                   # engineering and release documentation
├── LICENSE.md
└── README.md
~~~

The repository contains both QCSTS_frontend/ and frontend/. **QCSTS_frontend/** is the active Vite/React application wired into the Docker Compose stack. **frontend/** is not part of the current production deployment; treat it as inactive/experimental until it is explicitly promoted and integrated.

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

```bash
cp QCSTS/.env.production.example QCSTS/.env
# replace every placeholder, including the real public host and TLS certificate files
mkdir -p QCSTS/docker/certs
# place fullchain.pem and privkey.pem in QCSTS/docker/certs/
docker compose -f QCSTS/docker/docker-compose.production.yml up -d --build
```

The production stack explicitly loads `config.settings.production`, does not publish PostgreSQL or Redis ports, requires non-default database/Redis credentials, and terminates HTTPS in Nginx. Do not use `.env.example` or the development Compose stack for a real deployment.

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

Configure DATABASE_URL and REDIS_URL for the local PostgreSQL and Redis services.

## 8. Frontend development

~~~bash
cd QCSTS_frontend
npm install
npm run dev
npm run build
~~~

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

## 10. Production release gates

These roadmap gates are sequential. A merged PR is not, by itself, evidence that the system is production-ready.

| Roadmap PR | GitHub PR | Gate |
|---|---:|---|
| PR13 | #13 | Tenant authorization hardening |
| PR14 | #22 | Endpoint-wide RBAC authorization guard |
| PR15 | #24 | Cross-tenant and privilege-escalation security |
| PR16 | #25 | Stability Study / Protocol / Version / Specification |
| PR17 | #26 | Timepoint / SamplePull / Result lifecycle |
| PR18 | #27 | QA review / approval / locking / e-signatures |
| PR19 | #28 | OOS / OOT / Deviations / CAPA |
| PR20 | #29 | Audit integrity / controlled files |
| PR21 | #30 | Reports / exports / authorization |
| PR22 | #31 | Plans / Entitlements / Usage / Subscriptions / Invoices |
| PR23 | #32 | Paymob / verified idempotent webhooks |
| PR24 | #33 | Production infrastructure / observability |
| PR25 | #34 | Backup / restore / disaster recovery / RPO-RTO |
| PR26 | #35 | CI/CD / migration / deployment safety |
| PR27 | #36 | Full E2E / security regression gates |
| PR28 | #37 | Validation-ready pilot / production release package |

## 11. Production readiness model

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

QCSTS should not be described as a certified regulated system unless the required evidence and external/customer-specific activities actually exist.

## 12. Critical data integrity workflow

~~~text
Draft → Review → Approve → Sign → Lock
~~~

After controlled locking/signature, ordinary mutation must not silently change the historical record. Changes should use the appropriate controlled amendment/version mechanism and generate the required audit evidence.

Electronic signatures must identify the signer and signing event. Authentication credentials alone are not a complete electronic-signature and audit workflow.

## 13. Auditability

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

## 14. Regulatory positioning

QCSTS is designed with regulated pharmaceutical environments in mind, including controlled records, auditability, access control, electronic signatures, data integrity, and validation evidence.

However:

- QCSTS is not automatically GMP compliant because it implements GMP-related workflows.
- QCSTS is not automatically 21 CFR Part 11 compliant because it has electronic signatures.
- Regulatory compliance depends on the complete computerized-system lifecycle, configuration, procedures, validation/qualification evidence, supplier controls, security, operations, and intended use.
- Customer-specific validation remains required.
- Product documentation must not claim regulatory certification unless such certification has actually been obtained.

Preferred positioning:

> **Designed for GxP-regulated environments with a validation-ready architecture.**

## 15. Contributor security rules

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

## 16. Documentation

- Backend architecture and API documentation: QCSTS/README.md
- API documentation: QCSTS/API_DOCUMENTATION.md
- Engineering documentation: docs/
- Production release gates: docs/release-gates/

## 17. Project status

QCSTS has moved from feature development toward production hardening and controlled release engineering.

The current objective is to prove that tenant boundaries hold, permissions are enforced server-side, critical quality records are controlled, workflows are traceable, audit evidence is reliable, billing/payment state is authoritative, infrastructure is recoverable, releases are test-gated, and regulatory positioning matches the evidence actually available.

Until those conditions are demonstrated with implementation and test evidence, QCSTS should be treated as **pre-production / pilot-stage software**, not as a certified regulated system.

## License

This project is provided under the terms defined in LICENSE.md.