# Organizations

## Purpose

An Organization is the top-level tenant in QCSTS.

## Lifecycle

Active -> Suspended -> Archived.

Archived organizations are read-only except for administrative recovery actions.

## Required behavior

Organization creation must initialize:
- owner membership
- default role templates
- default site if selected
- plan/subscription state according to onboarding mode

## Validation

- slug globally unique
- ISO-like country code stored consistently
- valid IANA timezone
- supported currency code

## API

Suggested endpoints:

```text
GET    /api/v1/organizations/me/
PATCH  /api/v1/organizations/me/
GET    /api/v1/organizations/
POST   /api/v1/organizations/
GET    /api/v1/organizations/{id}/
PATCH  /api/v1/organizations/{id}/
```

External access must be restricted by membership.

## Acceptance criteria

1. Organization owner can update organization settings.
2. Non-admin members cannot change billing/legal settings.
3. Suspended organizations cannot create new operational records.
4. Archived organizations cannot execute operational workflows.
5. Organization events are audited.
