# PR15 — Cross-Tenant Security and Privilege-Escalation Regression Suite

## Objective

Turn the tenant boundary into an adversarial regression contract. A user who is a valid member of organization A must not obtain organization B data or mutate organization B resources by manipulating identifiers, headers, or submitted ownership fields.

## Threats covered

- Cross-tenant read by foreign object ID.
- Cross-tenant update by foreign object ID.
- Cross-tenant deletion by foreign object ID.
- Organization-header spoofing.
- Organization ownership spoofing during create.
- Missing permission on an otherwise authorized tenant resource.
- Membership bound to a role from another organization.
- Membership bound to a default site from another organization.

## Expected security model

```text
Authenticated user
        ↓
Active membership
        ↓
Organization context
        ↓
Site membership (when applicable)
        ↓
Explicit permission
        ↓
Tenant-scoped object lookup
        ↓
Action
```

Changing a UUID or HTTP context header must never create authority.

## Engineering decision

PR15 is primarily a regression/security-test PR rather than a large domain refactor. The goal is to establish a reusable adversarial test pattern before the stability domain is added. Where a test exposes an implementation defect, the defect should be fixed in the smallest follow-up commit/PR rather than weakening the test.

## Production gate

The suite must pass before tenant-isolated domain work is considered production-ready. Passing this PR does not prove that every future domain is secure; each new domain must remain behind the route-level guard from PR14 and receive equivalent object-level isolation tests.

## Verification

```bash
python manage.py check
python manage.py makemigrations --check
pytest QCSTS/apps/platform/tests/test_tenant_security_matrix.py
pytest QCSTS/core/tests/test_route_coverage.py
pytest
```
