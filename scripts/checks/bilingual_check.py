#!/usr/bin/env python3
"""Compare Spanish headwords with the CFPB Spanish-English glossary and check EN/ES parity.

Needs network and poppler (pdftotext). Prints a report; exits 0. Run before a release.
"""
import glob, json, re, subprocess, tempfile, unicodedata, pathlib

URL = "https://files.consumerfinance.gov/f/documents/cfpb_adult-fin-ed_spanish-style-guide-glossary.pdf"
def n(s): return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower().strip(' "“”.')
tmp = pathlib.Path(tempfile.mkdtemp())
# files.consumerfinance.gov refuses Python's urllib; curl with a browser UA works.
subprocess.run(["curl", "-s", "-L", "--max-time", "60", "-A", "Mozilla/5.0 Chrome/124", "-o", str(tmp / "g.pdf"), URL], check=True)
subprocess.run(["pdftotext", "-layout", str(tmp / "g.pdf"), str(tmp / "g.txt")], check=True)
G = {}
for line in (tmp / "g.txt").read_text().splitlines():
    parts = re.split(r"\s{3,}", line.strip())
    if len(parts) == 2 and parts[0] and parts[1] and len(parts[0]) < 60:
        G.setdefault(n(parts[0]), parts[1].strip())
T = [json.load(open(f)) for f in sorted(glob.glob("src/content/terms/*.json"))]
match, diffs = 0, []
for t in T:
    k = n(t["term"])
    if k not in G: continue
    cands = [n(x) for x in re.split(r",|;|/", G[k])]
    names = [n(t["es"]["term"])] + [n(a) for a in t["es"]["aliases"]]
    if any(c and (c in names or any(c in x for x in names)) for c in cands): match += 1
    else: diffs.append(f"  {t['slug']}: site '{t['es']['term']}' vs CFPB '{G[k]}'")
print(f"{match + len(diffs)} terms are in the CFPB glossary; {match} match a Spanish headword or alias; {len(diffs)} do not")
print("\n".join(diffs))
cfr = lambda s: set(re.findall(r"\b(?:10\d\d)\.\d+(?:\([a-z0-9]+\))*", s))
num = lambda s: set(re.findall(r"\b\d+(?:\.\d+)?\b", s))
for t in T:
    en = " ".join([t["definition"], t["details"], t["complianceNotes"]])
    es = " ".join([t["es"]["definition"], t["es"]["details"], t["es"]["complianceNotes"]])
    if num(en) - num(es): print(f"  numbers missing in Spanish: {t['slug']} {sorted(num(en) - num(es))}")
    if cfr(en) - cfr(es): print(f"  CFR references missing in Spanish: {t['slug']} {sorted(cfr(en) - cfr(es))}")
