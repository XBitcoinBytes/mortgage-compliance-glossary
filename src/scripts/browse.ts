import Fuse from "fuse.js";

interface Row {
  slug: string;
  cat: string;
  letter: string;
  parts: string;
  name: string;
  el: HTMLElement;
}

export function initBrowse() {
  const root = document.querySelector<HTMLElement>("#browse");
  if (!root) return;
  const input = root.querySelector<HTMLInputElement>("#browse-q");
  const regSelect = root.querySelector<HTMLSelectElement>("#browse-reg");
  const count = root.querySelector<HTMLElement>("#browse-count");
  const empty = root.querySelector<HTMLElement>("#browse-empty");
  const lang = root.dataset.lang === "es" ? "es" : "en";
  const locked = root.dataset.locked ?? "";
  let category = locked;
  let part = "";

  const rows: Row[] = [...root.querySelectorAll<HTMLElement>("[data-slug]")].map((el) => ({
    slug: el.dataset.slug ?? "",
    cat: el.dataset.cat ?? "",
    letter: el.dataset.letter ?? "",
    parts: el.dataset.parts ?? "",
    name: el.dataset.name ?? "",
    el,
  }));

  const fuse = new Fuse(rows, {
    threshold: 0.35,
    ignoreDiacritics: true,
    ignoreLocation: true,
    minMatchCharLength: 2,
    keys: ["name"],
  });

  const params = new URLSearchParams(location.search);
  if (!locked && params.get("category")) category = params.get("category") ?? "";
  if (params.get("reg")) {
    part = params.get("reg") ?? "";
    if (regSelect) regSelect.value = part;
  }
  if (input && params.get("q")) input.value = params.get("q") ?? "";

  function apply() {
    const query = input?.value.trim() ?? "";
    const matched = new Set((query ? fuse.search(query).map((result) => result.item.slug) : rows.map((row) => row.slug)));
    let visible = 0;
    rows.forEach((row) => {
      const show =
        matched.has(row.slug) &&
        (!category || row.cat === category) &&
        (!part || row.parts.split(" ").includes(part));
      row.el.hidden = !show;
      if (show) visible += 1;
    });
    root.querySelectorAll<HTMLElement>("[data-letter-group]").forEach((group) => {
      const any = [...group.querySelectorAll<HTMLElement>("[data-slug]")].some((item) => !item.hidden);
      group.hidden = !any;
    });
    if (count) {
      count.textContent = lang === "es" ? `${visible} términos` : `${visible} terms`;
    }
    if (empty) empty.hidden = visible !== 0;
    root.querySelectorAll<HTMLButtonElement>("button[data-cat]").forEach((button) => {
      button.setAttribute("aria-pressed", (button.dataset.cat ?? "") === category ? "true" : "false");
    });
    const url = new URL(location.href);
    if (query) url.searchParams.set("q", query);
    else url.searchParams.delete("q");
    if (part) url.searchParams.set("reg", part);
    else url.searchParams.delete("reg");
    if (!locked && category) url.searchParams.set("category", category);
    else url.searchParams.delete("category");
    history.replaceState(null, "", url);
  }

  input?.addEventListener("input", apply);
  root.querySelectorAll<HTMLButtonElement>("button[data-cat]").forEach((button) => {
    button.addEventListener("click", () => {
      category = button.dataset.cat ?? "";
      apply();
    });
  });
  regSelect?.addEventListener("change", () => {
    part = regSelect.value;
    apply();
  });
  apply();
}
