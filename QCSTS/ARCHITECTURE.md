# QCSTS Architecture

## Product boundary

QCSTS is a multi-tenant SaaS Quality Control and Stability Testing Management System for pharmaceutical organizations and laboratories.

The paying security boundary is Organization. Site represents a physical facility. Membership binds a user to an organization, site context and role.

## System topology

Browser
  ↓
Next.js frontend
  ↓ HTTPS
Django REST API
  ├── Authentication / JWT / MFA
  ├── Tenant context + RBAC
  ├── Domain applications
  ├── Billing / entitlement enforcement
  ├── Audit / compliance evidence
  └── Reporting
       ↓
PostgreSQL

Django
  ├── Celery → Redis → background workers
  └── Payment boundary → Paymob

## Domain decomposition

accounts
Identity, authentication, registration, recovery and MFA.

platform
Organization, Site, Membership, Role, Permission and tenant authorization primitives.

products
Product and controlled pharmaceutical master data.

batches
Batch traceability.

stability
Study, protocol/version, specification/version, timepoint and sample workflow.

chamber
Physical chamber/storage/pull execution.

results
Laboratory measurements and controlled review/approval.

quality
OOS, OOT, deviations, CAPA and change control.

schedule
Scheduled work and background tasks.

notifications
User-facing workflow notifications.

audit
Append-only audit evidence.

compliance
Electronic signatures, controlled records and validation evidence.

reports
Tenant-scoped analytics and exports.

billing
Plan, subscription, usage and entitlement enforcement.

## Tenant security model

Every customer resource follows:

Authenticated user
  ↓
Active Membership
  ↓
Organization
  ↓
Optional Site
  ↓
RBAC permission
  ↓
Object/query authorization

The organization is never trusted from a UUID supplied by the browser.

Route security is enforced structurally through tenant-aware base views and route-coverage tests. Exempt routes must explicitly document why they are not tenant-scoped.

## State and evidence model

Controlled workflows use explicit backend transitions.

Example result lifecycle:

Draft → Submitted → Under review → Approved → Locked

Correction is a controlled path. Approved/locked evidence must not be overwritten through generic update endpoints.

A domain state transition should produce the appropriate audit and, where required, signature/compliance evidence.

## Billing architecture

Plan → Entitlement → Subscription → Usage

Subscription state can restrict commercial operations, but billing checks never replace tenant/RBAC checks.

Payment callbacks are treated as hostile external input and require authenticity, amount, currency and idempotency validation.

## Frontend architecture

Next.js App Router provides public marketing/authentication routes and authenticated application routes.

Core client boundaries:
- AuthProvider: session lifecycle.
- api.ts: HTTP/API boundary.
- auth.ts: local session representation.
- AppShell: authenticated navigation and tenant context.
- reusable workspace components: tables, forms, signatures, status and error presentation.

The frontend improves usability but does not make authorization decisions.

## Infrastructure

Development and production are containerized. PostgreSQL is the system of record. Redis supports Celery and transient application workloads. Gunicorn serves Django and Next.js serves the frontend production build.

CI/CD validates:
- Python dependency integrity.
- Django system checks.
- deployment checks.
- migration graph.
- backend tests and coverage.
- frontend typecheck/build/smoke routes.
- container builds.
- database recovery verification.

## Validation posture

QCSTS should be described as designed for GxP-regulated environments with a validation-ready architecture.

Technical controls are evidence for a validation program, not a substitute for organization-specific SOPs, qualification, risk assessment, data integrity procedures or regulatory validation.

## Non-negotiable invariants

1. No cross-tenant read/write access.
2. No client-selected arbitrary organization membership.
3. No role escalation through request payloads.
4. No mutation of immutable audit evidence.
5. No mutation of locked controlled results.
6. Billing cannot bypass authorization.
7. External payment callbacks cannot mutate state without verification.
8. Reports and exports cannot aggregate unauthorized tenant data.
9. Background tasks must preserve tenant-safe object references.
10. Every API route must declare tenant posture.
