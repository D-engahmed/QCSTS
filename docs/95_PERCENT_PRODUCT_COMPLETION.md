# QCSTS 95% Product Completion Standard

## Purpose

QCSTS is considered commercially mature only when every major product area reaches at least 95% implementation, test coverage, workflow completeness, and operational readiness. The remaining 5% is reserved for customer-specific configuration, future integrations, and continuous improvement.

## Global Definition of 95%

An area is **95% complete** only when all applicable conditions are true:

1. Domain model exists and is tenant-aware.
2. Django API exists with validation and authorization.
3. Frontend workflow exists and uses the real API.
4. Happy path is implemented end-to-end.
5. Failure, empty, loading, and permission states exist.
6. Audit events exist for controlled changes.
7. Automated tests cover security and critical behavior.
8. Documentation exists.
9. Observability exists for production-critical failures.
10. No critical business rule is enforced only in the browser.

A visual mockup, placeholder page, or demonstration record does **not** count as implementation.

---

## 1. Frontend / UI — 95%

- [x] Professional SaaS shell
- [x] Command Center
- [x] Stability workspace
- [x] Study workspace
- [x] Master-data workspace
- [x] Quality workspace
- [x] Administration workspace
- [x] Billing workspace
- [x] Analytics workspace
- [ ] Real API integration for every page
- [ ] Authentication integration
- [ ] Organization switcher backed by API
- [ ] Site switcher backed by API
- [ ] Permission-aware navigation
- [ ] Loading/error/empty/forbidden states on every workflow
- [ ] Accessibility review
- [ ] Responsive QA
- [ ] Frontend integration tests
- [ ] Production performance pass

## 2. Multi-tenancy — 95%

- [x] Organization model
- [x] Site model
- [x] Membership model
- [x] Organization-aware domain foundation
- [ ] Mandatory organization ownership for every tenant record
- [ ] Central tenant context
- [ ] Tenant-scoped querysets
- [ ] Tenant-scoped create/update/delete
- [ ] Site-level data isolation
- [ ] Cross-tenant reference prevention
- [ ] Cross-tenant enumeration prevention
- [ ] Cross-tenant API security tests
- [ ] Organization export
- [ ] Organization archive/deletion workflow

## 3. Authentication — 95%

- [ ] Production login
- [ ] Session management
- [ ] Logout everywhere
- [ ] Password recovery
- [ ] Email verification
- [ ] MFA
- [ ] Session revocation
- [ ] Security event logging
- [ ] Login throttling / abuse protection
- [ ] Authentication tests
- [ ] Optional enterprise SSO foundation

## 4. Authorization / RBAC — 95%

- [x] Membership → Role → Permission foundation
- [ ] Membership role becomes sole authority
- [ ] Legacy user-role authority removed
- [ ] Organization authorization
- [ ] Site authorization
- [ ] Object authorization
- [ ] Permission matrix
- [ ] Permission-aware APIs
- [ ] Permission-aware frontend
- [ ] Negative authorization tests
- [ ] Privilege escalation tests

## 5. Billing — 95%

- [x] Plan model
- [x] Subscription foundation
- [x] Invoice/payment foundation
- [x] Entitlement foundation
- [ ] Production payment provider
- [ ] Signed webhook verification
- [ ] Webhook idempotency
- [ ] Trial lifecycle
- [ ] Upgrade
- [ ] Downgrade
- [ ] Cancellation
- [ ] Past-due handling
- [ ] Suspension
- [ ] Refund handling
- [ ] Invoice reconciliation
- [ ] Billing audit trail
- [ ] Billing integration tests

## 6. Entitlements / Usage — 95%

- [x] Entitlement model/service foundation
- [ ] Central entitlement checks
- [ ] User limits
- [ ] Site limits
- [ ] Study limits
- [ ] Storage limits
- [ ] API limits
- [ ] Usage aggregation
- [ ] Usage dashboard
- [ ] Enforcement tests
- [ ] Grace-period behavior

## 7. Stability Domain — 95%

- [x] StabilityStudy
- [x] Protocol
- [x] ProtocolVersion
- [x] Specification
- [x] SpecificationVersion
- [x] StudyBatch
- [x] StudyTimepoint
- [x] StabilitySample
- [x] StorageCondition
- [ ] Complete study lifecycle
- [ ] Study approval
- [ ] Effective/superseded rules
- [ ] Controlled study revision
- [ ] Execution workflow
- [ ] Historical reconstruction tests

## 8. Protocol Management — 95%

