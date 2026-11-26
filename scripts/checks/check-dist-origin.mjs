// Post-build guard: production artifacts must not use a localhost origin,
// internal hrefs must resolve, and term pages must carry complete DefinedTerm JSON-LD.
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";

const dist = path.resolve("dist");
const defaultOrigin = "https://mortgagecomplianceglossary.com";
const origin = (process.env.SITE_URL || defaultOrigin).replace(/\/$/, "");
const allowLocal = /127\.0\.0\.1|localhost/.test(origin);
const errors = [];
const warnings = [];

async function walk(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walk(full)));
    else out.push(full);
  }
  return out;
}

function fileForUrlPath(urlPath) {
  const clean = urlPath.split("#")[0].split("?")[0];
  if (!clean || clean === "/") return [path.join(dist, "index.html")];
  const trimmed = clean.replace(/\/$/, "");
  return [
    path.join(dist, trimmed, "index.html"),
    path.join(dist, `${trimmed}.html`),
    path.join(dist, trimmed),
  ];
}

async function existsAny(candidates) {
  for (const candidate of candidates) {
    try {
      const info = await stat(candidate);
      if (info.isFile()) return candidate;
    } catch {
      // continue
    }
  }
  return null;
}

const files = await walk(dist);
if (files.length === 0) {
  console.error("check-dist-origin: dist/ is empty");
  process.exit(1);
}

const htmlFiles = files.filter((file) => file.endsWith(".html"));
const textFiles = files.filter((file) => /\.(html|xml|txt|json)$/.test(file));

function leakedLocalOrigin(file, text) {
  if (allowLocal) return false;
  const rel = path.relative(dist, file);
  if (file.endsWith(".xml") || file.endsWith(".txt") || file.endsWith("robots.txt")) {
    return /127\.0\.0\.1|localhost/.test(text);
  }
  if (!file.endsWith(".html")) return false;
  const metadata = [];
  const canon = text.match(/rel="canonical" href="([^"]+)"/);
  if (canon) metadata.push(canon[1]);
  for (const m of text.matchAll(/property="og:url" content="([^"]+)"/g)) metadata.push(m[1]);
  for (const m of text.matchAll(/hreflang="[^"]+" href="([^"]+)"/g)) metadata.push(m[1]);
  for (const m of text.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) metadata.push(m[1]);
  const cite = text.match(/id="cite-text"[^>]*>([^<]+)/);
  if (cite) metadata.push(cite[1]);
  return metadata.some((value) => /127\.0\.0\.1|localhost/.test(value));
}

if (!allowLocal) {
  for (const file of textFiles) {
    const text = await readFile(file, "utf8");
    if (leakedLocalOrigin(file, text)) {
      errors.push(`${path.relative(dist, file)} has a localhost origin in metadata, sitemap, or robots.txt`);
    }
  }
}

const robots = path.join(dist, "robots.txt");
try {
  const body = await readFile(robots, "utf8");
  if (!body.includes(`Sitemap: ${origin}/sitemap-index.xml`)) {
    errors.push(`robots.txt sitemap is not ${origin}/sitemap-index.xml`);
  }
} catch {
  errors.push("robots.txt is missing from dist/");
}

const sitemapIndex = path.join(dist, "sitemap-index.xml");
const sitemap0 = path.join(dist, "sitemap-0.xml");
let sitemapBody = "";
try {
  sitemapBody = await readFile(sitemap0, "utf8");
} catch {
  errors.push("sitemap-0.xml is missing from dist/");
}
try {
  const indexBody = await readFile(sitemapIndex, "utf8");
  if (!indexBody.includes(`${origin}/sitemap-0.xml`)) {
    errors.push(`sitemap-index.xml does not point at ${origin}/sitemap-0.xml`);
  }
} catch {
  errors.push("sitemap-index.xml is missing from dist/");
}

