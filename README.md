# Mortgage Compliance Glossary

A static desk reference for mortgage origination, underwriting, disclosure, and servicing. Each entry starts with a plain-English definition, then shows where the item appears on the Loan Estimate, Closing Disclosure, or in the loan file, and cites a regulation, statute, or agency guide.

The default reading view is **Professional**: regulation detail, citations, the form example, and compliance notes stay open. **Borrower** view keeps the definition and the example and collapses the professional sections. The choice is stored in this browser.

This edition is educational. It is not legal advice, a compliance opinion, or a commitment to lend. An author credit can be added on the About page. There is no contact information on the site.

Spanish entries follow the [CFPB Spanish-English glossary](https://files.consumerfinance.gov/f/documents/cfpb_adult-fin-ed_spanish-style-guide-glossary.pdf) where the Bureau has a published term. That translation still needs a native-speaker legal review before it is treated as final.

## Run locally

```bash
npm install
npm run dev
```

The dev server listens on [http://127.0.0.1:4327](http://127.0.0.1:4327).

```bash
npm run validate   # related links, citations, required fields, Spanish
npm run build      # validate, then write the static site to dist/
```

Set `SITE_URL` before a future publication so canonical links and the sitemap use the real origin. Nothing in this repo deploys the site.

## Add a term

1. Add the slug to `scripts/reference_data.py` and run `npm run data`.
2. Create `src/content/terms/{slug}.json` with `term`, `aliases`, `category`, `definition`, `details`, `complianceNotes`, `example` (`setting` and `text`), `citations` (ids from `src/data/citations.json`), `related`, `reviewed`, and a matching `es` object.
3. English examples include the words `Example figures`. Spanish examples include `Cifras de ejemplo`. Do not hard-code figures that change every year.
4. Run `npm run validate`. The script makes related links bidirectional and fails if a slug, citation, or path step does not resolve.

Categories: `origination`, `underwriting`, `compliance`, `closing`, `servicing`, `loan-programs`, `borrower-faqs`.

Curated borrower topics live in `src/data/trending.json`. The list is editorial. It is not a search count. Learning paths live in `src/data/paths.json`. The regulation index is built from the citation catalog.
