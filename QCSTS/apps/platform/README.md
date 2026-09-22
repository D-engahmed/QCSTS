# Platform — Multi-Tenant Foundation & RBAC

## Purpose
The platform app defines the SaaS tenancy model and shared authorization primitives.

## Core model
Organization → Sites; Organization → Memberships → Users; Membership → Role → Permissions; Organization → Subscription.

An organization is the paying tenant. A site is a physical facility. Membership connects a user to an organization and role.

## Responsibilities
- Organization and site models.
- Membership lifecycle.
- Roles and permissions.
- Tenant context.
- Shared tenant-aware query/permission behavior.
- Platform administration boundaries.

## Security architecture
Tenant identity is derived from authenticated membership, never trusted from arbitrary request data. Every tenant resource must explicitly declare its posture through the tenant-scoped base classes or document why it is exempt.

## RBAC design
Permissions represent actions such as view/create/update/delete. Platform superusers are not equivalent to organization owners.

## Testing
The critical tests are negative: Tenant A cannot read or mutate Tenant B; membership IDs and site IDs cannot be invented to cross boundaries; UUID knowledge never bypasses authorization.

## Design invariant
Tenant isolation is a backend security invariant, not a frontend filtering feature.
