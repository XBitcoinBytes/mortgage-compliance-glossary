import Fuse from "fuse.js";

type View = "borrower" | "professional";
type Theme = "light" | "dark";

interface SearchRecord {
  slug: string;
  term: string;
  esTerm: string;
  aliases: string;
  esAliases: string;
  category: string;
  definition: string;
  esDefinition: string;
}

const CATEGORIES: Record<string, { en: string; es: string }> = {
  origination: { en: "Origination", es: "Originación" },
  underwriting: { en: "Underwriting", es: "Suscripción" },
  compliance: { en: "Compliance", es: "Cumplimiento" },
  closing: { en: "Closing", es: "Cierre" },
  servicing: { en: "Servicing", es: "Administración" },
  "loan-programs": { en: "Loan programs", es: "Programas de préstamo" },
  "borrower-faqs": { en: "Borrower questions", es: "Preguntas de prestatarios" },
};

function lang(): "en" | "es" {
  return document.documentElement.lang === "es" ? "es" : "en";
}

function termHref(slug: string): string {
  return lang() === "es" ? `/es/terms/${slug}` : `/terms/${slug}`;
}

function setTheme(theme: Theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("mcg-theme", theme);
  const button = document.querySelector<HTMLButtonElement>("#theme-toggle");
  const labels = document.querySelector<HTMLElement>("#theme-labels");
  if (button && labels) {
    button.setAttribute("aria-label", theme === "dark" ? labels.dataset.light ?? "" : labels.dataset.dark ?? "");
  }
}

function syncPro(view: View) {
  document.querySelectorAll<HTMLElement>("[data-pro-section]").forEach((panel) => {
    delete panel.dataset.open;
    panel.querySelector(".pro-toggle")?.setAttribute("aria-expanded", view === "professional" ? "true" : "false");
  });
}

function setView(view: View) {
  document.documentElement.dataset.view = view;
  localStorage.setItem("mcg-view", view);
  document.querySelectorAll<HTMLButtonElement>("[data-view-set]").forEach((button) => {
    button.setAttribute("aria-pressed", button.dataset.viewSet === view ? "true" : "false");
  });
  syncPro(view);
}

function currentView(): View {
  return document.documentElement.dataset.view === "borrower" ? "borrower" : "professional";
}

function initView() {
  setView(currentView());
  document.querySelectorAll<HTMLButtonElement>("[data-view-set]").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.viewSet === "borrower" ? "borrower" : "professional"));
  });
  document.querySelectorAll<HTMLButtonElement>(".pro-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const panel = button.closest<HTMLElement>("[data-pro-section]");
      if (!panel) return;
      const open = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", open ? "false" : "true");
      panel.dataset.open = open ? "false" : "true";
    });
  });
}

function initTheme() {
  const button = document.querySelector<HTMLButtonElement>("#theme-toggle");
  const theme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
  setTheme(theme);
  button?.addEventListener("click", () => {
    setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
  });
}

let indexPromise: Promise<SearchRecord[]> | null = null;
function loadIndex(): Promise<SearchRecord[]> {
  if (!indexPromise) {
    indexPromise = fetch("/search-index.json")
      .then((res) => (res.ok ? (res.json() as Promise<SearchRecord[]>) : []))
      .catch(() => {
        indexPromise = null; // allow a retry on the next open
        return [];
      });
  }
  return indexPromise;
}

