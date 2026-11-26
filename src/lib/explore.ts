/**
 * Progressive-disclosure explorer ("start simple, go as deep as you like").
 *
 * Pure, framework-free engine shared by the build (root screen, data file),
 * the browser script, and scripts/checks/check-explore.ts. The question layer
 * comes from src/data/explore-tree.json; every layer below a leaf is generated
 * from the glossary's own data (terms, related terms, citations, regulation
 * parts, learning paths, topics), so the tree grows with the glossary.
 *
 * Navigation is a stack of option ids kept in the URL hash
 * (#/buy/start/afford/t-credit-score/ex). Back always pops one level, so the
 * term graph's natural cycles can never trap a reader.
 */

export type ExploreLang = "en" | "es";
type Localized = { en: string; es: string };

export interface TreeSpec {
  id: string;
  label: Localized;
  hint?: Localized;
  q?: Localized;
  children?: TreeSpec[];
  terms?: string[];
  path?: string;
  category?: string;
  generate?: "paths" | "parts" | "categories";
}

export interface ExploreTerm {
  /** display name */ n: string;
  /** plain-language definition */ d: string;
  /** regulation detail */ h: string;
  /** example [setting, text] */ x: [string, string];
  /** compliance notes */ w: string;
  /** category id */ c: string;
  /** related slugs */ r: string[];
  /** citation ids */ s: string[];
}

export interface ExploreData {
  lang: ExploreLang;
  tree: TreeSpec;
  terms: Record<string, ExploreTerm>;
  cites: Record<string, { l: string; t: string; u: string; p: string; k: string }>;
  parts: { id: string; l: string; s: string; n: string }[];
  paths: { slug: string; t: string; steps: string[]; notes: string[] }[];
  cats: { id: string; l: string }[];
}

export interface Option {
  id: string;
  label: string;
  hint?: string;
}

export type Body =
  | { type: "text"; title?: string; text: string; tag?: string }
  | { type: "example"; setting: string; text: string; tag: string }
  | { type: "cites"; items: { label: string; title: string; url: string }[] };

export interface Screen {
  key: string;
  kind: "question" | "list" | "term" | "term-view";
  crumb: string;
  kicker?: string;
  heading: string;
  prompt: string;
  body: Body[];
  options: Option[];
  termSlug?: string;
}

/** Lists longer than this are split into smaller groups (another layer). */
export const MAX_OPTIONS = 12;
const CHUNK = 10;

