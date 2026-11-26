# Mortgage Compliance Glossary

Open-source English and Spanish mortgage compliance glossary of **393 terms**, by Shaun Barry, NMLS #30170.

A static desk reference for mortgage origination, underwriting, disclosure, and servicing. Each entry starts with a plain-English definition, then shows where the item appears on the Loan Estimate, Closing Disclosure, or in the loan file, and cites a regulation, statute, or agency guide. Spanish entries match the English set.

**Who it's for.** Loan officers, compliance staff, and other mortgage professionals who need a cited desk reference, and borrowers who want a plain-language explanation of the same terms. The default reading view is **Professional**: regulation detail, citations, the form example, and compliance notes stay open. **Borrower** view keeps the definition and the example and collapses the professional sections. The choice is stored in this browser.

This edition is educational. It is not legal advice, a compliance opinion, or a commitment to lend. An author credit can be added on the About page. There is no contact information on the site.

Spanish entries follow the [CFPB Spanish-English glossary](https://files.consumerfinance.gov/f/documents/cfpb_adult-fin-ed_spanish-style-guide-glossary.pdf) where the Bureau has a published term. That translation still needs a native-speaker legal review before it is treated as final.

## How to use it

### Run locally

```bash
npm install
npm run dev
```

The dev server listens on [http://127.0.0.1:4327](http://127.0.0.1:4327).

```bash
npm run validate   # related links, citations, required fields, Spanish
npm run build      # validate, then write the static site to dist/
```

Set `SITE_URL=https://mortgagecomplianceglossary.com` before a production build so canonical links and the sitemap use the public origin. Deploy only with the steps in `DEPLOY.md`.

### Add a term

1. Add the slug to `scripts/reference_data.py` and run `npm run data`.
2. Create `src/content/terms/{slug}.json` with `term`, `aliases`, `category`, `definition`, `details`, `complianceNotes`, `example` (`setting` and `text`), `citations` (ids from `src/data/citations.json`), `related`, `reviewed`, and a matching `es` object.
3. English examples include the words `Example figures`. Spanish examples include `Cifras de ejemplo`. Do not hard-code figures that change every year.
4. Run `npm run validate`. The script makes related links bidirectional and fails if a slug, citation, or path step does not resolve.

Categories: `origination`, `underwriting`, `compliance`, `closing`, `servicing`, `loan-programs`, `borrower-faqs`.

Curated borrower topics live in `src/data/trending.json`. The list is editorial. It is not a search count. Learning paths live in `src/data/paths.json`. The regulation index is built from the citation catalog.

## Contribute

How to add or improve terms, citation rules, and the review process are in [CONTRIBUTING.md](CONTRIBUTING.md) and on the site at `/contribute`.

## Related work

Other mortgage projects by Shaun Barry:

- **[MortgageEval](https://mortgageeval.com)** — a public site where anyone can test a mortgage AI against an open-source benchmark. Answers are checked against a licensed loan officer's answer key.
- **ClearEstimate** — coming soon. A TRID compliance checker that reads Loan Estimates and Closing Disclosures in the browser. Files stay on the device. No public site yet.
- **[Portfolio](https://shaun-barry-portfolio.vercel.app)** — Shaun's portfolio of mortgage and AI product work.
- **[GitHub](https://github.com/XBitcoinBytes)** — other public work under XBitcoinBytes. The public glossary repository is [XBitcoinBytes/mortgage-compliance-glossary](https://github.com/XBitcoinBytes/mortgage-compliance-glossary). The site footer still links the profile.

## Domain

`mortgagecomplianceglossary.com` is the public domain for this glossary. See `DEPLOY.md` for the current production host.