const locMatches = [...sitemapBody.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
const termPages = htmlFiles.filter((file) => /\/(es\/)?terms\/(?!index\.html$).+\/index\.html$/.test(file.replace(dist, "")) || /\/(es\/)?terms\/[^/]+\.html$/.test(file.replace(dist, "")));
// Count unique term slugs from html paths like dist/terms/foo/index.html and dist/es/terms/foo/index.html
const termHtml = htmlFiles.filter((file) => /\/terms\//.test(file) && !file.endsWith(`${path.sep}terms${path.sep}index.html`));
const termLocs = locMatches.filter((loc) => /\/terms\/[^/]+$/.test(loc));
if (sitemapBody && termLocs.length < 780) {
  errors.push(`sitemap-0.xml has only ${termLocs.length} term URLs (expected 393 English + 393 Spanish)`);
}

const sampleHtml = [
  path.join(dist, "index.html"),
  path.join(dist, "terms", "loan-estimate", "index.html"),
  path.join(dist, "es", "terms", "loan-estimate", "index.html"),
];

for (const file of sampleHtml) {
  let text;
  try {
    text = await readFile(file, "utf8");
  } catch {
    errors.push(`missing expected page ${path.relative(dist, file)}`);
    continue;
  }
  const rel = path.relative(dist, file);
  if (!text.includes(`rel="canonical" href="${origin}`)) {
    errors.push(`${rel} canonical is not ${origin}`);
  }
}

const existing = new Set(files);
const hrefExists = new Map();
function resolveHref(urlPath) {
  const key = urlPath.split("#")[0].split("?")[0];
  if (hrefExists.has(key)) return hrefExists.get(key);
  const found = fileForUrlPath(key).some((candidate) => existing.has(candidate));
  hrefExists.set(key, found);
  return found;
}

let brokenInternal = 0;
const brokenSamples = [];
const hrefRe = /href="([^"]+)"/g;
for (const file of htmlFiles) {
  const text = await readFile(file, "utf8");
  for (const match of text.matchAll(hrefRe)) {
    const href = match[1];
    if (href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) continue;
    let urlPath = null;
    if (href.startsWith("/")) urlPath = href;
    else if (href.startsWith(origin + "/") || href === origin) urlPath = href.slice(origin.length) || "/";
    else continue;
    if (!resolveHref(urlPath)) {
      brokenInternal += 1;
      if (brokenSamples.length < 20) {
        brokenSamples.push(`${path.relative(dist, file)} -> ${href}`);
      }
    }
  }
}
if (brokenInternal) {
  errors.push(`${brokenInternal} internal href(s) do not resolve in dist/`);
  errors.push(...brokenSamples);
}

// Structured data on every term page
const dateRe = /^\d{4}-\d{2}-\d{2}$/;
let jsonLdPages = 0;
let jsonLdIssues = 0;
for (const file of termHtml) {
  const text = await readFile(file, "utf8");
  const blocks = [...text.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  if (!blocks.length) {
    jsonLdIssues += 1;
    if (jsonLdIssues <= 8) errors.push(`${path.relative(dist, file)} is missing JSON-LD`);
    continue;
  }
  let ok = false;
  for (const block of blocks) {
    let data;
    try {
      data = JSON.parse(block);
    } catch {
      continue;
    }
    if (data["@type"] !== "DefinedTerm") continue;
    ok = true;
    jsonLdPages += 1;
    if (!data.name || !data.description || !data.url || !data.inDefinedTermSet || !data.inLanguage) {
      jsonLdIssues += 1;
      if (jsonLdIssues <= 8) errors.push(`${path.relative(dist, file)} DefinedTerm is missing required fields`);
    }
    if (data.url && !String(data.url).startsWith(origin)) {
      jsonLdIssues += 1;
      if (jsonLdIssues <= 8) errors.push(`${path.relative(dist, file)} DefinedTerm.url is ${data.url}`);
    }
    if (data.dateModified && !dateRe.test(String(data.dateModified))) {
      jsonLdIssues += 1;
      if (jsonLdIssues <= 8) errors.push(`${path.relative(dist, file)} dateModified is ${data.dateModified}`);
    }
  }
  if (!ok) {
    jsonLdIssues += 1;
    if (jsonLdIssues <= 8) errors.push(`${path.relative(dist, file)} has no DefinedTerm JSON-LD`);
  }
}

// LoanEstimateCheck must not appear in a production (master) build of this repo's default dist.
// This script cannot know the branch, so only warn if present; the funnel preview is allowed to include it.
const lecHits = [];
for (const file of textFiles) {
  const text = await readFile(file, "utf8");
  if (/loanestimatecheck\.com/i.test(text)) lecHits.push(path.relative(dist, file));
}
if (lecHits.length) {
  warnings.push(`${lecHits.length} file(s) mention loanestimatecheck.com (expected only on preview/lec-funnel): ${lecHits.slice(0, 5).join(", ")}`);
}

if (warnings.length) {
  console.warn(warnings.join("\n"));
}
if (errors.length) {
  console.error(`check-dist-origin failed with ${errors.length} issue(s):\n` + errors.join("\n"));
  process.exit(1);
}
console.log(
  `check-dist-origin ok: origin ${origin}, ${htmlFiles.length} html files, ${termLocs.length} term URLs in sitemap, ${jsonLdPages} DefinedTerm pages, 0 broken internal hrefs`,
);
