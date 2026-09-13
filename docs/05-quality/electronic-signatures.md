# Electronic Signatures

## Purpose

Persist evidence that an authenticated user intentionally signed a defined action on a specific record version.

## Signature record

Required fields:
- signer
- organization
- signature meaning
- target object type/id
- target object version
- canonical content hash
- signed_at
- authentication/re-authentication evidence reference
- session/device context where policy allows

## Signature meanings

- Performed
- Reviewed
- Approved
- Rejected
- Verified

## Re-authentication

For regulated actions, require an explicit authentication step appropriate to the organization's policy. A transient cache token alone is insufficient as the long-term record.

## Non-reuse

A signature must be unique to its intended action and record version. It must not be replayable against another record.

## Acceptance criteria

1. signature is persisted
2. record hash/version is persisted
3. signature meaning is persisted
4. audit event exists
5. user cannot reuse signature evidence for another action
6. signature does not permit post-sign modification of the signed record
