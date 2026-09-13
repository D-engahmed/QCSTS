# QCSTS Multi-Tenancy

## 1. Goal

Allow multiple independent pharmaceutical organizations to use one QCSTS deployment without cross-tenant disclosure, modification or deletion.

## 2. Tenancy model

Initial model:

```text
One PostgreSQL database
One logical schema
Explicit organization_id on tenant-owned records
Application-level tenant enforcement
PostgreSQL RLS as defense in depth where practical
```

## 3. Tenant anchor

`Organization` is the tenant boundary.

`Membership` connects a global user identity to an organization.

A user may belong to multiple organizations.

## 4. Request context

Every authenticated request must resolve:

- user
- organization
- membership
- optional site

The browser may request a context, but the server must verify membership before accepting it.

## 5. Query rule

Every tenant-owned query must be scoped by organization before object lookup.

Preferred:

```python
Batch.objects.filter(
    organization=request.organization,
    id=batch_id,
).first()
```

Not:

```python
Batch.objects.get(id=batch_id)
```

followed by a late authorization check.

## 6. Direct organization ownership

High-risk/high-volume entities should contain an explicit organization field even when organization can be inferred through relationships.

Examples:
- Product
- Protocol
- Study
- Batch
- Sample
- Result
- AuditEvent
- Report
- APIKey
- Subscription
- UsageRecord

## 7. Site scoping

Membership may have access to one or more sites.

Rules:
- organization access is required first
- site access is evaluated second
- absence of site assignment means organization-wide access only where the role explicitly permits it

## 8. Background jobs

Celery tasks must never query globally when processing tenant data.

Every task payload must include:
- organization_id
- object identifier
- relevant operation/version

The worker must re-check the object belongs to the organization before acting.

## 9. Files

Object-storage keys must include a tenant namespace, e.g.:

```text
org/{organization_id}/reports/{report_id}/...
```

Signed URLs must only be issued after tenant authorization.

## 10. Reports and exports

Report generation and CSV/Excel/PDF exports must be tenant scoped.

Export actions must be auditable.

## 11. Audit

Audit events are tenant-owned and must be filtered by organization. Platform-level events may be global but must never leak cross-tenant payloads.

## 12. Search

Search indexes or queries must include organization filters. Never implement a global search endpoint over tenant resources.

## 13. Caching

Cache keys must contain organization context where cached data is tenant-specific.

Bad:

```text
dashboard:overview
```

Good:

```text
dashboard:{organization_id}:{site_id}:overview
```

## 14. Isolation tests

Minimum matrix:

```text
Tenant A user -> Tenant A resource = allowed
Tenant A user -> Tenant B resource = denied/not found
Tenant B user -> Tenant A resource = denied/not found
```

Test list, retrieve, create, update, delete, export, reporting, files, background tasks and webhooks.

## 15. No tenant identifier trust

Never treat the following as authorization by themselves:
- request body organization_id
- query-string organization_id
- hidden frontend state
- localStorage organization state

## 16. Migration

Tenant migration is additive and reversible:
1. create platform tables
2. create a controlled legacy organization
3. add nullable organization fields
4. backfill deterministically
5. validate references
6. add tenant filters
7. enforce non-null constraints
8. replace global uniqueness with tenant-aware uniqueness
9. remove compatibility paths only after migration verification

## 17. Release blocker

Any confirmed cross-tenant data-access path blocks production release.
