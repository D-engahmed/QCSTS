# QCSTS Frontend

Professional multi-tenant pharmaceutical quality and stability SaaS interface built with Next.js 15, React 19 and TypeScript.

## Product surfaces

- Authentication entry point
- Organization/site context
- Command Center
- Stability Studies and controlled study creation wizard
- Study detail workspace
- Protocols and protocol versions
- Specifications and specification versions
- Products and batch enrollment
- Samples and timepoints
- Results, QA review, electronic-signature UX and locked records
- Chambers
- OOS/OOT
- Deviations
- CAPA
- Audit and compliance
- Organization administration
- Users and roles
- Billing and subscription
- Reports and analytics
- Settings

## API integration

Set `NEXT_PUBLIC_API_URL` to the Django API root, for example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

`src/lib/api.ts` centralizes API requests. `src/hooks/useTenantResource.ts` provides a tenant-aware client resource boundary and should be used by production pages instead of duplicating fetch logic.

The UI intentionally separates controlled workflows from presentation. Server-side authorization, tenant isolation, subscription entitlements, e-signature enforcement and record locking remain authoritative in the Django backend.

## Run

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Production readiness

The branch provides the product-facing frontend surfaces and workflow UX. Replace demonstration records with backend responses as each API endpoint becomes available; do not move authorization decisions into the browser.


## Architecture

Public routes handle acquisition and authentication. Authenticated routes are mounted under the application workspace and share AppShell. AuthProvider owns session lifecycle; api.ts owns HTTP behavior; auth.ts owns the local session representation; reusable workspace components provide tables, forms, signatures, status and error UI.

The browser is never the authorization authority. Django remains authoritative for identity, tenant isolation, RBAC, workflow transitions, record locking, signatures and billing entitlements.

## Quality gates

- npm ci
- npm run check:no-demo
- npm run typecheck
- npm run build
- npm run check:routes

The public experience includes a professional landing page, animated product walkthrough, explicit Sign in/Create workspace onboarding and persistent light/dark mode with reduced-motion support.
