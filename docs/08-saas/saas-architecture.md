# QCSTS SaaS Architecture

## Purpose

Define the commercial SaaS layer independently from the pharmaceutical domain.

## Tenant commercial boundary

Each Organization has zero or one current commercial subscription in normal operation.

```text
Organization
  -> Subscription
      -> Plan / Price
          -> Entitlements
      -> Usage
      -> Invoices
      -> Payments
```

## Plan vs entitlement

Plans are commercial bundles.

Entitlements are the actual machine-enforced capabilities/limits.

This separation allows:
- promotional plans
- founding customers
- enterprise contracts
- custom add-ons
- negotiated limits

without code branching.

## Billing interval

Supported intervals:
- monthly
- annual

Annual prices are separate price records linked to the same plan identity.

## Subscription state machine

```text
Trialing -> Active -> Past Due -> Active
                     |
                     +-> Paused
                     +-> Cancelled
                     +-> Expired
```

## Grace behavior

Billing failures must not destroy historical quality data.

Feature access changes should be policy-driven. Read access to historical records remains subject to contract/retention rules.

## Entitlement service

Provide one service/API for checks:

```python
can_create_study(organization)
can_add_user(organization)
can_add_site(organization)
can_use_api(organization)
can_use_sso(organization)
```

## Usage

Track usage in a way that supports current plans and future expansion.

Do not meter individual laboratory results as the primary commercial metric.

## Provider boundary

Billing service speaks to a PaymentProvider interface. Providers do not own application subscription state; they provide external transaction evidence.

## Audit

Subscription, plan, entitlement and payment changes are audited at organization level.

## Security

Billing endpoints must be organization-admin or billing-permission controlled.
