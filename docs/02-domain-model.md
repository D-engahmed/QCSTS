# QCSTS Domain Model

## Canonical business graph
```text
Organization
  -> Site
  -> Product
      -> Protocol
          -> ProtocolVersion
              -> StabilityStudy
                  -> Batch
                      -> Timepoint
                          -> Sample
                              -> TestAssignment
                                  -> Result
                                      -> Review/Approval/Signature
```
Quality events attach to impacted objects: OOS, OOT and Deviations.

## Core entities

### Organization
Tenant boundary. Fields: id, name, legal_name, slug, country, timezone, currency, status, timestamps.

### Site
Physical/logical operational location. Belongs to one organization.

### Product
Pharmaceutical product under stability management. Tenant/site scoped.

### Protocol
Logical identity for stability procedure. Content lives in immutable approved versions.

### ProtocolVersion
Defines study type, timepoints, storage conditions, sample requirements, tests and acceptance-criteria references. Immutable after approval.

### StabilityStudy
Primary execution container. Fields: study_id, organization, site, product, protocol_version, study_type, storage_condition, chamber, dates, status, approvals.

### Batch
Manufacturing lot under study. Tenant/site/product scoped.

### Chamber
Controlled storage equipment with target conditions, capacity, calibration and qualification status.

### Timepoint
Planned/actual study milestone with required samples/tests and status.

### Sample
Physical sample with custody and location history. Lifecycle: Created -> Stored -> Scheduled -> Pulled -> Received -> Testing -> Completed -> Archived.

### Test
Logical laboratory parameter.

### Specification / SpecificationVersion
Acceptance-criteria identity and effective rule set.

### Result
Immutable submitted observation tied to exact test assignment and specification version.

### Review / Approval
Historical decisions on a defined record version.

### Signature
Persistent evidence of a signer performing a defined action on a specific record version.

### AuditEvent
Append-only historical action record.

### Report
Traceable generated artifact based on a defined data snapshot/version.

## Mutability
| Entity | Rule |
|---|---|
| Organization/Site/Product | Controlled mutable |
| Protocol | Versioned |
| Approved ProtocolVersion | Immutable |
| Study/Batch/Timepoint/Sample | Controlled state changes + audit |
| Specification | Versioned |
| Approved SpecificationVersion | Immutable |
| Submitted Result | Immutable; corrections create linked records |
| Signature | Immutable |
| AuditEvent | Immutable |
| Report Snapshot | Immutable |

## Referential integrity
Prefer `PROTECT` for historical parents where deletion would make historical records semantically invalid.
