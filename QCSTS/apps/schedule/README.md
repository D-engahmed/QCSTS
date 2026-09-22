# Schedule — Timepoint & Background Task Scheduling

## Purpose
The schedule app handles scheduled work associated with QCSTS operational timelines.

## Responsibilities
- Scheduled task records.
- Timepoint scheduling.
- Celery task execution.
- Reminders and notification generation.
- Background maintenance.

## Architecture
Study/Timepoint → Schedule → Celery worker → reminder/notification/maintenance.

The scheduler coordinates work; domain models remain the source of truth.

## Reliability design
Tasks should be idempotent. Retries must not create duplicate business events or notifications.

## Security design
Background jobs carry validated tenant context through references to authoritative domain objects. Task payloads must not become an authorization bypass.

## Testing
Cover due-date behavior, retries, idempotency, tenant isolation and notification side effects.

## Design invariant
Scheduling tells the system when to act; domain models determine what the action means.
