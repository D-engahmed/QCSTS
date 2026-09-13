# QCSTS Multi-Tenancy

## Goal
Multiple independent pharmaceutical organizations must safely share a QCSTS deployment without cross-tenant access.

## Model
```text
User -> Membership -> Organization -> Site
```
A user may belong to multiple organizations. Membership is the authorization anchor.

## Request context
Every authenticated request resolves user, active organization, membership and optional site. A browser-supplied organization/site is only a request for context; the server verifies membership and scope before accepting it.

## Data rule
High-risk/high-volume tenant entities should contain explicit `organization_id`, including Product, Protocol, Study, Batch, Chamber, Sample, Result, AuditEvent, Report, APIKey, Subscription and UsageRecord.

## Query rule
Tenant scoping happens before object retrieval.
```python
Result.objects.filter(
    organization=request.organization,
    id=result_id,
)
```
Never retrieve globally and authorize later.

## Site scope
Membership may be organization-wide or limited to selected sites. Site assignment must belong to the same organization.

## Background jobs
Every tenant task carries organization context. The worker re-validates ownership before mutation. Scheduled tasks must never query all customers and act without tenant context.

## Cache
Tenant-specific cache keys contain organization/site context.

## Files
Object keys include tenant namespace: `org/{org_id}/...`. Signed URLs require server-side tenant authorization.

## Search/exports/reports
All must be tenant scoped. Export is auditable.

## Migration sequence
1. Create platform tables.
2. Create controlled legacy organization.
3. Add nullable organization fields.
4. Backfill deterministically.
5. Validate references.
6. Add tenant filters/policies.
7. Make fields non-null.
8. Replace global uniqueness with tenant-aware constraints.
9. Remove compatibility logic after verification.

## Release blocker
Any confirmed cross-tenant read, write, export, file or job path blocks production release.
