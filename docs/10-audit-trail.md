# QCSTS Audit Trail

## Purpose
Maintain an append-only record of critical security, quality and business actions.

## Required fields
```text
id
organization
actor
action
object_type
object_id
object_version
timestamp
request_id
ip/network context where appropriate
old_state
new_state
reason
```

## Critical events
Login success/failure, logout, membership/role changes, protocol/specification approval, study transitions, result submission, signatures, reviews, approvals/rejections, corrections, exports, API-key changes and billing changes.

## Atomicity
For regulated transitions, domain mutation and audit event are one transaction. If audit persistence fails, the regulated action fails closed.

## Immutability
Enforce at application and database layers. Model `save`/`delete` protections are not sufficient alone. Production should use database privileges/triggers or equivalent defense in depth.

## Outbox
Non-critical downstream notifications may use an outbox created in the same transaction. Outbox delivery retries must not repeat the original domain action.

## Retention
Retention is policy-driven and must preserve contractual/regulatory obligations.

## Export
Audit export is read-only, tenant scoped and itself auditable.

## Acceptance criteria
No critical regulated action can complete without its required audit evidence.
