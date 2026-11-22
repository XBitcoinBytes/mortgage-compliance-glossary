import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const dir = path.join(root, "src/content/terms");
const manifest = JSON.parse(await readFile(path.join(root, "src/data/term-manifest.json"), "utf8"));
const citations = JSON.parse(await readFile(path.join(root, "src/data/citations.json"), "utf8"));
const paths = JSON.parse(await readFile(path.join(root, "src/data/paths.json"), "utf8"));
const trending = JSON.parse(await readFile(path.join(root, "src/data/trending.json"), "utf8"));
const citationIds = new Set(citations.map((item) => item.id));
const categories = new Set([
  "origination",
  "underwriting",
  "compliance",
  "closing",
  "servicing",
  "loan-programs",
  "borrower-faqs",
]);
const errors = [];
const fail = (message) => errors.push(message);

const files = (await readdir(dir)).filter((name) => name.endsWith(".json"));
const terms = new Map();
for (const file of files) {
  let data;
  try {
    data = JSON.parse(await readFile(path.join(dir, file), "utf8"));
  } catch (error) {
    fail(`${file} is not valid JSON (${error.message})`);
    continue;
  }
  if (terms.has(data.slug)) fail(`duplicate slug ${data.slug}`);
  terms.set(data.slug, data);
  if (`${data.slug}.json` !== file) fail(`${file} slug is ${data.slug}`);
  if (!categories.has(data.category)) fail(`${data.slug} has invalid category`);
  if (typeof data.term !== "string" || data.term.trim().length < 2) fail(`${data.slug} missing term`);
  for (const field of ["definition", "details", "complianceNotes"]) {
    if (typeof data[field] !== "string" || data[field].trim().length < 12) fail(`${data.slug} missing ${field}`);
  }
  if (typeof data.reviewed !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(data.reviewed)) {
    fail(`${data.slug} missing reviewed`);
  }
  if ((data.definition ?? "").trim().length < 80) fail(`${data.slug} definition is too short`);
  if ((data.details ?? "").trim().length < 160) fail(`${data.slug} details are too short`);
  if ((data.complianceNotes ?? "").trim().length < 80) fail(`${data.slug} compliance notes are too short`);
  if (!data.example?.setting || !data.example?.text) fail(`${data.slug} missing example`);
  if (!String(data.example?.text ?? "").includes("Example figures")) {
    fail(`${data.slug} example must include the phrase "Example figures"`);
  }
  if (!Array.isArray(data.aliases)) fail(`${data.slug} aliases must be an array`);
  if (!Array.isArray(data.citations) || data.citations.length < 1) fail(`${data.slug} needs at least one citation`);
  for (const id of data.citations ?? []) {
    if (!citationIds.has(id)) fail(`${data.slug} cites unknown id ${id}`);
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(data.reviewed ?? "")) fail(`${data.slug} reviewed date is invalid`);
  const es = data.es;
  if (!es) fail(`${data.slug} missing Spanish`);
  else {
    if (typeof es.term !== "string" || es.term.trim().length < 2) fail(`${data.slug} missing es.term`);
    for (const field of ["definition", "details", "complianceNotes"]) {
      if (typeof es[field] !== "string" || es[field].trim().length < 12) fail(`${data.slug} missing es.${field}`);
    }
    if ((es.definition ?? "").trim() === (data.definition ?? "").trim()) fail(`${data.slug} Spanish definition copies English`);
    if (!/(\bel\b|\bla\b|\blos\b|\blas\b|\bde\b|\bque\b|\buna\b|\bpara\b)/i.test(es.definition ?? "")) {
      fail(`${data.slug} Spanish definition does not look like Spanish`);
    }
    if (!es.example?.setting || !es.example?.text) fail(`${data.slug} missing Spanish example`);
    if (!String(es.example?.text ?? "").includes("Cifras de ejemplo")) {
      fail(`${data.slug} Spanish example must include "Cifras de ejemplo"`);
    }
    if (!Array.isArray(es.aliases)) fail(`${data.slug} es.aliases must be an array`);
  }
  if (!Array.isArray(data.related)) fail(`${data.slug} related must be an array`);
  if (data.reviewFlag !== undefined && typeof data.reviewFlag !== "string") fail(`${data.slug} reviewFlag must be a string`);
}

const manifestSlugs = manifest.map((item) => item.slug);
if (new Set(manifestSlugs).size !== manifestSlugs.length) fail("duplicate slugs in the manifest");
for (const slug of manifestSlugs) {
  if (!terms.has(slug)) fail(`manifest slug missing file: ${slug}`);
}
for (const slug of terms.keys()) {
  if (!manifestSlugs.includes(slug)) fail(`file not in manifest: ${slug}`);
}
if (terms.size < 300) fail(`expected at least 300 terms, found ${terms.size}`);

for (const term of terms.values()) {
  const related = term.related ?? [];
  if (new Set(related).size !== related.length) fail(`${term.slug} has duplicate related slugs`);
  for (const slug of related) {
    if (slug === term.slug) fail(`${term.slug} relates to itself`);
    if (!terms.has(slug)) fail(`${term.slug} related slug missing: ${slug}`);
    else if (!terms.get(slug).related.includes(term.slug)) {
      fail(`${term.slug} related ${slug} is not bidirectional`);
    }
  }
}

for (const learningPath of paths) {
  const seen = new Set();
  if (!learningPath.steps || learningPath.steps.length < 6) fail(`path ${learningPath.slug} is too short`);
  for (const step of learningPath.steps ?? []) {
    if (!terms.has(step.slug)) fail(`path ${learningPath.slug} missing term ${step.slug}`);
    if (seen.has(step.slug)) fail(`path ${learningPath.slug} repeats ${step.slug}`);
    seen.add(step.slug);
    if (!step.note || !step.esNote) fail(`path ${learningPath.slug} step ${step.slug} missing notes`);
  }
}

if (!Array.isArray(trending.slugs) || trending.slugs.length < 8) fail("trending list is too short");
if ("count" in trending || "counts" in trending) fail("trending must not include fabricated counts");
for (const slug of trending.slugs ?? []) {
  if (!terms.has(slug)) fail(`trending slug missing: ${slug}`);
}
if (new Set(trending.slugs).size !== trending.slugs.length) fail("trending slugs repeat");

if (errors.length) {
  console.error(`validation failed with ${errors.length} error(s):`);
  for (const error of errors.slice(0, 80)) console.error(`- ${error}`);
  if (errors.length > 80) console.error(`... ${errors.length - 80} more`);
  process.exit(1);
}

const flagged = [...terms.values()].filter((term) => term.reviewFlag).map((term) => term.slug);
console.log(`validated ${terms.size} terms, ${flagged.length} flagged for expert review`);
