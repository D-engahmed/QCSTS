# Chamber — Stability Storage & Sample Pull Operations

## Purpose
The chamber app manages controlled stability chambers, storage locations and sample pull/movement operations.

## Responsibilities
- Register and manage chambers.
- Track storage conditions and operational state.
- Record sample placement and movement.
- Schedule and execute pulls.
- Preserve traceability between samples and storage history.

## Architecture
Study/Sample → Chamber → Storage condition + Pull/Movement events.

The chamber domain represents physical execution context. Scientific protocol definition remains in stability.

## Security design
Chambers and pulls are tenant-scoped and site-aware. Historical movement should not be silently rewritten.

## Integrity rules
A movement records source/destination and actor where applicable. Pull operations should be attributable and auditable.

## Testing
Cover CRUD, tenant/site isolation, valid transitions, sample references, scheduling and cross-tenant negative cases.

## Design invariant
Chamber records where controlled material resides and when it is pulled; it does not define the scientific protocol.
