# QCSTS Stability Studies

## Purpose
StabilityStudy is the primary operational unit for controlled stability work.

## Lifecycle
```text
Draft -> Pending Approval -> Approved -> Active -> Completed
  |          |
  +--------> Cancelled
```
Rejection/cancellation requires reason and audit evidence.

## Required data
- study_id
- organization/site
- product
- protocol_version
- study_type
- storage_condition
- chamber
- start/end dates
- status
- creator/approver
- description

## Creation rules
A study cannot reference a non-approved protocol version. A chamber must belong to the same site/organization and satisfy qualification policy.

## Schedule
The approved protocol version generates the study timepoints. Timepoints must record planned date, actual date, status, sample requirements, tests and assignment.

## Completion
A study can be completed only when required timepoints/tests are in valid terminal states or a controlled exception has been approved.

## Batch relationship
A study may contain one or more batches depending on protocol/business policy. Historical links must not be changed without controlled audit history.

## Operational dashboard
Study views should show active status, upcoming/overdue pulls, missing results, review queue, failures and chamber assignment.

## Acceptance criteria
1. Study creation is tenant scoped.
2. Protocol version is immutable once approved.
3. Schedule creation is deterministic and idempotent.
4. State transitions are authorized and audited.
5. Historical study state remains reproducible.