- [x] Protocol model
- [x] Version model
- [ ] Draft/review/approval workflow
- [ ] Effective version enforcement
- [ ] Superseding workflow
- [ ] Controlled revision
- [ ] Audit history
- [ ] E-signature integration
- [ ] API + UI integration tests

## 9. Specification Management — 95%

- [x] Specification model
- [x] SpecificationVersion model
- [ ] Parameter-level controlled records
- [ ] Version approval
- [ ] Effective version enforcement
- [ ] Superseding workflow
- [ ] Historical result binding
- [ ] Audit history
- [ ] E-signature integration

## 10. Sample Workflow — 95%

- [x] Sample model foundation
- [ ] Planned state
- [ ] Pull event
- [ ] Receipt event
- [ ] Testing state
- [ ] Completion state
- [ ] Retention/disposal
- [ ] Chain of custody
- [ ] Location tracking
- [ ] Audit events
- [ ] Exception handling
- [ ] API/UI tests

## 11. Timepoint Workflow — 95%

- [x] Timepoint model foundation
- [ ] Scheduled state
- [ ] Due state
- [ ] Completed state
- [ ] Missed/overdue state
- [ ] Rescheduling control
- [ ] Pull generation
- [ ] Notifications
- [ ] Audit trail
- [ ] Study impact handling

## 12. Result Workflow — 95%

- [ ] Result entry API
- [ ] Result validation
- [ ] Unit/method validation
- [ ] Specification evaluation
- [ ] Draft result
- [ ] Review
- [ ] QA review
- [ ] Approval
- [ ] Lock
- [ ] Controlled correction
- [ ] Historical versioning
- [ ] Audit coverage

## 13. QA Approval — 95%

- [ ] Review queue
- [ ] Reviewer assignment
- [ ] Review decision
- [ ] Comments/reason
- [ ] E-signature
- [ ] Approval audit event
- [ ] Rejection/rework
- [ ] Final lock
- [ ] Approval tests

## 14. Record Locking — 95%

- [ ] Server-side lock enforcement
- [ ] Locked object protection
- [ ] Locked API rejection
- [ ] Controlled correction workflow
- [ ] Version creation
- [ ] Audit trail
- [ ] Lock tests

## 15. Chamber Management — 95%

- [ ] Chamber CRUD
- [ ] Site ownership
- [ ] Qualification status
- [ ] Calibration status
- [ ] Capacity
- [ ] Conditions
- [ ] Monitoring integration boundary
- [ ] Excursions
- [ ] Affected-study detection
- [ ] Deviation integration

## 16. Audit Trail — 95%

- [x] Audit foundation
- [ ] Complete actor context
- [ ] Organization/site context
- [ ] Before/after values
- [ ] Reason-for-change
- [ ] Immutable enforcement
- [ ] Tamper detection
- [ ] Audit export
- [ ] Audit filtering
- [ ] Security tests

## 17. E-signatures — 95%

- [ ] Signer identity
- [ ] Record identity
- [ ] Record version
- [ ] Signature meaning
- [ ] Timestamp
- [ ] Authentication event
- [ ] Reason where required
- [ ] Signature verification
- [ ] Signature audit
- [ ] Non-repudiation controls
- [ ] Test coverage

## 18. OOS / OOT — 95%

- [ ] Automatic OOS detection
- [ ] OOT/trend detection workflow
- [ ] Investigation record
- [ ] Phase I investigation
- [ ] Phase II investigation
- [ ] Root cause
- [ ] Impact assessment
- [ ] Disposition
- [ ] CAPA/deviation linkage
- [ ] QA approval
- [ ] Audit/e-signature
- [ ] Reporting

## 19. Deviations — 95%

- [ ] Deviation record
- [ ] Classification
- [ ] Severity
- [ ] Investigation
- [ ] Root cause
- [ ] Impact assessment
- [ ] Actions
- [ ] CAPA linkage
- [ ] QA approval
- [ ] Closure
- [ ] Audit/e-signature

## 20. CAPA — 95%

- [ ] CAPA record
- [ ] Corrective action
- [ ] Preventive action
- [ ] Owner
- [ ] Due date
- [ ] Risk linkage
- [ ] Effectiveness check
- [ ] QA approval
- [ ] Closure
- [ ] Audit/e-signature

## 21. Organization Administration — 95%

- [ ] Organization profile
- [ ] Legal information
- [ ] Sites
- [ ] Members
- [ ] Invitations
- [ ] Membership lifecycle
- [ ] Security settings
- [ ] Data export
- [ ] Archive/deletion
- [ ] Billing access
- [ ] Organization audit

