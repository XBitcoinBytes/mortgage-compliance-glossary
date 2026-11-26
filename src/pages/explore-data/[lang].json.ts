import type { APIRoute } from "astro";
import { exploreData } from "../../lib/explore-data";

export function getStaticPaths() {
  return [{ params: { lang: "en" } }, { params: { lang: "es" } }];
}

export const GET: APIRoute = ({ params }) =>
  new Response(JSON.stringify(exploreData(params.lang === "es" ? "es" : "en")), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
