# QCSTS SaaS Gap Closure

## Objective

Transform QCSTS from a stability workflow application into a commercially deployable, multi-tenant pharmaceutical SaaS platform.

## Non-negotiable product invariant

```text
Authenticated User
    -> Organization Membership
    -> Role / Permission
    -> Site Scope
    -> Tenant-owned Resource
    -> Business Workflow
    -> Audit Evidence
```

No tenant-owned resource may be read, created, updated, deleted, approved, or referenced through another organization's scope.

## Delivery order

### Phase 1 — SaaS security foundation

- [x] Organization model
- [x] Site model
- [x] Membership model
- [x] Organization-scoped roles and permissions
- [x] Tenant-scoped serializer primitives
- [ ] Make organization mandatory on all tenant-owned legacy records
- [ ] Enforce tenant filtering on every list/retrieve endpoint
- [ ] Enforce tenant scope on every writable foreign key
- [ ] Enforce site scope where the resource is site-owned
- [ ] Remove `CustomUser.role` as an authorization source
- [ ] Add authorization matrix tests
- [ ] Add cross-tenant read/write/delete tests for every domain app

### Phase 2 — SaaS commercial foundation

- [x] Plan model
- [x] Subscription lifecycle model
- [x] Invoice model
- [x] Payment-event idempotency model
- [x] Usage tracking model
- [x] Central entitlement service
- [x] Standard Essential / Professional / Enterprise seed plans
- [ ] Customer-facing billing API
- [ ] Payment-provider adapter
- [ ] Webhook verification and replay protection
- [ ] Subscription suspension enforcement
- [ ] Trial lifecycle
- [ ] Invoice history API
- [ ] Usage-limit enforcement in domain services

### Phase 3 — Stability domain v2

- [ ] StabilityStudy
- [ ] Protocol
- [ ] ProtocolVersion
- [ ] Specification
- [ ] SpecificationVersion
- [ ] StorageCondition
- [ ] Batch-to-study relationship
- [ ] Sample lifecycle
- [ ] Pull lifecycle
- [ ] TestRequirement
- [ ] Result review workflow
- [ ] Approval workflow
- [ ] Historical specification snapshots

### Phase 4 — Data integrity and validation

- [ ] Immutable audit verification tests
- [ ] Full electronic-signature semantics
- [ ] Record version history
- [ ] Record locking after approval
- [ ] Reason-for-change enforcement
- [ ] Controlled master-data lifecycle
- [ ] URS
- [ ] FRS
- [ ] Risk assessment
- [ ] Traceability matrix
- [ ] IQ/OQ/PQ package
- [ ] Validation summary

### Phase 5 — Quality expansion

- [ ] OOS
- [ ] OOT
- [ ] Deviation
- [ ] Investigation
- [ ] CAPA
- [ ] Change Control
- [ ] Risk Management

### Phase 6 — Enterprise

- [ ] SSO
- [ ] SCIM
- [ ] API keys / service accounts
- [ ] Webhooks
- [ ] LIMS integration
- [ ] ERP integration
- [ ] Multi-site analytics
- [ ] SLA / support tiers
- [ ] Customer security questionnaire package

### Phase 7 — Intelligence

- [ ] Stability trend analytics
- [ ] Anomaly detection
- [ ] OOS investigation assistance
- [ ] Study risk scoring
- [ ] Natural-language analytics
- [ ] Forecasting

## Commercial baseline

| Plan | Monthly | Annual | Users | Sites | Studies | API |
|---|---:|---:|---:|---:|---:|---|
| Essential | $399 | $3,990 | 15 | 1 | 100 | No |
| Professional | $899 | $8,990 | 50 | 3 | 1,000 | Yes |
| Enterprise | $2,000+ | $24,000+ | Custom | Custom | Custom | Yes |

Prices are commercial starting points, not regulatory or market guarantees. Enterprise is custom-priced according to sites, validation, migration, integrations, SLA and deployment requirements.

## Commercial services

- Onboarding: starting at $1,000
- Implementation: starting at $3,000
- Validation package: starting at $4,000
- Data migration: starting at $2,000
- LIMS/ERP integration: starting at $5,000
- Enterprise implementation: custom

## Compliance positioning

Do not market QCSTS as universally `21 CFR Part 11 compliant` or universally `GMP compliant` merely because the application implements authentication, audit trails, or electronic signatures.

Preferred positioning until a deployment is formally validated:

> Designed for GxP-regulated environments with controls supporting electronic records, electronic signatures, audit trails, access control and data integrity.

After customer-specific validation, market the validated deployment and intended use, not an unqualified universal compliance claim.

## Definition of SaaS-ready

QCSTS reaches the first commercial milestone when a customer can:

1. create an organization;
2. create one or more sites;
3. invite users;
4. assign organization/site-scoped roles;
5. subscribe to a plan;
6. have plan entitlements enforced server-side;
7. create and execute a stability study;
8. record and review results;
9. approve controlled records with traceable signatures;
10. reconstruct the record history from audit evidence; and
11. export the organization's data without exposing another tenant.

That milestone comes before CAPA, AI, or a large integration catalog.
