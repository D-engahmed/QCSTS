# Current architecture audit

## Scope and baseline

Audit completed 2026-09-13 against `main` at `cb22743`. The checkout is three commits behind `origin/main` and contains unrelated, uncommitted frontend/readme edits. Those edits were not inspected for secrets, changed, committed, or included in this audit.

QCSTS is a two-application repository: a Django 4.2/DRF backend in `QCSTS/` and a React 19/Vite frontend in `QCSTS_frontend/`. Docker Compose provisions PostgreSQL 15, Redis 7, Gunicorn/Django, Celery worker/beat, Nginx and the Vite development server.

## Backend structure

`config.settings.base` establishes JWT bearer authentication, global `IsAuthenticated`, CORS, PostgreSQL via `DATABASE_URL`, Redis cache/Celery, DRF Spectacular, and a file/console logger. `config.urls` exposes versioned resource routes under `/api/v1/`, plus schema and Swagger UI. Celery Beat invokes the daily overdue-test-point task.

Apps and principal models:

| App | Models / responsibility |
| --- | --- |
| accounts | `CustomUser`; email authentication and a single role string |
| products | `Monograph`, `MonographTest`, `Product` |
| batches | `Batch` |
| schedule | `TestPoint` generated from ICH timepoint constants |
| chamber | `SamplePull`, `LocationHistory` |
| results | immutable-after-create `TestResult` |
| audit | immutable-at-ORM `AuditLog` |
| reports | dashboard aggregation only; no report model or PDF service |

`BaseModel` supplies UUID primary keys, creator/timestamps, `is_active`, and an active-only manager to most regulated models. Services hold schedule generation, result evaluation, cache-token signatures, and audit logging. DRF uses hand-written `APIView` classes and serializers; there are no viewsets, pagination, filtering backend, service boundary enforcement, or tenant context.

## Current data relationships

`Product -> Monograph -> MonographTest`; `Batch -> Product`; `TestPoint -> Batch`; `SamplePull -> Batch/TestPoint`; `TestResult -> TestPoint/MonographTest`; `LocationHistory -> Batch`; and `AuditLog` carries a polymorphic model/object reference as strings. `CustomUser` is referenced as creator, analyst, approver, or performer.

All data is global. There is no `Organization`, `Site`, membership, organization foreign key, request tenant context, object-level authorization, tenant-aware unique constraint, or tenant-aware background job query. Consequently every list/detail endpoint can disclose records across future customers until Phase 1 is implemented.

## Current stability workflow

1. A user creates a draft monograph and tests, then a QA manager approves it.
2. An analyst creates a product linked to the monograph.
3. An analyst creates a batch. Serializer validation checks dates, approved monograph, a globally unique batch number, and global shelf/rack/position availability.
4. `ScheduleEngine` atomically creates long-term (0, 3, 6, 9, 12, 18, 24, 36) or accelerated (0, 3, 6) `TestPoint`s.
5. Chamber sample pulls reduce quantity and can mark a test point pulled; batch locations can be changed with history.
6. The analyst re-enters a password, receives a five-minute one-time cache token, and submits one result per test point/monograph test.
7. `OutcomeEvaluator` parses selected text specifications and determines pass/fail. A signal recalculates test-point and batch status.
8. Dashboard and frontend-generated CSV/print-style reports expose operational summaries.

## Frontend structure

The React SPA uses React Router with page-level components, a shared sidebar, a custom fetch wrapper, browser `localStorage` for JWTs and user data, and a large global CSS file. It covers login, dashboard, products/monographs, batches, test points, chamber pulls/location history, result entry, reports, users, and audit logs. Routes hide restricted pages based on the cached role; backend role checks are still the actual control. There is no frontend test framework, component library, typed API contract, design-token system beyond CSS variables, organization switcher, error boundary, accessible visual-system specification, or end-to-end suite.

## Deployment and operations

Compose runs database migrations and static collection during web startup. Nginx proxies all root traffic to Django; it does not serve the Vite SPA in a production build. Static files and run logs are repository-tracked. There is no object storage, managed deployment/IaC, CI/CD, health endpoint, metrics, tracing, error tracker, backup/restore procedure, release process, or documented RPO/RTO.

## Existing strengths to retain

- UUIDs, soft delete baseline, timestamp/creator fields and PostgreSQL target.
- Versioned API prefix, standardized response envelope, OpenAPI generator and JWT refresh blacklisting.
- Schedule engine transaction boundary and daily overdue job.
- Result specification snapshot and prevention of normal ORM/API edits after submission.
- Audit model immutability at the Django ORM/API layer.
- Existing workflows and test factories as migration regression fixtures.

## Observed defects and technical debt

- `seed_roles.py` imports `Role`, but no `Role` model exists in the current source or migrations. The compiled cache references an absent migration, so the advertised dynamic-role feature is broken/incomplete.
- README claims configurable permissions, counter-signing, QA approval, PostgreSQL audit trigger, PDF/export and compliance status that the current source does not substantiate. Remove or qualify those claims before commercial use.
- `AuditService` intentionally swallows audit write failures. Critical regulated actions can therefore succeed without an audit event.
- Audit immutability is only enforced in model methods. The repository contains no PostgreSQL trigger migration; direct database changes remain possible.
- Login/logout, result submission, batch creation, sample pulls, and user administration are not consistently audit-logged. Audit action choices also omit several claimed events.
- Role strings and permission allow-lists are hard-coded across backend and frontend. They do not support owner/read-only, organization-specific permissions, least privilege, or separation of duties.
- `OutcomeEvaluator` silently parses free text, treats parse errors as failure, and gives exact numbers an unapproved implicit 2% tolerance. It has no units, precision, rounding, versioned rule or deterministic calculation record.
- A result signature is a short-lived, generic cache token; no persistent signature record, meaning, signed-record hash/version, session binding, review workflow, or signature audit exists.
- No `StabilityStudy`, protocol/version, controlled specification version, sample entity, chamber entity, quality-event, notification, billing, webhook, storage, or report-generation domain exists.
- `Batch.batch_number` and chamber position are globally unique; migration must scope these correctly by organization/site.
- The frontend stores bearer/refresh tokens in `localStorage`, making XSS token theft a material risk. Client-side role gating is presentation only and should be removed as a security assumption.
- Production settings omit secure cookie configuration details, CSP/referrer/content-type policies, CSRF trusted origins, proxy SSL header, rate-limit application, secret rotation, session/device management, file handling, and error monitoring.
- Compose has development credentials in the example and exposes database/Redis ports; it is not a production deployment design. The deployed nginx does not serve a built SPA.
- `staticfiles/`, server log output, development/production environment files, and caches are tracked. `.gitignore` does not prevent all frontend environment file variants. The untracked `QCSTS_frontend/src/.env` must never be staged without an explicit secret review.
- No pagination, request IDs, data-retention policy, attachment validation, structured logs, accessibility testing, frontend tests, tenant tests, workflow approval tests, or payment/security integration tests exist.

## Test baseline

There are 15 non-empty backend test modules (about 1,155 lines) across accounts, audit, batches, chamber, products, schedule, results and reports. They cover basic model behavior, API permissions, schedule generation, results and dashboard aggregation. `reports/tests/test_models.py` is empty. No tests cover multi-tenancy, object authorization, protocol/specification versioning, QA approval, correction, persisted signature evidence, billing, frontend behavior, E2E, database triggers, Celery isolation or deployment.

The local shell has no usable Python/pytest executable, so `pytest -q`, Django migration-drift, and deployment checks could not run. This is an environment limitation, not a passing test result. Re-run in the project virtual environment or Compose `web` service before Phase 1.
