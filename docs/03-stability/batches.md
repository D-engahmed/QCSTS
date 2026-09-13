# Batches

## Purpose

Represent manufacturing batches participating in stability studies.

## Rules

- batch belongs to one organization and site
- product must belong to same organization
- stability study must belong to same organization
- batch must not be attached to an archived organization

## Status

Draft -> Registered -> In Study -> Completed -> Archived.

Controlled exceptions may exist for Cancelled/Rejected.

## Existing compatibility

Preserve current batch functionality while migrating uniqueness constraints from global to organization/site-scoped rules.
