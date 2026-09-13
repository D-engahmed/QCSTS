# Tenant Isolation Verification

## Objective

Prove that multi-tenancy is not merely present in the schema but enforced in every execution path.

## Test matrix

For two organizations A and B, verify isolation for:
- organizations
- sites
- products
- monographs
- protocols
- studies
- batches
- chambers
- samples
- timepoints
- test assignments
- results
- reviews
- signatures
- audit events
- reports
- files
- notifications
- API keys
- webhooks
- subscriptions
- usage

## Execution paths

Test:
- list
- detail
- create
- update
- delete/archive
- export
- report generation
- search
- Celery tasks
- scheduled tasks
- webhook callbacks
- object storage access

## Expected result

Tenant A may only access records authorized for Tenant A.

Any violation is a release blocker.
