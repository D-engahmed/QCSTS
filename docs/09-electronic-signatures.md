# QCSTS Electronic Signatures

## Purpose
Persist evidence that an authenticated person intentionally signed a defined action on a specific record version.

## Signature record
Required fields:
- signer
- organization
- signature meaning
- target object type/id
- target version
- canonical content hash
- signed_at
- authentication/re-authentication evidence reference
- request/session context where policy allows

## Signature meanings
Performed, Reviewed, Approved, Rejected, Verified.

## Signing flow
```text
Authorized action
 -> re-authentication
 -> load exact object version
 -> compute canonical hash
 -> persist signature + action atomically
 -> persist audit event
```

## Non-reuse
A signature is scoped to one action/object/version and cannot be replayed for another target.

## Immutability
The signed record version becomes immutable for that workflow. A later correction creates a new controlled record/version.

## Security
Do not log passwords or signature secrets. Protect signing endpoints with rate limits and appropriate re-authentication.

## Acceptance criteria
- persisted signer and meaning
- persisted target version/hash
- timestamp from trusted server clock
- audit linkage
- no signature replay
- no post-sign mutation of signed content
