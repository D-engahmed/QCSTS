# QCSTS Authorization Model

## 1. Principles

Authorization is server-side, tenant-aware, site-aware and based on explicit permissions.

Frontend route hiding is not a security boundary.

## 2. Authorization layers

```text
Authenticated?
   ↓
Organization membership active?
   ↓
Site scope valid?
   ↓
Permission granted?
   ↓
Object state allows action?
   ↓
Separation-of-duties rules pass?
```

All layers are required where applicable.

## 3. Roles

Initial role templates:
- Owner
- Organization Admin
- QA Manager
- QC Manager
- Supervisor
- Analyst
- Read Only
- Service Account

System roles are templates. Organizations may receive organization-scoped custom roles.

## 4. Permissions

Use stable codes, e.g.:

```text
organization.view
organization.update
user.invite
user.deactivate
role.manage
product.create
product.update
protocol.create
protocol.approve
study.create
study.approve
sample.pull
result.submit
result.correct.request
result.review
result.approve
signature.perform
audit.view
report.generate
report.export
billing.view
billing.manage
api.manage
integration.manage
```

## 5. Object-level policy

A permission alone is insufficient when resource scope matters.

Example:

```text
result.review
AND
result.organization == active organization
AND
result.site in membership site scope
AND
result.status == SUBMITTED
```

## 6. Separation of duties

Default rule: an analyst who submitted a regulated result cannot be the sole approver of that same result unless an explicitly configured policy and applicable business process permit it.

## 7. Administrative boundary

Organization admins manage configuration and membership but must not bypass regulated state transitions merely because they are admins.

Emergency/break-glass access, if introduced, must be separately controlled and heavily audited.

## 8. Permission storage

Permissions are centralized data records.

Roles map to permissions.

Membership maps user to organization and role.

## 9. Policy service

Provide centralized policy checks such as:

```python
policy.can(user, "result.approve", result)
```

Do not duplicate equivalent checks in multiple views.

## 10. Deny-by-default

Unknown actions and missing permissions must deny access.

## 11. API behavior

Do not reveal whether a foreign-tenant object exists merely because a user is unauthorized. Prefer consistent `404` semantics for object lookups where appropriate.

## 12. Audit

Permission and role mutations must create audit events.

## 13. Tests

Cover:
- role matrix
- site restrictions
- self-approval prevention
- admin boundaries
- API-key scopes
- inactive memberships
- suspended organizations
- archived records
