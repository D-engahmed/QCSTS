# Sites

## Purpose

A Site represents a physical or logical operational location within an organization.

## Rules

- every site belongs to exactly one organization
- names are unique within an organization
- site cannot be moved to another organization
- membership site scope must reference sites from the same organization

## API

```text
GET    /api/v1/sites/
POST   /api/v1/sites/
GET    /api/v1/sites/{id}/
PATCH  /api/v1/sites/{id}/
POST   /api/v1/sites/{id}/archive/
```

## Operational use

Sites scope:
- chambers
- studies
- batches
- users
- reports
- notifications where applicable

## Acceptance criteria

Cross-organization site access is impossible through API, exports and background tasks.
