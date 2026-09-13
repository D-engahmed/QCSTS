# Protocol Versioning

## Version lifecycle

Draft -> Pending Review -> Approved -> Effective -> Retired.

Approved and effective versions are immutable.

## Version identity

Use a semantic or organization-defined version identifier, but enforce uniqueness within the protocol.

Store:
- version identifier
- content snapshot
- canonical hash
- effective dates
- approval metadata

## Historical guarantee

A study must retain the exact approved ProtocolVersion used when it was created/approved.

Changing the current protocol must never retroactively change a study.

## Acceptance criteria

1. old versions remain readable
2. approved versions cannot be modified
3. new changes create new versions
4. audit captures approval/retirement events
