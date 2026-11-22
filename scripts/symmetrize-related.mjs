import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const dir = path.resolve("src/content/terms");
const files = (await readdir(dir)).filter((name) => name.endsWith(".json"));
const terms = new Map();
for (const file of files) {
  const full = path.join(dir, file);
  const data = JSON.parse(await readFile(full, "utf8"));
  data.related = [...new Set(data.related ?? [])].filter((slug) => slug !== data.slug);
  terms.set(data.slug, { file: full, data });
}
for (const term of terms.values()) {
  for (const slug of term.data.related) {
    const other = terms.get(slug);
    if (!other) continue;
    if (!other.data.related.includes(term.data.slug)) other.data.related.push(term.data.slug);
  }
}
for (const term of terms.values()) {
  term.data.related = [...new Set(term.data.related)].filter((slug) => terms.has(slug) && slug !== term.data.slug).sort();
  await writeFile(term.file, `${JSON.stringify(term.data, null, 2)}\n`);
}
console.log(`symmetrized ${terms.size} terms`);
