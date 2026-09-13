# QCSTS Target Architecture

## Purpose
This is the target-state architecture for QCSTS as a multi-tenant B2B pharmaceutical stability-management SaaS. It preserves the existing Django/DRF + React/Vite + PostgreSQL + Redis/Celery foundation and favors a modular monolith over premature microservices.

## Product boundary
QCSTS owns controlled stability workflows from product/protocol definition through study execution, sample pulls, laboratory results, review/approval, reporting, auditability, notifications, subscriptions and integrations. It is not initially a full ERP, MES, generic QMS or generic LIMS.

## Logical architecture
```text
React Web / External API
        |
   Auth + API Layer
        |
 Tenant Context + Policy
        |
+-------+---------+---------+
|                 |         |
Stability      Laboratory  Quality
|                 |         |
+-----------------+---------+
          Shared Services
 Audit | Signatures | Reports
 Notifications | Billing | Storage
 Integrations | Observability
          |
 PostgreSQL | Redis | Celery | Object Storage
```

## Bounded contexts
- **Platform:** organizations, sites, memberships, roles, permissions, feature flags.
- **Stability:** products, monographs, protocols/versioning, studies, batches, chambers, conditions, timepoints, samples, pulls.
- **Laboratory:** tests, specifications/versioning, calculations, result submission/correction.
- **Quality:** reviews, approvals, signatures, audit events, deviations, OOS/OOT.
- **Reporting:** server-generated, versioned reports and artifacts.
- **Notifications:** event-driven in-app/email/webhook delivery.
- **Billing:** plans, prices, subscriptions, entitlements, usage, invoices, payments.
- **Integrations:** API keys, service accounts, webhooks, future LIMS/ERP adapters.
- **Operations:** storage, logs, metrics, backups, disaster recovery.

## Application layers
```text
API/View -> Serializer/Validation -> Policy -> Application Service
        -> Domain Model/Query Service -> Transaction
        -> Audit/Event Outbox
```
Business rules must not be duplicated in views or frontend code.

## Transaction boundaries
Regulated mutations and their audit records are atomic. Email, webhook delivery and large report generation are asynchronous through an outbox/task model.

## Required invariants
1. Tenant-owned records have a non-null organization reference after migration.
2. Site references always belong to the same organization.
3. Reads/writes are tenant scoped server-side.
4. Approved protocols/specifications are immutable.
5. Submitted results, signatures, approvals and audit events are append-only historical records.
6. Billing is isolated from regulated data mutation.
7. External provider callbacks are idempotent.

## Deployment
Initial SaaS uses shared application + PostgreSQL schema with explicit organization boundaries. Enterprise may use dedicated database/environment and regional data residency.

## Non-goals
Do not introduce microservices, blockchain audit trails, AI-controlled regulated decisions or per-result billing without a demonstrated product requirement.

## Definition of done
Architecture is accepted only when the described boundaries are reflected in code, tests and deployment, and tenant isolation has automated proof across API, jobs, reports and files.
