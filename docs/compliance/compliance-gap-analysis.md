# Compliance gap analysis

QCSTS currently has helpful controls—timestamps, creator references, result snapshots, soft deletion and ORM-level immutability—but these are a foundation, not proof of validated compliance or certification.

| Area | Current state | Required direction |
| --- | --- | --- |
| Audit | ORM immutability and partial events | transactional event coverage, database protection, reason/where/tenant, retention/export evidence |
| Electronic signatures | password-gated temporary token | persistent meaning, signer, timestamp, session/re-authentication evidence, record hash/version, non-reuse and audit |
| Results | create-only ORM result and text snapshot | controlled correction/supersession, review states, versioned specifications and deterministic calculations |
| Definitions | monograph approval | versioned protocols/specifications with effective periods and immutable approved versions |
| Authorization | global role strings | tenant/site permissions and separation of duties |
| Records/reports | frontend export/print | traceable server-generated report version/artifact/signature context |
| Operations | local Compose baseline | validation plan, change control, access review, backup/restore, incident and DR procedures |

Do not describe the application as GMP compliant, 21 CFR Part 11 compliant/certified, FDA approved, or validated. The correct positioning is that it is being architected to support controlled regulated workflows and customer validation activities.
