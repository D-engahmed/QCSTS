# QCSTS Target Architecture

## 1. Purpose

This document is the authoritative target-state architecture for QCSTS after productization. QCSTS is a multi-tenant B2B SaaS platform for pharmaceutical stability management.

The architecture must preserve the existing Django + DRF backend, React + Vite frontend, PostgreSQL, Redis and Celery foundations wherever practical. Prefer modular evolution over a rewrite.

## 2. Product boundary

QCSTS owns the workflow from controlled product/protocol definition through stability-study execution, sample pulls, laboratory results, review/approval, reporting and auditability.

QCSTS does not initially attempt to replace a complete ERP, MES, generic QMS or general-purpose LIMS.

## 3. Logical architecture

```text
Client Applications
  ├── React Enterprise Web App
  └── External API Clients
            |
            v
      API / Auth Layer
            |
            v
     Tenant Context Layer
            |
   +--------+--------+
   |        |        |
   v        v        v
Stability Laboratory Quality
   |        |        |
   +--------+--------+
            |
            v
      Shared Services
   ├── Audit
   ├── Signatures
   ├── Notifications
   ├── Reporting
   ├── Billing
   ├── Storage
   └── Integrations
            |
            v
 Infrastructure
 ├── PostgreSQL
 ├── Redis
 ├── Celery / Beat
 └── Object Storage
```

## 4. Bounded contexts

### Platform
Organizations, sites, memberships, roles, permissions, active context, feature flags and platform configuration.

### Stability
Products, monographs, protocols, protocol versions, studies, batches, chambers, storage conditions, timepoints, samples and pulls.

### Laboratory
Tests, specifications, specification versions, calculation rules, result submission, correction and supersession.

### Quality
Reviews, approvals, signatures, audit events, deviations, OOS and OOT.

### Reporting
Server-generated reports, report snapshots, versions and artifacts.

### Notifications
Domain event consumption, notification preferences, in-app/email delivery and outbound webhooks.

### Billing
Plans, prices, subscriptions, entitlements, usage, invoices, payments and provider events.

### Integrations
API keys, service accounts, scopes and external webhooks.

### Operations
Storage, observability, backups, recovery and deployment.

## 5. System invariants

1. Every tenant-owned record has a non-null organization reference after migration completion.
2. Site-owned records reference a site belonging to the same organization.
3. All reads and writes are tenant scoped server-side.
4. No regulated historical record is silently overwritten.
5. Approved protocol and specification versions are immutable.
6. Regulated transitions and their audit events are transactional.
7. Electronic signatures bind to a specific signable record version.
8. Plans and entitlements are configuration/data, not scattered code branches.
9. Historical data remains available according to contractual retention rules even if access to new features is restricted.
10. External provider callbacks are idempotent.

## 6. Data ownership hierarchy

```text
Organization
  └── Site
      ├── Products
      ├── Protocols
      ├── Studies
      ├── Batches
      ├── Chambers
      └── Users via Membership
```

All downstream domain entities inherit organization ownership either directly or through an explicitly controlled parent relationship. Direct organization columns are preferred for high-volume and security-critical records to make authorization and query planning explicit.

## 7. Application layering

Use the following layers:

```text
API/View
  -> Serializer / Request validation
  -> Policy / Authorization
  -> Application service
  -> Domain model / repository/query service
  -> Transaction boundary
  -> Audit / events / outbox
```

Views must not contain complex business rules.

Authorization must not depend on frontend state.

## 8. Synchronous vs asynchronous work

Synchronous:
- authentication
- authorization
- CRUD validation
- regulated state transitions
- signatures
- audit persistence

Asynchronous:
- email
- webhook delivery
- large report generation
- exports
- scheduled reminders
- non-critical analytics aggregation

A background task must carry organization context and must re-check authorization-sensitive state before acting.

## 9. API conventions

Retain `/api/v1/`.

Use:
- stable resource naming
- pagination
- filtering
- explicit error envelopes
- idempotency keys for mutation endpoints where duplicate delivery is possible
- OpenAPI documentation

## 10. Frontend architecture

The React application should have:
- authenticated shell
- organization/site context selector
- route guards as UX only
- server-authoritative permissions
- centralized API client
- error boundary
- reusable data table/form/status components
- design tokens
- accessibility checks

## 11. Deployment model

Initial SaaS:
- shared application deployment
- shared PostgreSQL database/schema
- row-level tenant boundaries enforced in application code
- PostgreSQL RLS considered as defense in depth after migration

Enterprise option:
- dedicated database/environment
- dedicated object storage namespace
- optional private networking
- regional data residency

## 12. Architecture decisions

### Shared-schema SaaS first
Use shared PostgreSQL schema with explicit organization ownership to keep initial operating cost low and avoid premature infrastructure fragmentation.

### Modular monolith first
Keep Django as a modular monolith. Introduce service boundaries without prematurely creating microservices.

### Provider adapters
Payments and storage are behind provider interfaces.

### Append-only quality records
Results, signatures, approvals and audit events are immutable historical records with linked corrections/supersessions.

## 13. Non-goals

Do not introduce:
- microservices without a measured need
- event sourcing for the whole system
- blockchain audit storage
- AI in regulated decision paths
- per-result billing

## 14. Definition of done

The target architecture is achieved when all production workflows conform to the boundaries, invariants and transaction rules above and the tenant/security test suite demonstrates isolation across every exposed resource and background workflow.
