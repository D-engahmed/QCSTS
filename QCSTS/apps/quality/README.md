# Quality — OOS, OOT, Deviations, CAPA & Change Control

## Purpose
The quality app manages investigations and corrective/preventive quality processes around laboratory and stability workflows.

## Responsibilities
- OOS records.
- OOT records.
- Deviations.
- CAPA.
- Change control.
- Quality workflow transitions and evidence.

## Architecture
Result/process event → Quality event → investigation → corrective/preventive action → approval/closure.

Quality records reference source evidence rather than replacing it.

## Workflow design
Quality entities use explicit states and controlled transition endpoints. Clients cannot jump directly to terminal states without backend validation and authorization.

## Security design
Quality data is tenant-scoped and often more sensitive than ordinary operational records. RBAC distinguishes creation, investigation, approval and closure.

## Testing
Test legal transitions, unauthorized transitions, cross-tenant isolation, source linkage and audit generation.

## Design invariant
A quality event explains and controls an exception; it does not erase the underlying result or audit history.
