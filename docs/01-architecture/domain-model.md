# QCSTS Domain Model

## 1. Purpose

This document defines the canonical business objects and their relationships. It is the source of truth for database design, API resources and workflow implementation.

## 2. Core relationship

```text
Organization
  -> Site
  -> Product
      -> Monograph / Quality Definition
          -> Protocol
              -> ProtocolVersion
                  -> StabilityStudy
                      -> Batch
                          -> Timepoint
                              -> Sample
                                  -> TestAssignment
                                      -> Result
```

Quality controls attach to the workflow:

```text
Result -> Review -> Approval -> Signature
                    |
                    +-> OOS / OOT / Deviation when applicable
```

## 3. Organization

Fields:
- id
- name
- legal_name
- slug
- country
- timezone
- currency
- status
- timestamps

Invariants:
- slug globally unique
- archived organizations cannot create new operational records

## 4. Site

Fields:
- id
- organization
- name
- address
- country
- timezone
- status

Invariants:
- unique name within organization
- site belongs to exactly one organization

## 5. Product

Represents a pharmaceutical product under stability management.

Fields should include:
- id
- organization
- site or site scope as required
- product_code
- name
- dosage_form
- strength
- packaging
- status
- version/effective metadata where controlled

## 6. Protocol

Represents the logical stability protocol identity.

A protocol is versioned through ProtocolVersion rather than mutated in place.

## 7. ProtocolVersion

Defines an approved version of a protocol.

Fields:
- protocol
- version
- status
- effective_from
- effective_to
- study_type
- timepoint definitions
- storage conditions
- tests
- approval metadata
- content hash/snapshot

Immutable once approved.

## 8. StabilityStudy

Fields:
- study_id
- organization
- site
- product
- protocol_version
- study_type
- start_date
- status
- storage_condition
- chamber
- created_by
- approved_by
- description

Statuses:
Draft, Pending Approval, Approved, Active, Completed, Cancelled, Archived.

## 9. Batch

Represents a manufacturing lot under the study.

Fields:
- organization
- site
- product
- batch_number
- manufacturing_date
- expiry_date
- quantity
- study reference
- status

Batch numbering must be scoped according to business rules, never assumed globally unique without evidence.

## 10. Chamber

Fields:
- organization
- site
- identifier
- location
- capacity
- condition
- temperature target
- humidity target
- status
- calibration status
- qualification status

A chamber must not be treated as qualified merely because it exists.

## 11. Timepoint

A planned or executed study milestone.

Fields:
- study
- period/unit
- planned_date
- actual_date
- status
- required_tests
- required_samples
- assignee

## 12. Sample

First-class physical-sample record.

Lifecycle:
Created -> Stored -> Scheduled -> Pulled -> Received -> Testing -> Completed -> Archived.

Fields:
- sample_id
- study
- batch
- timepoint
- storage location
- quantity
- status
- custody metadata

## 13. Test

Logical laboratory test/parameter.

Examples:
- assay
- pH
- dissolution
- appearance

The test defines the parameter identity. Acceptance criteria are owned by SpecificationVersion.

## 14. Specification

Logical identity for acceptance criteria.

SpecificationVersion contains the effective rule set.

## 15. Result

Represents an immutable submitted observation.

Fields should include:
- id
- organization
- test_assignment
- observed_value
- normalized_value
- unit
- specification_version
- evaluation result
- calculation record
- submitted_by
- submitted_at
- record hash/version

## 16. Correction

A correction does not mutate the original result.

Model:

```text
Original Result
   |
   +--> CorrectionRequest
             |
             +--> Corrected/Superseding Result
```

## 17. Quality event

A common quality-event base may support:
- OOS
- OOT
- Deviation

Each event must reference the impacted study/batch/result where applicable.

## 18. Review and approval

Reviews are explicit historical records rather than booleans on a result.

```text
Result
 -> ReviewTask
 -> ReviewDecision
 -> ApprovalDecision
```

## 19. Signature

Signature is an independent historical record binding an actor to a specific object version and signature meaning.

## 20. AuditEvent

Append-only event describing who did what, when, where and to which object.

## 21. Report

A generated report references an immutable data snapshot/version and its stored artifact.

## 22. Mutability matrix

| Entity | Mutable? | Notes |
|---|---|---|
| Organization | Yes | controlled admin changes |
| Site | Yes | controlled |
| Product | Yes | historical versions where required |
| Protocol | limited | use versions |
| Approved ProtocolVersion | No | immutable |
| Study | controlled | state machine |
| Batch | controlled | audit changes |
| Timepoint | controlled | derived schedule + exceptions |
| Sample | controlled | custody history |
| Specification | limited | use versions |
| Approved SpecificationVersion | No | immutable |
| Submitted Result | No | correction/supersession only |
| Signature | No | append-only |
| AuditEvent | No | append-only |
| Report snapshot | No | immutable |

## 23. Referential integrity

Prefer `PROTECT` for regulated historical parents where deleting the parent would make records semantically invalid.

Soft delete may be used for operational records, but soft delete must not erase the audit/history trail.
