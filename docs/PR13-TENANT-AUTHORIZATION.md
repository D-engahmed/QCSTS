# PR #13 — Tenant Authorization Hardening

## Objective

Close the first production security gate after the production-foundation work: platform site APIs must enforce explicit server-side authorization in addition to tenant scoping.

## Security contract

Every site API request is evaluated in this order:

1. Authenticated identity.
2. Active membership in the selected organization.
3. Valid site context when supplied.
4. Explicit organization permission for the requested operation.
5. Tenant-scoped object lookup.

The frontend must not be treated as an authorization boundary.

## Site permissions

- `site.view`
- `site.create`
- `site.update`
- `site.delete`

The permissions are evaluated from the active `Membership -> Role -> Permission` relationship.

## Important behavior

- A client cannot select another organization and create a site there.
- A foreign-tenant site is not returned through a tenant-scoped detail endpoint.
- A membership without the operation-specific permission receives HTTP 403.
- Site create always derives organization ownership from the server-resolved tenant context rather than trusting request data.

## Production gate

This PR establishes the authorization pattern that must be applied consistently to the remaining domain APIs. It does **not** claim that every QCSTS endpoint is now authorized; the remaining product domains require the same endpoint-level security coverage before production release.

## Verification

Run in the project environment:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
pytest QCSTS/apps/platform/tests/
pytest
```
