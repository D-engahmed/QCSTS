# Security gap analysis

## Critical before SaaS onboarding

1. **No tenant isolation:** global querysets expose all data to any authenticated role. Phase 1 must precede multi-customer deployment.
2. **Authorization design:** hard-coded global role strings and absent object policies cannot enforce membership/site scope or separation of duties.
3. **Audit fail-open:** audit writes are swallowed; critical actions can lack evidence. Make regulated transitions atomic with audit persistence.
4. **Audit database enforcement absent:** no trigger migration proves immutable audit records at PostgreSQL level.
5. **Frontend token storage:** access and refresh tokens in `localStorage` are vulnerable to XSS exfiltration. Evaluate secure httpOnly cookie/session strategy, CSP and token rotation as part of enterprise security.
6. **Tracked generated/sensitive artifacts:** environment variants, server logs and static artifacts are tracked. Review history, rotate any exposed secrets, tighten ignores and remove generated files in a separately approved hygiene change.

## High priority foundation

- Apply rate limiting to login, signature verification and APIs; audit successful/failed auth events without sensitive values.
- Add CSP, `SECURE_PROXY_SSL_HEADER`, secure/referrer/content-type headers, CSRF trusted origins, controlled CORS, HTTPS-only production verification and secret-management documentation.
- Add server-side file type/size scanning and signed object URLs before attachments.
- Add API keys/service accounts with hashed secrets, scopes, expiry/revocation and tenant binding.
- Use request IDs, tenant IDs and redaction in structured logs; never log passwords, tokens, API keys or signature credentials.
- Run dependency and secret scanning in CI; pin/update dependencies through a reviewed maintenance process.

## Validation evidence required

Tenant cross-read/write/delete/audit/report/file tests, authorization matrix tests, external security review, migration backup/restore rehearsal, audit trigger verification, and signed workflow tests are required evidence. QCSTS can support regulated workflows and validation; it must not claim automatic GMP, Part 11 or FDA certification.
