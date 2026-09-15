# QCSTS Stability Domain v2

## Purpose

This document defines the commercial stability-domain model introduced after the SaaS foundation. It separates stable business identities from controlled versions so historical studies can be reconstructed without relying on mutable master data.

## Aggregate

```text
Organization
  └── Site
       └── StabilityStudy
            ├── Product
            ├── ProtocolVersion
            │    └── Protocol
            ├── StudyBatch
            │    └── Batch
            ├── StudyTimepoint
            └── StabilitySample
                 └── StorageCondition
```

## Controlled master data

### Protocol / ProtocolVersion

`Protocol` is the stable identity. `ProtocolVersion` is the controlled version that a study actually uses.

A study must reference `ProtocolVersion`, not an unversioned protocol. A new protocol revision therefore does not rewrite historical studies.

### Specification / SpecificationVersion

`Specification` is the stable identity. `SpecificationVersion` records the applicable controlled version. Results must eventually reference the exact specification version used for evaluation.

### StorageCondition

Storage conditions are organization-scoped controlled records rather than free-form strings. Temperature and relative-humidity ranges are stored as structured values.

## Study lifecycle

```text
DRAFT → PLANNED → ACTIVE → COMPLETED → CLOSED
                     └──────→ CANCELED
```

The lifecycle is intentionally explicit. Approval, effective dates, e-signatures and audit events are implemented in the controlled-workflow phase.

## Sample traceability

Every `StabilitySample` identifies:

- organization
- study
- enrolled batch
- study timepoint
- storage condition
- quantity
- chamber/location reference
- lifecycle status

The model prevents a sample from combining a study, enrollment or timepoint belonging to different studies.

## Tenant safety

Every new stability record inherits `BaseModel.organization` and validates related-object organization consistency on save. API serializers must still enforce tenant-scoped querysets; model guards are defense in depth, not a substitute for request authorization.

## Next implementation

1. Tenant-scoped serializers/viewsets for these models.
2. Protocol/specification approval and effective-state transitions.
3. Exact specification-version linkage on results.
4. Chamber foreign-key integration and environmental excursion workflow.
5. Pull/receipt/analysis sample events.
6. OOS/OOT classification.
7. Validation traceability from URS → FRS → tests.
