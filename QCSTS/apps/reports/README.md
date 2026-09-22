# Reports — Operational Analytics & Exports

## Purpose
The reports app converts tenant-authorized operational data into dashboards, analytics and exports.

## Responsibilities
- Dashboard metrics.
- Analytics endpoints.
- CSV/report exports.
- Cross-domain aggregation.

## Architecture
Tenant-scoped domain data → report query layer → dashboard/analytics/export.

Reports query source-of-truth models instead of maintaining competing business state.

## Security design
Authorization is applied before aggregation. Export endpoints are treated as data-exfiltration surfaces.

## Performance design
Use indexed filters and bounded queries. Large exports should use asynchronous workers instead of blocking web workers.

## Testing
Test aggregate tenant isolation, export correctness, date filters and empty datasets.

## Design invariant
Reporting may aggregate data, but it must never weaken the source authorization boundary.
