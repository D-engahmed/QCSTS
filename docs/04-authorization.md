# QCSTS Authorization Model

## Customer identity boundary

A normal customer user has exactly one active authorization assignment:

```text
CustomUser
   -> Membership
       -> Organization
       -> Site
       -> Role
```

A customer user cannot belong to multiple organizations, multiple sites, or multiple customer roles simultaneously.

Authentication remains on `CustomUser`. Business authorization is derived only from `Membership.role` and its permissions.

## Context resolution

The server derives:

```text
organization = request.user.membership.organization
site         = request.user.membership.site
role         = request.user.membership.role
```

Organization and site headers, when retained for compatibility, may only assert the already assigned IDs. They cannot switch the user into another context.

## Role scope

Every role has an explicit scope:

- `SITE`: operations are limited to the user's assigned site.
- `ORGANIZATION`: operations may span sites inside the user's organization.

The assigned site remains part of the user's identity context even for an organization-scoped role.

## Evaluation order

```text
Authenticated?
 -> Active user?
 -> Active Membership?
 -> Active organization/site?
 -> Required permission?
 -> Role scope?
 -> Same organization?
 -> Same site when SITE-scoped?
 -> Object policy?
 -> Workflow state?
 -> Entitlement?
 -> Separation-of-duties?
```

## Object-level policy

UUIDs are identifiers, never authorization. Every tenant-owned query must constrain the object by the authenticated organization and, for site-scoped roles, the assigned site.

## Administration boundary

Organization administrators manage organization-wide configuration and people, but do not bypass regulated workflow controls.

## Platform administrators

Platform operators are a separate privileged boundary. A customer membership must never be converted into platform authority by setting organization/site fields to null.

## Migration safety

The single-assignment migration is fail-closed. It must not guess an organization, site, or role for ambiguous legacy data. Run:

```bash
python manage.py audit_single_tenant
```

before applying the enforcing migration.

## Tests

Regression coverage must include:
- zero/multiple legacy memberships
- zero/multiple legacy sites
- foreign role/site
- organization/site header switching attempts
- foreign object UUIDs
- inactive memberships
- site-scoped vs organization-scoped roles
- foreign-tenant create/update/delete/read attempts
- background jobs, files, exports and caches
