# QCSTS — Quality Control & Stability Testing Management System

QCSTS is a multi-tenant SaaS platform for pharmaceutical organizations and laboratories. It connects controlled master data, stability studies, laboratory results, quality investigations, compliance evidence, billing and tenant administration in one backend-authoritative workflow.

> **Validation posture:** QCSTS is designed for GxP-regulated environments with a validation-ready architecture. This wording does not claim that every deployment is automatically GxP compliant; deployment validation, SOPs, qualification and operational controls remain organization-specific.

## Architecture

Browser → Next.js 15 / React 19 → Django REST Framework → PostgreSQL

Django also uses Redis + Celery for background work and Paymob at the payment boundary.

The complete architecture is documented in [ARCHITECTURE.md](ARCHITECTURE.md).

## Tenant model

Organization is the paying tenant.

Organization
- Sites
- Memberships
  - User
  - Role
  - Permissions
- Subscription
- Domain records

The security invariant is simple: a customer request is authorized from authenticated membership and backend tenant context. A UUID supplied by a browser never grants access by itself.

## Domain applications

| App | Responsibility |
|---|---|
| accounts | Identity, authentication, MFA, recovery and onboarding |
| platform | Organization, site, membership, RBAC and tenant context |
| products | Pharmaceutical product master data |
| batches | Batch traceability |
| stability | Study, protocol/version, specification/version, timepoint and sample workflow |
| chamber | Chamber, storage and sample pulls |
| results | Laboratory results and controlled review/approval |
| quality | OOS, OOT, deviations, CAPA and change control |
| schedule | Scheduled work and Celery tasks |
| notifications | User workflow notifications |
| audit | Append-only audit evidence |
| compliance | Signatures, controlled records and validation evidence |
| reports | Tenant-scoped analytics and exports |
| billing | Plans, subscriptions, usage and entitlement enforcement |

Each Django app now has its own README describing purpose, responsibilities, architecture, security and design invariants.

## Controlled workflow

Product → Specification/TestDefinition → Batch → Study → ProtocolVersion → Timepoint → Sample → Result → Review → Approval/Lock

Quality events, audit events and compliance evidence attach to the workflow without replacing the source records.

## Authentication and authorization

- JWT access/refresh authentication.
- Password recovery and email verification.
- TOTP MFA support.
- Login throttling and account controls.
- Organization owner created by the backend during tenant onboarding.
- Explicit tenant-aware API base classes.
- Route-coverage tests requiring every API route to declare tenant posture.
- Action-level RBAC.
- Negative cross-tenant security tests.

## Billing

Plan → Entitlement → Subscription → Usage

Subscription states include trialing, active, past_due, suspended and canceled. Paymob callbacks are treated as untrusted external input and require authenticity, amount/currency verification and idempotency.

## Audit and compliance

Important workflow actions produce audit evidence. Audit records have database-level immutability protection. Electronic signatures and controlled records are handled as evidence linked to the underlying business workflow.

## Frontend

The Next.js frontend provides:
- Professional public landing page.
- Product walkthrough animation.
- Clear Sign in and Create workspace paths.
- Multi-step tenant onboarding.
- Authenticated tenant workspace.
- Light/dark mode.
- Responsive layouts and reduced-motion support.
- Stability, results, quality, compliance, reporting, administration and billing surfaces.

See [frontend/README.md](../frontend/README.md).

## CI/CD release gates

GitHub Actions currently validate:
1. Python dependency integrity.
2. Django system checks.
3. Production deployment checks.
4. Migration synchronization.
5. Backend tests and coverage threshold.
6. Frontend no-demo checks.
7. TypeScript typecheck.
8. Next.js production build.
9. Frontend route smoke tests.
10. Backend and frontend container builds.
11. Production compose configuration/build.
12. Database backup/restore verification.

The release gate is evidence, not a substitute for production deployment verification.

## Development

Backend:

    cd QCSTS
    pip install -r requirements/test.txt
    python manage.py check
    python manage.py migrate
    pytest

Frontend:

    cd frontend
    npm ci
    npm run check:no-demo
    npm run typecheck
    npm run build
    npm run check:routes

Docker:

    docker compose -f QCSTS/docker/docker-compose.yml up --build

Production configuration must use the production environment template and real secret management. Never commit real secrets.

## Testing philosophy

QCSTS treats negative security tests as first-class tests.

A passing happy-path test is not enough. The suite must prove that:
- one tenant cannot read another tenant;
- one tenant cannot mutate another tenant;
- users cannot invent roles or memberships;
- locked results cannot be rewritten;
- audit records cannot be modified;
- reports cannot aggregate unauthorized data;
- billing callbacks cannot forge subscription state.

## Current readiness interpretation

A software project should not be called “100% production ready” merely because all planned files exist. QCSTS therefore distinguishes implementation completeness from runtime evidence.

Current assessment on the audited repository state:

- Product/domain implementation: **88%**
- Tenant isolation/RBAC: **91%**
- Authentication/security: **88%**
- Stability/results workflow: **86%**
- Billing/entitlements/Paymob: **84%**
- Audit/compliance evidence: **82%**
- Frontend/API integration: **84%**
- Testing/security evidence: **83%**
- CI/CD/release engineering: **91%**
- Operations/DR/observability: **76%**
- Documentation: **92%**
- Validation/UAT evidence: **65%**

**Overall engineering completeness: ~85%.**

The remaining percentage is deliberately not treated as “missing code” alone. The largest remaining evidence gaps are real deployed-environment verification, full end-to-end tenant/security evidence, observability, backup/restore evidence against the actual production stack, and formal validation/UAT evidence.

## Documentation map

- [Backend architecture](ARCHITECTURE.md)
- [Frontend architecture](../frontend/README.md)
- [Accounts](apps/accounts/README.md)
- [Audit](apps/audit/README.md)
- [Batches](apps/batches/README.md)
- [Billing](apps/billing/README.md)
- [Chamber](apps/chamber/README.md)
- [Compliance](apps/compliance/README.md)
- [Notifications](apps/notifications/README.md)
- [Platform](apps/platform/README.md)
- [Products](apps/products/README.md)
- [Quality](apps/quality/README.md)
- [Reports](apps/reports/README.md)
- [Results](apps/results/README.md)
- [Schedule](apps/schedule/README.md)
- [Stability](apps/stability/README.md)
