# QCSTS Release Readiness Audit

Date: 2026-09-22

## Executive result

Repository-level engineering completeness: **85%**.

This is a weighted engineering assessment, not a claim that the application is 85% validated for regulated production. Runtime evidence is currently incomplete because the audited branch has no GitHub Actions workflow runs yet.

## Scorecard

| Area | Score | Main evidence / remaining gap |
|---|---:|---|
| Domain architecture | 88% | Broad domain decomposition is implemented; some workflows still need full end-to-end evidence |
| Tenant isolation | 91% | Tenant-aware base classes and route coverage exist; deployed negative testing still required |
| RBAC | 90% | Membership → Role → Permission exists; complete action matrix needs continuous regression coverage |
| Authentication | 88% | JWT, throttling, recovery, verification and MFA exist; external email delivery and production secret rotation need evidence |
| Stability workflow | 86% | Study/protocol/version/timepoint/sample chain exists; full scientific/UAT workflow needs evidence |
| Results workflow | 86% | Review/approval/locking architecture exists; complete E2E evidence remains |
| Quality | 82% | OOS/OOT/deviation/CAPA/change-control domains exist; full transition/E2E evidence remains |
| Billing | 84% | Subscription/trial/usage/entitlements and Paymob controls exist; live payment verification remains external |
| Audit | 90% | Audit service and PostgreSQL immutability protection exist; production restore/evidence verification remains |
| Compliance | 80% | Signature/controlled-record/validation structures exist; formal validation package is not code-complete |
| Reporting | 82% | Dashboard/export surfaces exist; large-scale performance and export authorization need runtime evidence |
| Frontend | 84% | Public/authenticated surfaces and API integration exist; complete browser E2E is still required |
| CI/CD | 91% | Production and release gate workflows exist; current audit branch has no executed run |
| Operations/DR | 76% | Backup/restore workflow exists; real deployment, monitoring, alerting and DR exercise remain |
| Documentation | 92% | Root architecture, frontend architecture and all 14 app READMEs are now documented |
| Validation/UAT | 65% | Requires organization-specific validation evidence, SOPs, qualification and UAT |

## Overall interpretation

The project is not honestly describable as 100% complete today.

The codebase is substantially beyond a prototype, but the missing percentage is concentrated in **evidence**, not simply missing CRUD screens.

## Remaining blockers

### 1. CI has not executed for the current audit branch
The branch was opened as PR #79, but GitHub currently reports zero Actions workflow runs for the branch and no status checks on the latest commit.

This means it would be incorrect to claim that typecheck, build, pytest and release gates passed after these changes.

### 2. Browser E2E evidence
The repository has route smoke checks, but regulated workflow confidence needs full browser scenarios:
- register tenant;
- verify email;
- sign in;
- MFA;
- create product/batch/study;
- execute timepoint/sample/result;
- review/approve/lock;
- create quality event;
- inspect audit evidence;
- verify tenant B cannot access tenant A.

### 3. Production environment evidence
The production compose/build path exists, but the actual deployed environment still needs:
- TLS termination;
- real secret management;
- database backup schedule;
- restore drill;
- monitoring;
- alerting;
- log retention;
- worker health monitoring;
- deployment rollback verification.

### 4. Payment evidence
Paymob integration needs a real sandbox verification cycle covering:
- valid callback;
- invalid HMAC;
- wrong amount;
- wrong currency;
- duplicate callback;
- out-of-order callback;
- canceled/past_due recovery.

### 5. Validation/UAT
The software can provide validation-ready technical controls, but a real regulated deployment also requires:
- requirements traceability;
- risk assessment;
- SOPs;
- IQ/OQ/PQ or the organization's chosen qualification approach;
- UAT;
- change control;
- access review;
- backup/restore evidence;
- audit review procedures.

## Documentation added

Every backend app now contains a README:

accounts, audit, batches, billing, chamber, compliance, notifications, platform, products, quality, reports, results, schedule and stability.

Each document covers purpose, responsibilities, architecture, security design, testing and design invariants.

## Release rule

Do not merge PR #79 solely because the code exists.

Merge only after the repository's release gates execute successfully and the remaining operational evidence is recorded.
