// Checks every citation and regulation-part URL. Network required; run before a release.
// Usage: node scripts/checks/check-links.mjs  (exit 1 on any non-2xx that is not a known bot-block)
import { readFile } from "node:fs/promises";
const citations = JSON.parse(await readFile("src/data/citations.json", "utf8"));
const parts = JSON.parse(await readFile("src/data/parts.json", "utf8"));
const urls = new Set();
for (const c of citations) { urls.add(c.url); if (c.cfpbUrl) urls.add(c.cfpbUrl); }
for (const p of parts) urls.add(p.url);
const figures = JSON.parse(await readFile("src/data/figures.json", "utf8"));
for (const f of figures) urls.add(f.url);
for (const c of citations) if (c.interpUrl) urls.add(c.interpUrl);
// Hosts that refuse scripted requests (401/403) but load in a browser. Re-verify by hand each release.
const BOT_BLOCKED = new Set(["guide.freddiemac.com", "www.fema.gov", "www.rd.usda.gov", "singlefamily.fanniemae.com"]);
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36";
const list = [...urls];
const bad = [];
const warn = [];
let i = 0;
async function worker() {
  while (i < list.length) {
    const url = list[i++];
    let status = 0;
    for (let attempt = 0; attempt < 4 && (status === 0 || status === 403 || status === 429); attempt++) {
      try {
        const res = await fetch(url, { redirect: "follow", headers: { "user-agent": UA }, signal: AbortSignal.timeout(25000) });
        status = res.status;
        if (status === 200 && /uscode\.house\.gov/.test(url) && /Page Not Found/.test(await res.text())) status = 404;
      } catch { status = 0; }
      if (status !== 200) await new Promise((r) => setTimeout(r, 4000 * (attempt + 1)));
    }
    const host = new URL(url).host;
    if (status >= 200 && status < 300) continue;
    if ((status === 401 || status === 403) && BOT_BLOCKED.has(host)) continue;
    if (status === 429) { warn.push(url); continue; }
    bad.push(`${status} ${url}`);
  }
}
await Promise.all(Array.from({ length: 4 }, worker));
if (warn.length) console.warn(`${warn.length} rate-limited (429), not verified this run:\n` + warn.join("\n"));
if (bad.length) { console.error(`${bad.length} of ${list.length} links failed:\n` + bad.join("\n")); process.exit(1); }
console.log(`all ${list.length} citation links resolve (${BOT_BLOCKED.size} bot-blocked hosts skipped: re-check by hand)`);
