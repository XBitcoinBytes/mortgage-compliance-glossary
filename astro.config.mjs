// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

const site = process.env.SITE_URL || "http://127.0.0.1:4327";
if (!process.env.SITE_URL && process.argv.includes("build")) {
  console.warn("\n[glossary] SITE_URL is not set: canonical links, the sitemap, and 'Cite this entry' will point at 127.0.0.1. Set SITE_URL before a production build.\n");
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
    }),
  ],
});
