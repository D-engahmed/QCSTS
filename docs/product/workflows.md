# Controlled workflows

## Existing workflow

Product → approved monograph → batch → generated test points → pull → signed result → pass/fail → dashboard/print report.

This is a useful foundation, but it has no first-class study/protocol, QA review/approval, persistent signature record, controlled correction, or organization boundary.

## Target workflow

1. An authorized organization user creates controlled product/protocol/specification drafts.
2. QA approval freezes explicit protocol and specification versions.
3. An authorized user creates a study and linked batch under a site/chamber/condition.
4. The schedule engine derives required timepoints, samples and tests from the approved version.
5. A pull is recorded with chain-of-custody state and assigned laboratory work.
6. An analyst submits a result using a purpose-bound electronic signature. Deterministic evaluation records its inputs and outcome.
7. Supervisor and QA transitions occur through policies, signatures and audit events; prohibited self-approval is rejected.
8. Failed, OOS/OOT and deviation flows become controlled quality events.
9. A traceable immutable report snapshot is generated and stored through object storage.

At every step the UI answers what happened, what is due or overdue, who owns the next action and why a result failed.
