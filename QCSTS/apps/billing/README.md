# Billing — Plans, Entitlements, Subscriptions & Usage

## Purpose
The billing app provides the commercial control plane for QCSTS subscriptions.

## Responsibilities
- Global plan catalog.
- Organization subscriptions.
- Entitlement and capacity enforcement.
- Usage tracking.
- Trial lifecycle.
- Paymob integration and webhook verification.
- Billing recovery states.

## Architecture
Plan → Entitlements/limits → Subscription → UsageRecord, with Paymob as the payment provider boundary.

Billing is not only a payment UI. Subscription state is an input to backend product authorization.

## Subscription lifecycle
Supported states include trialing, active, past_due, suspended and canceled. Billing recovery endpoints must remain reachable when service is restricted.

## Security design
Subscription ownership is derived from tenant context. Paymob callbacks must verify authenticity, amount and currency and be idempotent. The frontend never decides entitlement. Plans are global; subscriptions and usage are tenant-scoped.

## Testing
Cover limits, trial expiration, state transitions, webhook authenticity, amount/currency verification, duplicate callbacks and tenant isolation.

## Design invariant
Payment status controls commercial access; it never bypasses tenant/RBAC security.
