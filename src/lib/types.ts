export const CATEGORY_IDS = [
  "origination",
  "underwriting",
  "compliance",
  "closing",
  "servicing",
  "loan-programs",
  "borrower-faqs",
] as const;

export type CategoryId = (typeof CATEGORY_IDS)[number];
export type Lang = "en" | "es";
export type CitationKind = "regulation" | "statute" | "agency-guide" | "industry-practice";

export interface Citation {
  id: string;
  label: string;
  title: string;
  url: string;
  cfpbUrl?: string;
  interpUrl?: string;
  kind: CitationKind;
  partId: string;
}

export interface Part {
  id: string;
  label: string;
  short: string;
  name: string;
  summary: string;
  url: string;
}

export interface ExampleBlock {
  setting: string;
  text: string;
}

export interface SpanishTerm {
  term: string;
  aliases: string[];
  definition: string;
  details: string;
  complianceNotes: string;
  example: ExampleBlock;
}

export interface Term {
  slug: string;
  term: string;
  aliases: string[];
  category: CategoryId;
  definition: string;
  details: string;
  complianceNotes: string;
  example: ExampleBlock;
  citations: string[];
  related: string[];
  reviewed: string;
  reviewFlag?: string;
  es: SpanishTerm;
}

export interface PathStep {
  slug: string;
  note: string;
  esNote: string;
}

export interface LearningPath {
  slug: string;
  title: string;
  esTitle: string;
  summary: string;
  esSummary: string;
  audience: "professional" | "borrower";
  steps: PathStep[];
}

export interface Trending {
  heading: string;
  esHeading: string;
  disclosure: string;
  esDisclosure: string;
  slugs: string[];
}

export interface SearchRecord {
  slug: string;
  term: string;
  esTerm: string;
  aliases: string;
  esAliases: string;
  category: CategoryId;
  definition: string;
  esDefinition: string;
  letter: string;
  esLetter: string;
  parts: string;
}
