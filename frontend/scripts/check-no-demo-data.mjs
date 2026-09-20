import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const ROOT = path.resolve("src");
const EXTENSIONS = new Set([".ts", ".tsx", ".js", ".jsx"]);

const forbidden = [
  /STB-2026-\d+/i,
  /RES-18\d+/i,
  /SPEC-\d+/i,
  /Cairo Pharmaceutical Group/i,
  /STB-PRO-\d+/i,
  /86\s*\/\s*96/i,
  /24\s*active\s+stud/i,
  /CreateStudyWizard/i,
  /DataWorkspace/i,
  /testPointService/i,
  /(?:\.\.?\/)data\/db/i,
  /Date\.now\(\)/i,
];

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...await walk(full));
    else if (EXTENSIONS.has(path.extname(entry.name))) files.push(full);
  }
  return files;
}

const files = await walk(ROOT);
const violations = [];

for (const file of files) {
  const source = await readFile(file, "utf8");
  for (const pattern of forbidden) {
    if (pattern.test(source)) {
      violations.push(`${path.relative(process.cwd(), file)} matches ${pattern}`);
    }
  }
}

if (violations.length) {
  console.error("Frontend demo-data check failed:");
  console.error(violations.join("\n"));
  process.exit(1);
}

console.log(`Frontend demo-data check passed across ${files.length} source files.`);
