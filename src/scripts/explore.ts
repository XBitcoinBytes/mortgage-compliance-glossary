import { createExplorer, EXPLORE_UI, hashFor, parseHash, type Body, type ExploreData, type Explorer, type Screen } from "../lib/explore";

const host = document.getElementById("explorer");
if (host) init(host);

function init(host: HTMLElement) {
  const lang = host.dataset.lang === "es" ? "es" : "en";
  const ui = EXPLORE_UI[lang];
  const termBase = host.dataset.termBase || "/terms/";
  const panel = host.querySelector<HTMLElement>("#x-panel")!;
  const status = host.querySelector<HTMLElement>("#x-status")!;
  let explorer: Explorer | null = null;
  let loading: Promise<Explorer> | null = null;
  let userNavigated = false;

  function load(): Promise<Explorer> {
    if (explorer) return Promise.resolve(explorer);
    if (!loading) {
      loading = fetch(host.dataset.src!)
        .then((r) => {
          if (!r.ok) throw new Error(String(r.status));
          return r.json() as Promise<ExploreData>;
        })
        .then((data) => (explorer = createExplorer(data)))
        .catch((error) => {
          loading = null;
          throw error;
        });
    }
    return loading;
  }

  // Warm the data on the reader's first sign of intent, not on page load.
  const warm = () => {
    load().catch(() => {});
    for (const type of ["pointerover", "focusin", "touchstart"]) host.removeEventListener(type, warm);
  };
  for (const type of ["pointerover", "focusin", "touchstart"]) host.addEventListener(type, warm, { passive: true });

  function el<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, string> = {}, text?: string) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderBody(body: Body): HTMLElement {
    const wrap = el("div", { class: "x-body" });
    if (body.type === "text") {
      for (const para of body.text.split(/\n{2,}/)) wrap.append(el("p", {}, para));
    } else if (body.type === "example") {
      const box = el("div", { class: "x-example" });
      if (body.setting) box.append(el("p", { class: "x-setting" }, body.setting));
      box.append(el("p", {}, body.text));
      box.append(el("p", { class: "x-tag" }, body.tag));
      wrap.append(box);
    } else {
      const list = el("ul", { class: "x-cites" });
      for (const item of body.items) {
        const li = el("li");
        li.append(el("a", { href: item.url, rel: "noopener" }, item.label), el("span", {}, item.title));
        list.append(li);
      }
      wrap.append(list);
    }
    return wrap;
  }

  function render(stack: { id: string; screen: Screen }[]) {
    const ids = stack.slice(1).map((s) => s.id);
    const current = stack[stack.length - 1].screen;

    const nav = el("nav", { class: "x-crumbs", "aria-label": ui.youAreHere });
    const ol = el("ol");
    stack.forEach((entry, i) => {
      const li = el("li");
      if (i === stack.length - 1) li.append(el("span", { "aria-current": "location" }, entry.screen.crumb));
      else li.append(el("a", { href: hashFor(ids.slice(0, i)) }, entry.screen.crumb));
      ol.append(li);
    });
    nav.append(ol);

    const view = el("div", { class: "x-screen", "data-kind": current.kind });
    if (current.kicker) view.append(el("p", { class: "x-kicker" }, current.kicker));
    view.append(el("h2", { id: "x-h", tabindex: "-1" }, current.heading));
    for (const body of current.body) view.append(renderBody(body));
    if (current.options.length) {
      view.append(el("p", { class: "x-prompt" }, current.prompt));
      const list = el("ul", { class: "x-options" });
      for (const option of current.options) {
        const a = el("a", { class: "x-opt", href: hashFor([...ids, option.id]) });
        a.append(el("strong", {}, option.label));
        if (option.hint) a.append(el("span", {}, option.hint));
        const li = el("li");
        li.append(a);
        list.append(li);
      }
      view.append(list);
    }
    if (stack.length > 1 || current.termSlug) {
      const actions = el("p", { class: "x-actions" });
      if (current.termSlug) actions.append(el("a", { class: "btn", href: `${termBase}${current.termSlug}` }, ui.readFull));
      if (stack.length > 1) {
        actions.append(el("a", { class: "btn secondary", href: hashFor(ids.slice(0, -1)) }, `← ${ui.back}`));
        actions.append(el("a", { class: "btn secondary", href: "#/" }, ui.startOver));
      }
      view.append(actions);
    }
    if (userNavigated) view.classList.add("x-enter");
    panel.replaceChildren(nav, view);
    document.title = `${current.heading} · ${document.title.split(" · ").slice(-1)[0]}`;
    if (userNavigated) {
      status.textContent = current.heading;
      (view.querySelector("#x-h") as HTMLElement).focus({ preventScroll: true });
      // Keep the new layer's heading in view, below the sticky header.
      const header = document.querySelector<HTMLElement>(".site-header");
      const offset = (header?.getBoundingClientRect().height ?? 0) + 8;
      const top = panel.getBoundingClientRect().top;
      if (top < offset || top > window.innerHeight * 0.6) {
        window.scrollTo({ top: window.scrollY + top - offset });
      }
    }
  }

  function showMessage(text: string) {
    const view = panel.querySelector(".x-screen");
    let note = panel.querySelector<HTMLElement>(".x-loading");
    if (!note) {
      note = el("p", { class: "x-prompt x-loading", role: "status" });
      (view ?? panel).append(note);
    }
    note.textContent = text;
  }

  function route() {
    const segments = parseHash(location.hash);
    if (!segments.length && !explorer) return; // server-rendered top layer is already correct
    const draw = (ex: Explorer) => {
      const { stack, valid } = ex.resolve(segments);
      if (valid.length !== segments.length) history.replaceState(null, "", hashFor(valid));
      render(stack);
    };
    if (explorer) return draw(explorer);
    const timer = window.setTimeout(() => showMessage(ui.loading), 250);
    load()
      .then(draw)
      .catch(() => showMessage(ui.failed))
      .finally(() => window.clearTimeout(timer));
  }

  window.addEventListener("hashchange", () => {
    userNavigated = true;
    route();
  });
  route();
}
