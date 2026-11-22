"""Curated search aliases layered onto authored terms at compile time.

Only well-established names, acronyms, and desk shorthand. Nothing here is a
legal claim. Spanish aliases marked for native-speaker review with the rest of
the Spanish text. All-caps acronyms on the English side are copied to Spanish
automatically, because desks use the English acronym in both languages.
"""

EN = {
    "trid": ["TILA-RESPA Integrated Disclosure", "TILA-RESPA rule", "Know Before You Owe"],
    "closing-disclosure": ["CD"],
    # The Loan Estimate replaced the Good Faith Estimate for most closed-end mortgages (applications on or after Oct 3, 2015).
    "loan-estimate": ["Good Faith Estimate (replaced)", "GFE"],
    "changed-circumstance": ["COC", "change of circumstance", "changed circumstances"],
    "escrow-account": ["escrow", "impound account"],
    "points-and-fees": ["QM points and fees", "HOEPA points and fees"],
    "loan-originator-compensation": ["LO comp", "LO compensation"],
    "safe-act": ["Secure and Fair Enforcement for Mortgage Licensing Act"],
    "hpml-appraisal": ["HPML appraisal", "higher-priced mortgage appraisal"],
    "high-cost-mortgage": ["Section 32 loan", "HOEPA loan"],
    "higher-priced-mortgage-loan": ["Section 35 loan"],
    "request-for-information": ["RFI"],
    "loss-mitigation": ["loss mit"],
    "tolerance-cure": ["cure", "tolerance refund"],
    "ten-percent-tolerance": ["10% tolerance", "10% bucket", "ten percent tolerance"],
    "zero-tolerance": ["0% tolerance", "zero-tolerance bucket"],
    "right-of-rescission": ["rescission", "right to cancel"],
    "three-business-day-rule": ["three-day rule", "3-day rule"],
    "representative-credit-score": ["middle score", "qualifying credit score"],
    "pitia": ["housing payment"],
    "usda-guaranteed-loan": ["USDA loan", "Rural Development loan", "Section 502 Guaranteed"],
    "conforming-loan-limit": ["loan limit", "FHFA loan limit"],
    "lender-paid-mortgage-insurance": ["LPMI"],
    "borrower-paid-mortgage-insurance": ["BPMI"],
    "e-sign-act": ["ESIGN", "Electronic Signatures in Global and National Commerce Act"],
    "marketing-services-agreement": ["MSA"],
    "respa-section-8": ["Section 8", "12 USC 2607"],
    "red-flags-rule": ["identity theft red flags"],
    "adverse-action-notice": ["AAN", "statement of credit denial"],
    "risk-based-pricing-notice": ["RBPN"],
    "periodic-statement": ["mortgage statement", "monthly statement"],
    "servicing-transfer": ["transfer of servicing", "hello letter", "goodbye letter"],
    "escrow-analysis": ["annual escrow statement"],
    "dodd-frank-act": ["Dodd-Frank Wall Street Reform and Consumer Protection Act"],
    "general-qualified-mortgage": ["General QM", "price-based QM"],
    "reverse-mortgage": ["HECM"],
    "udaap": ["unfair, deceptive, or abusive acts or practices"],
    "closing-wire-fraud": ["wire fraud", "business email compromise"],
    "kickback": ["referral fee"],
}

ES = {
    # "Know Before You Owe" in the CFPB Spanish glossary is "Infórmese Antes de Deber".
    "trid": ["Divulgación integrada TILA-RESPA", "Infórmese antes de deber"],
    # CFPB Spanish glossary lists reserva and escrow as escrow-account equivalents.
    "escrow-account": ["reserva", "escrow"],
    "ten-percent-tolerance": ["tolerancia del 10%"],
    "three-business-day-rule": ["regla de tres días"],
    "reverse-mortgage": ["HECM"],
}

# CFPB Spanish glossary equivalents where the site's Spanish headword differs
# (found by scripts/checks/bilingual_check.py). Added as aliases only; whether to
# switch the headword is for the native-speaker review.
CFPB_ES = {
    'ability-to-repay': ['Capacidad de reembolso'],
    'cash-to-close': ['Dinero en efectivo para el cierre'],
    'co-signer': ['Cofirmante'],
    'credit-score': ['Puntaje crediticio', 'puntuación de crédito'],
    'demand-feature': ['Característica de la demanda'],
    'dual-tracking': ['Doble seguimiento (dual tracking)'],
    'finance-charge': ['Cargo financiero'],
    'fully-indexed-rate': ['Tasa completamente indexada'],
    'housing-expense-ratio': ['Relación de gastos de vivienda'],
    'installment-debt': ['Deuda en cuotas'],
    'mortgage-payoff': ['Pago completo de la hipoteca'],
    'power-of-attorney': ['Poder legal'],
    'prepaid-interest': ['Pago anticipado de interés'],
    'rate-lock': ['Tasa segura', 'bloqueo de tasa'],
    'redlining': ['Prácticas discriminatorias'],
    'reinstatement': ['Restitución'],
    'rental-income': ['Ingresos del alquiler'],
    'repayment-plan': ['Plan de pagos', 'plan de reembolso'],
    'revolving-debt': ['Deuda renovable'],
    'va-funding-fee': ['Tarifa de financiamiento del VA'],
}


def apply(doc):
    slug = doc["slug"]
    en = list(doc["aliases"])
    for alias in EN.get(slug, []):
        if alias.lower() not in {a.lower() for a in en} and alias.lower() != doc["term"].lower():
            en.append(alias)
    doc["aliases"] = en
    es = list(doc["es"]["aliases"])
    acronyms = [a for a in en if a.isupper() and 2 <= len(a) <= 6]
    for alias in acronyms + ES.get(slug, []) + CFPB_ES.get(slug, []):
        if alias.lower() not in {a.lower() for a in es} and alias.lower() != doc["es"]["term"].lower():
            es.append(alias)
    doc["es"]["aliases"] = es
    return doc
