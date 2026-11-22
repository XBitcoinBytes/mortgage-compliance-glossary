"""Paragraph-level citations placed ahead of each term's section-level citations.

Every pairing below was checked by reading the cited eCFR paragraph (text as of
2026-11-19). Add a pairing only after reading the paragraph.
"""

PINS = {
    "loan-estimate": ["reg-1026-19-e-1-iii"],
    "faq-what-is-a-loan-estimate": ["reg-1026-19-e-1-iii"],
    "written-list-of-providers": ["reg-1026-19-e-1-vi-C"],
    "intent-to-proceed": ["reg-1026-19-e-2-i-A"],
    "fee-worksheet": ["reg-1026-19-e-2-ii"],
    "zero-tolerance": ["reg-1026-19-e-3-i"],
    "ten-percent-tolerance": ["reg-1026-19-e-3-ii"],
    "no-tolerance-bucket": ["reg-1026-19-e-3-iii"],
    "changed-circumstance": ["reg-1026-19-e-3-iv"],
    "revised-loan-estimate": ["reg-1026-19-e-3-iv", "reg-1026-19-e-4"],
    "closing-disclosure": ["reg-1026-19-f-1-ii"],
    "three-business-day-rule": ["reg-1026-19-f-1-ii"],
    "cd-waiting-period-resets": ["reg-1026-19-f-2-ii"],
    "tolerance-cure": ["reg-1026-19-f-2-v"],
    "application-definition": ["reg-1026-2-a-3-ii"],
    "business-day": ["reg-1026-2-a-6"],
}


def apply(doc):
    pins = PINS.get(doc["slug"], [])
    doc["citations"] = pins + [c for c in doc["citations"] if c not in pins]
    return doc
