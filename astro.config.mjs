// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

const PRODUCTION_SITE = "https://mortgagecomplianceglossary.com";
const isBuild = process.argv.includes("build");
const site = process.env.SITE_URL || (isBuild ? PRODUCTION_SITE : "http://127.0.0.1:4327");
if (isBuild && !process.env.SITE_URL) {
  console.warn(
    `\n[glossary] SITE_URL is not set; using ${PRODUCTION_SITE} for canonicals, the sitemap, and 'Cite this entry'.\n`,
  );
}
if (isBuild && /127\.0\.0\.1|localhost/.test(site)) {
  console.warn(
    `\n[glossary] Building with a local origin (${site}). Canonicals and the sitemap will not be production-ready.\n`,
  );
}

export default defineConfig({
  site,
  trailingSlash: "never",
  integrations: [
    sitemap({
      filter: (page) => !page.includes("search-index") && !page.endsWith(".json"),
      i18n: {
        defaultLocale: "en",
        locales: { en: "en", es: "es" },
      },
      serialize(item) {
        const links = item.links ?? [];
        const english = links.find((link) => link.lang === "en")?.url ?? item.url.replace(/\/es(?=\/|$)/, "") ;
        if (english && !links.some((link) => link.lang === "x-default")) {
          item.links = [...links, { url: english, lang: "x-default" }];
        }
        return item;
      },
    }),
  ],
});
