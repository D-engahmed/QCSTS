# Results — Laboratory Measurements & Controlled Review

## Purpose
The results app owns laboratory measurements and their controlled review lifecycle.

## Core workflow
Draft → Submitted → Under review → Approved/Locked, with a controlled correction path.

## Responsibilities
- Result creation and validation.
- Test-point/result relationships.
- Review.
- Approval.
- Rejection/correction.
- Locking approved records.
- Audit and compliance integration.

## Architecture
Study/Sample/TestDefinition → Result → Review → Approval/Correction → Audit/Signature.

## Security design
Result ownership comes from tenant context. State-changing endpoints require explicit authorization. Locked results must not be mutable through generic update behavior.

## Integrity rules
Correction preserves the evidence trail rather than overwriting the original. Approval is a backend state transition, not a frontend convention.

## Testing
Cover state-machine transitions, locked-record mutation denial, tenant isolation, reviewer permissions, correction and audit events.

## Design invariant
A result is scientific data and controlled evidence; approved/locked history must remain reconstructable.
