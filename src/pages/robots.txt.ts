import type { APIRoute } from "astro";

export const GET: APIRoute = ({ site }) => {
  const origin = (site ?? new URL("http://127.0.0.1:4327")).toString().replace(/\/$/, "");
  const body = `User-agent: *\nAllow: /\nSitemap: ${origin}/sitemap-index.xml\n`;
  return new Response(body, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
};