## 22. RBAC Administration — 95%

- [ ] Role CRUD
- [ ] Permission assignment
- [ ] Membership assignment
- [ ] Site assignment
- [ ] Role hierarchy rules where required
- [ ] Privilege escalation protection
- [ ] Authorization matrix tests
- [ ] Audit of permission changes

## 23. Analytics — 95%

- [ ] Executive dashboard
- [ ] Stability portfolio
- [ ] Timepoint performance
- [ ] Sample throughput
- [ ] Result trends
- [ ] OOS/OOT trends
- [ ] Deviation/CAPA trends
- [ ] Chamber utilization
- [ ] Site comparison
- [ ] Exportable reports
- [ ] Tenant-safe analytics queries

## 24. Validation — 95%

- [ ] URS
- [ ] FRS
- [ ] Risk assessment
- [ ] Traceability matrix
- [ ] IQ
- [ ] OQ
- [ ] PQ
- [ ] Validation summary
- [ ] Test evidence storage
- [ ] Controlled validation versions
- [ ] Customer validation package template

## 25. Integrations — 95%

- [ ] Stable versioned API
- [ ] API authentication
- [ ] API authorization
- [ ] Idempotency
- [ ] Rate limiting
- [ ] Webhooks
- [ ] Webhook signatures
- [ ] LIMS integration boundary
- [ ] ERP/SAP integration boundary
- [ ] Instrument integration boundary
- [ ] SSO/SCIM enterprise boundary

## 26. Production Infrastructure — 95%

- [ ] Production cloud deployment
- [ ] Managed PostgreSQL
- [ ] Redis
- [ ] Worker infrastructure
- [ ] Object storage
- [ ] Secrets management
- [ ] CI/CD
- [ ] Security scanning
- [ ] Central logging
- [ ] Metrics
- [ ] Alerting
- [ ] Database backups
- [ ] Restore testing
- [ ] Disaster recovery
- [ ] Incident response
- [ ] Capacity/performance testing

## 27. AI — 95% of the *planned AI layer*

AI is intentionally last. 95% here means the AI layer is productionized after the underlying QCSTS data and workflows are trustworthy.

- [ ] Governed AI architecture
- [ ] Tenant-safe retrieval
- [ ] Permission-aware retrieval
- [ ] Stability trend analysis
- [ ] OOS investigation assistant
- [ ] OOT/anomaly detection
- [ ] Risk scoring
- [ ] Natural-language analytics
- [ ] Explainability/evidence links
- [ ] Prompt/version governance
- [ ] Model evaluation
- [ ] Hallucination safeguards
- [ ] AI audit trail
- [ ] Human approval for regulated decisions
- [ ] No autonomous regulated disposition

---

# Execution Order

## Wave 1 — Security and SaaS core

1. Tenant isolation
2. Authorization/RBAC
3. Authentication
4. Organization/site administration
5. API security
6. Billing provider and entitlements

## Wave 2 — Stability execution

7. Study lifecycle
8. Protocol lifecycle
9. Specification lifecycle
10. Batch enrollment
11. Timepoints
12. Samples
13. Chambers
14. Results
15. QA approval
16. Record locking
17. E-signatures
18. Audit hardening

## Wave 3 — Quality system

19. OOS/OOT
20. Deviations
21. CAPA
22. Change Control
23. Quality analytics

## Wave 4 — Validation and production

24. Validation package
25. Production infrastructure
26. Security hardening
27. Backup/restore/DR
28. Observability
29. Performance testing

## Wave 5 — Enterprise

30. Versioned public API
31. Webhooks
32. LIMS
33. ERP/SAP
34. SSO/SCIM
35. Enterprise deployment

## Wave 6 — Intelligence

36. Governed AI
37. Trend intelligence
38. OOS/OOT assistance
39. Risk intelligence
40. Natural-language analytics

# Release Gate

QCSTS must not be marketed as production-ready merely because the UI exists. A release candidate requires:

- all critical tenant isolation tests passing;
- all critical authorization tests passing;
- end-to-end stability workflow passing against real APIs;
- server-side record locking;
- server-side e-signature verification;
- billing webhooks verified and idempotent;
- audit integrity verified;
- backup/restore tested;
- validation documentation available;
- no critical security findings;
- no critical data-integrity findings;
- frontend no longer dependent on demonstration data for production workflows.

The target is **95%+ in every category**, measured by implementation + tests + evidence, not by UI surface area.