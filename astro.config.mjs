// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

const site = process.env.SITE_URL || "http://127.0.0.1:4327";

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
