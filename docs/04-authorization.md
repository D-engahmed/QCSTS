# QCSTS Authorization Model

## Principles
Authorization is server-side, tenant-aware, site-aware, deny-by-default and state-aware. Frontend route hiding is UX, never security.

## Evaluation order
```text
Authenticated?
 -> Active organization membership?
 -> Valid site scope?
 -> Permission?
 -> Object policy?
 -> State transition allowed?
 -> Separation-of-duties check?
```

## Initial roles
- Owner
- Organization Admin
- QA Manager
- QC Manager
- Supervisor
- Analyst
- Read Only
- Service Account

## Permission codes
Use stable `resource.action` codes, e.g.:
```text
organization.update
user.invite
role.manage
product.create
protocol.approve
study.create
study.approve
sample.pull
result.submit
result.review
result.approve
signature.perform
audit.view
report.generate
report.export
billing.manage
api.manage
integration.manage
```

## Object-level policy
A permission is not sufficient. The object must belong to the active organization and fall within site/state scope.

## Separation of duties
Default policy prevents an analyst from being the sole approver of the same regulated submission when a second-person review is required.

## Administration boundary
Organization admins manage people/configuration but do not bypass regulated workflow controls.

## Central policy service
Provide a single policy API such as `policy.can(user, action, object)`; do not reproduce logic across views.

## API behavior
Do not reveal foreign-tenant existence unnecessarily. Use appropriate 404/403 semantics consistently.

## Tests
Cover inactive memberships, suspended organizations, site restrictions, self-approval prevention, API scopes, custom roles and every critical regulated action.
