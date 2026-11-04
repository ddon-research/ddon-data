"""009 T004: every field or type name a packet page names in a code span exists in the 03040008 patterns or includes.

    python -X utf8 -I specs/009-docs-structure/research/T004-names.py

The re-check of the moved open questions against the names the patterns carry; a name a page gives as a lead or a
former name is expected to miss, and is read by hand.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "packets/patterns/03040008"
corpus = "".join(p.read_text(encoding="utf-8") for p in [*ROOT.glob("*-pattern.cpp"), *ROOT.glob("include/*")])
for name in ("packet-open-questions", "packet-includes"):
    page = (REPO / f"docs/reference/{name}.md").read_text(encoding="utf-8")
    missing = set()
    for span in set(re.findall(r"`([^`]+)`", page)):
        for word in re.findall(r"(?:unk_|CData|[A-Z][a-z]+[A-Z])\w+", span):
            if word not in corpus:
                missing.add(word)
    print(name, sorted(missing))
