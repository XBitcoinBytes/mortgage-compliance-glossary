#!/usr/bin/env python3
"""Compile authored term modules into src/content/terms/*.json."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))

from alias_overlay import apply as apply_aliases  # noqa: E402

MODULES = ["o", "u1", "u2", "c1", "c2", "l", "s", "p", "f"]


def main() -> None:
    manifest = json.loads((ROOT / "src/data/term-manifest.json").read_text())
    by_slug = {row["slug"]: row for row in manifest}
    citations = {row["id"] for row in json.loads((ROOT / "src/data/citations.json").read_text())}
    out = ROOT / "src/content/terms"
    out.mkdir(parents=True, exist_ok=True)
    seen = set()
    errors = []
    for name in MODULES:
        module = importlib.import_module(f"termdata.{name}")
        for entry in module.ENTRIES:
            slug = entry["slug"]
            if slug in seen:
                errors.append(f"duplicate authored slug {slug}")
                continue
            seen.add(slug)
            meta = by_slug.get(slug)
            if not meta:
                errors.append(f"{slug} is not in the manifest")
                continue
            for cite in entry["cites"]:
                if cite not in citations:
                    errors.append(f"{slug} bad citation {cite}")
            for rel in entry["related"]:
                if rel not in by_slug:
                    errors.append(f"{slug} bad related {rel}")
                if rel == slug:
                    errors.append(f"{slug} relates to itself")
            doc = {
                "slug": slug,
                "term": meta["term"],
                "aliases": entry["aliases"],
                "category": meta["category"],
                "definition": entry["definition"],
                "details": entry["details"],
                "complianceNotes": entry["notes"],
                "example": {"setting": entry["setting"], "text": entry["example"]},
                "citations": entry["cites"],
                "related": entry["related"],
                "reviewed": "2026-11-19",
                "es": {
                    "term": entry["es_term"],
                    "aliases": entry["es_aliases"],
                    "definition": entry["es_definition"],
                    "details": entry["es_details"],
                    "complianceNotes": entry["es_notes"],
                    "example": {"setting": entry["es_setting"], "text": entry["es_example"]},
                },
            }
            doc = apply_aliases(doc)
            if entry.get("flag"):
                doc["reviewFlag"] = entry["flag"]
            (out / f"{slug}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    missing = [row["slug"] for row in manifest if row["slug"] not in seen]
    if missing:
        errors.append(f"missing {len(missing)} slugs: {', '.join(missing[:30])}")
    if errors:
        print("\n".join(errors[:80]))
        raise SystemExit(1)
    print(f"wrote {len(seen)} terms")


if __name__ == "__main__":
    main()
