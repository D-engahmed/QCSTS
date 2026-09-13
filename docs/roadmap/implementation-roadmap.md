# Implementation roadmap

## Delivery discipline

Each phase is a small, reviewable branch/PR with a conventional commit, migration review, OpenAPI/frontend contract changes, backend/frontend tests, security review and updated documentation. Push only committed repository-owned work; never stage current user edits, environment files, logs, generated static content or secrets. `main` is currently behind `origin/main`; sync/rebase policy must be agreed before the first change branch.

## Phase 0: audit (this change)

The architecture, product, security, compliance and roadmap documents are created. Test execution is blocked locally by missing Python/pytest. Resolve runtime/CI baseline before accepting the audit commit as a green build.

## Phase 1: multi-tenancy and organization foundation

Detailed plan:

1. Add a `platform` app containing `Organization`, `Site`, `Membership`, `Role`, `Permission` and a migration-safe role compatibility plan.
2. Add active organization/site context resolution from authenticated membership. Define no-context and multi-membership behavior; initial API may use a server-validated context header or selection endpoint.
3. Add nullable `organization` and, where required, `site` foreign keys to existing tenant records: monographs/tests, products, batches, test points, sample pulls, location history, results, audit logs and future reports/files. Add all indexes before constraints.
4. Create one explicit legacy organization and backfill every current record transactionally. Validate counts, orphan relationships and references; only then make organization mandatory.
5. Replace global uniqueness with scoped constraints: batch number per organization, location per organization/site, monograph/product identity as defined by the business rules. Preserve old identifiers and URLs during the compatibility window.
6. Introduce centralized policy/queryset services. Every route, serializer related-field queryset, service and Celery job receives/verifies organization scope. Browser request data cannot select the authoritative tenant.
7. Tenant-scope audit logs and endpoint object lookups. Apply secure storage namespace design before attachments/files are added.
8. Add API endpoints and React administration/context UI for organization, sites and memberships. Use an accessible design-token shell and status language as the starting visual identity, without speculative page rewrites.
9. Add mandatory tests: cross-tenant read, write, delete, audit, report and file denial; membership/site authorization; background job isolation; legacy backfill integrity and existing workflow regressions.
10. Update OpenAPI, migration runbook, ADRs and user/admin guide. Run migration against a production-like PostgreSQL backup copy, then release through CI.

## Subsequent phase order

After Phase 1 approval and successful release: organization/site management → study domain → protocol versions → specification engine → scheduling → samples/chambers → controlled results → QA workflow → signature hardening → audit hardening → quality events → dashboard → notifications → reporting → billing → enterprise security → API/webhooks → storage → observability → backup/DR → test expansion → UX → demo → commercial site → AI.

## File-by-file Phase 1 implementation map

| Area | Planned files |
| --- | --- |
| Platform app | new `QCSTS/apps/platform/{models,services,permissions,serializers,views,urls,admin}.py`, migrations and tests |
| Settings/routes | `QCSTS/config/settings/base.py`, `QCSTS/config/urls.py`, new tenant-context middleware/settings |
| Shared core | `QCSTS/core/models.py`, new tenant query/policy/context modules, `core/permissions.py` migration adapters |
| Existing models | model/migration updates in accounts, audit, products, batches, schedule, results and chamber |
| Existing APIs/services | views/serializers/tasks/services in each tenant-owned app; eliminate unscoped related-field querysets |
| Frontend | `src/services/api.js`, app shell/router/sidebar, new administration/context components/pages, design token stylesheet and tests |
| Contracts/docs/CI | `schema.yml` regeneration, API docs, migration runbook, isolation matrix, CI workflow and deployment configuration as separately reviewed files |

## Risk register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Tenant data leak | critical | mandatory server scope, deny-by-default context, cross-tenant tests, PostgreSQL RLS defense in depth |
| Unsafe legacy backfill | critical | backup, dry run, counts/checksums, reversible staged migrations, acceptance gate |
| Existing workflow regression | high | preserve endpoints initially, regression suite, contract tests and rollout flags |
| Audit evidence gap | high | atomic critical audit writes, database protection migration, verification test |
| Production claims exceed evidence | high | accurate positioning, validation plan and traceable evidence |
| Secret leakage | high | do not stage env/logs; scan history/CI; rotate discovered credentials |
| Missing runtime/CI | high | establish reproducible test image and GitHub Actions before Phase 1 merge |
| Visual rewrite delays controls | medium | establish tokens/shell in Phase 1; sequence broad UX after workflows |
| Payment/provider dependency | medium | defer provider activation; adapter and tested webhook design only when authorized |
