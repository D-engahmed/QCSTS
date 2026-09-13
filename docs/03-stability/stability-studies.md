# Stability Studies

## Purpose

A StabilityStudy is the primary operational container for stability work.

## Required fields

- study_id
- organization
- site
- product
- protocol_version
- study_type
- storage_condition
- chamber
- start_date
- status
- description
- created_by
- approved_by
- timestamps

## Status machine

```text
Draft
  -> Pending Approval
  -> Approved
  -> Active
  -> Completed

Draft -> Cancelled
Pending Approval -> Rejected/Cancelled
Approved -> Cancelled (controlled)
Active -> Cancelled (controlled)
```

## Rules

- approved study protocol version cannot be changed in place
- study cannot become active without required approvals
- study completion requires all required timepoints/tests in acceptable terminal state
- cancellation requires reason

## Acceptance criteria

A user can create, review, activate and complete a study without bypassing protocol/version and tenant controls.
