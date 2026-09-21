# QCSTS User Acceptance Testing (UAT)

## Entry criteria
- Release candidate identified.
- Clean PostgreSQL migrations pass.
- Backend and frontend release gates are green.
- Synthetic test data is isolated from production.
- Test users for each required role exist.

## Critical scenarios
1. Register a new organization and confirm owner, site and trial subscription creation.
2. Exercise login failures, throttling and lockout.
3. Request and complete password reset; verify token reuse is rejected.
4. Verify a new email; verify the token is single-use.
5. Create product, monograph, protocol and stability study.
6. Enroll a batch and create timepoints and samples.
7. Enter, submit, review and approve a result with electronic signature.
8. Attempt cross-tenant UUID access and confirm denial.
9. Create OOS, link a deviation, then link a CAPA.
10. Exercise subscription entitlement limits.
11. Process a Paymob test webhook and verify idempotency and amount/currency validation.
12. Export tenant-scoped data.
13. Back up, destroy, restore and verify the database.

## Evidence fields
Tester, timestamp, environment, test-data identifier, expected result, actual result, result, defect ID, evidence attachment.

## Exit criteria
All critical scenarios pass, release-blocking defects are closed, and the traceability matrix contains evidence references.
