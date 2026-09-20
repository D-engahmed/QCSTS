# QCSTS Wave 4 — Final Release Gate

## Purpose

Wave 3 established the production engineering foundation. Wave 4 turns the remaining release risks into explicit, testable gates.

This document is intentionally stricter than a feature checklist. A model, endpoint, or merged PR is not evidence that the corresponding production requirement is complete.

## Release blockers

The following must have executable evidence before a customer production release:

1. **Billing enforcement**
   - Subscription state is authoritative.
   - Entitlements are enforced server-side.
   - Limits are tested at the API boundary.
   - Suspended/canceled tenants cannot continue consuming protected resources.

2. **Payment verification**
   - Paymob callbacks/webhooks are authenticated.
   - Processing is idempotent.
   - Duplicate, invalid, stale, wrong-amount, and unknown-transaction events are rejected safely.
   - Payment state and subscription state cannot diverge silently.

3. **End-to-end workflow**
   - Registration → product → monograph → batch → study → enrollment → timepoint/sample → result → review → QA approval → signature → lock → report.
   - The workflow must execute against real PostgreSQL and the real frontend/API contracts.

4. **Tenant-security regression**
   - Cross-organization read/write/delete attempts are denied.
   - Site boundary violations are denied.
   - UUID guessing cannot bypass tenant scope.
   - Inactive memberships and unauthorized roles fail closed.

5. **Backup and restore**
   - PostgreSQL backup is automated.
   - Restore is executed on a clean environment.
   - Restored data passes integrity checks.
   - RPO and RTO are documented and measured.

6. **Deployment verification**
   - Production Compose validates.
   - Images build reproducibly.
   - Migration and static-asset gates execute before application traffic.
   - Health/readiness checks pass.
   - TLS is terminated at the deployment boundary.
   - Rollback procedure is exercised.

7. **Validation/UAT**
   - Requirements are mapped to tests.
   - Critical workflows have approved acceptance criteria.
   - Deviations are recorded and dispositioned.
   - Customer-specific validation remains separate from product engineering claims.

## Current implementation gate

The repository now contains an additional GitHub Actions workflow, `.github/workflows/final-release-gate.yml`, that requires:

- PostgreSQL-backed Django checks and tests
- migration drift detection
- deployment checks
- pip dependency integrity
- frontend typecheck
- frontend production build
- production Compose configuration validation
- production image build validation

This gate does **not** falsely mark billing, Paymob, backup/restore, E2E, or customer validation as complete. Those require domain-specific evidence.

## Definition of done

QCSTS is ready for a controlled production pilot only when every blocker above has an executable verification record.

QCSTS must not be described as GMP/Part 11 compliant merely because the software contains audit trails, electronic signatures, controlled records, or related workflows.
