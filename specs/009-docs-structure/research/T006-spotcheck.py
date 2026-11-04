"""009 T006: spot-check that the facts of the old ida-transfer README reached a page or the cut list.

    python -X utf8 -I specs/009-docs-structure/research/T006-spotcheck.py <base sha>

Tokens: hex addresses, flags, script and module names, and every code span of the old README. A token
counts as found when it occurs in the pages or the README that replaced it, or in the section "Cut" of
T006-moves.md. Exit status 1 lists the misses of the first three kinds; code spans are a report only,
since many are prose fragments.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OLD = "research/03040008/ida-transfer/README.md"
PAGES = [
    "docs/how-to/query-ida-read-only.md",
    "docs/how-to/write-to-an-ida-database.md",
    "docs/how-to/transfer-annotations-ps4-to-pc.md",
    "docs/reference/ida-transfer-tools.md",
    "docs/explanation/ida-transfer-method.md",
    "docs/reference/status.md",
    "docs/reference/glossary.md",
    OLD,
]
HEX = re.compile(r"\b0x[0-9A-Fa-f]{2,}\b")
HASH = re.compile(r"\b[0-9a-f]{8}\.\.\.[0-9a-f]{4}\b")
FLAG = re.compile(r"(?<![\w-])--[a-z][a-z0-9-]+")
SCRIPT = re.compile(r"[\w/.-]+\.(?:py|tsv|jsonl|h)\b")
SPAN = re.compile(r"`([^`\n]+)`")


def main() -> int:
    old = subprocess.run(["git", "show", f"{sys.argv[1]}:{OLD}"], cwd=REPO, capture_output=True, check=True,
                         encoding="utf-8").stdout
    text = "\n".join((REPO / p).read_text(encoding="utf-8") for p in PAGES)
    moves = (REPO / "specs/009-docs-structure/research/T006-moves.md").read_text(encoding="utf-8")
    cut = moves.split("## Cut", 1)[1] if "## Cut" in moves else ""
    hay = (text + "\n" + cut).lower()
    misses = 0
    for label, rx in (("hex", HEX), ("hash", HASH), ("flag", FLAG), ("name", SCRIPT)):
        tokens = sorted(set(rx.findall(old)))
        missing = [t for t in tokens if t.lower() not in hay and t.rsplit("/", 1)[-1].lower() not in hay]
        print(f"{label}: {len(tokens)} tokens, {len(missing)} missing: {' '.join(missing)}")
        misses += len(missing)
    spans = sorted(set(SPAN.findall(old)))
    missing = [s for s in spans if s.lower() not in hay]
    print(f"code spans: {len(spans)} tokens, {len(missing)} missing (report only):")
    for s in missing:
        print("  " + s)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
