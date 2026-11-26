import type { Lang } from "./types";
import { categories } from "../data/categories";
import treeSpec from "../data/explore-tree.json";
import { citations, displayName, getTerms, parts, paths } from "./content";
import type { ExploreData, TreeSpec } from "./explore";

/** Build-time: the per-language data the explorer reads (also served as JSON). */
export function exploreData(lang: Lang): ExploreData {
  const terms: ExploreData["terms"] = {};
  for (const term of getTerms()) {
    const es = lang === "es";
    terms[term.slug] = {
      n: displayName(term, lang),
      d: es ? term.es.definition : term.definition,
      h: es ? term.es.details : term.details,
      x: es ? [term.es.example.setting, term.es.example.text] : [term.example.setting, term.example.text],
      w: es ? term.es.complianceNotes : term.complianceNotes,
      c: term.category,
      r: term.related,
      s: term.citations,
    };
  }
  const cites: ExploreData["cites"] = {};
  for (const c of citations) cites[c.id] = { l: c.label, t: c.title, u: c.url, p: c.partId, k: c.kind };
  return {
    lang,
    tree: treeSpec as TreeSpec,
    terms,
    cites,
    parts: parts.map((p) => ({ id: p.id, l: p.label, s: p.short, n: p.name })),
    paths: paths.map((p) => ({
      slug: p.slug,
      t: lang === "es" ? p.esTitle : p.title,
      steps: p.steps.map((s) => s.slug),
      notes: p.steps.map((s) => (lang === "es" ? s.esNote : s.note)),
    })),
    cats: categories.map((c) => ({ id: c.id, l: lang === "es" ? c.esLabel : c.label })),
  };
}
