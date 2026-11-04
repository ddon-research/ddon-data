"""009 T004: every packet id, hex address, .hexpat name and SHA-256 of the old README and adoc lands somewhere.

    python -X utf8 -I specs/009-docs-structure/research/T004-spotcheck.py

"Somewhere" is a page under docs/, a short packet README or the cut list of T004-moves.md. A token on none of them is a
miss; the exit status is 1 then. Each miss prints the spec report that holds it, or `nowhere`.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASE = "715f8f2305d"
SOURCES = ("packets/patterns/03040008/README.md", "packets/README-decrypt-annotate-streams.adoc")
TOKENS = {
    "id": re.compile(r"(?<![\w.])\d+\.\d+\.\d+(?![\w.]*\d)"),
    "address": re.compile(r"\b0[xX][0-9A-Fa-f]+\b"),
    "hexpat": re.compile(r"\b\w+\.hexpat\b"),
    "sha256": re.compile(r"\b[0-9a-f]{64}\b"),
}


def tokens(text):
    return {kind: set(rx.findall(text)) for kind, rx in TOKENS.items()}


def main():
    source = "\n".join(
        subprocess.run(["git", "-C", str(REPO), "show", f"{BASE}:{p}"], check=True, capture_output=True).stdout.decode("utf-8")
        for p in SOURCES)
    moves = REPO / "specs/009-docs-structure/research/T004-moves.md"
    targets = [*(REPO / "docs").rglob("*.md"), REPO / "packets/README.md", REPO / "packets/plbatch/README.md", moves]
    landed = "\n".join(p.read_text(encoding="utf-8") for p in targets if p.is_file())
    misses = 0
    for kind, found in tokens(source).items():
        for token in sorted(found):
            present = re.search(rf"(?<![\w.]){re.escape(token)}(?![\w])", landed, re.IGNORECASE if kind == "address" else 0)
            if present:
                continue
            misses += 1
            run = subprocess.run(["rg", "-l", "-i", "-F", token, "specs/005-netmsg-patterns", "specs/006-packet-pattern-coverage",
                                  "specs/008-remaining-packets", "-g", "*.md"], cwd=REPO, capture_output=True, encoding="utf-8")
            homes = [Path(h.replace("\\", "/")).name for h in run.stdout.splitlines()]
            print(f"{kind}\t{token}\t{','.join(homes[:2]) or 'nowhere'}")
    print(f"{sum(len(v) for v in tokens(source).values())} tokens, {misses} misses", file=sys.stderr)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
