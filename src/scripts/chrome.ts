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

  function pool(): SearchRecord[] {
    const query = input.value.trim();
    let list = query ? fuse.search(query).map((result) => result.item) : records.slice(0, 12);
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

  document.addEventListener("keydown", (event) => {
    const target = event.target as HTMLElement | null;
    const typing = target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA");
    if (event.key === "/" && !typing) {
      event.preventDefault();
      openSearch();
    }
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openSearch();
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

export function initChrome() {
  initTheme();
  initView();
  initSearch();
}
