import type { APIRoute } from "astro";
import { searchRecords } from "../lib/content";

// One shared, cacheable search index instead of ~250 KB inlined into every page.
export const GET: APIRoute = () =>
  new Response(JSON.stringify(searchRecords()), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
