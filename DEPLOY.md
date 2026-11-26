# Deploying

Production: https://mortgagecomplianceglossary.com (Vercel project `mortgage-glossary`, prj_Ab2QFGm6wKS85UPqfeJmEotId1xC).
The production alias https://mortgage-glossary.vercel.app permanently redirects (308) to https://mortgagecomplianceglossary.com. Unique deployment URLs (for example, mortgage-glossary-<id>-bitcoin-bytes-travel.vercel.app) are not redirected, so preview and rollback deploys stay reachable.
Deploys are direct uploads of a prebuilt `dist/` (no Git auto-deploy). Deploy only with Shaun's go.

```
npm ci
npm run data && python3 scripts/compile_terms.py
SITE_URL=https://mortgagecomplianceglossary.com npm run build
If SITE_URL is omitted, the build now defaults to https://mortgagecomplianceglossary.com. A post-build check fails if localhost origins leaked into `dist/` (canonicals, sitemap, robots.txt, or JSON-LD).
npm run check:links && npm run check:es
npm run preview   # then, in another shell:
PLAYWRIGHT_HOME=<dir with playwright + axe-core> npm run audit && npm run audit:search
tar czf site.tgz -C dist .   # uploaded with vercel.json; build command extracts into out/
```

Hosts that block automated checks (check by hand): guide.freddiemac.com, www.fema.gov, www.rd.usda.gov, singlefamily.fanniemae.com.
