# Architecture decision records

## ADR-001: shared PostgreSQL with row-level tenant boundaries

**Status:** proposed for Phase 1. Use a shared database/schema and a mandatory organization foreign key on tenant-owned tables. Enforce it in request context, queryset/policy layers, tests, foreign-key validation and later PostgreSQL RLS as defense in depth. This supports the initial MENA SaaS stage without prematurely operating per-tenant infrastructure. Dedicated deployments/data residency remain an Enterprise deployment option.

## ADR-002: membership is the authorization anchor

**Status:** proposed. Users are global identities. Membership links users to organizations and carries active status, organization role assignment and permitted site scope. Roles and permissions are centralized records, not a `CustomUser.role` string. The legacy role field remains temporarily for compatibility and is retired only after consumers migrate.

## ADR-003: additive, reversible tenant migration

**Status:** proposed. Add nullable organization columns and platform records first; create a controlled legacy organization; backfill deterministically; validate; then make fields non-null and replace global uniqueness with organization-scoped constraints. Release tenant filters only after backfill and isolation tests. No broad data rewrite or destructive migration.

## ADR-004: append-only quality records

**Status:** proposed. Results, signatures, approvals, audit events and generated reports are new-record workflows. Corrections and supersessions are linked immutable records. Use canonical JSON/hash procedures where a signature must bind to a record version.

## ADR-005: transactional audit outbox

**Status:** proposed. Critical action + audit event are atomic. Non-critical email/webhook delivery enters an outbox in the same transaction and is dispatched asynchronously. Audit persistence must fail closed for regulated transitions; delivery retries must not repeat domain actions.

## ADR-006: provider adapters at external boundaries

**Status:** proposed. Payments and object storage use provider interfaces with persisted provider references/idempotency keys. Start with no paid-provider claim until configured and tested; Paymob/Stripe adapters are future implementations behind the interface.
