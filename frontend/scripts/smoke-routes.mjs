const base = process.env.QCSTS_SMOKE_URL ?? "http://127.0.0.1:3000";
const routes = [
  "/",
  "/login",
  "/register",
  "/app",
  "/app/products",
  "/app/monographs",
  "/app/batches",
  "/app/protocols",
  "/app/protocol-versions",
  "/app/specifications",
  "/app/specification-versions",
  "/app/storage-conditions",
  "/app/studies",
  "/app/study-batches",
  "/app/timepoints",
  "/app/samples",
  "/app/test-points",
  "/app/sample-pulls",
  "/app/chambers",
  "/app/results",
  "/app/results/new",
  "/app/quality",
  "/app/quality/oos",
  "/app/quality/oot",
  "/app/quality/deviations",
  "/app/quality/capa",
  "/app/quality/change-control",
  "/app/audit",
  "/app/compliance",
  "/app/reports",
  "/app/billing",
  "/app/users",
  "/app/organization",
  "/app/settings",
];

async function waitForServer() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const response = await fetch(base + "/");
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Next.js production server did not become ready.");
}

await waitForServer();

const failures = [];
for (const route of routes) {
  const response = await fetch(base + route, { redirect: "manual" });
  if (response.status >= 400) {
    failures.push(route + " -> HTTP " + response.status);
  }
}

if (failures.length) {
  console.error("Frontend route smoke failures:");
  failures.forEach((failure) => console.error(" - " + failure));
  process.exit(1);
}

console.log("Frontend production route smoke passed for " + routes.length + " routes.");
