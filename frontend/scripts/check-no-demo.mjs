import { promises as fs } from "node:fs";
import path from "node:path";

const root = path.resolve("src");
const forbidden = [
  /demo[_-]?data/i,
  /sample[-_]?tenant/i,
  /sample[-_]?study/i,
  /fake[-_]?result/i,
  /hardcoded[-_]?result/i,
  /mock[-_]?data/i,
];

async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.name === "node_modules" || entry.name === ".next") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...await walk(full));
    else if (/\.(ts|tsx|js|jsx)$/.test(entry.name)) files.push(full);
  }
  return files;
}

const files = await walk(root);
const violations = [];

for (const file of files) {
  const content = await fs.readFile(file, "utf8");
  for (const pattern of forbidden) {
    if (pattern.test(content)) violations.push(`${path.relative(process.cwd(), file)} matches ${pattern}`);
  }
}

if (violations.length) {
  console.error("Known demonstration-data patterns detected:");
  for (const violation of violations) console.error(" - " + violation);
  process.exit(1);
}

console.log(`No known demonstration-data patterns found in ${files.length} source files.`);