export const EXPLORE_UI = {
  en: {
    title: "Find your way in",
    dek: "Start with one simple question. Each answer opens the next layer, from a topic to a term to the rule behind it. Go back or start over any time.",
    homeKicker: "Not sure where to start?",
    homeTitle: "Answer a question, then go as deep as you like",
    homeMore: "Open the guided explorer",
    start: "Start",
    back: "Back",
    startOver: "Start over",
    youAreHere: "Your path",
    goDeeper: "Go deeper",
    pickOne: "Pick one to go deeper.",
    pickTerm: "Pick a term to open it.",
    pickStep: "Pick a step. The path reads in this order.",
    pickRange: "This list is long. Pick a range to narrow it down.",
    pickPart: "Pick an authority to see the entries that cite it.",
    pickTopic: "Pick a topic.",
    pickPath: "Pick a learning path.",
    readFull: "Read the full entry",
    how: "How the rule works",
    howHint: "The regulation detail behind the definition.",
    example: "See it on the form or in the file",
    exampleHint: "An illustrative example.",
    exampleTag: "Illustrative example. Sample figures are not a current limit, fee, or quote.",
    why: "Why it matters to compliance",
    whyHint: "What an originator, underwriter, or examiner watches.",
    related: "Related terms",
    relatedHint: "Terms that connect to this one.",
    rules: "Sources behind it",
    rulesHint: "The regulation, statute, or guide it cites.",
    inPaths: "Learning paths with this term",
    inPathsHint: "Read it in context, step by step.",
    moreUnder: "More entries citing",
    moreUnderHint: "Every entry that cites this authority.",
    more: "More",
    moreHint: "The rest of this list.",
    terms: "terms",
    entries: "entries",
    steps: "steps",
    step: "Step",
    kindRegulation: "Regulations",
    kindRegulationHint: "Parts of the Code of Federal Regulations.",
    kindStatute: "Statutes",
    kindStatuteHint: "The laws behind the regulations.",
    kindGuide: "Agency and investor guides",
    kindGuideHint: "FHA, VA, USDA, Fannie Mae, Freddie Mac, CFPB, and others.",
    kindPractice: "Industry practice",
    kindPracticeHint: "Common practice with no single governing rule.",
    regsQ: "What kind of source?",
    loading: "Loading the next layer…",
    failed: "The next layer did not load. Check your connection and try again.",
    noscript: "The guided explorer needs JavaScript. You can still browse every term or follow a learning path.",
    browseAll: "Browse the glossary",
    allPaths: "Learning paths",
    otherWays: "Prefer to browse?",
    railTitle: "Keep exploring",
    railLink: "Go deeper from this term",
    railDek: "Examples, sources, and related terms, one layer at a time.",
  },
  es: {
    title: "Encuentre por dónde empezar",
    dek: "Empiece con una pregunta sencilla. Cada respuesta abre la siguiente capa: de un tema a un término y a la norma que lo respalda. Puede volver o empezar de nuevo en cualquier momento.",
    homeKicker: "¿No sabe por dónde empezar?",
    homeTitle: "Responda una pregunta y profundice cuanto quiera",
    homeMore: "Abrir el explorador guiado",
    start: "Inicio",
    back: "Volver",
    startOver: "Empezar de nuevo",
    youAreHere: "Su recorrido",
    goDeeper: "Profundizar",
    pickOne: "Elija una opción para profundizar.",
    pickTerm: "Elija un término para abrirlo.",
    pickStep: "Elija un paso. La ruta se lee en este orden.",
    pickRange: "La lista es larga. Elija un rango para acotarla.",
    pickPart: "Elija una fuente para ver las entradas que la citan.",
    pickTopic: "Elija un tema.",
    pickPath: "Elija una ruta de aprendizaje.",
    readFull: "Leer la entrada completa",
    how: "Cómo funciona la norma",
    howHint: "El detalle del reglamento detrás de la definición.",
    example: "Verlo en el formulario o el expediente",
    exampleHint: "Un ejemplo ilustrativo.",
    exampleTag: "Ejemplo ilustrativo. Las cifras de muestra no son un límite, cargo ni cotización vigente.",
    why: "Por qué importa para el cumplimiento",
    whyHint: "Lo que vigila un originador, un suscriptor o un examinador.",
    related: "Términos relacionados",
    relatedHint: "Términos que se conectan con este.",
    rules: "Fuentes que lo respaldan",
    rulesHint: "El reglamento, la ley o la guía que cita.",
    inPaths: "Rutas de aprendizaje con este término",
    inPathsHint: "Léalo en contexto, paso a paso.",
    moreUnder: "Más entradas que citan",
    moreUnderHint: "Todas las entradas que citan esta fuente.",
    more: "Más",
    moreHint: "El resto de esta lista.",
    terms: "términos",
    entries: "entradas",
    steps: "pasos",
    step: "Paso",
    kindRegulation: "Reglamentos",
    kindRegulationHint: "Partes del Código de Reglamentos Federales.",
    kindStatute: "Leyes",
    kindStatuteHint: "Las leyes detrás de los reglamentos.",
    kindGuide: "Guías de agencias e inversionistas",
    kindGuideHint: "FHA, VA, USDA, Fannie Mae, Freddie Mac, la CFPB y otras.",
    kindPractice: "Práctica de la industria",
    kindPracticeHint: "Práctica común sin una sola norma que la rija.",
    regsQ: "¿Qué tipo de fuente?",
    loading: "Cargando la siguiente capa…",
    failed: "La siguiente capa no se cargó. Revise su conexión e inténtelo de nuevo.",
    noscript: "El explorador guiado necesita JavaScript. Aun así puede ver todos los términos o seguir una ruta de aprendizaje.",
    browseAll: "Ver el glosario",
    allPaths: "Rutas de aprendizaje",
    otherWays: "¿Prefiere explorar por su cuenta?",
    railTitle: "Siga explorando",
    railLink: "Profundizar desde este término",
    railDek: "Ejemplos, fuentes y términos relacionados, una capa a la vez.",
  },
} as const;

export type ExploreUi = (typeof EXPLORE_UI)["en"];

/* ------------------------------------------------------------------ nodes */

