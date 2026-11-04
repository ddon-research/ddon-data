"""009 T007: spot-check that the facts of the old client READMEs reached a page, a kept README or the cut list.

    python -X utf8 -I specs/009-docs-structure/research/T007-spotcheck.py <base sha>

Tokens: hex addresses, SHA-256 values and prefixes, sub_ names, flags, script and file names. A token counts as found
when it occurs in the pages or READMEs that replaced its file, or in the section "Cut" of T007-moves.md. Exit status 1
lists the misses.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
STATUS = "docs/reference/status.md"
GLOSSARY = "docs/reference/glossary.md"
PATCHES = ["patches/README.md", "docs/how-to/apply-a-client-patch.md", "docs/how-to/add-a-client-patch-layer.md",
           "docs/reference/client-patches.md", STATUS, GLOSSARY]
FILES = {
    "patches/README.md": PATCHES,
    "research/03040008/protections/README.md": [
        "research/03040008/protections/README.md", "docs/how-to/triage-a-client-crash.md",
        "docs/reference/protection-inventory.md", "docs/explanation/client-lineage-and-protections.md",
        "docs/reference/client-patches.md", GLOSSARY],
    "binaries/PS4_02020005/elf-dumps/README.adoc": [
        "binaries/PS4_02020005/elf-dumps/README.adoc", "docs/how-to/regenerate-elf-dumps.md",
        "docs/reference/elf-dumps.md", "docs/explanation/ps4-elf.md", STATUS],
    "research/pharos/README.md": ["research/pharos/README.md", "docs/how-to/run-pharos.md"],
    "research/textures/how-to-extract-images.adoc": ["research/textures/README.md", "docs/how-to/convert-textures.md"],
    "research/rng-race/README.md": ["research/rng-race/README.md", "docs/explanation/rng-race.md"],
}
TOKENS = (
    ("hex", re.compile(r"\b0x[0-9A-Fa-f]{2,}\b")),
    ("hash", re.compile(r"\b[0-9a-f]{64}\b")),
    ("prefix", re.compile(r"(?<![\w.])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{4,8}(?![\w…])")),
    ("sub", re.compile(r"\bsub_[0-9A-Fa-fx]+\b")),
    ("flag", re.compile(r"(?<![\w-])--?[a-zA-Z][a-zA-Z0-9-]*\b")),
    ("name", re.compile(r"[\w/.-]+\.(?:py|sh|r2|json|jsonl|tsv|exe|dll|h|c|log|txt|zst|md|adoc)\b")),
)


def main():
    moves = (REPO / "specs/009-docs-structure/research/T007-moves.md").read_text(encoding="utf-8")
    cut = moves.split("## Cut", 1)[1] if "## Cut" in moves else ""
    misses = 0
    for old_path, pages in FILES.items():
        old = subprocess.run(["git", "show", f"{sys.argv[1]}:{old_path}"], cwd=REPO, capture_output=True, check=True,
                             ).stdout.decode("utf-8")
        hay = ("\n".join((REPO / p).read_text(encoding="utf-8") for p in pages) + "\n" + cut).lower()
        print(old_path)
        for label, rx in TOKENS:
            tokens = sorted(set(rx.findall(old)))
            missing = [t for t in tokens if t.lower() not in hay and t.rsplit("/", 1)[-1].lower() not in hay]
            print(f"  {label}: {len(tokens)} tokens, {len(missing)} missing: {' '.join(missing)}")
            misses += len(missing)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
