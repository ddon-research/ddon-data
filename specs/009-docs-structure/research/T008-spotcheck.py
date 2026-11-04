"""009 T008: spot-check that the paths, commands and URLs of the deleted or shortened docs reached a page or the cut list.

    python -X utf8 -I specs/009-docs-structure/research/T008-spotcheck.py <base sha>

Tokens: URLs, file and script names, flags, hex numbers. A token counts as found when it occurs in the pages that
replaced its file, or in the section "Cut" of T008-moves.md. Exit status 1 lists the misses.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DECODE = ["docs/how-to/decode-a-resource-format.md", "docs/how-to/choose-a-resource-target.md", "docs/reference/status.md",
          "research/README.md"]
FILES = {
    "research/README.adoc": DECODE,
    "research/rLandInfo-example.adoc": DECODE,
    "research/wikis-and-resources.adoc": ["docs/reference/community-resources.md"],
    "research/03040008/notes/quest-flag-data-source-mapping.adoc": ["docs/reference/quest-flag-sources.md"],
    "research/rng-race/README.md": ["research/rng-race/README.md", "docs/reference/inputs-and-builds.md",
                                    "docs/explanation/rng-race.md"],
    "readme.adoc": ["readme.adoc", "docs/reference/repository-layout.md", "docs/reference/tools-and-shell.md",
                    "docs/how-to/extract-client-resources.md", "docs/how-to/decode-a-resource-format.md",
                    "docs/how-to/decrypt-a-capture.md", "docs/reference/inputs-and-builds.md",
                    "docs/how-to/choose-a-resource-target.md"],
}
TOKENS = (
    ("url", re.compile(r"https?://[^\s\[\]<>)]+")),
    ("hex", re.compile(r"\b0x[0-9A-Fa-f]{2,}\b")),
    ("flag", re.compile(r"(?<![\w-])--?[a-zA-Z][a-zA-Z0-9-]*\b")),
    ("name", re.compile(r"[\w/.-]+\.(?:py|sh|r2|json|jsonl|tsv|exe|h|c|cpp|csv|txt|md|adoc|lai)\b")),
)


def main():
    moves = (REPO / "specs/009-docs-structure/research/T008-moves.md").read_text(encoding="utf-8")
    cut = moves.split("## Cut", 1)[1] if "## Cut" in moves else ""
    misses = 0
    for old_path, pages in FILES.items():
        old = subprocess.run(["git", "show", f"{sys.argv[1]}:{old_path}"], cwd=REPO, capture_output=True, check=True,
                             ).stdout.decode("utf-8")
        hay = ("\n".join((REPO / p).read_text(encoding="utf-8") for p in pages) + "\n" + cut).lower().replace("\\", "/")
        print(old_path)
        for label, rx in TOKENS:
            tokens = sorted(set(rx.findall(old)))
            missing = [t for t in tokens
                       if t.lower().replace("\\", "/") not in hay and t.rsplit("/", 1)[-1].lower() not in hay]
            print(f"  {label}: {len(tokens)} tokens, {len(missing)} missing: {' '.join(missing)}")
            misses += len(missing)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
