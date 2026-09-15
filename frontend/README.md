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
