# QCSTS Protocol Versioning

## Purpose
Ensure every stability study can be reconstructed against the exact procedure that governed it.

## Structure
```text
Protocol
  ├── v1.0
  ├── v1.1
  └── v2.0
```

## Version contents
- study type
- storage conditions
- timepoints
- sample requirements
- test assignments
- acceptance-criteria references
- scheduling rules
- effective dates
- approval metadata
- canonical content snapshot/hash

## Lifecycle
Draft -> Pending Review -> Approved -> Effective -> Retired.

## Immutability
Approved/effective versions cannot be edited. Changes create a new version.

## Historical binding
A StabilityStudy references the exact ProtocolVersion. Later changes must not alter historical study behavior.

## Approval
Approval is a persisted decision with signer and timestamp.

## Migration from current system
Existing monograph/test workflow remains supported while protocol entities are introduced. Current approved monograph definitions must be mapped into an initial protocol/version representation without losing history.

## Acceptance criteria
- old versions remain readable
- approved versions are immutable
- new versions have unique version identifiers
- study schedule generation references exact version
- approval/retirement is audited