function initSearch() {
  const dialog = document.querySelector<HTMLDialogElement>("#search-dialog");
  const openButton = document.querySelector<HTMLButtonElement>("#search-open");
  const closeButton = document.querySelector<HTMLButtonElement>("#search-close");
  const input = document.querySelector<HTMLInputElement>("#search-input");
  const results = document.querySelector<HTMLUListElement>("#search-results");
  const live = document.querySelector<HTMLElement>("#search-live");
  const cats = document.querySelector<HTMLElement>("#search-cats");
  const homeInput = document.querySelector<HTMLInputElement>("#home-search");
  if (!dialog || !input || !results || !cats) return;

  let records: SearchRecord[] = [];
  let fuse = new Fuse<SearchRecord>([], {});
  let ready = false;
  const fuseOptions = {
    threshold: 0.35,
    ignoreDiacritics: true,
    ignoreLocation: true,
    minMatchCharLength: 2,
    keys: [
      { name: "term", weight: 0.34 },
      { name: "esTerm", weight: 0.34 },
      { name: "aliases", weight: 0.12 },
      { name: "esAliases", weight: 0.12 },
      { name: "definition", weight: 0.04 },
      { name: "esDefinition", weight: 0.04 },
    ],
  };
  async function ensureIndex() {
    if (ready) return;
    records = await loadIndex();
    fuse = new Fuse(records, fuseOptions);
    ready = records.length > 0;
  }

  let category = "";
  let active = 0;
  const language = lang();
  const allLabel = language === "es" ? "Todos" : "All topics";

  function renderCats() {
    const ids = Object.keys(CATEGORIES);
    cats.innerHTML = "";
    const make = (id: string, label: string) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.setAttribute("aria-pressed", category === id ? "true" : "false");
      button.addEventListener("click", () => {
        category = id;
        renderCats();
        render();
      });
      cats.append(button);
    };
    make("", allLabel);
    ids.forEach((id) => make(id, CATEGORIES[id][language]));
  }

  const norm = (value: string) => value.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().trim();
  function exactHits(query: string): SearchRecord[] {
    const q = norm(query);
    const names = (item: SearchRecord) =>
      [item.term, item.esTerm, ...item.aliases.split("|"), ...item.esAliases.split("|")].map(norm);
    const exact = records.filter((item) => names(item).includes(q));
    // An exact name or acronym match outranks fuzzy matches; the term's own name outranks an alias.
    return exact.sort((a, b) => Number(norm(b.term) === q || norm(b.esTerm) === q) - Number(norm(a.term) === q || norm(a.esTerm) === q));
  }

  const STOP = new Set(["a", "an", "the", "of", "for", "to", "in", "on", "is", "my", "what", "how", "do", "i", "can", "de", "la", "el", "los", "las", "del", "y", "en", "un", "una", "que", "es", "mi"]);
  const words = (value: string) => norm(value).split(/[^a-z0-9%]+/).filter((w) => w.length > 0);
  // Word-level scorer for multi-word, natural-language queries ("denied loan letter").
  // Each query word must prefix-match a word in the name, aliases, or definition;
  // name and alias hits weigh more than definition hits.
  // Borrower phrasing -> glossary vocabulary. Small and editorial; extend from real search logs later.
  const EXPAND: Record<string, string[]> = {
    removal: ["cancellation", "termination"], remove: ["cancellation", "termination"], drop: ["cancellation", "termination"],
    cancel: ["cancellation", "rescission"], denied: ["adverse"], denial: ["adverse"], declined: ["adverse"], turned: ["adverse"],
    late: ["delinquency", "delinquent"], behind: ["delinquency", "delinquent"], missed: ["delinquency"],
    gfe: ["estimate"], lock: ["lock"], fee: ["fee", "charge"], fees: ["fees", "charges"],
  };
  const COMMON = new Set(["loan", "loans", "mortgage", "home", "credit", "payment", "rate", "prestamo", "hipoteca", "hipotecario", "credito", "pago", "tasa"]);
  function wordHits(query: string): SearchRecord[] {
    const raw = words(query).filter((w) => !STOP.has(w));
    const acronyms = new Set(raw.filter((w) => w.length >= 2 && w.length <= 6));
    const q = raw;
    if (q.length < 2) return [];
    const scored: { item: SearchRecord; score: number }[] = [];
    for (const item of records) {
      const name = words(`${item.term} ${item.esTerm}`);
      const alias = words(`${item.aliases} ${item.esAliases}`);
      const body = words(`${item.definition} ${item.esDefinition}`);
      let score = 0;
      let matched = 0;
      const aliasExact = new Set(`${item.aliases} | ${item.esAliases} | ${item.term}`.split("|").map(norm));
      for (const w of q) {
        const forms = [w, ...(EXPAND[w] ?? [])];
        const hit = (list: string[]) =>
          forms.some((f) => list.some((x) => x.startsWith(f) || (f.length > 4 && x.startsWith(f.slice(0, -1)))));
        // Words that appear in many names ("loan", "mortgage") carry little signal.
        const weak = COMMON.has(w) ? 0.25 : 1;
        if (acronyms.has(w) && aliasExact.has(w)) { score += 8; matched += 1; }
        else if (hit(name)) { score += 5 * weak; matched += 1; }
        else if (hit(alias)) { score += 4 * weak; matched += 1; }
        else if (hit(body)) { score += 1 * weak; matched += 1; }
      }
      if (score >= 4 && matched >= Math.max(1, q.length - 1)) scored.push({ item, score: score + matched });
    }
    return scored.sort((a, b) => b.score - a.score).map((row) => row.item);
  }

  function pool(): SearchRecord[] {
    const query = input.value.trim();
    let list: SearchRecord[];
    if (query) {
      const exact = exactHits(query);
      const seen = new Set(exact.map((item) => item.slug));
      const byWords = wordHits(query).filter((item) => !seen.has(item.slug));
      byWords.slice(0, 5).forEach((item) => seen.add(item.slug));
      const fuzzy = fuse.search(query).map((result) => result.item).filter((item) => !seen.has(item.slug));
      // Exact names first, then the best word matches, then fuzzy (typo-tolerant) matches.
      list = [...exact, ...byWords.slice(0, 5), ...fuzzy];
    } else {
      list = records.slice(0, 12);
    }
    if (!query && records.length === 0) list = [];
    if (category) list = list.filter((item) => item.category === category);
    return list.slice(0, 20);
  }

  function render() {
    const list = pool();
    results.innerHTML = "";
    if (active >= list.length) active = 0;
    list.forEach((item, index) => {
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", index === active ? "true" : "false");
      const link = document.createElement("a");
      link.href = termHref(item.slug);
      const title = document.createElement("strong");
      title.textContent = language === "es" ? item.esTerm : item.term;
      const meta = document.createElement("small");
      const cat = CATEGORIES[item.category]?.[language] ?? item.category;
      const alt = language === "es" ? item.term : item.esTerm;
      meta.textContent = `${cat} · ${alt}`;
      link.append(title, meta);
      li.append(link);
      results.append(li);
    });
    if (list.length === 0) {
      const li = document.createElement("li");
      li.textContent = !ready
        ? language === "es"
          ? "Cargando el índice… Si no carga, use el índice A–Z."
          : "Loading the index… If it does not load, use the A–Z index."
        : language === "es"
          ? "No hay términos que coincidan."
          : "No matching terms.";
      results.append(li);
    }
    if (live) {
      live.textContent = language === "es" ? `${list.length} términos` : `${list.length} terms`;
    }
  }

  function openSearch(seed = "") {
    if (seed) input.value = seed;
    dialog.showModal();
    document.body.classList.add("dialog-open");
    renderCats();
    render();
    input.focus();
    input.select();
    if (!ready) ensureIndex().then(render);
  }

  function closeSearch() {
    dialog.close();
    document.body.classList.remove("dialog-open");
    openButton?.focus();
  }

  openButton?.addEventListener("click", () => openSearch());
  closeButton?.addEventListener("click", closeSearch);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) closeSearch();
  });
  dialog.addEventListener("close", () => document.body.classList.remove("dialog-open"));
  input.addEventListener("input", () => {
    active = 0;
    render();
  });
  input.addEventListener("keydown", (event) => {
    const links = [...results.querySelectorAll("a")];
    if (event.key === "ArrowDown") {
      event.preventDefault();
      active = Math.min(links.length - 1, active + 1);
      render();
      links[active]?.focus();
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      active = Math.max(0, active - 1);
      render();
    } else if (event.key === "Enter") {
      const href = links[active]?.getAttribute("href");
      if (href) location.href = href;
    }
  });
  results.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const links = [...results.querySelectorAll("a")];
      active += event.key === "ArrowDown" ? 1 : -1;
      if (active < 0) active = 0;
      if (active >= links.length) active = links.length - 1;
      render();
      results.querySelectorAll("a")[active]?.focus();
    }
  });

  function visibleBrowseInput() {
    const browse = document.querySelector<HTMLInputElement>("#browse-q");
    if (browse && browse.getClientRects().length) return browse;
    return null;
  }

  function openBrowseOrSearch() {
    const browse = visibleBrowseInput();
    if (browse) {
      browse.focus();
      browse.select();
      return;
    }
    openSearch();
  }

  document.addEventListener("keydown", (event) => {
    const target = event.target as HTMLElement | null;
    const typing = target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA");
    if (event.key === "/" && !typing) {
      event.preventDefault();
      openBrowseOrSearch();
    }
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openBrowseOrSearch();
    }
  });

  homeInput?.addEventListener("focus", () => openSearch(homeInput.value));
  homeInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      openSearch(homeInput.value);
    }
  });
}

function initShare() {
  document.querySelectorAll<HTMLButtonElement>("[data-copy-link]").forEach((button) => {
    button.addEventListener("click", async () => {
      // Share the canonical URL plus the current section anchor, and the reader's view.
      const url = new URL(button.dataset.copyLink ?? location.href);
      if (location.hash) url.hash = location.hash;
      if (currentView() === "borrower") url.searchParams.set("view", "borrower");
      const text = url.toString();
      let ok = false;
      try {
        await navigator.clipboard.writeText(text);
        ok = true;
      } catch {
        const area = document.createElement("textarea");
        area.value = text;
        document.body.append(area);
        area.select();
        ok = document.execCommand("copy");
        area.remove();
      }
      const status = document.querySelector<HTMLElement>("#copy-status");
      if (status && ok) status.textContent = button.dataset.copied ?? "";
      if (ok) {
        const label = button.textContent;
        button.textContent = button.dataset.copied ?? label;
        setTimeout(() => (button.textContent = label), 1800);
      }
    });
  });
}

export function initChrome() {
  initShare();
  initTheme();
  initView();
  initSearch();
}
