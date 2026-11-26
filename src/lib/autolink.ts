import type { Lang, Term } from "./types";

/** Generic one-word aliases that would over-link ordinary English or Spanish. */
const SKIP_ALIASES = new Set([
  "toolkit",
  "cure",
  "points",
  "puntos",
  "lock",
  "total",
]);

const CITE_PHRASE = /^(?:\d+\s*(?:c\.?\s*f\.?\s*r\.?|u\.?\s*s\.?\s*c\.?)\b)/i;
const CITE_SPAN =
  /\b\d+\s*(?:C\.?\s*F\.?\s*R\.?|U\.?\s*S\.?\s*C\.?)\s*§?\s*[\d.]+|\b§\s*\d[\d.]*\b|https?:\/\/\S+/gi;

export interface LinkSegment {
  text: string;
  href?: string;
  slug?: string;
  preview?: string;
}

export interface Phrase {
  slug: string;
  folded: string;
  length: number;
  acronym: boolean;
}

export function fold(s: string): string {
  return s
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLowerCase();
}

function foldMap(s: string): { folded: string; index: number[] } {
  const chars: string[] = [];
  const index: number[] = [];
  for (let i = 0; i < s.length; ) {
    const cp = s.codePointAt(i)!;
    const ch = String.fromCodePoint(cp);
    const next = i + ch.length;
    for (const c of ch.normalize("NFD")) {
      if (/\p{M}/u.test(c)) continue;
      chars.push(c.toLowerCase());
      index.push(i);
    }
    i = next;
  }
  return { folded: chars.join(""), index };
}

function isWordChar(ch: string | undefined): boolean {
  return Boolean(ch && /\p{L}|\p{N}/u.test(ch));
}

function isBoundary(folded: string, start: number, length: number): boolean {
  const left = start === 0 || !isWordChar(folded[start - 1]);
  const end = start + length;
  const right = end >= folded.length || !isWordChar(folded[end]);
  return left && right;
}

function originalRange(text: string, index: number[], start: number, length: number): [number, number] {
  const from = index[start];
  const last = index[start + length - 1];
  const cp = text.codePointAt(last)!;
  const to = last + String.fromCodePoint(cp).length;
  return [from, to];
}

function isAcronymLabel(label: string): boolean {
  return /^[A-Za-z]{2,5}$/.test(label);
}

function citationRanges(text: string): Array<[number, number]> {
  const ranges: Array<[number, number]> = [];
  for (const match of text.matchAll(CITE_SPAN)) {
    if (match.index !== undefined) ranges.push([match.index, match.index + match[0].length]);
  }
  return ranges;
}

function overlaps(ranges: Array<[number, number]>, from: number, to: number): boolean {
  return ranges.some(([a, b]) => from < b && to > a);
}

function excerpt(text: string, max = 140): string {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  return `${clean.slice(0, max - 1).trimEnd()}…`;
}

export function buildPhrases(terms: Term[], lang: Lang): Phrase[] {
  const phrases: Phrase[] = [];
  const seen = new Set<string>();
  for (const term of terms) {
    const labels =
      lang === "es"
        ? [term.es.term, ...term.es.aliases]
        : [term.term, ...term.aliases];
    for (const [i, label] of labels.entries()) {
      const trimmed = label.trim();
      if (!trimmed || CITE_PHRASE.test(trimmed)) continue;
      if (i > 0 && SKIP_ALIASES.has(fold(trimmed))) continue;
      const folded = fold(trimmed);
      if (folded.length < 2) continue;
      const key = `${term.slug}::${folded}`;
      if (seen.has(key)) continue;
      seen.add(key);
      phrases.push({
        slug: term.slug,
        folded,
        length: folded.length,
        acronym: isAcronymLabel(trimmed),
      });
    }
  }
  phrases.sort((a, b) => b.length - a.length || a.folded.localeCompare(b.folded));
  return phrases;
}

export interface LinkOptions {
  lang: Lang;
  currentSlug: string;
  terms: Term[];
  hrefFor: (slug: string) => string;
  phrases?: Phrase[];
}

/**
 * Link the first mention of each other glossary term in a definition.
 * Longest match wins, word-boundary, case- and accent-insensitive.
 * Acronyms (2–5 letters) match only when the source token is uppercase.
 * Never links a term to itself. Skips legal citation spans (CFR, U.S.C., §, URLs).
 */
export function linkDefinition(text: string, options: LinkOptions): LinkSegment[] {
  const { currentSlug, terms, hrefFor, lang } = options;
  const phrases = options.phrases ?? buildPhrases(terms, lang);
  const bySlug = new Map(terms.map((term) => [term.slug, term]));
  const { folded, index } = foldMap(text);
  const skips = citationRanges(text);
  const used = new Set<string>([currentSlug]);
  const taken = new Uint8Array(folded.length);
  const hits: Array<{ from: number; to: number; slug: string }> = [];

  for (const phrase of phrases) {
    if (used.has(phrase.slug)) continue;
    if (phrase.folded.length > folded.length) continue;
    let searchFrom = 0;
    while (searchFrom <= folded.length - phrase.length) {
      const at = folded.indexOf(phrase.folded, searchFrom);
      if (at < 0) break;
      searchFrom = at + 1;
      if (!isBoundary(folded, at, phrase.length)) continue;
      let occupied = false;
      for (let i = 0; i < phrase.length; i++) {
        if (taken[at + i]) {
          occupied = true;
          break;
        }
      }
      if (occupied) continue;
      const [from, to] = originalRange(text, index, at, phrase.length);
      if (overlaps(skips, from, to)) continue;
      if (phrase.acronym) {
        const token = text.slice(from, to);
        if (token !== token.toUpperCase()) continue;
      }
      for (let i = 0; i < phrase.length; i++) taken[at + i] = 1;
      used.add(phrase.slug);
      hits.push({ from, to, slug: phrase.slug });
      break; // first mention of this slug only
    }
  }

  hits.sort((a, b) => a.from - b.from);
  const segments: LinkSegment[] = [];
  let cursor = 0;
  for (const hit of hits) {
    if (hit.from > cursor) segments.push({ text: text.slice(cursor, hit.from) });
    const term = bySlug.get(hit.slug);
    const preview = term
      ? excerpt(lang === "es" ? term.es.definition : term.definition)
      : undefined;
    segments.push({
      text: text.slice(hit.from, hit.to),
      href: hrefFor(hit.slug),
      slug: hit.slug,
      preview,
    });
    cursor = hit.to;
  }
  if (cursor < text.length) segments.push({ text: text.slice(cursor) });
  if (segments.length === 0) segments.push({ text });
  return segments;
}

export function linkedSlugs(segments: LinkSegment[]): string[] {
  return segments.filter((segment) => segment.slug).map((segment) => segment.slug!);
}
