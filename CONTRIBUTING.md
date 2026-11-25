# Contributing to the Mortgage Compliance Glossary

This is an open-source English and Spanish mortgage compliance glossary (393 terms) maintained by Shaun Barry, NMLS #30170. It is educational material, not legal advice, a compliance opinion, or a commitment to lend.

The GitHub repository is private while the glossary is first published. To offer a correction or a new term, use the contact path on the [portfolio site](https://shaun-barry-portfolio.vercel.app), or watch [GitHub under XBitcoinBytes](https://github.com/XBitcoinBytes) if a public contribution path is opened later. Do not submit real borrower data or non-public loan files.

A public version of this guide is at `/contribute` on the site.

## What belongs here

Add or improve terms used in mortgage origination, underwriting, disclosure, or servicing. Every entry needs:

- a plain-language definition
- an illustrative file or form example
- at least one primary-source citation (a regulation, statute, or agency guide)
- a Spanish rendering that follows [CFPB mortgage terminology](https://files.consumerfinance.gov/f/documents/cfpb_adult-fin-ed_spanish-style-guide-glossary.pdf) where the Bureau has published a term

## Data format

Each term is one JSON file at `src/content/terms/{slug}.json`. Required fields:

- `term`, `aliases`, `category`, `definition`, `details`, `complianceNotes`
- `example` with `setting` and `text`
- `citations` (ids from `src/data/citations.json`)
- `related` (other slugs; `npm run validate` makes links bidirectional)
- `reviewed` (ISO date)
- a matching `es` object with the same structure

Categories: `origination`, `underwriting`, `compliance`, `closing`, `servicing`, `loan-programs`, `borrower-faqs`.

## Citation requirements

- Cite the official text, not only a blog post or secondary explainer.
- Prefer eCFR, the U.S. Code, CFPB regulations and interpretations, and current Fannie Mae, Freddie Mac, FHA, VA, or USDA guides.
- Do not invent section numbers, dollar thresholds, or deadlines.
- If a figure changes every year, cite the source and do not hard-code the number in the example. English examples include the words `Example figures`. Spanish examples include `Cifras de ejemplo`.
- Do not present this project as affiliated with the CFPB, Fannie Mae, Freddie Mac, HUD, VA, or USDA.

## How to add or edit a term

1. Add the slug to `scripts/reference_data.py` and run `npm run data`.
2. Create or update `src/content/terms/{slug}.json`, including the `es` object.
3. Run `npm run validate`. Fix any missing citations, broken related links, or incomplete Spanish fields.
4. If you can, also run `npm run check:es` and `npm run check:links`.

## Review process

Entries are reviewed against the cited source and for plain language in both English and Spanish. Spanish that follows a published CFPB term should keep that wording unless a reviewer notes a reason to depart. Spanish that has not had a native-speaker legal review should stay flagged as such. Shaun Barry, NMLS #30170, reviews substantive compliance wording before an entry is treated as final.

## Local preview

```bash
npm install
npm run dev
```

The dev server listens on http://127.0.0.1:4327.
