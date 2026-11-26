#!/usr/bin/env node
/**
 * Integrity checks for the progressive-disclosure explorer (/explore).
 * Run from the repo root: npm run check:explore  (also part of `validate`).
 *
 * - Question tree: unique ids, every question has 2+ answers, every leaf has
 *   exactly one source, every source exists, EN and ES copy present, no digits
 *   in explorer copy (no invented figures), no Loan Estimate Check links.
 * - Generated graph (both languages): no dead ends, every option resolves,
 *   every layer can still reach a term, all terms reachable, screens stay small.
 * - Cycles: the term graph has natural cycles; navigation is a stack, so we
 *   check long random walks resolve exactly, keep a Back step, and never stall.
 * - EN/ES parity: same screens, same answers, same terms behind each answer.
 */
import { existsSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { categories } from "../../src/data/categories.ts";
import {
  createExplorer,
  EXPLORE_UI,
  hashFor,
  MAX_OPTIONS,
  nodeKey,
  parseHash,
  type ExploreData,
  type ExploreLang,
  type Node,
  type TreeSpec,
} from "../../src/lib/explore.ts";

const root = process.cwd();
const read = (p: string) => JSON.parse(readFileSync(path.join(root, p), "utf8"));
const termFiles = readdirSync(path.join(root, "src/content/terms")).filter((f) => f.endsWith(".json")).sort();
const rawTerms = termFiles.map((f) => read(`src/content/terms/${f}`));
const citations = read("src/data/citations.json");
const parts = read("src/data/parts.json");
const pathsData = read("src/data/paths.json");
const tree: TreeSpec = read("src/data/explore-tree.json");

function dataFor(lang: ExploreLang): ExploreData {
  const es = lang === "es";
  const terms: ExploreData["terms"] = {};
  for (const t of rawTerms) {
    terms[t.slug] = {
      n: es ? t.es.term : t.term,
      d: es ? t.es.definition : t.definition,
      h: es ? t.es.details : t.details,
      x: es ? [t.es.example.setting, t.es.example.text] : [t.example.setting, t.example.text],
      w: es ? t.es.complianceNotes : t.complianceNotes,
      c: t.category,
      r: t.related,
      s: t.citations,
    };
  }
  const cites: ExploreData["cites"] = {};
  for (const c of citations) cites[c.id] = { l: c.label, t: c.title, u: c.url, p: c.partId, k: c.kind };
  return {
    lang,
    tree,
    terms,
    cites,
    parts: parts.map((p: any) => ({ id: p.id, l: p.label, s: p.short, n: p.name })),
    paths: pathsData.map((p: any) => ({
      slug: p.slug,
      t: es ? p.esTitle : p.title,
      steps: p.steps.map((s: any) => s.slug),
      notes: p.steps.map((s: any) => (es ? s.esNote : s.note)),
    })),
    cats: categories.map((c) => ({ id: c.id, l: es ? c.esLabel : c.label })),
  };
}

const failures: string[] = [];
const fail = (msg: string) => failures.push(msg);
const slugSet = new Set(rawTerms.map((t: any) => t.slug));
const pathSet = new Set(pathsData.map((p: any) => p.slug));
const catSet = new Set(categories.map((c) => c.id));
// A learning path is shown whole so its order stays visible.
const MAX_PATH_STEPS = 16;
const RESERVED = /^(t-|p-|r-|c-|k-|g\d|@|more$)/;
const FORBIDDEN = /loan\s*estimate\s*check|loanestimatecheck|analytics|gtag|googletagmanager|plausible|posthog/i;

/* ------------------------------------------------------------ question tree */
let specNodes = 0;
let specLeaves = 0;
let specDepth = 0;
let specLeafTerms = new Set<string>();
function walkSpec(spec: TreeSpec, depth: number, trail: string) {
  specNodes++;
  specDepth = Math.max(specDepth, depth);
  const where = trail ? `${trail}/${spec.id}` : spec.id;
  for (const lang of ["en", "es"] as const) {
    if (!spec.label?.[lang]?.trim()) fail(`tree ${where}: missing ${lang} label`);
    if (depth > 0 && !spec.hint?.[lang]?.trim()) fail(`tree ${where}: missing ${lang} hint`);
  }
  const strings = [spec.label, spec.hint, spec.q].flatMap((l) => (l ? [l.en, l.es] : []));
  for (const s of strings) {
    if (/\d/.test(s)) fail(`tree ${where}: digits in explorer copy (no figures here): "${s}"`);
    if (FORBIDDEN.test(s)) fail(`tree ${where}: forbidden link/copy: "${s}"`);
  }
  if (depth > 0 && RESERVED.test(spec.id)) fail(`tree ${where}: id uses a reserved prefix`);
  if (!/^[a-z0-9-]+$/.test(spec.id)) fail(`tree ${where}: id must be lowercase letters, digits, hyphens`);
  const sources = [spec.children, spec.terms, spec.path, spec.category, spec.generate].filter((v) => v !== undefined).length;
  if (sources !== 1) fail(`tree ${where}: needs exactly one of children/terms/path/category/generate (has ${sources})`);
  if (spec.children) {
    if (spec.children.length < 2) fail(`tree ${where}: a question needs at least two answers`);
    if (spec.children.length > MAX_OPTIONS) fail(`tree ${where}: more than ${MAX_OPTIONS} answers`);
    if (!spec.q?.en || !spec.q?.es) fail(`tree ${where}: question text missing in EN or ES`);
    const ids = spec.children.map((c) => c.id);
    if (new Set(ids).size !== ids.length) fail(`tree ${where}: duplicate child ids`);
    for (const c of spec.children) walkSpec(c, depth + 1, where);
    return;
  }
  specLeaves++;
  if (spec.terms) {
    if (spec.terms.length < 2) fail(`tree ${where}: a term list needs at least two terms`);
    if (new Set(spec.terms).size !== spec.terms.length) fail(`tree ${where}: duplicate terms`);
    for (const s of spec.terms) {
      if (!slugSet.has(s)) fail(`tree ${where}: unknown term "${s}"`);
      specLeafTerms.add(s);
    }
  }
  if (spec.path && !pathSet.has(spec.path)) fail(`tree ${where}: unknown path "${spec.path}"`);
  if (spec.category && !catSet.has(spec.category as any)) fail(`tree ${where}: unknown category "${spec.category}"`);
}
walkSpec(tree, 0, "");

for (const lang of ["en", "es"] as const) {
  for (const [k, v] of Object.entries(EXPLORE_UI[lang])) {
    if (FORBIDDEN.test(v)) fail(`ui.${lang}.${k}: forbidden copy`);
    if (/\d/.test(v)) fail(`ui.${lang}.${k}: digits in explorer copy`);
  }
}
const enKeys = Object.keys(EXPLORE_UI.en).sort().join();
if (enKeys !== Object.keys(EXPLORE_UI.es).sort().join()) fail("ui: EN and ES string keys differ");

/* ------------------------------------------------------------ graph walk */
interface Walk {
  keys: Map<string, { node: Node; options: string[]; kind: string }>;
  termKeys: Set<string>;
  minDepth: Map<string, number>;
  answersTerms: Map<string, string[]>;
}
function walkGraph(lang: ExploreLang): Walk {
  const ex = createExplorer(dataFor(lang));
  const keys: Walk["keys"] = new Map();
  const minDepth = new Map<string, number>();
  const edges = new Map<string, string[]>();
  const queue: { node: Node; depth: number }[] = [{ node: ex.root, depth: 0 }];
  minDepth.set(nodeKey(ex.root), 0);
  while (queue.length) {
    const { node, depth } = queue.shift()!;
    const key = nodeKey(node);
    if (keys.has(key)) continue;
    const opts = ex.options(node);
    const screen = ex.screen(node, "x");
    keys.set(key, { node, options: opts.map((o) => o.id), kind: screen.kind });
    if (opts.length === 0) fail(`${lang} ${key}: dead end (no options)`);
    const limit = node.t === "path" ? MAX_PATH_STEPS : MAX_OPTIONS + 1;
    if (opts.length > limit) fail(`${lang} ${key}: ${opts.length} options on one screen`);
    const ids = opts.map((o) => o.id);
    if (new Set(ids).size !== ids.length) fail(`${lang} ${key}: duplicate option ids`);
    for (const o of opts) {
      if (!o.label.trim()) fail(`${lang} ${key}: empty option label`);
      if (FORBIDDEN.test(o.label) || FORBIDDEN.test(o.hint ?? "")) fail(`${lang} ${key}: forbidden copy in option`);
    }
    if (!screen.heading.trim()) fail(`${lang} ${key}: empty heading`);
    const out: string[] = [];
    for (const o of opts) {
      const next = ex.child(node, o.id);
      if (!next) {
        fail(`${lang} ${key}: option "${o.id}" does not resolve`);
        continue;
      }
      const nk = nodeKey(next);
      out.push(nk);
      if (!minDepth.has(nk)) minDepth.set(nk, depth + 1);
      if (!keys.has(nk)) queue.push({ node: next, depth: depth + 1 });
    }
    edges.set(key, out);
  }
  // Every layer must still lead to a term (reverse reachability from term screens).
  const termKeys = new Set([...keys.keys()].filter((k) => k.startsWith("term:")));
  const reverse = new Map<string, string[]>();
  for (const [from, tos] of edges) for (const to of tos) {
    if (!reverse.has(to)) reverse.set(to, []);
    reverse.get(to)!.push(from);
  }
  const canReach = new Set(termKeys);
  const stack = [...termKeys];
  while (stack.length) {
    const k = stack.pop()!;
    for (const from of reverse.get(k) ?? []) if (!canReach.has(from)) { canReach.add(from); stack.push(from); }
  }
  for (const k of keys.keys()) if (!canReach.has(k)) fail(`${lang} ${k}: cannot reach any term (trap)`);
  for (const slug of slugSet) if (!termKeys.has(`term:${slug}`)) fail(`${lang}: term "${slug}" is not reachable from the start`);
  // Terms behind each top-level answer path (for parity).
  const answersTerms = new Map<string, string[]>();
  for (const [k, v] of keys) {
    if (!k.startsWith("spec:")) continue;
    const seen = new Set<string>();
    const st = [k];
    const vis = new Set<string>();
    while (st.length) {
      const cur = st.pop()!;
      if (vis.has(cur) || cur.startsWith("term:") || cur.startsWith("view:")) {
        if (cur.startsWith("term:")) seen.add(cur.slice(5));
        continue;
      }
      vis.add(cur);
      for (const n of edges.get(cur) ?? []) st.push(n);
    }
    answersTerms.set(k, [...seen].sort());
    void v;
  }

  // Random deep walks: the hash must round-trip and Back must always exist.
  let seed = lang === "en" ? 20261125 : 20261126;
  const rand = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
  for (let w = 0; w < 400; w++) {
    const ids: string[] = [];
    let node = ex.root;
    for (let step = 0; step < 60; step++) {
      const opts = ex.options(node);
      if (!opts.length) { fail(`${lang} walk ${w}: stalled at ${nodeKey(node)}`); break; }
      const pick = opts[Math.floor(rand() * opts.length)];
      const next = ex.child(node, pick.id);
      if (!next) { fail(`${lang} walk ${w}: ${pick.id} did not resolve`); break; }
      ids.push(pick.id);
      node = next;
    }
    const hash = hashFor(ids);
    const back = parseHash(hash);
    const { stack, valid } = ex.resolve(back);
    if (valid.join("/") !== ids.join("/")) fail(`${lang} walk ${w}: hash did not round-trip`);
    if (stack.length !== ids.length + 1) fail(`${lang} walk ${w}: stack length mismatch`);
    if (nodeKey(stack[stack.length - 1].node) !== nodeKey(node)) fail(`${lang} walk ${w}: landed on a different layer`);
  }
  // Deep links from term pages (#/@slug) and junk segments degrade safely.
  for (const slug of slugSet) {
    const { stack, valid } = ex.resolve([`@${slug}`, "rel"]);
    if (valid[0] !== `@${slug}` || stack.length < 2) fail(`${lang}: #/@${slug} did not open the term`);
  }
  const junk = ex.resolve(["buy", "nope", "start"]);
  if (junk.valid.join("/") !== "buy") fail(`${lang}: junk segments were not trimmed`);

  return { keys, termKeys, minDepth, answersTerms };
}

const en = walkGraph("en");
const es = walkGraph("es");

/* ------------------------------------------------------------ parity */
const enSet = [...en.keys.keys()].sort();
const esSet = [...es.keys.keys()].sort();
if (enSet.join("\n") !== esSet.join("\n")) {
  const onlyEn = enSet.filter((k) => !es.keys.has(k)).slice(0, 5);
  const onlyEs = esSet.filter((k) => !en.keys.has(k)).slice(0, 5);
  fail(`parity: EN and ES screens differ (EN only: ${onlyEn.join(", ")}; ES only: ${onlyEs.join(", ")})`);
}
for (const [k, v] of en.keys) {
  const o = es.keys.get(k);
  if (!o) continue;
  // Range groups are cut by each language's alphabetical order, so compare counts there.
  const sameCount = o.options.length === v.options.length;
  const idsMatch = v.options.join() === o.options.join();
  const isRange = v.options.every((id) => /^g\d+$/.test(id));
  const termList = v.options.every((id) => id.startsWith("t-"));
  if (!sameCount) fail(`parity ${k}: EN ${v.options.length} options, ES ${o.options.length}`);
  else if (!isRange && !termList && !idsMatch) fail(`parity ${k}: option ids differ`);
  else if (termList && !/\/g\d+$/.test(k) && [...v.options].sort().join() !== [...o.options].sort().join()) fail(`parity ${k}: different terms`);
  // A list split into ranges must hold the same terms overall in both languages.
  if (isRange && !/\/g\d+$/.test(k)) {
    const all = (w: Walk) => {
      const out = new Set<string>();
      const st = [k];
      while (st.length) {
        const cur = st.pop()!;
        for (const id of w.keys.get(cur)?.options ?? []) {
          if (id.startsWith("t-")) out.add(id.slice(2));
          else if (/^g\d+$/.test(id)) st.push(`${cur}/${id}`);
        }
      }
      return [...out].sort().join();
    };
    if (all(en) !== all(es)) fail(`parity ${k}: different terms across the ranges`);
  }
}
for (const [k, terms] of en.answersTerms) {
  if ((es.answersTerms.get(k) ?? []).join() !== terms.join()) fail(`parity ${k}: different terms behind this answer`);
}

/* ------------------------------------------------------------ built output */
const dist = path.join(root, "dist");
if (existsSync(path.join(dist, "explore-data/en.json"))) {
  for (const lang of ["en", "es"] as const) {
    const built = JSON.parse(readFileSync(path.join(dist, `explore-data/${lang}.json`), "utf8"));
    const local = dataFor(lang);
    const builtSlugs = Object.keys(built.terms).sort();
    if (builtSlugs.join() !== Object.keys(local.terms).sort().join()) fail(`dist ${lang}: explore data has different terms`);
    for (const slug of builtSlugs) {
      if (JSON.stringify(built.terms[slug]) !== JSON.stringify(local.terms[slug])) fail(`dist ${lang}: explore data for "${slug}" differs from sources`);
    }
    if (JSON.stringify(built.tree) !== JSON.stringify(local.tree)) fail(`dist ${lang}: explore tree differs from sources`);
    const page = readFileSync(path.join(dist, lang === "en" ? "explore/index.html" : "es/explore/index.html"), "utf8");
    if (FORBIDDEN.test(page)) fail(`dist ${lang}: explorer page contains forbidden link/copy`);
  }
}

/* ------------------------------------------------------------ report */
const termDepths = [...en.minDepth].filter(([k]) => k.startsWith("term:")).map(([, d]) => d);
const kinds = new Map<string, number>();
for (const { kind } of en.keys.values()) kinds.set(kind, (kinds.get(kind) ?? 0) + 1);
const stats = {
  questionTree: { nodes: specNodes, leaves: specLeaves, maxDepth: specDepth, handPickedTerms: specLeafTerms.size },
  generatedScreensPerLanguage: en.keys.size,
  screensByKind: Object.fromEntries(kinds),
  termsReachable: `${en.termKeys.size}/${slugSet.size} EN, ${es.termKeys.size}/${slugSet.size} ES`,
  clicksToReachATerm: { min: Math.min(...termDepths), max: Math.max(...termDepths), mean: +(termDepths.reduce((a, b) => a + b, 0) / termDepths.length).toFixed(2) },
  randomWalks: "400 per language x 60 clicks, all round-tripped",
};
console.log(JSON.stringify(stats, null, 2));
if (failures.length) {
  console.error(`\ncheck-explore: ${failures.length} failure(s)`);
  for (const f of failures.slice(0, 60)) console.error(`  - ${f}`);
  process.exit(1);
}
console.log("check-explore: PASS");
