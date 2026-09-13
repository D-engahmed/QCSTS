# QA Workflow

## Objective

Provide explicit review and approval states with separation of duties.

## Standard result workflow

```text
Analyst
  -> Submit
Supervisor
  -> Review
QA
  -> Approve / Reject
```

## Review record

Store:
- reviewer
- timestamp
- decision
- comments/reason
- object version
- signature reference where required

## Rejection

Rejected records are retained. Rework creates a new controlled state or correction workflow.

## Self-approval

Default policy prevents a user from approving their own regulated submission when separation of duties is required.

## Acceptance criteria

Every approval is attributable and reconstructable from persisted records.
