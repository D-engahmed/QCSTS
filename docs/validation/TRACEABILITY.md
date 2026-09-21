# QCSTS Requirements Traceability Matrix

| Requirement | Implementation area | Verification |
|---|---|---|
| URS-001 | core tenant-scoped views/models | tenant isolation tests |
| URS-003 | apps/accounts | auth and recovery tests |
| URS-005 | apps/stability, apps/schedule, apps/results | stability and result tests |
| URS-006 | apps/results | result immutability tests |
| URS-007 | apps/results, apps/quality, apps/compliance | lifecycle/signature tests |
| URS-008 | apps/quality | OOS/deviation/CAPA linkage tests |
| URS-009 | apps/billing | billing entitlement tests |
| URS-010 | apps/audit and audit service | audit tests |
| URS-011 | docker backup/restore workflows | recovery CI |
| URS-012 | docs/validation and UAT | executed evidence |

## Verification rule
Implementation presence is not verification. Every critical requirement needs an executable test, inspection record, or approved UAT evidence.
