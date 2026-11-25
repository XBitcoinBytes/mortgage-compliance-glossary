# Deploying

Production: https://mortgagecomplianceglossary.com (Vercel project `mortgage-glossary`, prj_Ab2QFGm6wKS85UPqfeJmEotId1xC).
Until DNS is pointed at Vercel, the same production deployment is also served at https://mortgage-glossary.vercel.app.
Deploys are direct uploads of a prebuilt `dist/` (no Git auto-deploy). Deploy only with Shaun's go.

```
npm ci
npm run data && python3 scripts/compile_terms.py
SITE_URL=https://mortgagecomplianceglossary.com npm run build
npm run check:links && npm run check:es
npm run preview   # then, in another shell:
PLAYWRIGHT_HOME=<dir with playwright + axe-core> npm run audit && npm run audit:search
tar czf site.tgz -C dist .   # uploaded with vercel.json; build command extracts into out/
```

Hosts that block automated checks (check by hand): guide.freddiemac.com, www.fema.gov, www.rd.usda.gov, singlefamily.fanniemae.com.
