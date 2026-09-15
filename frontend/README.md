# QCSTS Frontend

Professional B2B SaaS frontend for the QCSTS pharmaceutical quality and stability platform.

## Stack

- Next.js 15
- React 19
- TypeScript
- Lucide icons
- CSS design system (no UI framework lock-in)

## Current product surfaces

- Command Center dashboard
- Stability Studies workspace
- Professional SaaS navigation shell
- Organization/site context
- Operational alerts
- Study health and progress
- Timepoint queue
- Responsive layouts

## Run

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Next frontend milestones

1. Connect the shell to the Django API.
2. Replace mock dashboard data with tenant-scoped API data.
3. Add authentication and organization switching.
4. Add study detail workspace.
5. Add protocol/specification version management UI.
6. Add sample/timepoint/result workflows.
7. Add audit/compliance views.
8. Add organization administration and billing.
9. Add loading, empty, error and permission states for every workflow.
