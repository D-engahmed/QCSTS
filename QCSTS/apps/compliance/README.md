# Compliance — Controlled Records, Signatures & Validation Evidence

## Purpose
The compliance app provides technical controls supporting regulated pharmaceutical workflows.

## Responsibilities
- Electronic signature records.
- Controlled-record metadata.
- Validation artifacts and evidence.
- Compliance-oriented workflow evidence.
- Links between evidence and source business records.

## Architecture
Business record → state transition → electronic signature/audit → controlled record or validation evidence.

Compliance is an evidence layer, not a replacement for domain models.

## Security design
Signatures bind an authenticated identity to a specific record/version/action. A signature is evidence of an action, not a boolean field.

## Validation posture
The system should be described as designed for GxP-regulated environments with a validation-ready architecture. Technical controls alone do not make a deployment compliant; validation, procedures and operational qualification remain deployment responsibilities.

## Testing
Cover signature authorization, record locking, tenant isolation, audit linkage and invalid state transitions.

## Design invariant
Compliance evidence must remain traceable to the exact business state and actor that produced it.
