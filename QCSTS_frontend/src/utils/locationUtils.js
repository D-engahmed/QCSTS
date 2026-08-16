// ─── LOCATION UTILITIES ──────────────────────────────────────
// NOTE: this file previously also held mock-data helpers (getBatch,
// getProduct, isLocationTaken, confirmLocationChange, showLocationHistory,
// showChangeLocation) that operated on a static in-memory prototype
// dataset (../data/db.js) using a different schema (camelCase fields,
// integer IDs) than the real Django API (snake_case, UUIDs). Nothing in
// the app called them — they were dead code left over from before the
// backend existed, and importing them today would silently produce
// wrong data. Removed; formatDate (the only helper actually used
// elsewhere) is kept below.

export function formatDate(dateStr) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
}
