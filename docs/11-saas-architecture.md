# QCSTS SaaS Architecture

## Purpose
Separate commercial SaaS concerns from pharmaceutical workflow concerns while maintaining one fixed customer authorization context.

## Customer tenancy

```text
QCSTS
 |
 +-- Platform Operators
 |
 +-- Organization A
 |    +-- Sites
 |    +-- Billing
 |    +-- Users
 |         +-- exactly one Membership
 |              +-- Organization A
 |              +-- exactly one Site
 |              +-- exactly one Role
 |
 +-- Organization B
```

A customer user never selects or switches organization context after authentication. Site reassignment is an explicit audited administrative mutation, not a second membership.

## Commercial hierarchy

```text
Organization
   -> Subscription
      -> Plan + Price
         -> Entitlements
      -> Usage
      -> Invoices
      -> Payments
```

## Plan vs entitlement
A Plan is a commercial bundle. Entitlements are machine-readable capabilities and limits. This supports promotions, negotiated enterprise contracts, add-ons and founding customers without code branches.

## Subscription lifecycle
Trialing -> Active -> Past Due -> Active
                    |
                    +-> Paused / Cancelled / Expired

## Billing isolation
Billing state must not mutate or delete regulated records. Feature restrictions may apply to new operations according to policy, but historical data remains governed by retention/access rules.

## Entitlement service
Provide centralized checks such as:
```text
can_create_study()
can_add_user()
can_add_site()
can_use_api()
can_use_sso()
can_generate_advanced_report()
```

No scattered `if plan == ...` branches.

## Usage metering
Meter organization-level capacity: users, sites, active studies, batches, chambers, API usage and storage where commercially useful.

## Billing events
Persist provider event identifiers and processing status. Webhooks are idempotent and reconciliatory.

## Payment provider boundary
Business logic uses a provider interface. Provider adapters translate external operations into internal subscription/payment state.

## Audit
Subscription, plan, entitlement and payment changes are audited at organization level.

## Security
Only billing-authorized organization members may access billing data. Payment secrets remain provider-side and server-side. Tenant identity is derived from the user's single Membership rather than client-selected headers.
