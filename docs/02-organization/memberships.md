# Memberships

## Purpose

Membership is the authorization link between a global user identity and an organization.

## Fields

- user
- organization
- role
- allowed sites
- default site
- active status
- timestamps

## Rules

- one active membership record per user/organization identity
- role must belong to the same organization or be a system role
- default site must belong to organization and membership scope
- inactive membership grants no access

## Invitation lifecycle

Pending -> Accepted -> Active -> Suspended/Removed.

Invitation tokens must be:
- single-use
- expiring
- non-guessable
- never stored in plaintext if persistent storage is used

## Acceptance criteria

- user can accept invitation only once
- deactivated membership immediately blocks API authorization
- membership changes are audited
