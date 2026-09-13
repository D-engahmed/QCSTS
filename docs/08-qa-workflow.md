# QCSTS QA Workflow

## Objective
Provide controlled review and approval of laboratory/stability records.

## Default workflow
```text
Analyst -> Submit Result
       -> Supervisor Review
       -> QA Review
       -> Approve / Reject
```
The exact stages may be configurable by organization policy, but regulated transitions must remain explicit and auditable.

## Result states
Prepared -> Submitted -> Under Review -> Approved / Rejected -> Superseded.

## Review record
Capture reviewer, organization/site, timestamp, decision, comments/reason, target record/version and signature reference.

## Rejection
Rejection retains the original submission. Rework is represented as a new controlled state or correction workflow.

## Self-approval
Default policy disallows prohibited self-approval.

## Quality events
A failed result may create or link to OOS. An in-specification but suspicious trend may create OOT. Execution deviations create Deviation records.

## Study approval
Study/protocol approval must verify tenant/site scope, required data, protocol version and authorized approver.

## Acceptance criteria
1. No unauthorized state transition is possible through API.
2. Every approval has persistent evidence.
3. Rejected records remain historical.
4. Self-approval policy is enforced server-side.
5. Workflow decisions are tenant isolated and auditable.
