# Accounts — Identity, Authentication & Tenant Membership

## Purpose
The accounts app owns user identity and authentication. It is the entry point for login, registration, password lifecycle, email verification, MFA and organization membership context.

## Responsibilities
- Create and authenticate CustomUser accounts.
- Public SaaS onboarding: create the first organization, site, owner membership and trial subscription atomically.
- Issue and revoke JWT access/refresh tokens.
- Enforce login throttling and account lockout controls.
- Support password change/recovery and email verification.
- Support TOTP MFA setup, confirmation and login challenges.
- Manage staff users inside an existing tenant through authenticated administrative endpoints.
- Record authentication events through the audit service.

## Architecture
HTTP → accounts/urls.py → views.py → serializers.py → identity/platform/billing services.

Authentication is deliberately separated from tenant authorization. A user does not select an arbitrary organization or role during registration; the backend creates the initial tenant relationship.

## Security design
Public registration is throttled. Tenant operations inherit tenant-scoped base views and RBAC. The owner role is created server-side. JWTs authenticate the caller; membership resolves tenant authority. Password recovery and verification are tokenized. MFA secrets are encrypted at rest. Authentication actions are auditable.

## Data model
CustomUser is identity. Membership connects the user to Organization, Role and default Site. This keeps authorization explicit rather than embedding organization ownership directly into the user.

## Testing
Tests cover models, authentication, registration atomicity, throttling, CORS, MFA and recovery. Security tests must include negative cross-tenant cases.

## Design invariant
Authentication answers who the user is. Membership and RBAC answer what the user may do inside the tenant.
