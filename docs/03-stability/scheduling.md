# Stability Scheduling Engine

## Purpose

Generate and maintain timepoints from approved protocols.

## Inputs

- protocol version
- study start date
- manufacturing/baseline dates where applicable
- study type
- storage condition
- scheduling rules

## Output

Timepoint records containing:
- period
- planned date
- status
- sample requirement
- tests required
- assigned group/user where applicable

## Scheduling rules

Scheduling must be deterministic. Regenerating a schedule must not duplicate existing approved timepoints.

## Date handling

Use organization/site timezone for operational dates while storing timestamps consistently in UTC.

## Celery

Background tasks may update reminder/overdue state, but they must not invent or change the approved study schedule without an explicit business rule.

## Acceptance criteria

- protocol-driven schedule generation works
- duplicate timepoints are prevented
- overdue detection is repeatable/idempotent
- tenant context is enforced
