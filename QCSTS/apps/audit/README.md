# Audit — Immutable Evidence Trail

## Purpose
The audit app records security, administrative and regulated workflow events so important actions can be reconstructed later.

## Responsibilities
- Persist actor, action, model, object and tenant context.
- Capture structured before/after evidence where applicable.
- Associate events with request/IP context when available.
- Expose tenant-scoped audit history.
- Protect audit records from application-level mutation and deletion.

## Architecture
Domain/API action → AuditService → AuditLog → PostgreSQL immutability trigger.

The service is preferred over scattered direct audit writes so event semantics stay consistent.

## Security design
Audit records are tenant-scoped. PostgreSQL immutability provides a second control layer. Audit endpoints must never accept an arbitrary tenant identifier as an authorization decision.

## Evidence design
Every important event should answer who acted, what happened, which resource was affected, which organization/site context applied, when it happened, and what changed.

## Testing
Cover creation, tenant isolation, serialization, endpoint authorization and database-level immutability.

## Design invariant
Audit is append-only evidence, not a mutable activity feed.
