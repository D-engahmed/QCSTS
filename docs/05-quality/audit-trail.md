# Audit Trail

## Purpose

Maintain an append-only historical record of security, quality and business-significant actions.

## Required fields

- id
- organization
- actor
- action
- object type
- object id
- object version where applicable
- timestamp
- IP/network context where appropriate
- request ID
- old state
- new state
- reason/comment

## Critical actions

At minimum:
- login success/failure
- logout
- user/membership changes
- role/permission changes
- product/protocol approval
- study state transitions
- result submission
- signature
- review
- approval/rejection
- correction/supersession
- export
- API key changes
- billing/plan changes

## Transaction rule

For regulated transitions, the domain change and audit event must be in the same transaction. If audit persistence fails, the regulated action fails closed.

## Immutability

Enforce at multiple layers:
1. application model/API restrictions
2. database privileges
3. PostgreSQL trigger/RLS or equivalent defense in depth where appropriate

## Retention

Retention is policy-driven and must not be shorter than contractual/regulatory obligations.

## Acceptance criteria

No critical workflow may complete without its required audit evidence.
