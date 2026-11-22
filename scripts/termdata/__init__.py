"""Shared constructor for glossary entries."""


def E(
    slug,
    es,
    cites,
    related,
    setting,
    es_setting,
    definition,
    es_definition,
    details,
    es_details,
    notes,
    es_notes,
    example,
    es_example,
    aliases=None,
    es_aliases=None,
    flag=None,
):
    if "Example figures" not in example:
        example = example.rstrip() + " Example figures, not a quote or a legal limit."
    if "Cifras de ejemplo" not in es_example:
        es_example = es_example.rstrip() + " Cifras de ejemplo, no una cotización ni un límite legal."
    row = {
        "slug": slug,
        "es_term": es,
        "aliases": list(aliases or []),
        "es_aliases": list(es_aliases or []),
        "cites": list(cites),
        "related": list(related),
        "setting": setting,
        "es_setting": es_setting,
        "definition": definition.strip(),
        "es_definition": es_definition.strip(),
        "details": details.strip(),
        "es_details": es_details.strip(),
        "notes": notes.strip(),
        "es_notes": es_notes.strip(),
        "example": example.strip(),
        "es_example": es_example.strip(),
    }
    if flag:
        row["flag"] = flag
    return row