type TermView = "how" | "ex" | "why" | "rel" | "rules" | "inpaths";
const TERM_VIEWS: TermView[] = ["how", "ex", "why", "rel", "rules", "inpaths"];
const KINDS = ["regulation", "statute", "agency-guide", "industry-practice"] as const;
type Kind = (typeof KINDS)[number];

export type Node =
  | { t: "spec"; spec: TreeSpec }
  | { t: "terms"; key: string; title: string; slugs: string[]; hints?: Record<string, string>; sorted: boolean }
  | { t: "path"; slug: string }
  | { t: "paths"; key: string; title: string; slugs: string[] }
  | { t: "kinds" }
  | { t: "parts"; key: string; title: string; ids: string[] }
  | { t: "cats" }
  | { t: "term"; slug: string }
  | { t: "view"; slug: string; view: TermView };

export function nodeKey(node: Node): string {
  switch (node.t) {
    case "spec": return `spec:${node.spec.id}`;
    case "terms": return node.key;
    case "path": return `path:${node.slug}`;
    case "paths": return node.key;
    case "kinds": return "kinds";
    case "parts": return node.key;
    case "cats": return "cats";
    case "term": return `term:${node.slug}`;
    case "view": return `view:${node.slug}:${node.view}`;
  }
}

export function createExplorer(data: ExploreData) {
  const lang = data.lang;
  const ui: ExploreUi = EXPLORE_UI[lang];
  const terms = data.terms;
  const collator = new Intl.Collator(lang, { sensitivity: "base", numeric: true });
  const pathBySlug = new Map(data.paths.map((p) => [p.slug, p]));
  const partById = new Map(data.parts.map((p) => [p.id, p]));
  const catById = new Map(data.cats.map((c) => [c.id, c]));

  // Derived indexes (built once).
  const termsByPart = new Map<string, string[]>();
  const partsByTerm = new Map<string, string[]>();
  for (const [slug, term] of Object.entries(terms)) {
    const ids = [...new Set(term.s.map((id) => data.cites[id]?.p).filter((p): p is string => Boolean(p)))];
    partsByTerm.set(slug, ids);
    for (const id of ids) {
      if (!termsByPart.has(id)) termsByPart.set(id, []);
      termsByPart.get(id)!.push(slug);
    }
  }
  const partKind = new Map<string, Kind>();
  for (const part of data.parts) {
    const counts = new Map<Kind, number>();
    for (const cite of Object.values(data.cites)) {
      if (cite.p === part.id) counts.set(cite.k as Kind, (counts.get(cite.k as Kind) ?? 0) + 1);
    }
    let best: Kind = "regulation";
    let bestN = -1;
    for (const kind of KINDS) {
      const n = counts.get(kind) ?? 0;
      if (n > bestN) { best = kind; bestN = n; }
    }
    partKind.set(part.id, best);
  }
  const pathsByTerm = new Map<string, string[]>();
  for (const path of data.paths) {
    for (const step of path.steps) {
      if (!pathsByTerm.has(step)) pathsByTerm.set(step, []);
      if (!pathsByTerm.get(step)!.includes(path.slug)) pathsByTerm.get(step)!.push(path.slug);
    }
  }

  const has = (slug: string) => Object.prototype.hasOwnProperty.call(terms, slug);
  const name = (slug: string) => terms[slug]?.n ?? slug;
  const clip = (text: string, max = 96) => {
    const clean = text.replace(/\s+/g, " ").trim();
    if (clean.length <= max) return clean;
    const cut = clean.slice(0, max - 1);
    const space = cut.lastIndexOf(" ");
    return `${(space > max * 0.6 ? cut.slice(0, space) : cut).replace(/[\s,;:.]+$/, "")}…`;
  };
  const firstSentence = (text: string) => {
    const m = text.replace(/\s+/g, " ").trim().match(/^.+?[.?!](?=\s|$)/);
    return clip(m ? m[0] : text);
  };
  const sortSlugs = (slugs: string[]) => [...slugs].sort((a, b) => collator.compare(name(a), name(b)));
  const initial = (s: string) => {
    const ch = s.replace(/^[^\p{L}\p{N}]+/u, "").charAt(0).toLocaleUpperCase(lang);
    return /\p{N}/u.test(ch) ? "#" : ch;
  };
  const partsForTerm = (slug: string) => (partsByTerm.get(slug) ?? []).filter((id) => partById.has(id));
  const pathsForTerm = (slug: string) => (pathsByTerm.get(slug) ?? []).filter((id) => pathBySlug.has(id));
  const relatedOf = (slug: string) => [...new Set(terms[slug]?.r ?? [])].filter((r) => r !== slug && has(r));
  const partLabel = (id: string) => {
    const part = partById.get(id)!;
    return part.s && part.s !== part.l ? `${part.s} · ${part.l}` : part.l;
  };

  function chunks<T>(items: T[]): T[][] {
    // Up to CHUNK groups of about CHUNK; a very long list gets groups of groups.
    let k = Math.ceil(items.length / CHUNK);
    if (k > MAX_OPTIONS) k = CHUNK;
    const size = Math.ceil(items.length / k);
    const out: T[][] = [];
    for (let i = 0; i < items.length; i += size) out.push(items.slice(i, i + size));
    return out;
  }
  const count = (n: number, unit: string) => `${n} ${unit}`;

  const root: Node = { t: "spec", spec: data.tree };

  function termListNode(key: string, title: string, slugs: string[], sorted = false, hints?: Record<string, string>): Node {
    const clean = [...new Set(slugs.filter(has))];
    return { t: "terms", key, title, slugs: sorted ? sortSlugs(clean) : clean, hints, sorted };
  }

  function specLeaf(spec: TreeSpec): Node | null {
    if (spec.terms) return null;
    if (spec.path) return { t: "path", slug: spec.path };
    if (spec.category) {
      const slugs = Object.keys(terms).filter((s) => terms[s].c === spec.category);
      return termListNode(`cat:${spec.category}`, catById.get(spec.category)?.l ?? spec.label[lang], slugs, true);
    }
    if (spec.generate === "paths") return { t: "paths", key: "paths", title: spec.label[lang], slugs: data.paths.map((p) => p.slug) };
    if (spec.generate === "parts") return { t: "kinds" };
    if (spec.generate === "categories") return { t: "cats" };
    return null;
  }

  /** The options a node offers, in display order. */
  function options(node: Node): Option[] {
    switch (node.t) {
      case "spec": {
        const spec = node.spec;
        if (spec.children) {
          return spec.children.map((c) => ({ id: c.id, label: c.label[lang], hint: c.hint?.[lang] }));
        }
        if (spec.terms) return termListOptions(termListNode(`spec:${spec.id}`, spec.label[lang], spec.terms) as Extract<Node, { t: "terms" }>);
        const leaf = specLeaf(spec);
        return leaf ? options(leaf) : [];
      }
      case "terms":
        return termListOptions(node);
      case "path": {
        const path = pathBySlug.get(node.slug);
        if (!path) return [];
        return path.steps
          .map((slug, i) => ({ slug, i }))
          .filter(({ slug }) => has(slug))
          .map(({ slug, i }) => ({ id: `t-${slug}`, label: `${i + 1}. ${name(slug)}`, hint: path.notes[i] || firstSentence(terms[slug].d) }));
      }
      case "paths": {
        if (node.slugs.length > MAX_OPTIONS) {
          const head = node.slugs.slice(0, CHUNK);
          return [
            ...head.map((slug) => pathOption(slug)),
            { id: "more", label: `${ui.more} (${node.slugs.length - CHUNK})`, hint: ui.moreHint },
          ];
        }
        return node.slugs.filter((s) => pathBySlug.has(s)).map((slug) => pathOption(slug));
      }
      case "kinds": {
        const labels: Record<Kind, [string, string]> = {
          regulation: [ui.kindRegulation, ui.kindRegulationHint],
          statute: [ui.kindStatute, ui.kindStatuteHint],
          "agency-guide": [ui.kindGuide, ui.kindGuideHint],
          "industry-practice": [ui.kindPractice, ui.kindPracticeHint],
        };
        return KINDS.filter((k) => partsOfKind(k).length > 0).map((k) => ({
          id: `k-${k}`,
          label: `${labels[k][0]} (${partsOfKind(k).length})`,
          hint: labels[k][1],
        }));
      }
      case "parts": {
        const ids = node.ids;
        const shown = ids.length > MAX_OPTIONS ? ids.slice(0, CHUNK) : ids;
        const opts: Option[] = shown.map((id) => ({
          id: `r-${id}`,
          label: partLabel(id),
          hint: `${partById.get(id)!.n} · ${count(termsByPart.get(id)?.length ?? 0, ui.entries)}`,
        }));
        if (ids.length > MAX_OPTIONS) opts.push({ id: "more", label: `${ui.more} (${ids.length - CHUNK})`, hint: ui.moreHint });
        return opts;
      }
      case "cats":
        return data.cats
          .map((c) => ({ c, n: Object.values(terms).filter((t) => t.c === c.id).length }))
          .filter(({ n }) => n > 0)
          .map(({ c, n }) => ({ id: `c-${c.id}`, label: c.l, hint: count(n, ui.terms) }));
      case "term":
        return termViewOptions(node.slug, null);
      case "view": {
        const slug = node.slug;
        if (node.view === "rel") {
          return termListOptions(termListNode(`rel:${slug}`, "", relatedOf(slug), true) as Extract<Node, { t: "terms" }>);
        }
        if (node.view === "rules") {
          return partsForTerm(slug).map((id) => ({
            id: `r-${id}`,
            label: `${ui.moreUnder} ${partById.get(id)!.s || partById.get(id)!.l} (${termsByPart.get(id)?.length ?? 0})`,
            hint: partById.get(id)!.n,
          }));
        }
        if (node.view === "inpaths") return pathsForTerm(slug).map((p) => pathOption(p));
        return termViewOptions(slug, node.view);
      }
    }
  }

  function pathOption(slug: string): Option {
    const path = pathBySlug.get(slug)!;
    return { id: `p-${slug}`, label: path.t, hint: count(path.steps.filter(has).length, ui.steps) };
  }

  function partsOfKind(kind: Kind): string[] {
    return data.parts
      .map((p) => p.id)
      .filter((id) => partKind.get(id) === kind && (termsByPart.get(id)?.length ?? 0) > 0)
      .sort((a, b) => (termsByPart.get(b)!.length - termsByPart.get(a)!.length) || collator.compare(partLabel(a), partLabel(b)));
  }

  function termListOptions(node: Extract<Node, { t: "terms" }>): Option[] {
    const slugs = node.slugs;
    if (slugs.length > MAX_OPTIONS) {
      const sorted = node.sorted ? slugs : sortSlugs(slugs);
      return chunks(sorted).map((group, i) => {
        const a = initial(name(group[0]));
        const b = initial(name(group[group.length - 1]));
        return {
          id: `g${i + 1}`,
          label: a === b ? `${a}: ${name(group[0])} – ${name(group[group.length - 1])}` : `${a}–${b}`,
          hint: `${name(group[0])} … ${name(group[group.length - 1])} · ${count(group.length, ui.terms)}`,
        };
      });
    }
    return slugs.map((slug) => ({ id: `t-${slug}`, label: name(slug), hint: node.hints?.[slug] ?? firstSentence(terms[slug].d) }));
  }

  function termViewOptions(slug: string, current: TermView | null): Option[] {
    const term = terms[slug];
    const out: Option[] = [];
    const add = (view: TermView, label: string, hint: string) => {
      if (view !== current) out.push({ id: view, label, hint });
    };
    if (term.h) add("how", ui.how, ui.howHint);
    if (term.x[1]) add("ex", ui.example, term.x[0] || ui.exampleHint);
    if (term.w) add("why", ui.why, ui.whyHint);
    const rel = relatedOf(slug).length;
    if (rel) add("rel", `${ui.related} (${rel})`, ui.relatedHint);
    const cites = term.s.filter((id) => data.cites[id]).length;
    if (cites) add("rules", `${ui.rules} (${cites})`, ui.rulesHint);
    const inPaths = pathsForTerm(slug).length;
    if (inPaths) add("inpaths", `${ui.inPaths} (${inPaths})`, ui.inPathsHint);
    return out;
  }

  /** Follow one option id from a node. Returns null for an unknown id. */
  function child(node: Node, id: string): Node | null {
    if (id.startsWith("t-")) {
      const slug = id.slice(2);
      return has(slug) && options(node).some((o) => o.id === id) ? { t: "term", slug } : null;
    }
    switch (node.t) {
      case "spec": {
        const spec = node.spec;
        if (spec.children) {
          const next = spec.children.find((c) => c.id === id);
          return next ? { t: "spec", spec: next } : null;
        }
        if (spec.terms) return child(termListNode(`spec:${spec.id}`, spec.label[lang], spec.terms), id);
        const leaf = specLeaf(spec);
        return leaf ? child(leaf, id) : null;
      }
      case "terms": {
        const m = id.match(/^g(\d+)$/);
        if (!m || node.slugs.length <= MAX_OPTIONS) return null;
        const sorted = node.sorted ? node.slugs : sortSlugs(node.slugs);
        const group = chunks(sorted)[Number(m[1]) - 1];
        if (!group) return null;
        const label = options(node).find((o) => o.id === id)!.label;
        return { t: "terms", key: `${node.key}/${id}`, title: `${node.title ? `${node.title} · ` : ""}${label}`, slugs: group, sorted: true, hints: node.hints };
      }
      case "paths": {
        if (id === "more" && node.slugs.length > MAX_OPTIONS) {
          return { t: "paths", key: `${node.key}/more`, title: node.title, slugs: node.slugs.slice(CHUNK) };
        }
        const slug = id.startsWith("p-") ? id.slice(2) : "";
        return node.slugs.includes(slug) && pathBySlug.has(slug) ? { t: "path", slug } : null;
      }
      case "kinds": {
        const kind = id.slice(2) as Kind;
        if (!id.startsWith("k-") || !KINDS.includes(kind) || partsOfKind(kind).length === 0) return null;
        const label = options(node).find((o) => o.id === id)!.label;
        return { t: "parts", key: `parts:${kind}`, title: label, ids: partsOfKind(kind) };
      }
      case "parts": {
        if (id === "more" && node.ids.length > MAX_OPTIONS) {
          return { t: "parts", key: `${node.key}/more`, title: node.title, ids: node.ids.slice(CHUNK) };
        }
        const pid = id.startsWith("r-") ? id.slice(2) : "";
        if (!options(node).some((o) => o.id === id)) return null;
        return termListNode(`part:${pid}`, partLabel(pid), termsByPart.get(pid) ?? [], true);
      }
      case "cats": {
        const cid = id.startsWith("c-") ? id.slice(2) : "";
        if (!catById.has(cid)) return null;
        return termListNode(`cat:${cid}`, catById.get(cid)!.l, Object.keys(terms).filter((s) => terms[s].c === cid), true);
      }
      case "path":
        return null;
      case "term":
        return (TERM_VIEWS as string[]).includes(id) && options(node).some((o) => o.id === id)
          ? { t: "view", slug: node.slug, view: id as TermView }
          : null;
      case "view": {
        const slug = node.slug;
        if (node.view === "rel") return child(termListNode(`rel:${slug}`, name(slug), relatedOf(slug), true), id);
        if (node.view === "rules") {
          const pid = id.startsWith("r-") ? id.slice(2) : "";
          if (!partsForTerm(slug).includes(pid)) return null;
          return termListNode(`part:${pid}`, partLabel(pid), termsByPart.get(pid) ?? [], true);
        }
        if (node.view === "inpaths") {
          const ps = id.startsWith("p-") ? id.slice(2) : "";
          return pathsForTerm(slug).includes(ps) ? { t: "path", slug: ps } : null;
        }
        return (TERM_VIEWS as string[]).includes(id) && options(node).some((o) => o.id === id)
          ? { t: "view", slug, view: id as TermView }
          : null;
      }
    }
  }

  /** The screen for a node; crumb is the label of the option that led here. */
  function screen(node: Node, crumb: string): Screen {
    const base = { key: nodeKey(node), crumb, options: options(node) };
    switch (node.t) {
      case "spec": {
        const spec = node.spec;
        const isQuestion = Boolean(spec.children);
        let prompt: string = ui.pickOne;
        if (!isQuestion) {
          if (spec.path) prompt = ui.pickStep;
          else if (spec.generate === "paths") prompt = ui.pickPath;
          else if (spec.generate === "parts") prompt = ui.pickPart;
          else if (spec.generate === "categories") prompt = ui.pickTopic;
          else prompt = base.options[0]?.id.startsWith("g") ? ui.pickRange : ui.pickTerm;
        }
        const heading = spec.q?.[lang] ?? (spec.path ? pathBySlug.get(spec.path)?.t ?? spec.label[lang] : spec.label[lang]);
        return {
          ...base,
          kind: isQuestion ? "question" : "list",
          kicker: spec.q && spec.id !== "root" ? spec.label[lang] : undefined,
          heading,
          prompt,
          body: [],
        };
      }
      case "terms":
        return { ...base, kind: "list", heading: node.title, prompt: base.options[0]?.id.startsWith("g") ? ui.pickRange : ui.pickTerm, body: [] };
      case "path": {
        const path = pathBySlug.get(node.slug)!;
        return { ...base, kind: "list", kicker: ui.allPaths, heading: path.t, prompt: ui.pickStep, body: [] };
      }
      case "paths":
        return { ...base, kind: "list", heading: node.title, prompt: ui.pickPath, body: [] };
      case "kinds":
        return { ...base, kind: "question", heading: ui.regsQ, prompt: ui.pickOne, body: [] };
      case "parts":
        return { ...base, kind: "list", heading: node.title, prompt: ui.pickPart, body: [] };
      case "cats":
        return { ...base, kind: "list", heading: ui.pickTopic, prompt: ui.pickOne, body: [] };
      case "term": {
        const term = terms[node.slug];
        return {
          ...base,
          kind: "term",
          termSlug: node.slug,
          kicker: catById.get(term.c)?.l,
          heading: term.n,
          prompt: ui.goDeeper,
          body: [{ type: "text", text: term.d }],
        };
      }
      case "view": {
        const term = terms[node.slug];
        const heads: Record<TermView, string> = {
          how: ui.how, ex: ui.example, why: ui.why, rel: ui.related, rules: ui.rules, inpaths: ui.inPaths,
        };
        let body: Body[] = [];
        let prompt: string = ui.goDeeper;
        if (node.view === "how") body = [{ type: "text", text: term.h }];
        if (node.view === "ex") body = [{ type: "example", setting: term.x[0], text: term.x[1], tag: ui.exampleTag }];
        if (node.view === "why") body = [{ type: "text", text: term.w }];
        if (node.view === "rules") {
          body = [{
            type: "cites",
            items: term.s.filter((id) => data.cites[id]).map((id) => ({ label: data.cites[id].l, title: data.cites[id].t, url: data.cites[id].u })),
          }];
        }
        if (node.view === "rel") prompt = base.options[0]?.id.startsWith("g") ? ui.pickRange : ui.pickTerm;
        if (node.view === "inpaths") prompt = ui.pickPath;
        return {
          ...base,
          kind: "term-view",
          termSlug: node.slug,
          kicker: term.n,
          heading: heads[node.view],
          prompt,
          body,
        };
      }
    }
  }

  /**
   * Resolve a hash path. Segments that do not resolve are dropped, so a stale
   * or mistyped link lands on the deepest valid layer instead of an error.
   * A leading "@slug" segment starts at that term (links from term pages).
   */
  function resolve(segments: string[]): { stack: { id: string; node: Node; screen: Screen }[]; valid: string[] } {
    const stack = [{ id: "", node: root, screen: screen(root, ui.start) }];
    const valid: string[] = [];
    let i = 0;
    if (segments[0]?.startsWith("@") && has(segments[0].slice(1))) {
      const node: Node = { t: "term", slug: segments[0].slice(1) };
      stack.push({ id: segments[0], node, screen: screen(node, name(segments[0].slice(1))) });
      valid.push(segments[0]);
      i = 1;
    }
    for (; i < segments.length; i++) {
      const current = stack[stack.length - 1];
      const id = segments[i];
      const opt = current.screen.options.find((o) => o.id === id);
      const next = opt ? child(current.node, id) : null;
      if (!opt || !next) break;
      stack.push({ id, node: next, screen: screen(next, opt.label) });
      valid.push(id);
    }
    return { stack, valid };
  }

  return { root, options, child, screen, resolve, nodeKey };
}

export type Explorer = ReturnType<typeof createExplorer>;

export function hashFor(segments: string[]): string {
  return segments.length ? `#/${segments.map((s) => encodeURIComponent(s).replace(/^%40/, "@")).join("/")}` : "#/";
}

export function parseHash(hash: string): string[] {
  return hash
    .replace(/^#\/?/, "")
    .split("/")
    .filter(Boolean)
    .map((s) => {
      try { return decodeURIComponent(s); } catch { return s; }
    });
}
