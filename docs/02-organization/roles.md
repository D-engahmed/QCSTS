# Roles

## Purpose

Roles group permissions for organization users.

## System roles

- Owner
- Organization Admin
- QA Manager
- QC Manager
- Supervisor
- Analyst
- Read Only
- Service Account

## Custom roles

Organizations may clone or create custom roles from allowed permission templates.

System-protected permissions must not be granted to custom roles unless explicitly permitted by product policy.

## Role versioning

Changes to role membership affect future authorization. Historical audit records retain the actor and effective time; they do not rewrite past decisions.

## Acceptance criteria

- role names unique within organization
- role permission changes audited
- deleting a role with active memberships is prevented or requires reassignment
