#!/usr/bin/env python3
"""Emit citation catalog, regulation parts, term manifest, paths, and trending.

JSON in src/data is what the site and the validator read. Re-run this script
after editing the tables below.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "data"

ECFR12 = "https://www.ecfr.gov/current/title-12/chapter-X/part-{part}"
ECFR12S = ECFR12 + "/section-{section}"
CFPB = "https://www.consumerfinance.gov/rules-policy/regulations/{part}/{sec}/"
# uscode.house.gov retired the view.xhtml?req=granuleid links in 2026; the
# unversioned /us/usc/t{title}/s{section}/ route serves the current text.
USC = "https://uscode.house.gov/us/usc/t{title}/s{section}/"


def C(id_, label, title, url, kind, part, cfpb=None):
    row = {
        "id": id_,
        "label": label,
        "title": title,
        "url": url,
        "kind": kind,
        "partId": part,
    }
    if cfpb:
        row["cfpbUrl"] = cfpb
    return row


# The CFPB interactive-regulations site has no page for these parts (404 as of Nov 2026).
NO_CFPB_REG_PAGE = {"1014"}


def reg(part, section, name, part_id=None):
    sec = str(section)
    pid = part_id or part
    label = f"12 CFR {part}.{sec}" if sec != "part" else f"12 CFR Part {part}"
    if sec == "part":
        url = ECFR12.format(part=part)
        cfpb = f"https://www.consumerfinance.gov/rules-policy/regulations/{part}/"
        cid = f"reg-{part}"
    else:
        url = ECFR12S.format(part=part, section=f"{part}.{sec}")
        cfpb = CFPB.format(part=part, sec=sec)
        cid = f"reg-{part}-{sec.replace('.', '-')}"
    if part in NO_CFPB_REG_PAGE:
        cfpb = None
    return C(cid, label, name, url, "regulation", pid, cfpb)


def statute(id_, label, title, usc_title, section, part):
    return C(id_, label, title, USC.format(title=usc_title, section=section), "statute", part)


citations = []

# Regulation Z
for sec, name in [
    ("part", "Regulation Z (Truth in Lending Act)"),
    ("2", "Regulation Z — Definitions, including application and business day"),
    ("4", "Regulation Z — Finance charge"),
    ("17", "Regulation Z — General disclosure requirements"),
    ("18", "Regulation Z — Content of disclosures for closed-end credit"),
    ("19", "Regulation Z — Mortgage disclosure timing, Loan Estimate, and Closing Disclosure"),
    ("20", "Regulation Z — Post-consummation disclosures, including ARM adjustments"),
    ("22", "Regulation Z — Determination of the annual percentage rate"),
    ("23", "Regulation Z — Right of rescission"),
    ("24", "Regulation Z — Advertising"),
    ("32", "Regulation Z — High-cost mortgages (HOEPA)"),
    ("34", "Regulation Z — Prohibited acts and practices for high-cost mortgages"),
    ("35", "Regulation Z — Higher-priced mortgage loans"),
    ("36", "Regulation Z — Loan originator compensation and mortgage-related prohibitions"),
    ("37", "Regulation Z — Content of the Loan Estimate"),
    ("38", "Regulation Z — Content of the Closing Disclosure"),
    ("39", "Regulation Z — Mortgage transfer disclosures"),
    ("40", "Regulation Z — Requirements for home-equity plans"),
    ("41", "Regulation Z — Periodic statements for residential mortgage loans"),
    ("42", "Regulation Z — Valuation independence"),
    ("43", "Regulation Z — Ability to repay and qualified mortgages"),
]:
    citations.append(reg("1026", sec, name, "1026"))

for sec, name in [
    ("part", "Regulation X (Real Estate Settlement Procedures Act)"),
    ("2", "Regulation X — Definitions"),
    ("6", "Regulation X — Special information booklet"),
    ("7", "Regulation X — Good Faith Estimate (legacy open-end and other covered transactions)"),
    ("8", "Regulation X — HUD-1 settlement statement (legacy transactions)"),
    ("14", "Regulation X — Prohibition against kickbacks and unearned fees"),
    ("15", "Regulation X — Affiliated business arrangements"),
    ("17", "Regulation X — Escrow accounts"),
    ("20", "Regulation X — List of homeownership counseling organizations"),
    ("33", "Regulation X — Mortgage servicing transfers"),
    ("34", "Regulation X — Timely escrow payments and treatment of escrow account balances"),
    ("35", "Regulation X — Error resolution procedures"),
    ("36", "Regulation X — Requests for information"),
    ("37", "Regulation X — Force-placed insurance"),
    ("38", "Regulation X — General servicing policies, procedures, and requirements"),
    ("39", "Regulation X — Early intervention requirements for certain borrowers"),
    ("40", "Regulation X — Continuity of contact"),
    ("41", "Regulation X — Loss mitigation procedures"),
]:
    citations.append(reg("1024", sec, name, "1024"))

for sec, name in [
    ("part", "Regulation B (Equal Credit Opportunity Act)"),
    ("4", "Regulation B — General rules, including the prohibition on discrimination"),
    ("5", "Regulation B — Rules concerning requests for information"),
    ("6", "Regulation B — Rules concerning evaluation of applications"),
    ("7", "Regulation B — Rules concerning extensions of credit"),
    ("9", "Regulation B — Notifications"),
    ("12", "Regulation B — Record retention"),
    ("13", "Regulation B — Information for monitoring purposes"),
    ("14", "Regulation B — Appraisals and other valuations"),
]:
    citations.append(reg("1002", sec, name, "1002"))

for sec, name in [
    ("part", "Regulation C (Home Mortgage Disclosure Act)"),
    ("2", "Regulation C — Definitions"),
    ("4", "Regulation C — Compilation of reportable data"),
    ("5", "Regulation C — Disclosure and reporting"),
]:
    citations.append(reg("1003", sec, name, "1003"))

citations += [
    reg("1022", "part", "Regulation V (Fair Credit Reporting Act)", "1022"),
    C(
        "reg-1022-72",
        "12 CFR 1022.72",
        "Regulation V — Risk-based pricing notice",
        "https://www.ecfr.gov/current/title-12/chapter-X/part-1022/subpart-H/section-1022.72",
        "regulation",
        "1022",
        "https://www.consumerfinance.gov/rules-policy/regulations/1022/72/",
    ),
    reg("1016", "part", "Regulation P (Privacy of consumer financial information)", "1016"),
    reg("1007", "part", "Regulation G (SAFE Act — depository institution MLOs)", "1007"),
    reg("1008", "part", "Regulation H (SAFE Act — state-licensed MLOs)", "1008"),
    reg("1014", "part", "Regulation N (Mortgage Acts and Practices — Advertising)", "1014"),
    C(
        "reg-232",
        "32 CFR Part 232",
        "Military Lending Act regulation — limitations on consumer credit to covered borrowers",
        "https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-M/part-232",
        "regulation",
        "mla",
    ),
    C(
        "reg-232-3",
        "32 CFR 232.3",
        "Military Lending Act regulation — definitions, including the residential-mortgage exception",
        "https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-M/part-232/section-232.3",
        "regulation",
        "mla",
    ),
    C(
        "cfr-38-36",
        "38 CFR Part 36",
        "VA loan guaranty regulations",
        "https://www.ecfr.gov/current/title-38/chapter-I/part-36",
        "regulation",
        "va",
    ),
    C(
        "cfr-24-206",
        "24 CFR Part 206",
        "Home Equity Conversion Mortgage insurance",
        "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-II/subchapter-B/part-206",
        "regulation",
        "hecm",
    ),
    C(
        "cfr-7-3555",
        "7 CFR Part 3555",
        "USDA Single Family Housing Guaranteed Loan Program",
        "https://www.ecfr.gov/current/title-7/subtitle-B/chapter-XXXV/part-3555",
        "regulation",
        "usda",
    ),
    C(
        "cfr-16-314",
        "16 CFR Part 314",
        "Standards for safeguarding customer information (Safeguards Rule)",
        "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314",
        "regulation",
        "safeguards",
    ),
    C(
        "cfr-16-681",
        "16 CFR Part 681",
        "Identity theft red flags",
        "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-F/part-681",
        "regulation",
        "red-flags",
    ),
    C(
        "cfr-31-1029",
        "31 CFR Part 1029",
        "FinCEN rules for loan or finance companies, including residential mortgage lenders and originators",
        "https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1029",
        "regulation",
        "bsa",
    ),
    C(
        "cfr-31-1010-230",
        "31 CFR 1010.230",
        "FinCEN beneficial-ownership customer due diligence",
        "https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1010/section-1010.230",
        "regulation",
        "bsa",
    ),
]

citations += [
    statute("usc-15-1601", "15 USC 1601", "Truth in Lending Act — congressional findings and purpose", "15", "1601", "tila"),
    statute("usc-15-1639c", "15 USC 1639c", "TILA — minimum standards for residential mortgage loans (ability to repay)", "15", "1639c", "tila"),
    statute("usc-15-1639", "15 USC 1639", "TILA — requirements for certain mortgages (HOEPA)", "15", "1639", "tila"),
    statute("usc-12-2601", "12 USC 2601", "Real Estate Settlement Procedures Act — congressional findings and purpose", "12", "2601", "respa"),
    statute("usc-12-2607", "12 USC 2607", "RESPA — prohibition against kickbacks and unearned fees", "12", "2607", "respa"),
    statute("usc-15-1691", "15 USC 1691", "Equal Credit Opportunity Act — scope of prohibition", "15", "1691", "ecoa"),
    statute("usc-12-2801", "12 USC 2801", "Home Mortgage Disclosure Act — congressional findings and purpose", "12", "2801", "hmda"),
    statute("usc-15-1681", "15 USC 1681", "Fair Credit Reporting Act — congressional findings and statement of purpose", "15", "1681", "fcra"),
    statute("usc-15-1681b", "15 USC 1681b", "Fair Credit Reporting Act — permissible purposes of consumer reports", "15", "1681b", "fcra"),
    statute("usc-15-1681m", "15 USC 1681m", "Fair Credit Reporting Act — requirements on users of consumer reports", "15", "1681m", "fcra"),
    statute("usc-15-6801", "15 USC 6801", "Gramm-Leach-Bliley Act — protection of nonpublic personal information", "15", "6801", "glba"),
    statute("usc-12-5101", "12 USC 5101", "SAFE Act — purposes and methods for licensing and registration", "12", "5101", "safe"),
    statute("usc-12-5104", "12 USC 5104", "SAFE Act — state license and registration", "12", "5104", "safe"),
    statute("usc-12-4901", "12 USC 4901", "Homeowners Protection Act — definitions", "12", "4901", "hpa"),
    statute("usc-12-4902", "12 USC 4902", "Homeowners Protection Act — termination of private mortgage insurance", "12", "4902", "hpa"),
    statute("usc-12-5531", "12 USC 5531", "Dodd-Frank Act — prohibiting unfair, deceptive, or abusive acts or practices", "12", "5531", "udaap"),
    statute("usc-12-5536", "12 USC 5536", "Dodd-Frank Act — prohibited acts", "12", "5536", "udaap"),
    statute("usc-50-3937", "50 USC 3937", "Servicemembers Civil Relief Act — maximum rate of interest", "50", "3937", "scra"),
    statute("usc-50-3953", "50 USC 3953", "Servicemembers Civil Relief Act — mortgages and trust deeds", "50", "3953", "scra"),
    statute("usc-42-4012a", "42 USC 4012a", "National Flood Insurance Act — flood insurance purchase and compliance", "42", "4012a", "flood"),
    statute("usc-42-4001", "42 USC 4001", "National Flood Insurance Act — congressional findings and declaration of purpose", "42", "4001", "flood"),
    statute("usc-42-3604", "42 USC 3604", "Fair Housing Act — discrimination in the sale or rental of housing", "42", "3604", "fair-housing"),
    statute("usc-42-3605", "42 USC 3605", "Fair Housing Act — discrimination in residential real estate-related transactions", "42", "3605", "fair-housing"),
    statute("usc-31-5311", "31 USC 5311", "Bank Secrecy Act — declaration of purpose", "31", "5311", "bsa"),
    statute("usc-31-5318", "31 USC 5318", "Bank Secrecy Act — compliance, exemptions, and summons authority", "31", "5318", "bsa"),
    statute("usc-15-7001", "15 USC 7001", "E-SIGN Act — general validity of electronic signatures and records", "15", "7001", "esign"),
    statute("usc-10-987", "10 USC 987", "Military Lending Act", "10", "987", "mla"),
    statute("usc-12-1709", "12 USC 1709", "National Housing Act — mortgage insurance (FHA)", "12", "1709", "fha"),
    statute("usc-12-1715z20", "12 USC 1715z-20", "National Housing Act — home equity conversion mortgages", "12", "1715z-20", "hecm"),
    statute("usc-38-3701", "38 USC 3701", "VA housing loan program — definitions", "38", "3701", "va"),
    statute("usc-38-3703", "38 USC 3703", "VA housing — basic provisions relating to loan guaranty and insurance", "38", "3703", "va"),
]

FANNIE = "https://selling-guide.fanniemae.com/sel/{path}"
fannie_sections = [
    ("fannie-guide", "Fannie Mae Selling Guide", "Selling Guide", "", "agency-guide"),
    ("fannie-b2-1-2-01", "B2-1.2-01", "Loan-to-value (LTV) ratios", "b2-1.2-01/loan-value-ltv-ratios", "agency-guide"),
    ("fannie-b3-1-01", "B3-1-01", "Comprehensive risk assessment", "b3-1-01/comprehensive-risk-assessment", "agency-guide"),
    ("fannie-b3-2", "Chapter B3-2", "Desktop Underwriter (DU)", "b3-2/desktop-underwriter-du", "agency-guide"),
    ("fannie-b3-2-01", "B3-2-01", "General information on DU", "b3-2-01/general-information-du", "agency-guide"),
    ("fannie-b3-2-02", "B3-2-02", "DU validation service", "b3-2-02/du-validation-service", "agency-guide"),
    ("fannie-b3-2-05", "B3-2-05", "Approve/Eligible recommendations", "b3-2-05/approveeligible-recommendations", "agency-guide"),
    ("fannie-b3-2-06", "B3-2-06", "Approve/Ineligible recommendations", "b3-2-06/approveineligible-recommendations", "agency-guide"),
    ("fannie-b3-2-07", "B3-2-07", "Refer with Caution recommendations", "b3-2-07/refer-caution-recommendations", "agency-guide"),
    ("fannie-b3-2-08", "B3-2-08", "Out of Scope recommendations", "b3-2-08/out-scope-recommendations", "agency-guide"),
    ("fannie-b3-2-10", "B3-2-10", "Accuracy of DU data, tolerances, and credit-report errors", "b3-2-10/accuracy-du-data-du-tolerances-and-errors-credit-report", "agency-guide"),
    ("fannie-b3-2-11", "B3-2-11", "DU Underwriting Findings report", "b3-2-11/du-underwriting-findings-report", "agency-guide"),
    ("fannie-b3-3-1-01", "B3-3.1-01", "General income information", "b3-3.1-01/general-income-information", "agency-guide"),
    ("fannie-b3-3-1-02", "B3-3.1-02", "Tax return and transcript documentation", "b3-3.1-02/tax-return-and-transcript-documentation-requirements", "agency-guide"),
    ("fannie-b3-3-1-03", "B3-3.1-03", "Income Calculator", "b3-3.1-03/income-calculator", "agency-guide"),
    ("fannie-b3-3-1-04", "B3-3.1-04", "Verbal verification of employment", "b3-3.1-04/verbal-verification-employment", "agency-guide"),
    ("fannie-b3-3-2-01", "B3-3.2-01", "Standards for employment and income documentation", "b3-3.2-01/standards-employment-and-income-documentation", "agency-guide"),
    ("fannie-b3-3-3-01", "B3-3.3-01", "Base income", "b3-3.3-01/base-income", "agency-guide"),
    ("fannie-b3-3-3-02", "B3-3.3-02", "Bonus, commission, overtime, and tip income", "b3-3.3-02/bonus-commission-overtime-and-tip-income", "agency-guide"),
    ("fannie-b3-3-4-02", "B3-3.4-02", "Alimony, child support, equalization payments, or separate maintenance", "b3-3.4-02/alimony-child-support-equalization-payments-or-separate-maintenance", "agency-guide"),
    ("fannie-b3-3-4-12", "B3-3.4-12", "Public assistance income", "b3-3.4-12/public-assistance-income", "agency-guide"),
    ("fannie-b3-3-5", "Section B3-3.5", "Self-employment income", "b3-3.5/self-employment-income", "agency-guide"),
    ("fannie-b3-4-1-01", "B3-4.1-01", "Minimum reserve requirements", "b3-4.1-01/minimum-reserve-requirements", "agency-guide"),
    ("fannie-b3-4-3-04", "B3-4.3-04", "Personal gifts", "b3-4.3-04/personal-gifts", "agency-guide"),
    ("fannie-b3-4-3-05", "B3-4.3-05", "Gifts of equity", "b3-4.3-05/gifts-equity", "agency-guide"),
    ("fannie-b3-5-1-01", "B3-5.1-01", "General requirements for credit scores", "b3-5.1-01/general-requirements-credit-scores", "agency-guide"),
    ("fannie-b3-5-1-02", "B3-5.1-02", "Determining the credit score for a mortgage loan", "b3-5.1-02/determining-credit-score-mortgage-loan", "agency-guide"),
    ("fannie-b3-5-2-01", "B3-5.2-01", "Requirements for credit reports", "b3-5.2-01/requirements-credit-reports", "agency-guide"),
    ("fannie-b3-5-3-04", "B3-5.3-04", "Inquiries: recent attempts to obtain new credit", "b3-5.3-04/inquiries-recent-attempts-obtain-new-credit", "agency-guide"),
    ("fannie-b3-5-3-06", "B3-5.3-06", "Authorized users of credit", "b3-5.3-06/authorized-users-credit", "agency-guide"),
    ("fannie-b3-5-3-07", "B3-5.3-07", "Significant derogatory credit events", "b3-5.3-07/significant-derogatory-credit-events-waiting-periods-and-re-establishing-credit", "agency-guide"),
    ("fannie-b3-6-02", "B3-6-02", "Debt-to-income ratios", "b3-6-02/debt-income-ratios", "agency-guide"),
    ("fannie-b3-6-03", "B3-6-03", "Monthly housing expense for the subject property", "b3-6-03/monthly-housing-expense-subject-property", "agency-guide"),
    ("fannie-b3-6-04", "B3-6-04", "Qualifying payment requirements", "b3-6-04/qualifying-payment-requirements", "agency-guide"),
    ("fannie-b3-6-05", "B3-6-05", "Monthly debt obligations", "b3-6-05/monthly-debt-obligations", "agency-guide"),
    ("fannie-b3-6-07", "B3-6-07", "Debts paid off at or prior to closing", "b3-6-07/debts-paid-or-prior-closing", "agency-guide"),
    ("fannie-b4-1-1-01", "B4-1.1-01", "Definition of market value", "b4-1.1-01/definition-market-value", "agency-guide"),
    ("fannie-b4-1-1-02", "B4-1.1-02", "Appraisal lender responsibilities", "b4-1.1-02/lender-responsibilities", "agency-guide"),
    ("fannie-b4-1-4-10", "B4-1.4-10", "Value acceptance", "b4-1.4-10/value-acceptance", "agency-guide"),
    ("fannie-b4-1-4-11", "B4-1.4-11", "Value acceptance + property data", "b4-1.4-11/value-acceptance-property-data", "agency-guide"),
    ("fannie-b5-6-02", "B5-6-02", "HomeReady mortgage underwriting", "b5-6-02/homeready-mortgage-underwriting-methods-and-requirements", "agency-guide"),
    ("fannie-air", "Appraiser Independence Requirements", "Appraiser Independence Requirements", "", "agency-guide"),
]
for id_, label, title, path, kind in fannie_sections:
    if id_ == "fannie-guide":
        url = "https://selling-guide.fanniemae.com/"
    elif id_ == "fannie-air":
        url = "https://selling-guide.fanniemae.com/"
    else:
        url = FANNIE.format(path=path)
    citations.append(C(id_, label, f"Fannie Mae Selling Guide — {title}", url, kind, "fannie"))

citations += [
    C("fannie-urla", "URLA / Form 1003", "Uniform Residential Loan Application (Fannie Mae Form 1003 / Freddie Mac Form 65)", "https://singlefamily.fanniemae.com/delivering/uniform-mortgage-data-program/uniform-residential-loan-application", "agency-guide", "urla"),
    C("freddie-guide", "Freddie Mac Seller/Servicer Guide", "Freddie Mac Single-Family Seller/Servicer Guide", "https://guide.freddiemac.com/app/guide/", "agency-guide", "freddie"),
    C("freddie-lpa", "Loan Product Advisor", "Freddie Mac Loan Product Advisor", "https://sf.freddiemac.com/tools-learning/technology-tools/our-solutions/loan-product-advisor", "agency-guide", "freddie"),
    C("hud-4000-1", "HUD Handbook 4000.1", "FHA Single Family Housing Policy Handbook 4000.1", "https://www.hud.gov/program_offices/housing/sfh/handbook_4000-1", "agency-guide", "fha"),
    C("va-pamphlet", "VA Pamphlet 26-7", "VA Lenders Handbook, Pamphlet 26-7", "https://www.benefits.va.gov/homeloans/lenders.asp", "agency-guide", "va"),
    C("usda-hb", "USDA HB-1-3555", "USDA Single Family Housing Guaranteed Loan Program Technical Handbook", "https://www.rd.usda.gov/resources/directives/handbooks", "agency-guide", "usda"),
    C("fhfa-cll", "FHFA conforming loan limits", "FHFA conforming loan limit data", "https://www.fhfa.gov/data/conforming-loan-limit", "agency-guide", "fhfa"),
    C("ginnie", "Ginnie Mae", "Ginnie Mae mortgage-backed securities program", "https://www.ginniemae.gov/", "agency-guide", "ginnie"),
    C("nmls", "NMLS", "Nationwide Multistate Licensing System", "https://mortgage.nationwidelicensingsystem.org/", "agency-guide", "nmls"),
    C("cfpb-le", "CFPB Loan Estimate", "CFPB interactive Loan Estimate", "https://www.consumerfinance.gov/owning-a-home/loan-estimate/", "agency-guide", "cfpb"),
    C("cfpb-cd", "CFPB Closing Disclosure", "CFPB interactive Closing Disclosure", "https://www.consumerfinance.gov/owning-a-home/closing-disclosure/", "agency-guide", "cfpb"),
    C("cfpb-toolkit", "Your Home Loan Toolkit", "CFPB Your Home Loan Toolkit", "https://www.consumerfinance.gov/owning-a-home/explore/home-loan-toolkit/", "agency-guide", "cfpb"),
    C("cfpb-owning", "CFPB Owning a Home", "CFPB Owning a Home mortgage tools", "https://www.consumerfinance.gov/owning-a-home/", "agency-guide", "cfpb"),
    C("cfpb-forms", "TRID model forms", "CFPB TILA-RESPA integrated disclosure forms and samples", "https://www.consumerfinance.gov/compliance/compliance-resources/mortgage-resources/tila-respa-integrated-disclosures/forms-samples/", "agency-guide", "cfpb"),
    C("cfpb-spanish", "CFPB Spanish glossary", "CFPB Spanish-English glossary of financial terms", "https://files.consumerfinance.gov/f/documents/cfpb_adult-fin-ed_spanish-style-guide-glossary.pdf", "agency-guide", "cfpb"),
    C("cfpb-mortgage-resources", "CFPB mortgage resources", "CFPB mortgage compliance resources", "https://www.consumerfinance.gov/compliance/compliance-resources/mortgage-resources/", "agency-guide", "cfpb"),
    C("fema-flood", "FEMA flood insurance", "FEMA National Flood Insurance Program", "https://www.fema.gov/flood-insurance", "agency-guide", "flood"),
    C("ofac", "OFAC", "Treasury Office of Foreign Assets Control sanctions programs", "https://ofac.treasury.gov/", "agency-guide", "ofac"),
    C("fincen", "FinCEN", "Financial Crimes Enforcement Network", "https://www.fincen.gov/", "agency-guide", "bsa"),
    C("practice-file", "Industry file practice", "Fannie Mae Selling Guide — origination through closing (file-stage vocabulary)", "https://selling-guide.fanniemae.com/", "industry-practice", "practice"),
    C("practice-cfpb", "CFPB consumer guidance", "CFPB Owning a Home — consumer-facing mortgage guidance", "https://www.consumerfinance.gov/owning-a-home/", "industry-practice", "practice"),
    C("practice-urla", "URLA instructions", "Uniform Residential Loan Application", "https://singlefamily.fanniemae.com/delivering/uniform-mortgage-data-program/uniform-residential-loan-application", "industry-practice", "practice"),
    C("practice-nmls", "NMLS Resource Center", "NMLS for mortgage originators", "https://mortgage.nationwidelicensingsystem.org/", "industry-practice", "practice"),
    C("practice-hud", "HUD Handbook 4000.1", "FHA Single Family Housing Policy Handbook 4000.1", "https://www.hud.gov/program_offices/housing/sfh/handbook_4000-1", "industry-practice", "practice"),
    C("practice-va", "VA Pamphlet 26-7", "VA Lenders Handbook", "https://www.benefits.va.gov/homeloans/lenders.asp", "industry-practice", "practice"),
    C("practice-freddie", "Freddie Mac Guide", "Freddie Mac Single-Family Seller/Servicer Guide", "https://guide.freddiemac.com/app/guide/", "industry-practice", "practice"),
]

# Stable ids used by term authors. reg() generated ids like reg-1026-19.
# Add short aliases that point at the same records? Authors will use the generated ids.
# Document the id pattern in the manifest header via a sidecar list of ids.

parts = [
    {"id": "1026", "label": "12 CFR Part 1026", "short": "Reg Z", "name": "Regulation Z — Truth in Lending", "summary": "Closed-end mortgage disclosures, the Loan Estimate and Closing Disclosure, advertising, high-cost and higher-priced mortgages, loan-originator compensation, right of rescission, periodic statements, and ability-to-repay / qualified mortgage standards.", "url": ECFR12.format(part="1026")},
    {"id": "1024", "label": "12 CFR Part 1024", "short": "Reg X", "name": "Regulation X — RESPA", "summary": "Settlement-service kickbacks, affiliated business arrangements, escrow accounts, servicing transfers, error resolution, requests for information, force-placed insurance, and loss-mitigation procedures.", "url": ECFR12.format(part="1024")},
    {"id": "1002", "label": "12 CFR Part 1002", "short": "Reg B", "name": "Regulation B — ECOA", "summary": "Discrimination in credit transactions, what a creditor may ask, evaluation rules, adverse-action notices, record retention, government monitoring information, and appraisal copies.", "url": ECFR12.format(part="1002")},
    {"id": "1003", "label": "12 CFR Part 1003", "short": "Reg C", "name": "Regulation C — HMDA", "summary": "Which applications and loans are reported, the data fields on the loan/application register, and the annual filing.", "url": ECFR12.format(part="1003")},
    {"id": "1022", "label": "12 CFR Part 1022", "short": "Reg V", "name": "Regulation V — FCRA", "summary": "Consumer-report duties that sit with mortgage creditors, including risk-based pricing notices. The statute is the Fair Credit Reporting Act.", "url": "https://www.ecfr.gov/current/title-12/chapter-X/part-1022"},
    {"id": "1016", "label": "12 CFR Part 1016", "short": "Reg P", "name": "Regulation P — GLBA privacy", "summary": "Privacy notices and the limits on sharing nonpublic personal information by financial institutions under the CFPB's Regulation P.", "url": "https://www.ecfr.gov/current/title-12/chapter-X/part-1016"},
    {"id": "1007", "label": "12 CFR Part 1007", "short": "Reg G", "name": "Regulation G — SAFE Act registration", "summary": "Registration of mortgage loan originators who are employees of depository institutions and certain subsidiaries.", "url": ECFR12.format(part="1007")},
    {"id": "1008", "label": "12 CFR Part 1008", "short": "Reg H", "name": "Regulation H — SAFE Act state licensing", "summary": "The federal floor for state licensing and registration of mortgage loan originators who are not covered by Regulation G.", "url": ECFR12.format(part="1008")},
    {"id": "1014", "label": "12 CFR Part 1014", "short": "Reg N", "name": "Regulation N — MAP Rule", "summary": "Mortgage Acts and Practices advertising. Commercial communications about mortgage credit terms cannot be materially misleading.", "url": ECFR12.format(part="1014")},
    {"id": "tila", "label": "15 USC 1601 et seq.", "short": "TILA", "name": "Truth in Lending Act", "summary": "The statute behind Regulation Z, including ability-to-repay and HOEPA provisions now implemented in 12 CFR 1026.", "url": USC.format(title=15, section=1601)},
    {"id": "respa", "label": "12 USC 2601 et seq.", "short": "RESPA", "name": "Real Estate Settlement Procedures Act", "summary": "The statute behind Regulation X, including the Section 8 prohibition on kickbacks and unearned fees.", "url": USC.format(title=12, section=2601)},
    {"id": "ecoa", "label": "15 USC 1691 et seq.", "short": "ECOA", "name": "Equal Credit Opportunity Act", "summary": "The statute prohibiting discrimination in credit transactions, implemented by Regulation B.", "url": USC.format(title=15, section=1691)},
    {"id": "hmda", "label": "12 USC 2801 et seq.", "short": "HMDA", "name": "Home Mortgage Disclosure Act", "summary": "The statute requiring mortgage data collection and reporting, implemented by Regulation C.", "url": USC.format(title=12, section=2801)},
    {"id": "fcra", "label": "15 USC 1681 et seq.", "short": "FCRA", "name": "Fair Credit Reporting Act", "summary": "Permissible purposes, adverse-action duties, and the accuracy framework for consumer reports.", "url": USC.format(title=15, section=1681)},
    {"id": "glba", "label": "15 USC 6801 et seq.", "short": "GLBA", "name": "Gramm-Leach-Bliley Act privacy", "summary": "The privacy and safeguard duties for nonpublic personal information of customers.", "url": USC.format(title=15, section=6801)},
    {"id": "safe", "label": "12 USC 5101 et seq.", "short": "SAFE Act", "name": "SAFE Mortgage Licensing Act", "summary": "Licensing and registration of mortgage loan originators through NMLS, implemented in part by Regulations G and H and by state law.", "url": USC.format(title=12, section=5101)},
    {"id": "hpa", "label": "12 USC 4901 et seq.", "short": "HPA", "name": "Homeowners Protection Act", "summary": "Borrower-requested cancellation and automatic termination of private mortgage insurance on covered residential mortgages.", "url": USC.format(title=12, section=4901)},
    {"id": "udaap", "label": "12 USC 5531 and 5536", "short": "UDAAP", "name": "Unfair, deceptive, or abusive acts or practices", "summary": "The Dodd-Frank standards the CFPB uses against unfair, deceptive, or abusive conduct. There is no separate UDAAP part of Regulation Z.", "url": USC.format(title=12, section=5531)},
    {"id": "scra", "label": "50 USC 3901 et seq.", "short": "SCRA", "name": "Servicemembers Civil Relief Act", "summary": "Interest-rate relief and foreclosure protections for servicemembers. Distinct from the Military Lending Act.", "url": USC.format(title=50, section=3937)},
    {"id": "flood", "label": "42 USC 4012a", "short": "Flood", "name": "Flood insurance purchase requirement", "summary": "Mandatory flood insurance in a special flood hazard area for designated loans, and the FEMA National Flood Insurance Program.", "url": USC.format(title=42, section="4012a")},
    {"id": "fair-housing", "label": "42 USC 3601 et seq.", "short": "FHA Act", "name": "Fair Housing Act", "summary": "Discrimination prohibitions in housing and in residential real estate-related transactions, enforced primarily by HUD and the Department of Justice.", "url": USC.format(title=42, section=3604)},
    {"id": "bsa", "label": "31 USC 5311 / 31 CFR Chapter X", "short": "BSA/AML", "name": "Bank Secrecy Act and FinCEN rules", "summary": "Anti-money-laundering programs, suspicious-activity reporting, and customer identification. Residential mortgage lenders and originators have a FinCEN rule at 31 CFR Part 1029.", "url": "https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X/part-1029"},
    {"id": "mla", "label": "32 CFR Part 232", "short": "MLA", "name": "Military Lending Act", "summary": "Limits on certain consumer credit to covered borrowers. A residential mortgage secured by a dwelling is excluded from the MLA definition of consumer credit.", "url": "https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-M/part-232"},
    {"id": "fha", "label": "12 USC 1709 / HUD 4000.1", "short": "FHA", "name": "FHA single-family mortgage insurance", "summary": "The National Housing Act insurance program and HUD's Single Family Housing Policy Handbook 4000.1.", "url": "https://www.hud.gov/program_offices/housing/sfh/handbook_4000-1"},
    {"id": "va", "label": "38 USC Chapter 37 / VA Pamphlet 26-7", "short": "VA", "name": "VA-guaranteed home loans", "summary": "Eligibility, guaranty, underwriting, and refinance rules for VA loans, in the statute, 38 CFR Part 36, and the Lenders Handbook.", "url": "https://www.benefits.va.gov/homeloans/lenders.asp"},
    {"id": "usda", "label": "7 CFR Part 3555", "short": "USDA", "name": "USDA guaranteed rural housing", "summary": "The Single Family Housing Guaranteed Loan Program and HB-1-3555.", "url": "https://www.ecfr.gov/current/title-7/subtitle-B/chapter-XXXV/part-3555"},
    {"id": "hecm", "label": "24 CFR Part 206", "short": "HECM", "name": "Home Equity Conversion Mortgage", "summary": "FHA-insured reverse mortgages under the National Housing Act and 24 CFR Part 206.", "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-II/subchapter-B/part-206"},
    {"id": "fannie", "label": "Fannie Mae Selling Guide", "short": "Fannie", "name": "Fannie Mae Selling Guide", "summary": "Eligibility, underwriting, property, and mortgage-insurance rules for loans delivered to Fannie Mae, including Desktop Underwriter.", "url": "https://selling-guide.fanniemae.com/"},
    {"id": "freddie", "label": "Freddie Mac Guide", "short": "Freddie", "name": "Freddie Mac Seller/Servicer Guide", "summary": "Eligibility and servicing standards for loans sold to or serviced for Freddie Mac, including Loan Product Advisor.", "url": "https://guide.freddiemac.com/app/guide/"},
    {"id": "ginnie", "label": "Ginnie Mae", "short": "Ginnie", "name": "Ginnie Mae MBS", "summary": "The guarantor of securities backed by FHA, VA, USDA, and other government loans. Ginnie Mae is not a lender and does not set underwriting overlays.", "url": "https://www.ginniemae.gov/"},
    {"id": "fhfa", "label": "FHFA loan limits", "short": "FHFA", "name": "Conforming loan limits", "summary": "The Federal Housing Finance Agency publishes the baseline and high-cost-area conforming loan limits. The dollar amounts change.", "url": "https://www.fhfa.gov/data/conforming-loan-limit"},
    {"id": "cfpb", "label": "CFPB mortgage resources", "short": "CFPB", "name": "Consumer Financial Protection Bureau", "summary": "Official explainers, model forms, and the interactive regulations for the mortgage rules the Bureau administers.", "url": "https://www.consumerfinance.gov/compliance/compliance-resources/mortgage-resources/"},
    {"id": "esign", "label": "15 USC 7001", "short": "E-SIGN", "name": "Electronic Signatures in Global and National Commerce Act", "summary": "When an electronic signature or record can satisfy a writing requirement, and the consumer-consent rules that go with it.", "url": USC.format(title=15, section=7001)},
    {"id": "nmls", "label": "NMLS", "short": "NMLS", "name": "Nationwide Multistate Licensing System", "summary": "The registry used for SAFE Act licensing and registration. NMLS is the system; the SAFE Act and state law are the license rules.", "url": "https://mortgage.nationwidelicensingsystem.org/"},
    {"id": "urla", "label": "URLA / Form 1003", "short": "URLA", "name": "Uniform Residential Loan Application", "summary": "The standard application dataset used by Fannie Mae and Freddie Mac. It is a form, not a disclosure under TRID.", "url": "https://singlefamily.fanniemae.com/delivering/uniform-mortgage-data-program/uniform-residential-loan-application"},
    {"id": "safeguards", "label": "16 CFR Part 314", "short": "Safeguards", "name": "FTC Safeguards Rule", "summary": "Information-security program requirements for nonbank financial institutions under the Gramm-Leach-Bliley Act.", "url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314"},
    {"id": "red-flags", "label": "16 CFR Part 681", "short": "Red Flags", "name": "Identity theft red flags", "summary": "The identity-theft prevention program required of creditors that offer covered accounts.", "url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-F/part-681"},
    {"id": "ofac", "label": "OFAC", "short": "OFAC", "name": "Sanctions screening", "summary": "Treasury's Office of Foreign Assets Control administers economic sanctions. Mortgage lenders screen parties against the sanctions lists.", "url": "https://ofac.treasury.gov/"},
    {"id": "practice", "label": "Industry practice", "short": "Practice", "name": "File practice and market vocabulary", "summary": "Terms that desks use — clear to close, prior-to-doc, float-down — when no single regulation defines the phrase. The citation is the closest official source, marked industry practice.", "url": "https://selling-guide.fanniemae.com/"},
]

# slug, english term, batch, hint
RAW = [
# --- origination ---
("loan-estimate", "Loan Estimate", "o", "TRID form. Cite reg-1026-19 and reg-1026-37. Three business days after application is in 1026.19(e). Do not call it a GFE."),
("uniform-residential-loan-application", "Uniform Residential Loan Application", "o", "URLA, Fannie Form 1003 / Freddie Form 65. Not a TRID disclosure. Cite fannie-urla."),
("application-definition", "Application (six pieces)", "o", "Reg Z application for TRID exists when creditor has the six items in 12 CFR 1026.2(a)(3)(ii): name, income, SSN, property address, estimate of value, loan amount. Cite reg-1026-2."),
("intent-to-proceed", "Intent to proceed", "o", "1026.19(e)(2). After LE, creditor generally cannot impose a fee other than a bona fide reasonable credit-report fee until the consumer receives the LE and indicates intent to proceed."),
("rate-lock", "Rate lock", "o", "Creditor commitment to hold a rate for a period. Industry practice plus LE lock fields in 1026.37. Do not invent a federal lock period."),
("rate-lock-extension", "Rate lock extension", "o", "Industry extension of a lock. May be a changed circumstance only if the regulation's revision rules are actually met. Do not promise that an extension always permits a revised LE."),
("float-down", "Float-down", "o", "Contractual option to obtain a lower rate before closing. Industry/pricing. Not a TRID right."),
("loan-originator-compensation", "Loan originator compensation", "o", "12 CFR 1026.36(d). Compensation may not be based on a term of a transaction or a proxy, other than the amount of credit. No dual compensation."),
("borrower-paid-compensation", "Borrower-paid compensation", "o", "LO comp paid by the consumer. Still subject to 1026.36(d). Cannot be collected from both consumer and another person in the same transaction."),
("lender-paid-compensation", "Lender-paid compensation", "o", "LO comp paid by the creditor. 1026.36(d) prohibits dual compensation and term-based comp."),
("nmls", "NMLS", "o", "The registry system. SAFE Act is the statute. Cite usc-12-5101 and nmls. Do not say NMLS itself issues state licenses."),
("safe-act", "SAFE Act", "o", "12 USC 5101 and following; Reg G (1007) and Reg H (1008). Do not state current education hour counts; point to the statute and state law."),
("mortgage-loan-originator", "Mortgage loan originator", "o", "Defined in Reg Z 1026.36 and the SAFE Act. Takes an application or offers/negotiates terms for compensation."),
("pre-approval", "Pre-approval", "o", "Creditor review of credit and documentation before a property is identified. Not a TRID application until the six items, including property address, exist. Do not treat it as a commitment unless the creditor says so."),
("pre-qualification", "Pre-qualification", "o", "Informal payment estimate from unverified figures. Not an underwriting decision and not an application by itself."),
("origination-charges", "Origination charges", "o", "LE page 2, Section A. Zero-tolerance bucket under 1026.19(e)(3)(i) generally. Cite reg-1026-37 and reg-1026-19."),
("discount-points", "Discount points", "o", "Prepaid interest to reduce the note rate, usually shown in Section A. One point is 1 percent of the loan amount as a matter of market usage; say that is the customary meaning, not a statutory price."),
("lender-credits", "Lender credits", "o", "Amounts the creditor contributes, including credits for a higher rate. LE/CD presentation is in 1026.37 and 1026.38. General lender credits interact with tolerance cure math."),
("bona-fide-discount-point", "Bona fide discount point", "o", "Points that may be excluded from QM and HOEPA points-and-fees if they are bona fide under 1026.32(b)(1)(i)(E) and the related rules. Do not state the current exclusion math from memory if unsure; cite reg-1026-32 and reg-1026-43 and describe the concept."),
("written-list-of-providers", "Written list of providers", "o", "Required when the consumer can shop for a service. Identifying information for available providers. Affects whether a shoppable fee stays in the 10 percent bucket. Cite reg-1026-19."),
("services-you-can-shop-for", "Services you can shop for", "o", "LE page 2, Section C. Cite reg-1026-37 and the tolerance rules in reg-1026-19."),
("services-you-cannot-shop-for", "Services you cannot shop for", "o", "LE page 2, Section B. Generally zero tolerance if required by the creditor. Cite reg-1026-19 and reg-1026-37."),
("your-home-loan-toolkit", "Your Home Loan Toolkit", "o", "Special information booklet for federally related purchase mortgages. Reg X 1024.6. CFPB publishes the booklet."),
("homeownership-counseling-list", "Homeownership counseling list", "o", "Reg X 1024.20. List of HUD-approved counselors provided shortly after application. Do not invent the day count if unsure; the rule says within a prescribed period — cite the section and say the timing is in 1024.20."),
("business-day", "Business day", "o", "Reg Z uses two definitions in 1026.2(a)(6): a general business day, and a more specific rescission/CD business day (all calendar days except Sundays and legal public holidays). This distinction is the point of the entry."),
("consummation", "Consummation", "o", "When the consumer becomes contractually obligated on the loan, under state law. Not always the same day as settlement or funding. Cite reg-1026-2."),
("mortgage-broker", "Mortgage broker", "o", "A loan originator who is not the creditor. Comp and disclosure rules in 1026.36. Not the same as a creditor."),
("mortgage-lender", "Mortgage lender", "o", "The person to whom the obligation is initially payable, i.e. the creditor under Reg Z, when that person funds the loan. Distinguish broker and correspondent."),
("correspondent-lender", "Correspondent lender", "o", "A lender that originates and may fund in its own name and sells the loan. Table funding is a related but different concept. Industry plus Reg X definition of table funding if relevant."),
("wholesale-lending", "Wholesale lending", "o", "Channel in which a creditor funds loans originated by a broker. Industry practice. LO comp still applies."),
("retail-lending", "Retail lending", "o", "Channel in which the creditor's own originators take the application. Industry practice."),
("table-funding", "Table funding", "o", "Defined in Reg X 1024.2: a settlement at which a loan is funded by a contemporaneous advance of loan funds and an assignment to the person advancing the funds. Cite reg-1024-2."),
("loan-officer", "Loan officer", "o", "Common job title for a mortgage loan originator. The legal category is MLO under SAFE and 1026.36, not the job title."),
("loan-processor", "Loan processor", "o", "Collects documents and supports the file. Licensing depends on whether the person is an MLO under the SAFE Act definition. Do not say processors are never licensed."),
("co-borrower", "Co-borrower", "o", "A person who applies for and is obligated on the note. Contrast with co-signer and non-occupant co-borrower. URLA and Reg B."),
("co-signer", "Co-signer", "o", "A person who signs the note but is not an applicant in the same way. Reg B 1002.7 limits when a signature of a spouse or other person may be required."),
("non-occupant-co-borrower", "Non-occupant co-borrower", "o", "A borrower who will not occupy. Agency guides treat income, DTI, and contribution rules differently. Cite fannie guide and do not invent an occupancy percentage."),
("power-of-attorney", "Power of attorney", "o", "Agency guides and title practice allow a POA in limited cases. Not a right created by TRID. Cite fannie-guide and practice-file. Do not invent witness requirements."),
("gift-funds", "Gift funds", "o", "Fannie B3-4.3-04. Gifts from an acceptable donor for a principal residence or second home. Not allowed on investment property. Minimum borrower contribution rules differ by LTV and units. Do not restate the contribution table from memory if you might misstate it; cite the section and describe the structure."),
("gift-letter", "Gift letter", "o", "Donor letter required by agency guides: amount, no repayment, donor identity and relationship. Cite fannie-b3-4-3-04."),
("earnest-money", "Earnest money", "o", "Deposit under the purchase contract, credited on the CD. Source-of-funds documentation. Industry and agency asset rules."),
("purchase-agreement", "Purchase agreement", "o", "Contract that supplies sale price, concessions, and property details used for LTV and TRID. Not a federal form."),
("seller-concessions", "Seller concessions", "o", "Seller-paid costs. Interested-party contribution limits are in agency guides and differ by occupancy and LTV. Do not hardcode the current IPC grid; cite fannie-guide and say the caps are in the guide and change."),
("interested-party-contributions", "Interested party contributions", "o", "Payments by seller, builder, agent, or other interested party toward borrower costs. Agency guides cap them. Do not state a current percentage cap as if it cannot change; cite the guide and describe that caps depend on occupancy and LTV."),
("down-payment", "Down payment", "o", "Borrower's cash investment. Minimums differ by program and are set in agency guides and HUD/VA/USDA rules. Do not hardcode FHA 3.5 percent as a current figure; say HUD publishes the minimum cash investment in 4000.1."),
("source-of-funds", "Source of funds", "o", "Documenting that funds to close are eligible and not undisclosed borrowed funds. Agency asset sections."),
("cash-to-close", "Cash to close", "o", "LE and CD calculating-cash-to-close table. Cite reg-1026-37 and reg-1026-38."),
("rate-lock-confirmation", "Rate lock confirmation", "o", "The creditor's written lock terms. Industry practice. The LE also discloses whether the rate is locked and until when."),
("e-sign-act", "E-SIGN Act", "o", "15 USC 7001. Electronic records and signatures. Consumer consent requirements before electronic delivery can replace certain written disclosures."),
("electronic-consent", "Electronic consent", "o", "The E-SIGN consumer consent demonstrable-ability process. Cite usc-15-7001. Do not confuse with intent to proceed."),
("fee-worksheet", "Fee worksheet", "o", "A pre-application worksheet is not a Loan Estimate. If it looks like an LE it can create TRID problems. Cite reg-1026-19 and CFPB forms guidance. Mark the worksheet itself industry practice."),
("prepaids", "Prepaids", "o", "LE page 2, Section F. Prepaid interest, insurance, taxes. Generally in the no-tolerance or variation-permitted category when not required by the creditor in a zero-tolerance way. Be careful: prepaid interest can change with the per diem. Cite reg-1026-19 and reg-1026-37."),
("initial-escrow-payment", "Initial escrow payment at closing", "o", "LE page 2, Section G. Deposit to start the escrow account. Cite reg-1026-37 and reg-1024-17 for escrow accounting."),
("settlement-service", "Settlement service", "o", "RESPA definition in 1024.2. Broad list of services incident to a federally related mortgage. The hook for Section 8."),
("mortgage-broker-compensation", "Mortgage broker compensation", "o", "Shown on the LE and subject to 1026.36. Do not describe a legal way to pay a broker twice."),
("creditor", "Creditor", "o", "Reg Z definition: the person to whom the obligation is initially payable, regularly extending credit. Cite reg-1026-2."),
("credit-report-fee", "Credit report fee", "o", "The fee that may be charged before intent to proceed if it is bona fide and reasonable. 1026.19(e)(2)."),
("changed-circumstance", "Changed circumstance", "o", "Defined for revised LE purposes in 1026.19(e)(3)(iv). An extraordinary event, inaccurate information, or new information specific to the consumer or transaction. Not every change qualifies. Timing to reset charges is in that paragraph. Do not invent extra grounds."),
("revised-loan-estimate", "Revised Loan Estimate", "o", "A new LE permitted only for the reasons in 1026.19(e)(3)(iv), generally within three business days of receiving the information, and not on or after the CD when the rule forbids it. Cite reg-1026-19."),
# --- underwriting u1 ---
("debt-to-income-ratio", "Debt-to-income ratio", "u1", "Total monthly obligations divided by qualifying income. Fannie B3-6-02 publishes manual and DU maximums that the guide can revise. Say the caps are in the current Selling Guide and cite it; you may mention that manual and DU are treated differently. Do not present a number as a statute."),
("housing-expense-ratio", "Housing expense ratio", "u1", "Front-end ratio: proposed housing payment over income. Fannie emphasizes total DTI. FHA and VA treat housing and residual income in their own handbooks. Do not invent a universal 28 percent rule as law."),
("loan-to-value-ratio", "Loan-to-value ratio", "u1", "Fannie B2-1.2-01. Purchase: loan amount divided by the lesser of price or appraised value. Describe rounding only if you cite the guide. Cite fannie-b2-1-2-01."),
("combined-loan-to-value", "Combined loan-to-value ratio", "u1", "First lien plus other financed amounts secured by the property, over value. Cite fannie-b2-1-2-01."),
("hcltv", "HCLTV", "u1", "Home equity combined LTV includes the undrawn HELOC limit, not just the balance. Cite fannie-b2-1-2-01."),
("automated-underwriting-system", "Automated underwriting system", "u1", "Umbrella term for DU, LPA, TOTAL, GUS. The finding is not a legal approval. Cite fannie-b3-2 and freddie-lpa and hud-4000-1."),
("desktop-underwriter", "Desktop Underwriter", "u1", "Fannie Mae AUS. Recommendations include Approve/Eligible. Cite fannie-b3-2-01. Lender must still verify data and conditions."),
("loan-product-advisor", "Loan Product Advisor", "u1", "Freddie Mac AUS. Do not invent recommendation names if unsure; describe risk class and eligibility and cite freddie-lpa."),
("fha-total-scorecard", "FHA TOTAL Scorecard", "u1", "FHA's TOTAL Mortgage Scorecard used with an AUS. HUD 4000.1. A refer result requires manual underwriting."),
("gus", "GUS", "u1", "USDA Guaranteed Underwriting System. Cite usda-hb and cfr-7-3555. Do not invent score cutoffs."),
("reserves", "Reserves", "u1", "Liquid assets remaining after closing, measured in months of PITIA. Fannie B3-4.1-01. Requirements vary by transaction. Do not hardcode a universal months number as applying to every loan."),
("appraisal", "Appraisal", "u1", "Opinion of value. ECOA appraisal-copy rule is 1002.14. ATR/valuation independence is 1026.42. Agency property standards in the selling guide and HUD 4000.1. AIR for conventional."),
("value-acceptance", "Value acceptance", "u1", "Fannie offer to accept value without an appraisal in some cases. B4-1.4-10. Not a waiver the lender invents. Formerly called an appraisal waiver in market speech; use Fannie's current name and mention the old phrase as an alias."),
("appraisal-independence-requirements", "Appraisal independence", "u1", "Reg Z 1026.42 and the agency Appraiser Independence Requirements. No one may cause the value to be based on a desired result."),
("uniform-appraisal-dataset", "Uniform Appraisal Dataset", "u1", "Standard data format for appraisal reports delivered to the GSEs. Cite fannie-b4-1-1-02 or fannie-guide."),
("uniform-collateral-data-portal", "Uniform Collateral Data Portal", "u1", "The portal used to submit appraisal data to the GSEs. Cite fannie-guide."),
("verification-of-employment", "Verification of employment", "u1", "Documenting employment and income. Fannie B3-3.2-01 and B3-3.1-01. Written VOE is not the same as verbal VOE."),
("verbal-verification-of-employment", "Verbal verification of employment", "u1", "Fannie B3-3.1-04. Timing is in the guide and differs for employment versus self-employment. Do not state a day count unless you describe it as guide text that can be revised and cite the section."),
("verification-of-income", "Verification of income", "u1", "Third-party or document verification of qualifying income. Related to ATR documentation and agency guides."),
("verification-of-deposit", "Verification of deposit", "u1", "Asset verification. Bank statements or a VOD. Cite fannie guide asset section via fannie-guide if you lack a tighter id."),
("pay-stub", "Pay stub", "u1", "Standard employment income document. Fannie B3-3.2-01. Do not invent a required stub count as law; the guide states the documentation standard."),
("form-w-2", "Form W-2", "u1", "Wage and tax statement used with pay stubs and sometimes transcripts. Agency income documentation."),
("tax-returns", "Tax returns", "u1", "Required for self-employment and certain other income. Fannie B3-3.1-02. Personal returns are Form 1040."),
("form-4506-c", "Form 4506-C", "u1", "IRS form authorizing a transcript. Fannie B3-3.1-02. Do not call it 4506-T as the current form; 4506-C replaced it. Mention 4506-T only as a former name."),
("self-employment-income", "Self-employment income", "u1", "Fannie section B3-3.5. Generally a history and access to the business income. Do not invent a universal two-year rule as a statute; the guide states the history it wants and the exceptions."),
("bank-statements", "Bank statements", "u1", "Asset documentation and, in non-agency programs, sometimes income documentation. Distinguish agency asset statements from a bank-statement non-QM program."),
("large-deposit", "Large deposit", "u1", "Agency guides require sourcing deposits that are large relative to income. Do not invent the percentage threshold; cite fannie-guide and say the guide defines what must be sourced."),
("seasoned-funds", "Seasoned funds", "u1", "Funds that have been in the account long enough that the guide does not require the same sourcing. The seasoning period is guide text. Cite fannie-guide and do not state a day count as if it were a statute."),
("tri-merge-credit-report", "Tri-merge credit report", "u1", "Report from Experian, Equifax, and TransUnion. Fannie B3-5.2-01. Permissible purpose under FCRA."),
("credit-score", "Credit score", "u1", "A score on the credit report. The representative score for the loan is a separate defined step. FCRA adverse-action score disclosure may apply. Cite fannie-b3-5-1-01 and usc-15-1681m."),
("representative-credit-score", "Representative credit score", "u1", "Fannie B3-5.1-02. For one borrower, generally the middle of three or the lower of two. For multiple borrowers, the guide selects among the borrower scores. Describe the method and cite the section rather than paraphrasing a shortcut that might be wrong."),
("tradeline", "Tradeline", "u1", "A credit account reported on the credit report. Agency credit history uses tradelines to measure depth of credit. Cite fannie-b3-5-2-01."),
("collection-account", "Collection account", "u1", "A debt with a collection. How it counts in DTI and whether it must be paid is guide- and program-specific. Do not state a universal payoff rule."),
("charge-off", "Charge-off", "u1", "A creditor has written the debt off for accounting. It can remain collectible. Underwriting treatment is program-specific."),
("bankruptcy-seasoning", "Bankruptcy seasoning", "u1", "Waiting period after bankruptcy before a new mortgage. Fannie B3-5.3-07. Periods differ by chapter and extenuating circumstances and the guide revises them. Cite the section and do not present a single number of years as applying to every case."),
("foreclosure-seasoning", "Foreclosure seasoning", "u1", "Waiting period after foreclosure, deed-in-lieu, or short sale. Same section family as bankruptcy. Do not collapse all events into one number."),
("credit-inquiry", "Credit inquiry", "u1", "Fannie B3-5.3-04. Recent inquiries may require an explanation or verification that no new debt was opened."),
("letter-of-explanation", "Letter of explanation", "u1", "Borrower statement addressing a credit, address, employment, or deposit question. It does not replace documentation the guide requires."),
# --- underwriting u2 ---
("installment-debt", "Installment debt", "u2", "Amortizing debt with a fixed payment. Fannie B3-6-05. When a payment may be omitted because few payments remain is in the guide. Do not invent the remaining-payment count."),
("revolving-debt", "Revolving debt", "u2", "Credit cards and lines. If no payment is reported, guides impute a payment. Do not state the imputation percentage from memory; cite fannie-b3-6-05 and say the guide specifies the payment to use."),
("student-loans", "Student loan payment", "u2", "Income-driven payments and deferred loans have specific guide treatments. Cite fannie-b3-6-05. Do not invent the percentage of the balance used when a payment is missing."),
("authorized-user", "Authorized user account", "u2", "Fannie B3-5.3-06. An authorized-user tradeline is not the same as a joint obligation. DU and manual rules differ."),
("community-property", "Community property", "u2", "State-law marital property regime. Non-borrowing spouse debts may count. Cite fannie-guide and reg-1002-6. Do not list states unless you are sure; say it depends on state law."),
("non-borrowing-spouse", "Non-borrowing spouse", "u2", "A spouse who is not on the note. Reg B limits required signatures. Community-property debts can still matter. Cite reg-1002-7."),
("residual-income", "Residual income", "u2", "Money left after debts, taxes, and the housing payment. Central to VA underwriting in Pamphlet 26-7 Chapter 4. FHA manual underwriting can use it as a compensating factor by reference to the VA table. Do not reprint the dollar chart; it is regional and household-size specific and should be read from the handbook."),
("compensating-factor", "Compensating factor", "u2", "A strength that can offset a weakness in manual underwriting. What counts is program-specific. Cite fannie-b3-1-01 and hud-4000-1."),
("manual-underwriting", "Manual underwriting", "u2", "A person, not an AUS approval, makes the credit decision. Fannie B3-1-01. Required documentation is usually heavier. DU Approve is not manual."),
("approve-eligible", "Approve/Eligible", "u2", "DU recommendation. Fannie B3-2-05. Meets Fannie credit risk and eligibility only if data are accurate and conditions are cleared."),
("approve-ineligible", "Approve/Ineligible", "u2", "DU B3-2-06. Credit risk may be acceptable but an eligibility rule failed. Not a denial by itself and not a license to deliver."),
("refer-with-caution", "Refer with Caution", "u2", "DU B3-2-07. Not an Approve recommendation. Describe it from the guide, not as an automatic denial."),
("out-of-scope", "Out of Scope", "u2", "DU B3-2-08. The casefile is outside what DU evaluates."),
("underwriting-conditions", "Underwriting conditions", "u2", "Requirements that must be cleared before documents or funding. Industry file language. Cite practice-file and fannie-b3-2-11 for DU conditions."),
("prior-to-document", "Prior-to-document condition", "u2", "Industry shorthand for a condition due before the closing package is drawn. Not a regulatory category."),
("prior-to-funding", "Prior-to-funding condition", "u2", "Industry shorthand for a condition due before the loan funds. Not a regulatory category."),
("clear-to-close", "Clear to close", "u2", "Internal status meaning conditions required before closing are cleared. Not a federal status and not consummation."),
("conditional-approval", "Conditional approval", "u2", "Approval subject to conditions. It is not clear-to-close and not a commitment to fund if conditions fail."),
("occupancy", "Occupancy", "u2", "Principal residence, second home, or investment. Misstatement is a serious eligibility and fraud issue. Cite fannie-guide. Do not provide advice on how to misstate occupancy."),
("primary-residence", "Primary residence", "u2", "The borrower will occupy as the principal residence. Agency guides require intent to occupy within a stated period. Cite the guide and do not invent the day count; say the guide sets the occupancy timeline."),
("second-home", "Second home", "u2", "A one-unit property occupied by the borrower for part of the year, not subject to rental controls the way a principal residence is, and not a rental investment. Guide requirements restrict rental and property type. Cite fannie-guide."),
("investment-property", "Investment property", "u2", "Held for rental or other income, not occupied as a principal or second home. Different LTV, reserve, and gift rules."),
("pitia", "PITIA", "u2", "Principal, interest, taxes, insurance, and association dues or similar assessments. The qualifying housing payment. Cite fannie-b3-6-03."),
("qualifying-rate", "Qualifying rate", "u2", "The rate used to calculate the payment for DTI, which may differ from the start rate on an ARM or buydown. Cite fannie-b3-6-04. Do not state a universal fully-indexed or note-rate-plus formula unless you tie it to the specific product and the current guide."),
("stable-income", "Stable monthly income", "u2", "Fannie B3-3.1-01. Income that is stable, documented, and expected to continue. The three-year continuance test applies only to income with a defined expiration."),
("bonus-overtime-commission", "Bonus, overtime, and commission income", "u2", "Fannie B3-3.3-02. History and likelihood of continuance. Do not state a universal two-year average as a statute."),
("rental-income", "Rental income", "u2", "Subject property and other real estate. Schedules E, leases, and add-backs are guide-specific. Cite fannie-guide. Do not invent a vacancy factor."),
("schedule-c", "Schedule C income", "u2", "Sole proprietorship income on Form 1040 Schedule C. Part of self-employment analysis. Cite fannie-b3-3-5."),
("schedule-k-1", "Schedule K-1 income", "u2", "Partnership or S corporation income reported on a K-1. Percentage of ownership changes the analysis. Fannie has a K-1 topic. Cite fannie-b3-3-5 and do not invent the ownership percentage cutoff."),
("nontaxable-income", "Nontaxable income", "u2", "May be grossed up under agency rules because it is not taxed. Cite fannie-guide and say the gross-up factor is in the guide. Do not hardcode a percentage if you are not looking at the current section."),
("employment-gap", "Employment gap", "u2", "A break in employment that may need an explanation. Guide treatment depends on the income type. Do not invent a maximum gap."),
("multiple-financed-properties", "Multiple financed properties", "u2", "Fannie limits the number of financed properties and adds reserves for second homes and investment properties. Cite fannie-b3-4-1-01 and fannie-guide. The numeric cap is guide policy; say it is in the guide rather than quoting a number you have not verified in this session."),
("gift-of-equity", "Gift of equity", "u2", "Fannie B3-4.3-05. Equity the seller gives the buyer, documented. Not the same as a cash gift. A gift of equity may not be used as reserves."),
("subordinate-financing", "Subordinate financing", "u2", "A second lien or HELOC behind the first mortgage. Included in CLTV and HCLTV. Cite fannie-b2-1-2-01."),
("debts-paid-at-closing", "Debts paid at closing", "u2", "Fannie B3-6-07. A debt paid off at or before closing may be omitted from DTI if the guide's conditions are met, including source of funds."),
("undisclosed-debt", "Undisclosed debt", "u2", "Debt that appears after the credit report, often through a monitoring service or a new inquiry. May require resubmission to the AUS. Cite fannie-b3-2-10 on data accuracy."),
("homeowners-association", "Homeowners association", "u2", "Collects dues that count in PITIA and may have to be current. Project eligibility is a separate question. Cite fannie-b3-6-03."),
("condominium-project", "Condominium project review", "u2", "Agency review of the project, not just the unit appraisal. Warrantable versus non-warrantable is guide language. Cite fannie-guide. Do not invent the owner-occupancy or delinquency percentage."),
("planned-unit-development", "Planned unit development", "u2", "A PUD is a project of individual lots with common areas. Different from a condo. Cite fannie-guide."),
("manufactured-housing", "Manufactured housing", "u2", "Built to the HUD code, not the same as modular or mobile in older usage. Titling as real property versus chattel changes eligibility. Cite fannie-guide and hud-4000-1. Do not invent width or year cutoffs."),
("flood-determination", "Flood zone determination", "u2", "A determination of whether the improvements are in a Special Flood Hazard Area. Triggers flood insurance if it is a designated loan. Cite usc-42-4012a and fema-flood."),
("homeowners-insurance", "Homeowners insurance", "u2", "Hazard insurance required by the security instrument and guides. Not the same as mortgage insurance or flood insurance. Cite fannie-guide."),
("du-validation-service", "DU validation service", "u2", "Fannie B3-2-02. Electronic validation of income, employment, or assets that can replace some documents. Market name Day 1 Certainty is an alias. Validation is optional and message-specific."),
("income-calculator", "Income Calculator", "u2", "Fannie B3-3.1-03. A Fannie tool for calculating certain income. Using it has guide conditions. Do not describe it as required for every file."),
("alimony-child-support", "Alimony and child support", "u2", "Can be qualifying income or a debt. Fannie B3-3.4-02 and B3-6-05. ECOA limits how the creditor treats it. Cite reg-1002-6 as well."),
("public-assistance-income", "Public assistance income", "u2", "ECOA prohibits discounting income because it comes from public assistance. 1002.6. Documentation is still required. Fannie B3-3.4-12."),
("asset-documentation", "Asset documentation", "u2", "Statements, verifications, and large-deposit sourcing used for funds to close and reserves. Cite fannie-guide."),
# --- compliance c1 ---
("trid", "TRID", "c1", "TILA-RESPA Integrated Disclosure rule. The Loan Estimate and Closing Disclosure for most closed-end consumer mortgages secured by real property. Implemented in Reg Z 1026.19, 1026.37, and 1026.38. Name the main exemptions: HELOC, reverse mortgage, chattel-dwelling not secured by real property, and certain housing-assistance loans."),
("tila", "Truth in Lending Act", "c1", "15 USC 1601 et seq. Implemented for these purposes by Regulation Z. Do not use TILA and RESPA interchangeably."),
("regulation-z", "Regulation Z", "c1", "12 CFR Part 1026. The CFPB's TILA regulation. Overview entry that points to the part."),
("respa", "RESPA", "c1", "12 USC 2601 et seq. Settlement procedures, kickbacks, escrow, servicing. Implemented by Regulation X. TRID moved the GFE and HUD-1 for most closed-end mortgages into Reg Z."),
("regulation-x", "Regulation X", "c1", "12 CFR Part 1024. Overview entry."),
("ecoa", "Equal Credit Opportunity Act", "c1", "15 USC 1691. Implemented by Regulation B. Prohibits discrimination on a prohibited basis."),
("regulation-b", "Regulation B", "c1", "12 CFR Part 1002. Overview entry."),
("hmda", "Home Mortgage Disclosure Act", "c1", "12 USC 2801. Implemented by Regulation C. Data collection, not a disclosure to the borrower at application."),
("regulation-c", "Regulation C", "c1", "12 CFR Part 1003. Overview entry."),
("fcra", "Fair Credit Reporting Act", "c1", "15 USC 1681. Permissible purpose, adverse action, dispute duties. Regulation V is 12 CFR 1022."),
("regulation-v", "Regulation V", "c1", "12 CFR Part 1022. Overview entry. Include risk-based pricing notice pointer."),
("glba", "Gramm-Leach-Bliley Act", "c1", "15 USC 6801. Privacy and safeguards. Regulation P is the CFPB privacy rule. The Safeguards Rule for many nonbanks is FTC 16 CFR 314."),
("regulation-p", "Regulation P", "c1", "12 CFR Part 1016. Privacy notices and reuse limits."),
("ability-to-repay", "Ability to repay", "c1", "12 CFR 1026.43(c) and 15 USC 1639c. Eight underwriting factors. A QM is one way to presume ATR. Do not say QM is the only legal mortgage."),
("qualified-mortgage", "Qualified mortgage", "c1", "12 CFR 1026.43(e). Restrictions on product features, a points-and-fees cap, and underwriting. Dollar breakpoints in the cap are adjusted annually — do not state this year's dollar cutoffs. The 3 percent tier is the regulatory cap for loans at or above the adjusted threshold; say the percentage steps and the dollar thresholds are in 1026.43 and the CFPB's annual adjustment."),
("general-qualified-mortgage", "General qualified mortgage", "c1", "The QM definition based on price and underwriting in 1026.43(e), as amended. Do not describe the expired temporary GSE QM patch as if it were still the general rule. If you mention the patch, say it ended and cite the current section."),
("qm-safe-harbor", "Qualified mortgage safe harbor", "c1", "A QM that is not higher-priced receives a safe harbor of compliance with ATR. 1026.43(b) and (e). A higher-priced QM receives a rebuttable presumption, not a safe harbor."),
("rebuttable-presumption", "Rebuttable presumption QM", "c1", "A higher-priced qualified mortgage is presumed to comply with ATR, and the consumer can rebut that presumption. Cite reg-1026-43 and reg-1026-35."),
("points-and-fees", "Points and fees", "c1", "The QM and HOEPA calculation in 1026.32(b), used by 1026.43. What is included and excluded is specific. Bona fide discount points can be excluded only if the rule is met. Do not state this year's dollar threshold."),
("hoepa", "HOEPA", "c1", "Home Ownership and Equity Protection Act, implemented at 12 CFR 1026.32 and 1026.34. High-cost mortgage coverage tests. APR and points-and-fees thresholds are adjusted. Do not state this year's numbers. Cite the sections."),
("high-cost-mortgage", "High-cost mortgage", "c1", "A loan that triggers HOEPA. Additional restrictions, counseling, and ability-to-repay style limits. Cite reg-1026-32 and reg-1026-34."),
("higher-priced-mortgage-loan", "Higher-priced mortgage loan", "c1", "Defined in 1026.35(a) by an APR spread over APOR. The regulatory spreads are 1.5, 2.5, and 3.5 percentage points depending on lien and loan size. Say those are the spreads in the regulatory text and the reader should confirm the current subsection because it has been amended. Do not confuse with high-cost/HOEPA."),
("hpml-escrow", "HPML escrow requirement", "c1", "1026.35(b) requires an escrow account for certain higher-priced mortgage loans, with exemptions. Do not list exemption dollar amounts that adjust; cite the section."),
("hpml-appraisal", "HPML appraisal rule", "c1", "1026.35(c) requires a written appraisal and, for some flips, a second appraisal. Describe the existence of the rule and cite the section. Do not invent the flip price-increase percentages unless you are sure; you may omit the percentages and point to the section."),
("finance-charge", "Finance charge", "c1", "12 CFR 1026.4. The cost of consumer credit in dollars. Not the same as APR and not the same as all closing costs. Some real-estate related fees are excluded if bona fide and reasonable."),
("annual-percentage-rate", "Annual percentage rate", "c1", "12 CFR 1026.22. The cost of credit as a yearly rate, including certain finance charges. Not the note rate. Disclosed on the LE and CD."),
("amount-financed", "Amount financed", "c1", "Reg Z disclosure of the amount of credit provided to the consumer or on the consumer's behalf. 1026.18 for non-TRID closed-end; TRID uses the LE/CD calculations. Do not equate it with the note principal."),
("prepayment-penalty", "Prepayment penalty", "c1", "A charge for paying early. QM limits prepayment penalties. 1026.43. Adding a prepayment penalty is also one of the CD changes that can reset the three-business-day wait under 1026.19(f)(2)."),
("right-of-rescission", "Right of rescission", "c1", "12 CFR 1026.23. For many refinances and closed-end junior liens on a principal dwelling, each consumer with an ownership interest may rescind until midnight of the third business day. Purchases and some other transactions are exempt. Use the rescission business-day definition."),
("loan-originator-rule", "Loan originator rule", "c1", "Reg Z 1026.36 as a whole: compensation, qualification, and prohibited steering and loan-document practices. Distinct from the SAFE Act license."),
("anti-steering", "Anti-steering", "c1", "12 CFR 1026.36(e). A loan originator may not steer a consumer to a transaction that increases originator compensation unless the safe-harbor loan options were presented. Describe the safe harbor only at a high level and cite the section."),
# --- compliance c2 ---
("udaap", "UDAAP", "c2", "Unfair, deceptive, or abusive acts or practices. 12 USC 5531 and 5536. There is no UDAAP CFR part. Define unfair, deceptive, and abusive from the statute at a high level and do not invent elements."),
("unfair-practice", "Unfair act or practice", "c2", "12 USC 5531(c). Substantial injury, not reasonably avoidable, not outweighed by benefits. Cite the statute. Do not add a fourth element."),
("deceptive-practice", "Deceptive act or practice", "c2", "The CFPB uses a representation, omission, or practice that misleads or is likely to mislead a reasonable consumer, and that is material. The standard is articulated in CFPB examination and enforcement materials rather than a single CFR section. Cite usc-12-5531 and cfpb-mortgage-resources. Mark the exam-manual gloss carefully and do not invent a CFR cite."),
("abusive-practice", "Abusive act or practice", "c2", "12 USC 5531(d). Materially interferes, or takes unreasonable advantage of a lack of understanding, inability to protect, or reasonable reliance. Quote the structure, not a made-up test."),
("fair-lending", "Fair lending", "c2", "The set of ECOA and Fair Housing Act duties, plus UDAAP overlap. Not a single form. Cite ecoa, reg B, and fair housing."),
("disparate-treatment", "Disparate treatment", "c2", "Treating people differently on a prohibited basis. ECOA and Fair Housing. Includes overt discrimination and less obvious unequal treatment. Cite reg-1002-4."),
("disparate-impact", "Disparate impact", "c2", "A neutral policy with a disproportionate adverse effect on a prohibited basis, without a sufficient justification. It is a contested and fact-specific theory. Do not overstate that every gap is a violation. Cite the Fair Housing Act and Regulation B and flag the entry for expert review because case law moves."),
("fair-housing-act", "Fair Housing Act", "c2", "42 USC 3601 and following, especially 3604 and 3605. Protected classes are not identical to ECOA. Do not merge the two lists. HUD is the primary enforcing agency."),
("redlining", "Redlining", "c2", "Denying or discouraging credit in a geographic area because of the race or other protected characteristic of residents. Fair lending. Do not provide targeting advice. Cite fair housing and ECOA."),
("steering", "Steering", "c2", "Directing a borrower to a product or neighborhood for an improper reason. Can be a fair-lending issue and, separately, a 1026.36(e) compensation issue. Keep the two doctrines distinct."),
("flood-insurance", "Flood insurance", "c2", "Required on designated loans secured by improved real property in a special flood hazard area. 42 USC 4012a. Coverage amount rules are statutory. Do not state a premium. Cite fema-flood."),
("special-flood-hazard-area", "Special flood hazard area", "c2", "FEMA-mapped area where mandatory purchase applies, generally zones beginning with A or V. Say 'generally' and cite FEMA rather than pretending every map panel is simple."),
("bank-secrecy-act", "Bank Secrecy Act", "c2", "31 USC 5311 and following. AML program and reporting. Mortgage companies that are residential mortgage lenders or originators look to 31 CFR 1029."),
("anti-money-laundering", "Anti-money-laundering program", "c2", "Policies, controls, a compliance officer, training, and independent testing. For nonbank mortgage lenders, 31 CFR 1029.210 is the program requirement if you are confident; otherwise cite cfr-31-1029 at the part level and do not invent a subsection."),
("customer-identification-program", "Customer identification program", "c2", "Banks have a CIP rule. Nonbank mortgage CIP expectations should not be stated as if they were the bank CIP at 31 CFR 1020.220 unless that section applies. Cite cfr-31-1029 and fincen and describe customer identification at a program level. Flag if you discuss nonbank CIP specifics."),
("suspicious-activity-report", "Suspicious activity report", "c2", "A SAR is filed with FinCEN. Do not describe how to structure a transaction to avoid a SAR. Cite 31 USC 5318 and cfr-31-1029. Do not state a dollar threshold unless you cite the current subsection; thresholds differ by institution type. Safer to say the threshold and the confidentiality rule are in the FinCEN rule and that a SAR is confidential."),
("ofac-screening", "OFAC screening", "c2", "Screening parties against sanctions lists. Cite ofac. Do not invent a match-resolution procedure as law."),
("state-licensing", "State mortgage licensing", "c2", "SAFE Act floor plus state statutes. License triggers, surety bonds, and net worth are state law. Do not state a bond amount. Cite usc-12-5104 and reg-1008 and nmls."),
("mortgage-advertising", "Mortgage advertising", "c2", "Reg Z 1026.24 and the MAP Rule, Reg N, 12 CFR 1014. Trigger terms, clear and conspicuous disclosures, and a ban on material misrepresentation."),
("trigger-terms", "Trigger terms", "c2", "Specific credit terms in an advertisement that require additional disclosures under 1026.24. Do not invent the list; name examples you are sure of (the amount or percentage of any down payment, the number of payments or period of repayment, the amount of any payment, the amount of any finance charge) and cite the section."),
("map-rule", "MAP Rule", "c2", "Regulation N, 12 CFR 1014. Mortgage Acts and Practices — Advertising. Prohibits material misrepresentations in commercial communications about mortgage products."),
("adverse-action-notice", "Adverse action notice", "c2", "Reg B 1002.9. Generally within 30 days of a completed application. Content requirements include the statement of action, reasons or the right to request them, and ECOA notice. FCRA adds score and credit-agency content when a consumer report was used. Cite both."),
("appraisal-delivery", "Appraisal delivery", "c2", "Reg B 1002.14. Provide a copy of appraisals and other written valuations promptly upon completion, or no later than three business days before consummation, whichever is earlier. Applicant may waive the timing but must still receive the copy no later than at or before consummation. Do not shorten this into 'three days' without the promptly-upon-completion branch."),
("hmda-lar", "HMDA loan/application register", "c2", "The LAR. Data fields are in 1003.4. Submission timing is in 1003.5. You may say the annual submission deadline is in 1003.5 rather than stating the calendar date, or state March 1 only if you describe it as the regulatory deadline in 1003.5 and note it can fall on the next business day. Safer: cite 1003.5 and say the annual deadline is specified there."),
("demographic-information", "Demographic information", "c2", "HMDA and Reg B monitoring information: ethnicity, race, and sex collected for government monitoring. 1003.4 and 1002.13. Taking it is required in covered cases; using it to discriminate is forbidden."),
("affiliated-business-arrangement", "Affiliated business arrangement", "c2", "Reg X 1024.15. A person referring settlement-service business to an affiliate may receive a return on ownership if the AfBA disclosure is given, the use is not required, and the only thing of value is a permissible return. Cite reg-1024-15."),
("respa-section-8", "RESPA Section 8", "c2", "12 USC 2607 and 12 CFR 1024.14. No kickback or split of a charge except for services actually performed. Things of value are broad."),
("kickback", "Kickback", "c2", "A thing of value given for the referral of settlement-service business. Illegal under RESPA Section 8. Cite reg-1024-14. Do not describe how to disguise one."),
("thing-of-value", "Thing of value", "c2", "Reg X 1024.14. Broad: money, discounts, trips, free marketing, and other benefits. The definition is in the section and the official interpretations."),
("privacy-notice", "Privacy notice", "c2", "Regulation P. Initial and annual privacy notices, with an exception from the annual notice in some cases. Do not state that every institution must mail a full annual notice every year; the exception is real. Cite reg-1016."),
("safeguards-rule", "Safeguards Rule", "c2", "FTC 16 CFR Part 314 for nonbanks. Written information-security program. Do not attribute this part to the CFPB."),
("risk-based-pricing-notice", "Risk-based pricing notice", "c2", "12 CFR 1022.72 and FCRA. Notice when credit is on materially less favorable terms based on a consumer report. The credit-score disclosure exception exists. Cite the section and do not invent the cutoff."),
("permissible-purpose", "Permissible purpose", "c2", "FCRA 15 USC 1681b. A consumer report may be pulled only for a listed purpose, commonly a credit transaction involving the consumer. Do not suggest pulling credit without a purpose."),
("dodd-frank-act", "Dodd-Frank Act", "c2", "The 2010 Act that created the CFPB and enacted ATR/QM, LO comp amendments, and UDAAP. Cite usc-12-5531 as one anchor and describe it as the statute, not a CFR part."),
("cfpb", "Consumer Financial Protection Bureau", "c2", "The federal agency that administers Regs Z, X, B, C, V, and P for most mortgage creditors. It does not insure deposits and it is not a lender."),
("scra", "Servicemembers Civil Relief Act", "c2", "50 USC 3937 is the six-percent interest-rate cap on pre-service debts, upon a proper request. 50 USC 3953 addresses mortgage foreclosure protections. Do not confuse with the Military Lending Act. The six percent figure is statutory."),
("military-lending-act", "Military Lending Act", "c2", "10 USC 987 and 32 CFR Part 232. A residential mortgage secured by a dwelling is excluded from consumer credit under 32 CFR 232.3(f)(2). Do not tell lenders to ignore SCRA because MLA does not apply."),
("record-retention", "Record retention", "c2", "Reg B 1002.12 is 25 months for most consumer credit and 12 months is NOT the mortgage rule — for certain mortgage applications Reg B requires a longer period. Be careful: 1002.12(b) requires creditors to retain records for 25 months generally, and for 12 months is business credit... For mortgage, I recall 25 months for most and HMDA is different (generally 3 years for the LAR in older rules, but modified). DO NOT state a retention period unless sure. Hint to the writer: cite 1002.12 and 1003.5 and say the retention period is specified in those sections. Do not quote a number of months or years."),
("small-servicer", "Small servicer", "c2", "Defined in Reg Z 1026.41. Certain Reg X and statement rules have small-servicer exemptions. Do not state the loan-count threshold; it is in the definition and should be read there. Cite reg-1026-41 and reg-1024."),
("small-creditor", "Small creditor", "c2", "A Reg Z category used for certain QM and HPML escrow provisions. The origination-count and asset limits are adjusted. Do not state this year's numbers. Cite reg-1026-35 and reg-1026-43."),
("required-use", "Required use", "c2", "Reg X concept: requiring a consumer to use a particular settlement-service provider. Relevant to AfBAs and Section 8. Cite reg-1024-15 and reg-1024-2."),
("marketing-services-agreement", "Marketing services agreement", "c2", "A contract to pay for actual marketing services. Can be a Section 8 violation if it pays for referrals. There is no safe-harbor CFR section. Cite reg-1024-14 and cfpb-mortgage-resources. Flag for expert review."),
("red-flags-rule", "Red Flags Rule", "c2", "16 CFR 681. Identity-theft detection program for creditors with covered accounts. A mortgage loan can be a covered account. Cite cfr-16-681."),
("valuation-independence", "Valuation independence", "c2", "12 CFR 1026.42. Misrepresenting or influencing an appraisal, and the prohibition on basing compensation on a desired value."),
("occupancy-misrepresentation", "Occupancy misrepresentation", "c2", "Stating an occupancy that is not true in order to obtain loan terms. It is fraud and a repurchase/rep-and-warranty problem. Do not explain how to conceal occupancy. Cite fannie-guide and practice-file."),
("limited-english-proficiency", "Limited English proficiency", "c2", "Borrowers with limited English proficiency. ECOA and UDAAP do not require a Spanish closing package by themselves, but misleading English-only conduct can be a UDAAP or fair-lending problem. Do not invent a translation mandate. Cite reg-1002-4, usc-12-5531, and cfpb-spanish. Flag for expert review."),
# --- closing ---
("closing-disclosure", "Closing Disclosure", "l", "The five-page TRID closing form. 1026.19(f) and 1026.38. Delivered so the consumer receives it at least three business days before consummation. Not the HUD-1 for TRID loans."),
("three-business-day-rule", "Three-business-day rule", "l", "Two different TRID clocks share this nickname: the LE within three business days after application, and the CD at least three business days before consummation. Also rescission is three business days. The entry must separate them. Use the correct business-day definition for the CD and rescission."),
("cd-waiting-period-resets", "Closing Disclosure waiting-period reset", "l", "1026.19(f)(2)(ii): a new three-business-day wait if the APR becomes inaccurate under 1026.22, the loan product changes, or a prepayment penalty is added. Other changes may require a corrected CD without resetting the wait. Do not say every change restarts the clock."),
("zero-tolerance", "Zero tolerance", "l", "1026.19(e)(3)(i). Charges that generally may not increase from the LE: the creditor's or broker's charges, transfer taxes, and charges paid to an affiliate or to a provider the consumer cannot shop for, with the section's exceptions. Cite the section rather than a homemade list if you might omit an exception."),
("ten-percent-tolerance", "10 percent tolerance", "l", "1026.19(e)(3)(ii). The cumulative bucket for recording fees and for shoppable services when the consumer picks a provider on the written list. The 10 percent is in the regulation. It is cumulative, not item by item."),
("no-tolerance-bucket", "Charges that can change", "l", "1026.19(e)(3)(iii). Charges that can increase without a tolerance limit, including prepaid interest, property insurance, escrow amounts, and services the consumer shops for off the written list, subject to the section. Also a changed circumstance can revise estimates."),
("tolerance-cure", "Tolerance cure", "l", "If a charge exceeds the allowed tolerance, the creditor cures by refunding the excess, generally at or within 60 days after consummation. The 60-day cure period is in 1026.19(f)(2)(v). You may state it and cite that paragraph. A principal curtailation is one method the rule discusses; do not invent others."),
("closing-costs", "Closing costs", "l", "The costs to close, disclosed in the LE and CD, not a single regulated number. Separate lender charges, shoppable services, taxes, prepaids, and escrow."),
("seller-credits", "Seller credits", "l", "Amounts the seller contributes, shown in the CD summaries of transactions and in cash to close. Not the same as a lender credit. Interested-party contribution limits are a separate agency rule."),
("aggregate-adjustment", "Aggregate adjustment", "l", "The escrow aggregate adjustment on the CD that prevents collecting more than the RESPA aggregate escrow analysis allows. Cite reg-1024-17 and reg-1026-38. It is often a negative number. Do not invent the cushion months; the RESPA cushion is in 1024.17 and is up to one-sixth of the estimated annual disbursements, which is two months. That one-sixth / two-month cushion is regulatory. You may state it and cite 1024.17."),
("title-insurance", "Title insurance", "l", "Insures against covered title defects. Lender's policy and owner's policy are different. Shown in LE/CD services sections. Industry rate is state-regulated. Cite practice and reg-1026-37 for placement on the form."),
("lenders-title-policy", "Lender's title policy", "l", "Protects the lender's lien. Usually required. LE/CD Section B or C depending on whether the consumer can shop."),
("owners-title-policy", "Owner's title policy", "l", "Protects the owner. Optional in many purchase transactions but often requested. On a purchase LE it is disclosed in a specific way. Do not say it is federally required."),
("simultaneous-issue", "Simultaneous issue", "l", "Pricing when an owner's policy is issued at the same time as the lender's policy. State title practice, not a federal rate. Industry practice."),
("settlement-agent", "Settlement agent", "l", "The person who conducts the closing and disburses. May be a title company, escrow company, or attorney depending on the state. RESPA settlement service. Not always the lender."),
("prepaid-interest", "Prepaid interest", "l", "Interest from funding to the start of the first payment period. LE/CD Section F. Can change with the closing date. Per diem."),
("per-diem-interest", "Per diem interest", "l", "The daily interest amount used to compute prepaid interest. Example math must be labeled as an example. Cite reg-1026-37."),
("recording-fees", "Recording fees", "l", "Government fees to record the deed and security instrument. In the 10 percent cumulative bucket. LE Section E. Cite reg-1026-19."),
("transfer-taxes", "Transfer taxes", "l", "State or local taxes on the transfer. Generally zero tolerance. LE Section E. Cite reg-1026-19."),
("prorations", "Prorations", "l", "Dividing taxes, HOA dues, or rents between buyer and seller at closing. Shown on the CD summaries. Contract and local custom. Not a TRID tolerance category by that name."),
("cash-to-close-calculation", "Calculating cash to close", "l", "The CD table comparing the LE cash to close with the final cash to close. Cite reg-1026-38."),
("total-interest-percentage", "Total interest percentage", "l", "TIP. The total interest paid over the loan term as a percentage of the loan amount, on the CD comparisons. Cite reg-1026-38. Not the APR and not the note rate."),
("comparisons-table", "Comparisons table", "l", "CD page 5 comparisons: in five years, APR, and TIP. Cite reg-1026-38."),
("loan-calculations", "Loan calculations", "l", "CD page 5: total of payments, finance charge, amount financed, APR, and TIP. Cite reg-1026-38."),
("assumption", "Assumption", "l", "Whether a later buyer may assume the loan at the original terms. Disclosed on the LE and CD. FHA and VA are often assumable with approval; conventional loans often have a due-on-sale clause. Do not say every FHA loan is freely assumable without credit approval."),
("demand-feature", "Demand feature", "l", "A term allowing the creditor to demand early repayment. Disclosed on the LE and CD. Most standard first mortgages do not have one. Cite reg-1026-37."),
("negative-amortization", "Negative amortization", "l", "When the payment does not cover interest and the principal increases. Disclosed on the LE and CD. Restricted for qualified mortgages. Cite reg-1026-37 and reg-1026-43."),
("partial-payments", "Partial payment policy", "l", "Whether the servicer accepts payments that are less than the full amount due. Disclosed on the LE and CD. Cite reg-1026-38. The disclosure is not a promise that a partial payment cures default."),
("wet-settlement", "Wet settlement", "l", "Funding and disbursement occur at the closing table, common in some states. Contrast dry funding. Industry and state practice. No federal requirement to be wet or dry."),
("dry-funding", "Dry funding", "l", "Documents are signed and funds are disbursed later, after a review, common in some western states. Industry and state practice."),
("closing-wire-fraud", "Closing wire fraud", "l", "Criminal diversion of closing funds by impersonating the settlement agent. A security practice entry. Do not provide attack instructions. Tell the reader to verify wiring instructions by a known phone number. Cite practice-cfpb or cfpb-owning if it has guidance; otherwise practice-file and describe it as a fraud risk, industry practice."),
("disbursement", "Disbursement", "l", "The release of loan funds. May be the same day as consummation or later. Not the defined term consummation."),
("seller-closing-disclosure", "Seller Closing Disclosure", "l", "The seller receives a CD showing the seller's side. The buyer and seller may receive different versions. Cite reg-1026-38."),
("survey", "Survey", "l", "A measurement of the property boundaries and improvements. May be required by title or the lender. Not the appraisal. Industry and title practice."),
("title-commitment", "Title commitment", "l", "The title company's commitment to insure, listing requirements and exceptions. A closing condition. Industry practice."),
("security-instrument", "Security instrument", "l", "The mortgage or deed of trust that creates the lien. Separate from the promissory note. State law chooses which instrument. Cite practice-file."),
("promissory-note", "Promissory note", "l", "The borrower's promise to repay. The note rate lives here. It is not the APR and not the security instrument."),
("closing-protection-letter", "Closing protection letter", "l", "A title underwriter's letter covering certain closing-agent acts. Industry and state practice. Often a shoppable or required title charge on the LE."),
("final-walkthrough", "Final walkthrough", "l", "The buyer's inspection of the property shortly before closing under the purchase contract. Not a federal requirement and not the appraisal."),
("confirm-receipt", "Confirm receipt", "l", "The CD signature line confirms receipt, not acceptance of the loan. Say that explicitly. Cite cfpb-cd and reg-1026-38."),
("escrow-account-disclosure", "Escrow account disclosure", "l", "LE page 1 states whether the loan has an escrow account. The initial escrow disclosure is also a RESPA document. Cite reg-1026-37 and reg-1024-17."),
("closing-package", "Closing package", "l", "The set of documents signed at closing: note, security instrument, CD, and riders. Industry term. Not a single federal form."),
# --- servicing ---
("mortgage-servicer", "Mortgage servicer", "s", "The person responsible for receiving payments and administering the loan. Reg X servicing rules. The servicer may not be the owner of the loan."),
("servicing-transfer", "Servicing transfer", "s", "12 CFR 1024.33. Notices and the protection of borrowers who pay the old servicer during a transition period. Do not state day counts unless you cite 1024.33 and describe them as the regulatory periods, including the 60-day late-fee protection if you are accurate. You may say: the rule requires notices and, for a period stated in 1024.33, a payment sent to the old servicer cannot be treated as late. If unsure of the numbers, do not quote them."),
("servicing-transfer-notices", "Servicing transfer notices", "s", "The goodbye and hello notices under 1024.33. Cite the section. Avoid a day count if unsure; the section states when each notice is due."),
("payment-during-transfer", "Payment during a servicing transfer", "s", "1024.33 protects a borrower who sends a timely payment to the transferor servicer for a stated period. Describe the protection and cite the section."),
("escrow-account", "Escrow account", "s", "An account the servicer maintains to pay taxes and insurance. Reg X 1024.17. Also called impound. Not the same as earnest-money escrow at closing."),
("escrow-analysis", "Escrow analysis", "s", "The annual analysis required by 1024.17. Determines shortage, surplus, and the new payment. Cite reg-1024-17."),
("escrow-shortage", "Escrow shortage", "s", "When the escrow account will not have enough to pay items when due. 1024.17 allows collecting the shortage in monthly installments or, in some cases, a lump sum. Do not invent the shortage threshold for a lump-sum demand; cite the section."),
("escrow-surplus", "Escrow surplus", "s", "When the account is over the target balance. 1024.17 requires a refund above a threshold and otherwise allows a credit. The threshold is in the section (a surplus of 50 dollars or more is refunded — this is a longstanding regulatory figure in 1024.17). You may state it only as the figure in 1024.17 and tell the reader to confirm the current text. If you do not want the risk, say the refund threshold is specified in 1024.17."),
("escrow-cushion", "Escrow cushion", "s", "The buffer 1024.17 allows, up to one-sixth of estimated annual disbursements (two months), unless state law or the loan documents set a lower cushion. That one-sixth is regulatory."),
("force-placed-insurance", "Force-placed insurance", "s", "Hazard insurance the servicer obtains when the borrower's policy lapses. 1024.37. Notice requirements and cancellation when the borrower provides proof of coverage. Do not call it mortgage insurance."),
("loss-mitigation", "Loss mitigation", "s", "Alternatives to foreclosure: forbearance, repayment plans, modifications, and other options. Reg X 1024.41 is the procedure. The product terms come from the investor (Fannie, Freddie, FHA, VA, USDA, or a private investor)."),
("loss-mitigation-application", "Loss mitigation application", "s", "1024.41. A complete application triggers evaluation timelines and foreclosure protections. Acknowledge-receipt timing is in the section. Do not quote day counts unless you are describing 1024.41's text (acknowledgment within 5 business days is the regulatory standard, excluding some violations). You may state the 5-business-day acknowledgment and the 30-day evaluation if you cite 1024.41 and mention exceptions."),
("forbearance", "Forbearance", "s", "A temporary reduction or suspension of payments. It is not forgiveness. Interest and the missed amounts are handled by the agreement. Investor rules differ. Cite reg-1024-41 for the procedure and the investor guide for the program."),
("loan-modification", "Loan modification", "s", "A permanent change to one or more loan terms. Not a refinance and not forbearance. Investor programs set the waterfall. Cite reg-1024-41 and fannie-guide or hud-4000-1 as applicable."),
("repayment-plan", "Repayment plan", "s", "An agreement to cure a delinquency by paying the regular payment plus an extra amount. Not a modification. Industry and investor rules."),
("payment-deferral", "Payment deferral", "s", "Moving missed amounts to the end of the loan without capitalizing them the way a modification might. Investor-specific. Do not describe a Fannie COVID program as if it were still open. Cite fannie-guide and say the available deferral is the one in the current guide."),
("partial-claim", "FHA partial claim", "s", "An FHA loss-mitigation tool that puts missed amounts in a subordinate, often zero-interest, note due at payoff. HUD 4000.1. Do not state the current maximum percentage; HUD revises it. Cite hud-4000-1."),
("short-sale", "Short sale", "s", "A sale for less than the amount owed, with the investor's approval. Foreclosure alternative. Credit and waiting-period effects are guide-specific."),
("deed-in-lieu", "Deed in lieu of foreclosure", "s", "The borrower transfers the title to the lienholder instead of a foreclosure sale. Investor approval. Not available by federal right in every case."),
("foreclosure", "Foreclosure", "s", "The legal process of enforcing the lien after default. Judicial or nonjudicial is state law. Federal servicing rules limit the first notice or filing and dual tracking. Cite reg-1024-41. Do not describe a uniform 90-day federal foreclosure."),
("dual-tracking", "Dual tracking", "s", "Proceeding with foreclosure while a complete loss-mitigation application is being evaluated. 1024.41 restricts it. Describe the restriction and cite the section rather than saying dual tracking is always illegal."),
("delinquency-foreclosure-wait", "120-day foreclosure wait", "s", "1024.41(f): a servicer shall not make the first notice or filing for foreclosure until the borrower is more than 120 days delinquent, with exceptions in the section. The 120 days is regulatory. State the exceptions exist."),
("notice-of-error", "Notice of error", "s", "12 CFR 1024.35. Written notice asserting a covered error. Acknowledgment and response timelines are in the section. The old name qualified written request overlaps. You may state the regulatory timelines if you cite 1024.35: generally acknowledge within 5 business days and respond within 30 business days, with a possible extension. Mention covered errors are listed in the section."),
("request-for-information", "Request for information", "s", "12 CFR 1024.36. A written request for information about the account. Separate from a notice of error. Timelines are in the section."),
("qualified-written-request", "Qualified written request", "s", "The older RESPA name. For loans covered by the current servicing rule, borrowers use a notice of error or a request for information. Explain the relationship. Cite reg-1024-35 and reg-1024-36."),
("early-intervention", "Early intervention", "s", "12 CFR 1024.39. Live contact and a written notice early in delinquency. Small servicers have modifications. You may describe the 36-day live-contact and 45-day written-notice standards as the text of 1024.39 if you mention exemptions. If you are not sure, cite the section without numbers."),
("continuity-of-contact", "Continuity of contact", "s", "12 CFR 1024.40. Personnel accessible to a delinquent borrower who can discuss loss mitigation. The market says single point of contact. The rule does not require one named person in every case. Be precise."),
("periodic-statement", "Periodic statement", "s", "12 CFR 1026.41. Periodic billing statement for residential mortgage loans, with exemptions including some small servicers and certain fixed-rate loans with coupon books. Do not say every mortgage gets a statement."),
("arm-adjustment-notice", "ARM adjustment notice", "s", "12 CFR 1026.20(c) and (d). Notices before the first adjustment and before later adjustments. The lookback and day counts are in the section. Cite reg-1026-20 and avoid a specific day count if unsure."),
("homeowners-protection-act", "Homeowners Protection Act", "s", "12 USC 4901 and 4902. Borrower-requested cancellation and automatic termination of borrower-paid PMI on covered mortgages. Not FHA MIP."),
("pmi-borrower-cancellation", "Borrower-requested PMI cancellation", "s", "12 USC 4902(a). The borrower may request cancellation on the date the principal balance is first scheduled to reach 80 percent of the original value, if conditions in the statute are met, including being current and a good payment history. Do not omit the conditions. Original value is defined in the statute."),
("pmi-automatic-termination", "Automatic PMI termination", "s", "12 USC 4902(b). Automatic termination on the termination date, based on the initial amortization schedule reaching 78 percent of original value, if the borrower is current. If not current, termination occurs when the borrower becomes current. Final termination at the midpoint is also in the statute. Do not collapse this into 'PMI drops off at 78' without the current-payment condition."),
("payoff-statement", "Payoff statement", "s", "A statement of the amount needed to pay the loan in full. Reg Z 1026.36 addresses payoff statements. Do not state a day count; say the timing standard and its exceptions are in 1026.36 and must be read there."),
("delinquency", "Delinquency", "s", "The loan is past due. Reg X early intervention and foreclosure timing use delinquency. The servicing definition is in Reg X. Do not equate one missed payment with foreclosure."),
("acceleration", "Acceleration", "s", "The creditor's right, after default, to declare the full balance due, if the note and state law allow it. Not the same as a demand feature on a non-defaulted loan."),
("reinstatement", "Reinstatement", "s", "Curing the default by paying the amount required to bring the loan current and stop acceleration or foreclosure, when the contract or state law allows it. Not a federal uniform right. Cite the note/state practice and reg-1024-41 only for the servicing overlay."),
("successor-in-interest", "Successor in interest", "s", "A person who obtains an ownership interest after the origination, such as by death or divorce. Reg X and Reg Z have successor rules. Cite reg-1024 and reg-1026-2 if the definition is there. Confirmed successors are treated as borrowers for certain servicing rules. Do not overstate that they become personally liable on the note."),
("escrow-waiver", "Escrow waiver", "s", "The creditor does not require an escrow account. Some loans, including certain HPMLs, cannot waive escrow. A fee for waiving escrow is a product term. Cite reg-1026-35 and fannie-guide. Do not say escrow can always be waived."),
("loss-mitigation-appeal", "Loss mitigation appeal", "s", "1024.41 gives a right to appeal certain denials of loan-modification options when the denial is based on the complete application and the section's conditions are met. Do not say every denial can be appealed. Cite the section."),
("mortgage-payoff", "Mortgage payoff", "s", "Paying the loan in full, obtaining a release of the lien, and stopping escrow collection. Related to the payoff statement. State law controls the recording of the release."),
("error-resolution", "Error resolution", "s", "The Reg X 1024.35 process as a whole. Overview entry that points to notice of error and the covered-error list."),
# --- loan programs ---
("conventional-loan", "Conventional loan", "p", "A mortgage that is not insured or guaranteed by FHA, VA, or USDA. It may be conforming or jumbo. Private mortgage insurance may apply above a guide LTV."),
("conforming-loan", "Conforming loan", "p", "A conventional loan within FHFA loan limits and the GSE guide. Cite fhfa-cll. Do not state this year's dollar limit."),
("conforming-loan-limit", "Conforming loan limit", "p", "The FHFA baseline and high-cost-area limits. They change. Cite fhfa-cll and do not print a dollar figure."),
("high-balance-loan", "High-balance loan", "p", "A conforming loan above the baseline limit and at or under the high-cost-area limit in a designated county. Also called super conforming. Cite fhfa-cll and fannie-guide. Do not print dollars."),
("jumbo-loan", "Jumbo loan", "p", "A loan above the conforming limit for the county. Not eligible for standard GSE delivery. Portfolio or private-investor guidelines. No single federal jumbo regulation."),
("fha-loan", "FHA loan", "p", "A mortgage insured by FHA under the National Housing Act. HUD Handbook 4000.1. Mortgage insurance premiums change by mortgagee letter. Do not state a current MIP rate or the minimum down payment as a fixed law; say HUD publishes both in 4000.1 and mortgagee letters."),
("fha-203k", "FHA 203(k)", "p", "FHA rehabilitation mortgage. Limited and standard versions exist. Cite hud-4000-1. Do not state renovation caps from memory."),
("fha-streamline-refinance", "FHA streamline refinance", "p", "An FHA-to-FHA refinance with reduced documentation. Net tangible benefit is required. Cite hud-4000-1. Do not say no appraisal is always prohibited or always waived; the handbook states when an appraisal is not required."),
("va-loan", "VA loan", "p", "A loan guaranteed by the Department of Veterans Affairs. 38 USC Chapter 37, 38 CFR Part 36, Pamphlet 26-7. Guaranty is not the same as a down payment. Funding fee rules and exemptions are on VA's schedule. Do not state the current funding-fee percentage."),
("va-entitlement", "VA entitlement", "p", "The amount of guaranty available to the veteran. Basic versus bonus entitlement is handbook material. Cite va-pamphlet and usc-38-3703. Do not state a dollar entitlement as current; VA publishes it."),
("certificate-of-eligibility", "Certificate of eligibility", "p", "VA document showing entitlement. Chapter 2 of Pamphlet 26-7. Cite va-pamphlet."),
("va-irrrl", "VA IRRRL", "p", "Interest Rate Reduction Refinance Loan. Pamphlet 26-7 Chapter 6. A streamlined VA-to-VA refinance. Occupancy and net tangible benefit rules are in the handbook. Do not invent seasoning numbers; cite the handbook and say seasoning is specified there."),
("va-cash-out-refinance", "VA cash-out refinance", "p", "A VA refinance that can take equity out. Different from an IRRRL. Chapter 6. Loan-to-value and seasoning are handbook rules. Do not hardcode them."),
("usda-guaranteed-loan", "USDA guaranteed loan", "p", "Section 502 guaranteed rural housing loan. 7 CFR 3555 and HB-1-3555. Income limits, rural eligibility, and the guarantee fee change. Do not state current income limits or fee rates."),
("adjustable-rate-mortgage", "Adjustable-rate mortgage", "p", "A loan whose note rate can change with an index plus a margin, subject to caps. Disclosed on the LE product line and in ARM notices under 1026.20. The CHARM booklet is required for ARM applications under 1026.19(b). Cite reg-1026-19 and reg-1026-20."),
("hybrid-arm", "Hybrid ARM", "p", "An ARM with a fixed period and then adjustments, such as a 5/6 or 7/6. The numbers are product names. Caps are in the note. Cite reg-1026-37 for the product disclosure."),
("arm-caps", "ARM caps", "p", "Limits on how much the rate can change at the first adjustment, at later adjustments, and over the life of the loan. Disclosed on the LE. Contract terms, not a universal federal cap."),
("arm-index", "ARM index", "p", "The published rate the note uses, such as SOFR-based indexes in current notes. The old LIBOR transition is history. Do not say LIBOR is the current standard index. Cite the note and reg-1026-20."),
("arm-margin", "ARM margin", "p", "The fixed percentage added to the index to get the rate before caps. Disclosed to the borrower. It is not the start rate."),
("fully-indexed-rate", "Fully indexed rate", "p", "Index plus margin, before considering the start rate or caps. Used in some qualifying and disclosure contexts. Cite fannie-b3-6-04 and reg-1026-20. Do not claim every ARM is qualified at the fully indexed rate."),
("interest-only", "Interest-only", "p", "Payments of interest only for a period, then amortizing payments. A QM generally cannot have an interest-only period. Cite reg-1026-43. ATR still requires qualifying on a fully amortizing payment."),
("balloon-payment", "Balloon payment", "p", "A larger payment due at the end. Generally not a qualified mortgage, with limited exceptions that should be described only by citing 1026.43 rather than by inventing which small-creditor balloons still exist."),
("heloc", "HELOC", "p", "Home equity line of credit. Open-end credit under Reg Z 1026.40. TRID LE/CD do not apply. Early disclosures do. Right of rescission may apply to a principal dwelling."),
("home-equity-loan", "Home equity loan", "p", "A closed-end second mortgage. TRID applies if it is a closed-end consumer loan secured by real property. Rescission may apply. Different from a HELOC."),
("reverse-mortgage", "Reverse mortgage", "p", "A loan that converts equity to payments or a line, generally repaid when the borrower dies, sells, or no longer occupies. Not a TRID LE/CD loan. Counseling is required for FHA HECMs. Cite hud-4000-1 and cfr-24-206. Proprietary reverse mortgages are not HECMs."),
("hecm", "HECM", "p", "Home Equity Conversion Mortgage, the FHA-insured reverse mortgage. 12 USC 1715z-20 and 24 CFR 206. Counseling, eligibility, and principal limits are in the rule and HUD mortgagee letters. Do not state the current principal-limit factor or lending limit."),
("non-qm", "Non-qualified mortgage", "p", "A loan that is not a QM. It still needs evidence of ability to repay under 1026.43 unless an exemption applies. Guidelines are investor-specific. Cite reg-1026-43."),
("fixed-rate-mortgage", "Fixed-rate mortgage", "p", "The note rate does not change. The payment can still change if taxes or insurance escrow changes. Contrast with an ARM."),
("temporary-buydown", "Temporary buydown", "p", "A subsidy, often from the seller or lender, that reduces the payment for the first years. The note rate is not permanently reduced. Qualifying may use a different rate than the bought-down payment. Cite fannie-guide. Do not state a universal qualifying rule."),
("construction-to-permanent", "Construction-to-permanent loan", "p", "Finances construction and converts to permanent financing. One-close versus two-close is product design. TRID coverage of construction is technical. Cite reg-1026-17 and reg-1026-19 at a high level and flag the entry because construction disclosure options are easy to get wrong."),
("renovation-mortgage", "Renovation mortgage", "p", "A loan that includes repair costs, such as Fannie HomeStyle or FHA 203(k). Cite fannie-guide and hud-4000-1. Do not mix the program rules."),
("homeready", "HomeReady", "p", "Fannie Mae's affordable product. Income limits and underwriting flexibilities are in B5-6. Cite fannie-b5-6-02. Do not state the current area-median-income percentage; Fannie can change it. Say the income limit is in the guide."),
("home-possible", "Home Possible", "p", "Freddie Mac's affordable product. Cite freddie-guide. Do not state the current income-limit percentage from memory."),
("down-payment-assistance", "Down payment assistance", "p", "Funds from a housing agency or nonprofit for the down payment. Can be a subordinate lien, a grant, or a deferred loan. Agency guides treat repayment terms differently. Cite fannie-guide. Not the same as a personal gift."),
("fannie-mae", "Fannie Mae", "p", "A government-sponsored enterprise that buys mortgages and issues guaranteed MBS. It does not originate loans to consumers. Selling Guide and DU."),
("freddie-mac", "Freddie Mac", "p", "A government-sponsored enterprise that buys mortgages. Seller/Servicer Guide and Loan Product Advisor. Not a retail lender."),
("ginnie-mae", "Ginnie Mae", "p", "Guarantees securities backed by government-insured or guaranteed loans. Does not buy loans the way Fannie and Freddie do and does not set FHA credit policy."),
("assumable-mortgage", "Assumable mortgage", "p", "A loan a buyer may take over with the creditor's approval and, for FHA and VA, the agency rules. Creditworthiness is still reviewed. Cite hud-4000-1 and va-pamphlet. Due-on-sale is the contrasting conventional clause."),
("due-on-sale-clause", "Due-on-sale clause", "p", "A contract clause allowing the lender to call the loan due if the property is transferred. Common in conventional notes. Federal preemption of due-on-sale enforcement is the Garn-St. Germain Act, 12 USC 1701j-3. Cite that only if you add a statute id; otherwise describe it as a contract term and cite fannie-guide. Prefer not to invent the USC section in the prose if the catalog does not have it. Catalog does not have Garn-St. Germain. Do not cite a section number. Say it is a contract clause and that federal law limits some enforcement, and flag for expert review if you mention Garn-St. Germain by name without a catalog statute."),
("portfolio-loan", "Portfolio loan", "p", "A loan the lender keeps rather than sells to a GSE or Ginnie pool. Guidelines can be the lender's own, but ATR still applies. Industry practice plus reg-1026-43."),
("rate-and-term-refinance", "Rate-and-term refinance", "p", "A refinance primarily to change the rate or term, with limited cash back. Fannie calls a version limited cash-out. The cash-back limit is in the guide. Do not hardcode the dollar limit; cite fannie-guide."),
("cash-out-refinance", "Cash-out refinance", "p", "A refinance that produces cash to the borrower above the limited amount allowed on a rate-and-term refinance, or pays off debts in a way the guide treats as cash-out. Waiting periods, LTV, and seasoning are guide rules. Cite fannie-guide. Do not state a universal 12-month seasoning rule as law."),
("community-seconds", "Community seconds", "p", "A subsidized subordinate lien from a housing agency or nonprofit, paired with a first mortgage. Fannie has a community-seconds topic. Cite fannie-guide. Do not invent the CLTV."),
("private-mortgage-insurance", "Private mortgage insurance", "p", "Insurance that protects the lender against default on a conventional loan, usually when LTV exceeds 80 percent under the guide. Borrower-paid PMI is subject to the Homeowners Protection Act. Not FHA MIP."),
("borrower-paid-mortgage-insurance", "Borrower-paid mortgage insurance", "p", "The borrower pays the MI premium monthly or in a financed single premium. HPA cancellation applies to borrower-paid PMI. Cite usc-12-4902."),
("lender-paid-mortgage-insurance", "Lender-paid mortgage insurance", "p", "The lender pays the MI premium and charges a higher note rate or price. HPA borrower cancellation generally does not work the same way because the borrower is not paying a PMI premium. Do not tell borrowers they can cancel LPMI at 80 percent under HPA. Cite usc-12-4901 and fannie-guide. Flag for expert review on the HPA scope sentence."),
("fha-mip", "FHA mortgage insurance premium", "p", "The annual mortgage insurance premium on an FHA loan, collected monthly. Rates and duration are set by HUD and change. Do not state a current rate or whether it drops off. Cite hud-4000-1."),
("upfront-mortgage-insurance-premium", "Upfront mortgage insurance premium", "p", "The one-time FHA premium at closing, which may be financed. The rate changes. Do not state the current percentage. Cite hud-4000-1."),
("va-funding-fee", "VA funding fee", "p", "A fee that supports the VA guaranty. Some veterans are exempt, including many with disability compensation. The percentage depends on down payment, use, and loan type and is published by VA. Do not state a current percentage. Cite va-pamphlet."),
("usda-guarantee-fee", "USDA guarantee fee", "p", "The upfront fee on a USDA guaranteed loan. The rate changes. Do not state the current percentage. Cite cfr-7-3555 and usda-hb."),
("usda-annual-fee", "USDA annual fee", "p", "The annual fee on a USDA guaranteed loan, collected with the payment. The rate changes. Cite usda-hb. Do not state the current percentage."),
("energy-efficient-mortgage", "Energy efficient mortgage", "p", "A feature that can finance energy improvements, available in FHA, VA, and conventional forms. Do not blend the program caps. Cite hud-4000-1 and fannie-guide at a high level."),
("note-rate", "Note rate", "p", "The interest rate in the promissory note. It is not the APR. On the LE it is the interest rate in the Loan Terms table."),
# --- borrower FAQs: questions staff are asked. Plain answer first, compliance note for the desk. ---
("faq-what-is-a-loan-estimate", "What is a Loan Estimate?", "f", "Borrower question. Answer in plain English and point to the loan-estimate entry. CFPB Spanish: Estimación del préstamo."),
("faq-what-is-a-closing-disclosure", "What is a Closing Disclosure?", "f", "CFPB Spanish: Divulgación del cierre. Point to closing-disclosure and the three-business-day rule."),
("faq-apr-vs-interest-rate", "What is the difference between APR and the interest rate?", "f", "The most common comparison question. Note rate versus APR. Point to annual-percentage-rate and note-rate. Do not use a fake current market rate; example figures only."),
("faq-what-is-pmi", "What is PMI?", "f", "Private mortgage insurance, not FHA MIP and not homeowners insurance. Point to private-mortgage-insurance and HPA."),
("faq-what-is-an-escrow-account", "What is an escrow account?", "f", "Taxes and insurance account. CFPB: cuenta de depósito en garantía. Point to escrow-account. Distinguish earnest money."),
("faq-what-is-a-rate-lock", "What is a rate lock?", "f", "Point to rate-lock. It is a contract, not a right to the lowest rate later, unless a float-down was sold."),
("faq-what-is-dti", "What is DTI?", "f", "Debt-to-income. CFPB: relación deuda-ingreso. Point to debt-to-income-ratio. Do not state a universal maximum as law."),
("faq-what-are-points", "What are points?", "f", "Discount points. CFPB uses puntos. One point customarily means 1 percent of the loan amount. Point to discount-points and lender-credits."),
("faq-how-much-are-closing-costs", "How much are closing costs?", "f", "There is no legal fixed amount. Explain categories and that the LE itemizes them. Example figures only. Point to closing-costs."),
("faq-what-is-preapproval", "What is a pre-approval?", "f", "Point to pre-approval and pre-qualification. CFPB: preaprobación."),
("faq-what-is-earnest-money", "What is earnest money?", "f", "Point to earnest-money. It is a contract deposit, usually credited at closing."),
("faq-what-is-a-down-payment", "What is a down payment?", "f", "CFPB style: pago inicial. Point to down-payment. Program minimums change and are not one number."),
("faq-can-i-use-gift-funds", "Can I use gift money for the down payment?", "f", "Often yes on a principal residence, with a gift letter and transfer evidence, subject to the guide. Not a universal yes for investment property. Point to gift-funds."),
("faq-what-is-cash-to-close", "What is cash to close?", "f", "Point to cash-to-close. It is not only the down payment."),
("faq-what-is-title-insurance", "What is title insurance?", "f", "Point to title-insurance, lender's policy, and owner's policy."),
("faq-who-chooses-the-title-company", "Who chooses the title company?", "f", "RESPA Section 9, 12 USC 2608, prohibits a seller from requiring a particular title company as a condition of the sale in a covered transaction, with liability for damages. The catalog does not have 2608. Do not cite 12 USC 2608 unless you only describe the rule in prose without a fake catalog id, and cite respa at the act level (usc-12-2601) plus reg-1024. Actually 2608 is real. You may explain the rule in prose as RESPA's rule against a seller requiring a title company, and cite usc-12-2601 and reg-1024. Avoid inventing a subsection. Flag for expert review so the Section 9 citation can be confirmed. Also the buyer often can shop, which affects the 10 percent tolerance."),
("faq-what-is-an-appraisal", "What is an appraisal?", "f", "CFPB: tasación. It is for the lender, not a home inspection. Point to appraisal."),
("faq-what-if-the-appraisal-is-low", "What if the appraisal is lower than the price?", "f", "The LTV uses the lower of price or value on a purchase. Options are renegotiate, bring cash, or a reconsideration of value. Do not promise a second appraisal will be ordered. Point to loan-to-value-ratio and appraisal."),
("faq-what-is-underwriting", "What is underwriting?", "f", "The lender's risk decision. Point to manual-underwriting and automated-underwriting-system. It is not the same as pre-qualification."),
("faq-what-are-underwriting-conditions", "Why was my loan conditionally approved?", "f", "Point to conditional-approval and underwriting-conditions. Conditional is not clear to close."),
("faq-which-debts-count-in-dti", "Which debts count in my DTI?", "f", "Point to debt-to-income-ratio, installment-debt, revolving-debt, and student-loans. Authorized-user and omitted debts are nuances."),
("faq-can-i-cancel-pmi", "Can I cancel PMI?", "f", "HPA borrower-requested cancellation and automatic termination. Not MIP. Point to the HPA entries. Do not promise cancellation at 80 percent without the statutory conditions."),
("faq-what-is-the-three-day-rule", "What is the three-day rule?", "f", "Separate the CD waiting period, the LE timing, and rescission. Point to three-business-day-rule."),
("faq-why-did-my-closing-costs-change", "Why did my closing costs change?", "f", "Tolerances and changed circumstances. Point to zero-tolerance, ten-percent-tolerance, changed-circumstance, and tolerance-cure."),
("faq-what-is-a-mortgage-servicer", "What is a mortgage servicer?", "f", "CFPB servicing language: administrador del préstamo. The company you pay may not own the loan. Point to mortgage-servicer and servicing-transfer."),
("faq-what-if-i-cannot-pay", "What if I cannot make my mortgage payment?", "f", "Contact the servicer, ask about loss mitigation, and do not ignore mail. Point to loss-mitigation and forbearance. This is not legal advice for a particular default."),
("faq-what-is-forbearance", "What is forbearance?", "f", "A pause or reduction, not forgiveness. Point to forbearance."),
("faq-fha-vs-conventional", "What is the difference between FHA and conventional?", "f", "Insurance, down payment source, MIP versus PMI, and guidelines. Do not state current MIP or a minimum down payment percentage. Point to fha-loan and conventional-loan."),
("faq-what-is-an-arm", "What is an adjustable-rate mortgage?", "f", "Point to adjustable-rate-mortgage, arm-caps, arm-index, and arm-margin. The payment can change."),
("faq-what-is-a-jumbo-loan", "What is a jumbo loan?", "f", "Above the conforming limit. Point to jumbo-loan and conforming-loan-limit. Do not state the current limit."),
("faq-what-is-a-heloc", "What is a HELOC?", "f", "Open-end credit line. CFPB describes a línea de crédito con garantía hipotecaria. Not a closed-end second. Point to heloc."),
("faq-what-is-a-reverse-mortgage", "What is a reverse mortgage?", "f", "Point to reverse-mortgage and hecm. Counseling, occupancy, and repayment events. Not free money."),
("faq-what-documents-do-i-need", "What documents will the lender ask for?", "f", "Income, assets, credit, and identity. Point to pay-stub, form-w-2, tax-returns, and bank-statements. The AUS findings control the actual list."),
("faq-how-do-i-avoid-wire-fraud", "How do I avoid wire fraud at closing?", "f", "Verify wiring instructions using a phone number you looked up, not one in an email. Do not include attack steps. Point to closing-wire-fraud."),
("faq-can-i-cancel-after-closing", "Can I cancel the loan after I sign?", "f", "Only if the right of rescission applies. Purchases generally cannot be rescinded. Point to right-of-rescission. Signing the CD is not acceptance."),
("faq-cosigner-vs-coborrower", "What is the difference between a co-signer and a co-borrower?", "f", "Point to co-signer, co-borrower, and non-occupant-co-borrower. Reg B signature rules."),
]

CATS = {
    "o": "origination",
    "u1": "underwriting",
    "u2": "underwriting",
    "c1": "compliance",
    "c2": "compliance",
    "l": "closing",
    "s": "servicing",
    "p": "loan-programs",
    "f": "borrower-faqs",
}


# Pinpoint citations (paragraph level). Each paragraph id and its wording were
# checked against the eCFR text current as of 2026-11-19 before it was added.
def pin(part, sec, para, name, interp=True):
    section = f"{part}.{sec}"
    pid = para.replace(")(", "-").strip("()")
    row = C(
        f"reg-{part}-{sec}-{pid}",
        f"12 CFR {section}{para}",
        name,
        ECFR12S.format(part=part, section=section) + f"#p-{section}{para}",
        "regulation",
        part,
        CFPB.format(part=part, sec=sec) + "#" + pid,
    )
    if interp:
        # Official Interpretation (Supplement I) comment anchor on the CFPB page; verified present.
        row["interpUrl"] = CFPB.format(part=part, sec=sec) + f"#{sec}-{pid}-Interp"
    return row


citations += [
    pin("1026", "19", "(e)(1)(iii)", "Regulation Z — Loan Estimate delivery timing (third business day after application)"),
    pin("1026", "19", "(e)(1)(vi)(C)", "Regulation Z — Written list of providers", interp=False),
    pin("1026", "19", "(e)(2)(i)(A)", "Regulation Z — Fee restriction before the Loan Estimate and intent to proceed"),
    pin("1026", "19", "(e)(2)(ii)", "Regulation Z — Written estimates given before the Loan Estimate"),
    pin("1026", "19", "(e)(3)(i)", "Regulation Z — Good faith general rule (zero tolerance)"),
    pin("1026", "19", "(e)(3)(ii)", "Regulation Z — Limited increases for certain charges (10 percent tolerance)"),
    pin("1026", "19", "(e)(3)(iii)", "Regulation Z — Variations permitted for certain charges"),
    pin("1026", "19", "(e)(3)(iv)", "Regulation Z — Revised estimates and changed circumstances"),
    pin("1026", "19", "(e)(4)", "Regulation Z — Provision and receipt of revised Loan Estimates"),
    pin("1026", "19", "(f)(1)(ii)", "Regulation Z — Closing Disclosure timing (three business days before consummation)"),
    pin("1026", "19", "(f)(2)(ii)", "Regulation Z — Changes before consummation requiring a new waiting period"),
    pin("1026", "19", "(f)(2)(v)", "Regulation Z — Refunds related to the good faith analysis"),
    pin("1026", "2", "(a)(3)(ii)", "Regulation Z — Application (six pieces of information) for TRID loans", interp=False),
    pin("1026", "2", "(a)(6)", "Regulation Z — Business day (general and specific definitions)"),
]


def build_manifest():
    seen = set()
    manifest = []
    for slug, term, batch, hint in RAW:
        if slug in seen:
            raise SystemExit(f"duplicate slug {slug}")
        seen.add(slug)
        if batch not in CATS:
            raise SystemExit(f"bad batch {batch} on {slug}")
        manifest.append(
            {
                "slug": slug,
                "term": term,
                "category": CATS[batch],
                "batch": batch,
                "hint": hint,
            }
        )
    return manifest


def step(slug, note, es_note):
    return {"slug": slug, "note": note, "esNote": es_note}


PATHS = [
    {
        "slug": "trid-application-to-closing",
        "title": "TRID from application to closing",
        "esTitle": "TRID de la solicitud al cierre",
        "summary": "The disclosure clock compliance staff actually administer: when an application exists, what the Loan Estimate locks in, which changes permit a revision, and when the Closing Disclosure waiting period starts over.",
        "esSummary": "El reloj de divulgación que administra el personal de cumplimiento: cuándo existe una solicitud, qué fija la Estimación del préstamo, qué cambios permiten una revisión y cuándo vuelve a empezar la espera de la Divulgación del cierre.",
        "audience": "professional",
        "steps": [
            step("application-definition", "The six items start the LE clock.", "Los seis datos inician el plazo de la Estimación del préstamo."),
            step("loan-estimate", "Content and the three-business-day delivery.", "Contenido y entrega en tres días hábiles."),
            step("intent-to-proceed", "Fee restriction before the consumer proceeds.", "Restricción de cargos antes de que el consumidor continúe."),
            step("your-home-loan-toolkit", "The purchase booklet is a separate Reg X duty.", "El folleto de compra es un deber distinto del Reglamento X."),
            step("written-list-of-providers", "Shopping affects the tolerance bucket.", "Comparar proveedores afecta la tolerancia."),
            step("changed-circumstance", "Not every change permits a new LE.", "No todo cambio permite una nueva Estimación."),
            step("revised-loan-estimate", "Timing and the ban on a late LE.", "Plazos y la prohibición de una Estimación tardía."),
            step("zero-tolerance", "Lender charges that generally cannot increase.", "Cargos del prestamista que por lo general no pueden subir."),
            step("ten-percent-tolerance", "The cumulative 10 percent bucket.", "El grupo acumulado del 10 por ciento."),
            step("closing-disclosure", "The final form and its delivery.", "El formulario final y su entrega."),
            step("three-business-day-rule", "Separate the LE, CD, and rescission clocks.", "Separe los plazos de la Estimación, la Divulgación y la rescisión."),
            step("cd-waiting-period-resets", "Only three events restart the CD wait.", "Solo tres eventos reinician la espera de la Divulgación."),
            step("tolerance-cure", "How an excess is refunded.", "Cómo se reembolsa el exceso."),
            step("consummation", "State law, not the signing table, defines the moment.", "La ley estatal, no la mesa de firma, define el momento."),
        ],
    },
    {
        "slug": "reading-the-loan-estimate",
        "title": "Reading the Loan Estimate",
        "esTitle": "Cómo leer la Estimación del préstamo",
        "summary": "A page-by-page reading order for LOs and processors: Loan Terms, the Section A through G costs, credits, and the APR comparison.",
        "esSummary": "Un orden de lectura para oficiales de préstamos y procesadores: términos del préstamo, costos de las secciones A a G, créditos y la comparación de la tasa porcentual anual.",
        "audience": "professional",
        "steps": [
            step("loan-estimate", "What the three pages are for.", "Para qué sirven las tres páginas."),
            step("origination-charges", "Section A and the zero-tolerance baseline.", "Sección A y la base de tolerancia cero."),
            step("services-you-cannot-shop-for", "Section B.", "Sección B."),
            step("services-you-can-shop-for", "Section C and the written list.", "Sección C y la lista escrita."),
            step("discount-points", "A price paid to lower the note rate.", "Un precio para bajar la tasa del pagaré."),
            step("lender-credits", "A credit, often for a higher rate.", "Un crédito, a menudo por una tasa más alta."),
            step("prepaids", "Section F, including prepaid interest.", "Sección F, incluido el interés pagado por adelantado."),
            step("initial-escrow-payment", "Section G.", "Sección G."),
            step("cash-to-close", "The bottom line the borrower will ask about.", "La cifra que preguntará el prestatario."),
            step("annual-percentage-rate", "Why APR is not the note rate.", "Por qué la APR no es la tasa del pagaré."),
            step("total-interest-percentage", "TIP is a third, different number.", "El TIP es un tercer número, distinto."),
        ],
    },
    {
        "slug": "closing-disclosure-and-tolerances",
        "title": "Closing Disclosure and tolerance cures",
        "esTitle": "Divulgación del cierre y correcciones de tolerancia",
        "summary": "For closers and compliance: which bucket a fee sits in, when the waiting period resets, and how a cure is documented.",
        "esSummary": "Para el cierre y el cumplimiento: en qué grupo cae un cargo, cuándo se reinicia la espera y cómo se documenta una corrección.",
        "audience": "professional",
        "steps": [
            step("closing-disclosure", "The five-page form.", "El formulario de cinco páginas."),
            step("three-business-day-rule", "Receipt at least three business days before consummation.", "Recepción al menos tres días hábiles antes de la consumación."),
            step("zero-tolerance", "Charges that should match the LE.", "Cargos que deben coincidir con la Estimación."),
            step("ten-percent-tolerance", "The cumulative shoppable and recording bucket.", "El grupo acumulado de cargos comparables y de registro."),
            step("no-tolerance-bucket", "Charges the rule allows to move.", "Cargos que la regla permite que cambien."),
            step("changed-circumstance", "The legal reason, not a pricing preference.", "La razón legal, no una preferencia de precio."),
            step("tolerance-cure", "Refund timing and method.", "Plazo y método del reembolso."),
            step("seller-credits", "Where the seller's money appears.", "Dónde aparece el dinero del vendedor."),
            step("cash-to-close-calculation", "The comparison table against the LE.", "La tabla de comparación con la Estimación."),
            step("prepaid-interest", "The per diem that moves with the funding date.", "El interés diario que cambia con la fecha de desembolso."),
            step("aggregate-adjustment", "Why Section G can show a negative number.", "Por qué la sección G puede mostrar un número negativo."),
        ],
    },
    {
        "slug": "underwriting-conditions-101",
        "title": "Underwriting conditions 101",
        "esTitle": "Condiciones de suscripción",
        "summary": "How a conditional approval moves through prior-to-document and prior-to-funding to clear to close, and which conditions are guide requirements rather than internal slang.",
        "esSummary": "Cómo una aprobación condicional pasa de las condiciones previas a los documentos y al desembolso hasta la autorización para cerrar.",
        "audience": "professional",
        "steps": [
            step("underwriting-conditions", "What a condition is.", "Qué es una condición."),
            step("conditional-approval", "Approved only if the list is cleared.", "Aprobado solo si se cumple la lista."),
            step("prior-to-document", "Due before the package is drawn.", "Se debe antes de preparar el paquete."),
            step("prior-to-funding", "Due before money moves.", "Se debe antes de que salga el dinero."),
            step("clear-to-close", "An internal status, not consummation.", "Un estado interno, no la consumación."),
            step("verification-of-employment", "The written file.", "El expediente escrito."),
            step("verbal-verification-of-employment", "The closer-in-time call.", "La verificación verbal más cercana al cierre."),
            step("bank-statements", "Assets and large deposits.", "Activos y depósitos grandes."),
            step("large-deposit", "What has to be sourced.", "Qué hay que documentar."),
            step("letter-of-explanation", "What a letter can and cannot cure.", "Qué puede y qué no puede resolver una carta."),
            step("appraisal", "Collateral condition.", "Condición de la garantía."),
            step("title-commitment", "Lien and exception condition.", "Condición de gravámenes y excepciones."),
        ],
    },
    {
        "slug": "income-assets-and-credit",
        "title": "Income, assets, and credit",
        "esTitle": "Ingresos, activos y crédito",
        "summary": "The borrower-qualification file: stable income, the two ratios, reserves, gifts, and the representative credit score.",
        "esSummary": "El expediente de calificación: ingreso estable, las dos relaciones, reservas, regalos y el puntaje de crédito representativo.",
        "audience": "professional",
        "steps": [
            step("stable-income", "The standard the rest of the file has to meet.", "El estándar que debe cumplir el resto del expediente."),
            step("debt-to-income-ratio", "The total ratio.", "La relación total."),
            step("housing-expense-ratio", "The housing payment alone.", "Solo el pago de la vivienda."),
            step("pay-stub", "Current employment income.", "Ingreso de empleo actual."),
            step("form-w-2", "The annual wage record.", "El registro anual de salarios."),
            step("tax-returns", "Self-employment and other income.", "Trabajo por cuenta propia y otros ingresos."),
            step("form-4506-c", "The transcript authorization.", "La autorización de transcripciones."),
            step("self-employment-income", "Business income is not W-2 income.", "El ingreso del negocio no es ingreso de W-2."),
            step("reserves", "What is left after closing.", "Lo que queda después del cierre."),
            step("gift-funds", "Eligible gifts and the letter.", "Regalos permitidos y la carta."),
            step("tri-merge-credit-report", "The report itself.", "El informe."),
            step("representative-credit-score", "Which score the guide uses.", "Qué puntaje usa la guía."),
        ],
    },
    {
        "slug": "servicing-and-loss-mitigation",
        "title": "Servicing and loss mitigation",
        "esTitle": "Administración y mitigación de pérdidas",
        "summary": "Regulation X from transfer and escrow through early intervention, a complete application, and the foreclosure hold.",
        "esSummary": "El Reglamento X desde la transferencia y el depósito en garantía hasta la intervención temprana, una solicitud completa y la pausa de ejecución hipotecaria.",
        "audience": "professional",
        "steps": [
            step("mortgage-servicer", "Who the borrower pays, and who owns the loan.", "A quién le paga el prestatario y quién es dueño del préstamo."),
            step("servicing-transfer", "Notices and misdirected payments.", "Avisos y pagos enviados al administrador anterior."),
            step("escrow-account", "Taxes and insurance.", "Impuestos y seguros."),
            step("escrow-analysis", "The annual review.", "La revisión anual."),
            step("periodic-statement", "The monthly accounting.", "El estado de cuenta."),
            step("early-intervention", "The delinquency outreach.", "El contacto al inicio de la morosidad."),
            step("notice-of-error", "How a borrower challenges an error.", "Cómo el prestatario disputa un error."),
            step("request-for-information", "How a borrower asks for information.", "Cómo el prestatario pide información."),
            step("loss-mitigation", "The menu of alternatives.", "Las alternativas."),
            step("forbearance", "A pause is not forgiveness.", "Una pausa no es perdón de la deuda."),
            step("loan-modification", "A permanent change to terms.", "Un cambio permanente de los términos."),
            step("dual-tracking", "What must stop once an application is complete.", "Qué debe detenerse cuando la solicitud está completa."),
            step("foreclosure", "State procedure plus the federal timing overlay.", "El procedimiento estatal más el plazo federal."),
        ],
    },
    {
        "slug": "fair-lending-and-udaap",
        "title": "Fair lending and UDAAP",
        "esTitle": "Préstamos justos y UDAAP",
        "summary": "ECOA, the Fair Housing Act, and unfair, deceptive, or abusive conduct, including the monitoring data examiners compare to the decision.",
        "esSummary": "ECOA, la Ley de Vivienda Justa y las prácticas injustas, engañosas o abusivas, incluidos los datos de monitoreo que los examinadores comparan con la decisión.",
        "audience": "professional",
        "steps": [
            step("fair-lending", "The map of the laws.", "El mapa de las leyes."),
            step("ecoa", "The credit-discrimination statute.", "La ley contra la discriminación en el crédito."),
            step("regulation-b", "The implementing rule.", "El reglamento que la aplica."),
            step("disparate-treatment", "Different treatment on a prohibited basis.", "Trato distinto por un motivo prohibido."),
            step("disparate-impact", "A neutral policy with a disproportionate effect.", "Una política neutra con un efecto desproporcionado."),
            step("fair-housing-act", "Housing and real-estate credit.", "Vivienda y crédito inmobiliario."),
            step("redlining", "Geographic discouragement.", "Desaliento por zona geográfica."),
            step("steering", "Directing borrowers for the wrong reason.", "Dirigir a los prestatarios por una razón indebida."),
            step("udaap", "Unfair, deceptive, or abusive.", "Injusto, engañoso o abusivo."),
            step("adverse-action-notice", "The written decision.", "La decisión por escrito."),
            step("demographic-information", "Collected, and not used to discriminate.", "Se recopila y no se usa para discriminar."),
            step("hmda", "The data examiners will already have.", "Los datos que el examinador ya tendrá."),
        ],
    },
    {
        "slug": "atr-qm-hoepa-hpml",
        "title": "ATR, QM, HOEPA, and HPML",
        "esTitle": "Capacidad de pago, QM, HOEPA y HPML",
        "summary": "The price-and-terms ladder: ability to repay, the qualified-mortgage presumption, high-cost coverage, and higher-priced appraisal and escrow duties.",
        "esSummary": "La escala de precio y términos: capacidad de pago, la presunción de hipoteca calificada, la cobertura de alto costo y los deberes de tasación y depósito en garantía de una hipoteca de precio más alto.",
        "audience": "professional",
        "steps": [
            step("ability-to-repay", "The eight-factor duty.", "El deber de los ocho factores."),
            step("qualified-mortgage", "One way to presume compliance.", "Una forma de presumir el cumplimiento."),
            step("qm-safe-harbor", "Not higher-priced.", "No es de precio más alto."),
            step("rebuttable-presumption", "Higher-priced QM.", "QM de precio más alto."),
            step("points-and-fees", "The cap and its exclusions.", "El límite y sus exclusiones."),
            step("prepayment-penalty", "A restricted feature.", "Una característica restringida."),
            step("higher-priced-mortgage-loan", "The APOR spread test.", "La prueba del diferencial sobre el APOR."),
            step("hoepa", "The high-cost statute.", "La ley de alto costo."),
            step("high-cost-mortgage", "What triggers the extra restrictions.", "Qué activa las restricciones adicionales."),
            step("finance-charge", "The dollar cost inside the APR.", "El costo en dólares dentro de la APR."),
            step("annual-percentage-rate", "The rate used in the price tests.", "La tasa que se usa en las pruebas de precio."),
        ],
    },
    {
        "slug": "mortgage-insurance-and-hpa",
        "title": "Mortgage insurance and the HPA",
        "esTitle": "Seguro hipotecario y la HPA",
        "summary": "Borrower-paid PMI, lender-paid MI, FHA MIP, the VA funding fee, and the USDA fee — and which of them the Homeowners Protection Act actually cancels.",
        "esSummary": "El PMI pagado por el prestatario, el seguro pagado por el prestamista, la MIP de la FHA, la cuota VA y la cuota USDA, y cuál de ellos cancela la Ley de Protección de los Propietarios.",
        "audience": "professional",
        "steps": [
            step("private-mortgage-insurance", "Conventional MI.", "Seguro hipotecario convencional."),
            step("borrower-paid-mortgage-insurance", "The premium the HPA can cancel.", "La prima que la HPA puede cancelar."),
            step("lender-paid-mortgage-insurance", "Priced into the rate, not a monthly PMI line.", "Incluido en la tasa, no como una línea mensual de PMI."),
            step("homeowners-protection-act", "The statute.", "La ley."),
            step("pmi-borrower-cancellation", "The 80 percent request.", "La solicitud al 80 por ciento."),
            step("pmi-automatic-termination", "The 78 percent termination.", "La terminación al 78 por ciento."),
            step("fha-mip", "Not PMI.", "No es PMI."),
            step("upfront-mortgage-insurance-premium", "The FHA upfront premium.", "La prima inicial de la FHA."),
            step("va-funding-fee", "Not mortgage insurance.", "No es seguro hipotecario."),
            step("usda-guarantee-fee", "The USDA upfront fee.", "La cuota inicial de USDA."),
        ],
    },
    {
        "slug": "loan-program-comparison",
        "title": "Loan programs side by side",
        "esTitle": "Programas de préstamo comparados",
        "summary": "A desk comparison of conventional, FHA, VA, USDA, jumbo, ARM, and home-equity products without treating program numbers as permanent.",
        "esSummary": "Una comparación de trabajo de los productos convencional, FHA, VA, USDA, jumbo, ARM y de valor líquido, sin tratar las cifras de los programas como permanentes.",
        "audience": "professional",
        "steps": [
            step("conventional-loan", "Not government-insured.", "No está asegurado por el gobierno."),
            step("conforming-loan-limit", "The line between conforming and jumbo.", "La línea entre conforme y jumbo."),
            step("fha-loan", "FHA insurance.", "Seguro de la FHA."),
            step("va-loan", "VA guaranty.", "Garantía VA."),
            step("usda-guaranteed-loan", "Rural housing guaranty.", "Garantía de vivienda rural."),
            step("jumbo-loan", "Above the local conforming limit.", "Por encima del límite conforme local."),
            step("adjustable-rate-mortgage", "A rate that can change.", "Una tasa que puede cambiar."),
            step("fixed-rate-mortgage", "A note rate that does not.", "Una tasa del pagaré que no cambia."),
            step("heloc", "Open-end equity line.", "Línea de crédito abierta."),
            step("reverse-mortgage", "Equity drawn, repaid later.", "Valor líquido que se paga después."),
        ],
    },
    {
        "slug": "origination-conduct",
        "title": "Origination conduct",
        "esTitle": "Conducta en la originación",
        "summary": "Licensing, compensation, steering, Section 8, and advertising: the conduct rules for MLOs and the companies that pay them.",
        "esSummary": "Licencias, compensación, dirección indebida, Sección 8 y publicidad: las reglas de conducta para los originadores y las empresas que les pagan.",
        "audience": "professional",
        "steps": [
            step("safe-act", "The license statute.", "La ley de licencias."),
            step("nmls", "The registry, not the license grantor.", "El registro, no quien otorga la licencia."),
            step("mortgage-loan-originator", "Who is covered.", "Quién está cubierto."),
            step("loan-originator-compensation", "The Reg Z compensation rule.", "La regla de compensación del Reglamento Z."),
            step("borrower-paid-compensation", "Paid by the consumer.", "Pagada por el consumidor."),
            step("lender-paid-compensation", "Paid by the creditor.", "Pagada por el acreedor."),
            step("anti-steering", "The loan-option safe harbor.", "El puerto seguro de las opciones de préstamo."),
            step("respa-section-8", "Referrals are not a thing you sell.", "Las referencias no se venden."),
            step("affiliated-business-arrangement", "The narrow permission.", "El permiso limitado."),
            step("mortgage-advertising", "Reg Z and the MAP Rule.", "El Reglamento Z y la regla MAP."),
            step("trigger-terms", "A rate or payment that pulls in more disclosures.", "Una tasa o un pago que exige más divulgaciones."),
        ],
    },
]


def main():
    manifest = build_manifest()
    slugs = {row["slug"] for row in manifest}
    for path in PATHS:
        for s in path["steps"]:
            if s["slug"] not in slugs:
                raise SystemExit(f"path {path['slug']} missing term {s['slug']}")
    trending_slugs = [
        "loan-estimate",
        "closing-costs",
        "faq-apr-vs-interest-rate",
        "private-mortgage-insurance",
        "escrow-account",
        "rate-lock",
        "debt-to-income-ratio",
        "discount-points",
        "closing-disclosure",
        "pre-approval",
    ]
    for slug in trending_slugs:
        if slug not in slugs:
            raise SystemExit(f"trending missing {slug}")
    ids = [c["id"] for c in citations]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        raise SystemExit(f"duplicate citation ids {dupes}")
    part_ids = {p["id"] for p in parts}
    for c in citations:
        if c["partId"] not in part_ids:
            raise SystemExit(f"citation {c['id']} part {c['partId']} has no part record")
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "citations.json").write_text(json.dumps(citations, indent=2) + "\n")
    (DATA / "parts.json").write_text(json.dumps(parts, indent=2) + "\n")
    (DATA / "term-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (DATA / "paths.json").write_text(json.dumps(PATHS, indent=2) + "\n")
    trending = {
        "heading": "Most looked-up by borrowers",
        "esHeading": "Lo más consultado por prestatarios",
        "disclosure": "A curated list of topics borrowers ask loan officers about. It is not a count of searches on this site. There is no live traffic yet. When analytics are added, replace the slugs in this file. Do not display fabricated counts.",
        "esDisclosure": "Una lista seleccionada de temas que los prestatarios preguntan a los oficiales de préstamos. No es un conteo de búsquedas en este sitio. Todavía no hay tráfico en vivo. Cuando haya analítica, reemplace los slugs de este archivo. No muestre conteos inventados.",
        "slugs": trending_slugs,
    }
    (DATA / "trending.json").write_text(json.dumps(trending, indent=2) + "\n")
    from collections import Counter
    counts = Counter(row["category"] for row in manifest)
    print(f"terms {len(manifest)}")
    for key, value in counts.items():
        print(f"  {key} {value}")
    print(f"citations {len(citations)}")
    print(f"parts {len(parts)}")
    print(f"paths {len(PATHS)}")


if __name__ == "__main__":
    main()
