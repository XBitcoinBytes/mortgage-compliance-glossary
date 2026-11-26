#!/usr/bin/env node
/**
 * Flags false auto-links and prints a sample for editorial review.
 * Run from the repo root: npm run check:autolink
 */
import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { linkDefinition, type LinkSegment } from "../../src/lib/autolink.ts";
import type { Lang, Term } from "../../src/lib/types.ts";

const root = process.cwd();
const dir = path.join(root, "src/content/terms");
const terms: Term[] = readdirSync(dir)
  .filter((name) => name.endsWith(".json"))
  .map((name) => JSON.parse(readFileSync(path.join(dir, name), "utf8")) as Term);

const hrefFor = (slug: string) => `/terms/${slug}`;

function links(segments: LinkSegment[]): LinkSegment[] {
  return segments.filter((segment) => segment.slug);
}

const failures: string[] = [];
const stats = {
  enDefs: 0,
  esDefs: 0,
  enLinked: 0,
  esLinked: 0,
  enLinkCount: 0,
  esLinkCount: 0,
};

type Row = { slug: string; lang: Lang; term: string; text: string; found: LinkSegment[] };

const rows: Row[] = [];

for (const term of terms) {
  for (const [lang, text] of [
    ["en", term.definition],
    ["es", term.es.definition],
  ] as const) {
    const found = links(
      linkDefinition(text, { lang, currentSlug: term.slug, terms, hrefFor }),
    );
    if (lang === "en") {
      stats.enDefs += 1;
      if (found.length) stats.enLinked += 1;
      stats.enLinkCount += found.length;
    } else {
      stats.esDefs += 1;
      if (found.length) stats.esLinked += 1;
      stats.esLinkCount += found.length;
    }
    rows.push({ slug: term.slug, lang, term: lang === "es" ? term.es.term : term.term, text, found });
    if (found.some((item) => item.slug === term.slug)) {
      failures.push(`self-link on ${lang} ${term.slug}`);
    }
  }
}

// Known false-positive guards
const loanEn = terms.find((term) => term.slug === "loan-estimate")!;
const totalHits = linkDefinition(
  "The total payment and the total interest are not the TOTAL Scorecard.",
  { lang: "en", currentSlug: "note-rate", terms, hrefFor },
);
if (totalHits.some((item) => item.slug === "fha-total-scorecard" && item.text !== "TOTAL")) {
  failures.push(`TOTAL acronym matched a non-uppercase token: ${JSON.stringify(links(totalHits))}`);
}
const leInside = linkDefinition("The legal review is complete.", {
  lang: "en",
  currentSlug: "creditor",
  terms,
  hrefFor,
});
if (leInside.some((item) => item.slug === "loan-estimate")) {
  failures.push("LE matched inside 'legal'");
}
const twice = links(
  linkDefinition("A Loan Estimate, then another Loan Estimate later.", {
    lang: "en",
    currentSlug: "creditor",
    terms,
    hrefFor,
  }),
).filter((item) => item.slug === "loan-estimate");
if (twice.length !== 1) {
  failures.push(`expected one Loan Estimate link, got ${twice.length}`);
}
const self = links(
  linkDefinition(loanEn.definition, { lang: "en", currentSlug: "loan-estimate", terms, hrefFor }),
);
if (self.some((item) => item.slug === "loan-estimate")) {
  failures.push("loan-estimate definition linked to itself");
}
const cite = linkDefinition(
  "See 12 CFR 1026.19(e). The Loan Estimate is due after application.",
  { lang: "en", currentSlug: "ability-to-repay", terms, hrefFor },
);
if (cite.some((item) => item.slug === "regulation-z" && (item.text.includes("CFR") || item.text.includes("1026")))) {
  failures.push(`citation span was auto-linked: ${JSON.stringify(links(cite))}`);
}
if (!cite.some((item) => item.slug === "loan-estimate")) {
  failures.push("Loan Estimate after a citation was not linked");
}

const banned = new Set(["toolkit", "cure", "points", "lock", "total"]);
for (const row of rows) {
  for (const item of row.found) {
    if (banned.has(item.text.toLowerCase()) && item.text !== item.text.toUpperCase()) {
      failures.push(`generic alias ${JSON.stringify(item.text)} linked on ${row.lang} ${row.slug}`);
    }
  }
}

// Sample for review: high-degree pages plus a spread of others
const sampleSlugs = [
  "loan-estimate",
  "closing-disclosure",
  "annual-percentage-rate",
  "creditor",
  "ability-to-repay",
  "ten-percent-tolerance",
  "debt-to-income-ratio",
  "escrow-account",
  "qualified-mortgage",
  "trid",
];
console.log("Autolink review sample (first mention of each term, EN then ES):\n");
for (const slug of sampleSlugs) {
  for (const row of rows.filter((item) => item.slug === slug)) {
    const list = row.found.map((item) => `${item.text}→${item.slug}`).join("; ") || "(none)";
    console.log(`- ${row.lang} ${row.term} (${row.slug}): ${list}`);
  }
}

const densest = [...rows]
  .sort((a, b) => b.found.length - a.found.length)
  .slice(0, 8);
console.log("\nMost densely linked definitions:");
for (const row of densest) {
  console.log(`- ${row.lang} ${row.slug}: ${row.found.length} links (${row.found.map((item) => item.slug).join(", ")})`);
}

console.log("\nStats:");
console.log(
  `  EN: ${stats.enLinked}/${stats.enDefs} definitions linked, ${stats.enLinkCount} links, avg ${(stats.enLinkCount / stats.enDefs).toFixed(2)}`,
);
console.log(
  `  ES: ${stats.esLinked}/${stats.esDefs} definitions linked, ${stats.esLinkCount} links, avg ${(stats.esLinkCount / stats.esDefs).toFixed(2)}`,
);

if (failures.length) {
  console.error("\nFAIL:");
  for (const line of failures) console.error(`  - ${line}`);
  process.exit(1);
}
console.log("\nPASS: no self-links, no LE-in-legal, no lowercase TOTAL, citation spans skipped.");
