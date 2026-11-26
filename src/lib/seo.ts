import type { Lang, Term } from "./types";
import { displayName, excerpt, resolvedCitations } from "./content";
import { hrefFor } from "./i18n";

export function metaDescription(text: string, max = 160): string {
  return excerpt(text, max);
}

export function termJsonLd(term: Term, lang: Lang, origin: string) {
  const name = displayName(term, lang);
  const otherName = lang === "es" ? term.term : term.es.term;
  const aliases = lang === "es" ? term.es.aliases : term.aliases;
  const definition = lang === "es" ? term.es.definition : term.definition;
  const pageUrl = new URL(hrefFor(lang, `/terms/${term.slug}`), origin + "/").toString();
  const termsSet = new URL(hrefFor(lang, "/terms"), origin + "/").toString();
  const citations = resolvedCitations(term).map((source) => ({
    "@type": "CreativeWork",
    name: source.label,
    url: source.url,
  }));
  return {
    "@context": "https://schema.org",
    "@type": "DefinedTerm",
    name,
    alternateName: [otherName, ...aliases].filter(Boolean),
    description: definition,
    inLanguage: lang,
    inDefinedTermSet: termsSet,
    url: pageUrl,
    dateModified: term.reviewed,
    citation: citations,
  };
}
