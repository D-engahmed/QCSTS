# Single customer authorization assignment migration

QCSTS customer identity is migrating from a multi-membership model to one fixed authorization assignment:

```
CustomUser -> Membership -> Organization + Site + Role
```

Before the enforcing migration is applied, run:

```bash
python manage.py audit_single_tenant
```

The command fails closed when it finds:

- zero or multiple memberships for a user
- zero or multiple sites on a membership
- a default site inconsistent with the selected sites
- a site belonging to another organization
- a role belonging to another organization
- duplicate user/organization membership rows

No migration step should guess which organization, site, or role is authoritative for an ambiguous record.

The migration is intentionally split into audit, enforcement, request-context, API, frontend, and regression-test increments so each security boundary can be reviewed independently.
