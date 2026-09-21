# QCSTS Functional Requirements Specification (FRS)

## Tenant security
FRS-001: Organization-scoped queries SHALL use the authenticated tenant context.
FRS-002: Direct object access by UUID SHALL NOT bypass tenant authorization.
FRS-003: Server-side authorization SHALL remain authoritative.

## Authentication
FRS-010: Login SHALL throttle repeated attempts and avoid user enumeration.
FRS-011: Password reset SHALL use an expiring, invalidatable token.
FRS-012: Email verification SHALL use a hashed, single-use token.
FRS-013: Security-sensitive events SHALL be auditable.

## Stability
FRS-020: A study SHALL reference an organization-owned site, product and protocol version.
FRS-021: A study batch SHALL reference a compatible batch.
FRS-022: A sample SHALL reference the same study through enrollment and timepoint.
FRS-023: Results SHALL preserve the applicable specification snapshot.

## Quality
FRS-030: OOS SHALL reference the source test result.
FRS-031: A deviation MAY reference an OOS investigation.
FRS-032: A CAPA MAY reference a deviation.
FRS-033: Lifecycle transitions SHALL be controlled and audited.
FRS-034: Approval and closure SHALL require electronic-signature authentication.

## Billing
FRS-040: Payment webhooks SHALL validate authenticity, amount and currency.
FRS-041: Duplicate payment events SHALL be idempotent.
FRS-042: Subscription state SHALL drive entitlement enforcement.

## Recovery
FRS-050: Application health checks SHALL be available.
FRS-051: Database backup SHALL be restorable into a clean PostgreSQL instance.
FRS-052: Release CI SHALL validate migrations before tests and packaging.
