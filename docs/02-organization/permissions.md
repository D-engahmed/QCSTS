# Permissions

## Purpose

Provide stable, centralized capability codes.

## Naming

Use:

```text
resource.action
```

Examples:

```text
study.view
study.create
study.approve
result.submit
result.review
result.approve
```

## Permission lifecycle

Permissions are platform-defined. Organizations assign them through roles.

Do not let arbitrary tenant admins create security capabilities.

## Acceptance criteria

- permissions have immutable codes
- permissions are documented
- unknown permission checks deny access
- permission changes are audited through role changes
