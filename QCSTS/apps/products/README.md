# Products — Pharmaceutical Master Data

## Purpose
The products app owns pharmaceutical product master data used by batches, specifications and stability studies.

## Responsibilities
- Product identity and metadata.
- Monographs and specifications where modeled.
- Test definitions used by QC workflows.
- Controlled master-data relationships.
- Tenant-scoped product access.

## Architecture
Product → Monograph/Specification/TestDefinition → Batch → Stability study.

Products define what is being tested. Execution belongs to stability, chamber and results.

## Security design
Products are tenant-owned. All access derives organization from server-side tenant context.

## Design principles
Avoid duplicating product data downstream. Preserve version references where a historical study depends on a specific specification. Treat controlled master data as more stable than execution records.

## Testing
Cover uniqueness, tenant isolation, relationships, version selection and RBAC.

## Design invariant
Master data defines the object and rules; execution records capture what happened.
