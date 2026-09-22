# Stability — Core Pharmaceutical Stability Workflow

## Purpose
The stability app is the central scientific workflow domain for stability testing.

## Core model
Product → Specification/TestDefinition → Batch → Study → ProtocolVersion → Timepoint → Sample → Result → Review/Approval.

Chamber and pull records provide the physical storage/execution connection.

## Responsibilities
- Stability studies.
- Storage conditions.
- Protocols and protocol versions.
- Specifications and specification versions.
- Study-batch relationships.
- Timepoints.
- Samples and sample pulls.

## Versioning design
Controlled protocol and specification versions remain addressable so historical studies identify the rules under which they were executed.

## Security design
All stability records are tenant-scoped. Site context applies to facility execution. API views explicitly declare tenant posture and action authorization.

## Workflow integrity
A study should not silently switch protocol versions after execution begins. Timepoint/sample relationships preserve the chain from planned condition to measured evidence.

## Testing
Cover constraints, version selection, study lifecycle, tenant isolation, route posture, state transitions and integrations with batches/chambers/results.

## Design invariant
Stability is the scientific backbone; results, quality and compliance attach to it without duplicating the workflow.
