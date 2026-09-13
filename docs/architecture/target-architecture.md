# Target architecture

QCSTS will evolve as a modular Django SaaS with a React enterprise application. Keep the current REST API and domain apps where practical; add bounded-context apps rather than rewriting working capabilities.

## Platform foundation

- `platform`: `Organization`, `Site`, `Membership`, organization-scoped `Role` and `Permission`, tenant context middleware, policy services, feature flags and configuration.
- A request resolves the active organization from a server-verified membership and optional site context. It never accepts a browser-supplied organization as authority.
- Every organization-owned table has a non-null `organization` foreign key; site-owned records also have a constrained `site` foreign key. Managers/query services are tenant-scoped by default and all object retrieval applies that scope.
- Background jobs, files, audit events, report exports, API keys, webhooks, billing usage and observability include organization context.

## Domain boundaries

| Bounded context | Core responsibility |
| --- | --- |
| stability | Products, protocols/versions, studies, batches, timepoints, samples, chambers and pulls |
| laboratory | Tests, specifications/versions/rules, calculations, immutable submissions and corrections |
| quality | Reviews, approvals, persistent electronic signatures, audit events, deviations/OOS/OOT and change history |
| reporting | Traceable report definitions, generation jobs, immutable report snapshots and object-storage artifacts |
| notifications | Event outbox, in-app/email/webhook delivery, retry and preference controls |
| billing | Plans, subscriptions, entitlements, metered usage, provider adapters, invoices/payments/events |
| integrations | API keys/service accounts, `/api/v1/`, outbound webhooks and future LIMS/ERP connectors |
| operations | Object storage abstraction, structured logs, request IDs, health/metrics and backup procedures |

## Required invariants

- Approved protocol/specification versions are immutable. A study/result references the exact approved version and snapshot/hash used.
- Result submissions are append-only. Corrections create a linked controlled result, reason, authorization and audit history; they never update the original.
- Workflow transitions use explicit server-side policies and prohibit prohibited self-approval.
- Signatures persist the actor, meaning, timestamp, authenticated re-entry/session evidence, canonical record ID and record hash/version, and are one-time per signable action.
- Audit event persistence participates in the same transaction as regulated actions. Application actors cannot update/delete audit events; PostgreSQL privileges/trigger controls enforce this in production.
- Entitlement checks are centralized in `EntitlementService`; plans are data, never branching constants scattered through views.

## API and UI direction

Retain `/api/v1/` and standard response/error conventions through a compatibility window. Introduce organization/site endpoints and explicit active-context selection first. Publish an OpenAPI contract, pagination/filtering, consistent resource naming and contract tests before extending external integrations.

The React application becomes a task-oriented enterprise interface with a shared design token system: sober scientific palette, strong status semantics, readable tabular density, keyboard-accessible components, responsive layouts, an organization/site context indicator, attention-driven dashboard and the requested Stability/Laboratory/Quality/Administration navigation. Visual identity work follows the stabilized tenant shell; it must be backed by accessible contrast, real content and API states rather than a cosmetic rewrite.
