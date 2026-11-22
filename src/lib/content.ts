import type {
  CategoryId,
  Citation,
  Lang,
  LearningPath,
  Part,
  SearchRecord,
  Term,
  Trending,
} from "./types";
import { categoryMap } from "../data/categories";
import citationsData from "../data/citations.json";
import partsData from "../data/parts.json";
import pathsData from "../data/paths.json";
import trendingData from "../data/trending.json";

const modules = import.meta.glob<Term>("../content/terms/*.json", {
  eager: true,
  import: "default",
});

export const citations = citationsData as Citation[];
export const citationMap = new Map(citations.map((citation) => [citation.id, citation]));
export const parts = partsData as Part[];
export const partMap = new Map(parts.map((part) => [part.id, part]));
export const paths = pathsData as LearningPath[];
export const trending = trendingData as Trending;

function letterOf(name: string): string {
  const stripped = name
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .replace(/^[^A-Za-z]+/, "");
  const ch = stripped[0]?.toUpperCase() ?? "#";
  return /[A-Z]/.test(ch) ? ch : "#";
}

function symmetrize(list: Term[]): Term[] {
  const map = new Map(list.map((term) => [term.slug, { ...term, related: [...new Set(term.related)] }]));
  for (const term of map.values()) {
    for (const slug of [...term.related]) {
      const other = map.get(slug);
      if (!other || slug === term.slug) continue;
      if (!other.related.includes(term.slug)) other.related.push(term.slug);
    }
  }
  for (const term of map.values()) {
    term.related = term.related.filter((slug) => slug !== term.slug && map.has(slug)).sort();
  }
  return [...map.values()];
}

let cached: Term[] | null = null;

export function getTerms(): Term[] {
  if (cached) return cached;
  const list = Object.values(modules);
  cached = symmetrize(list).sort((a, b) => a.term.localeCompare(b.term, "en"));
  return cached;
}

export function getTerm(slug: string): Term | undefined {
  return getTerms().find((term) => term.slug === slug);
}

export function termsInCategory(category: CategoryId): Term[] {
  return getTerms().filter((term) => term.category === category);
}

export function displayName(term: Term, lang: Lang): string {
  return lang === "es" ? term.es.term : term.term;
}

export function displayDefinition(term: Term, lang: Lang): string {
  return lang === "es" ? term.es.definition : term.definition;
}

export function sortTerms(terms: Term[], lang: Lang): Term[] {
  return [...terms].sort((a, b) =>
    displayName(a, lang).localeCompare(displayName(b, lang), lang === "es" ? "es" : "en"),
  );
}

export function groupByLetter(terms: Term[], lang: Lang): { letter: string; terms: Term[] }[] {
  const sorted = sortTerms(terms, lang);
  const groups = new Map<string, Term[]>();
  for (const term of sorted) {
    const letter = letterOf(displayName(term, lang));
    const bucket = groups.get(letter) ?? [];
    bucket.push(term);
    groups.set(letter, bucket);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([letter, grouped]) => ({ letter, terms: grouped }));
}

export function relatedTerms(term: Term): Term[] {
  const all = getTerms();
  return term.related
    .map((slug) => all.find((item) => item.slug === slug))
    .filter((item): item is Term => Boolean(item));
}

export function pathsForTerm(slug: string): { path: LearningPath; index: number }[] {
  const found: { path: LearningPath; index: number }[] = [];
  for (const path of paths) {
    const index = path.steps.findIndex((step) => step.slug === slug);
    if (index >= 0) found.push({ path, index });
  }
  return found;
}

export function resolvedCitations(term: Term): Citation[] {
  return term.citations
    .map((id) => citationMap.get(id))
    .filter((citation): citation is Citation => Boolean(citation));
}

export function termsCitingPart(partId: string): Term[] {
  return getTerms().filter((term) =>
    term.citations.some((id) => citationMap.get(id)?.partId === partId),
  );
}

export function partCounts(): Map<string, number> {
  const counts = new Map<string, number>();
  for (const part of parts) counts.set(part.id, termsCitingPart(part.id).length);
  return counts;
}

export function searchRecords(): SearchRecord[] {
  return getTerms().map((term) => ({
    slug: term.slug,
    term: term.term,
    esTerm: term.es.term,
    aliases: term.aliases.join(" | "),
    esAliases: term.es.aliases.join(" | "),
    category: term.category,
    definition: term.definition.slice(0, 220),
    esDefinition: term.es.definition.slice(0, 220),
    letter: letterOf(term.term),
    esLetter: letterOf(term.es.term),
  }));
}

export function categoryLabel(id: CategoryId, lang: Lang): string {
  const category = categoryMap.get(id);
  if (!category) return id;
  return lang === "es" ? category.esLabel : category.label;
}

export const HOME_PARTS = ["1026", "1024", "1002", "1003", "1022", "1016", "1008", "hpa", "udaap", "fannie"];

export function excerpt(text: string, max = 180): string {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  return `${clean.slice(0, max - 1).trimEnd()}…`;
}
