"""Write ``dumps/MANIFEST.tsv``: one row per JSONL dump (file, sha256, source sha256, script, version).

    uv run python manifest.py [dumps_dir]

The source sha256 is the header's ``input_sha256`` (IDA dumps: the database's input file) or
``elf_sha256`` (DWARF dumps). The dumps themselves are gitignored; the manifest is committed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

COLUMNS = ("file", "sha256", "bytes", "lines", "script", "script_version", "side", "source_sha256")


def manifest_row(path: Path) -> dict:
    sha = hashlib.sha256()
    lines = 0
    header = None
    with open(path, "rb") as fh:
        for raw in fh:
            sha.update(raw)
            if header is None:
                header = json.loads(raw)
            lines += 1
    header = header or {}
    return {"file": path.name, "sha256": sha.hexdigest(), "bytes": path.stat().st_size, "lines": lines,
            "script": header.get("script"), "script_version": header.get("script_version"),
            "side": header.get("side"),
            "source_sha256": header.get("input_sha256") or header.get("elf_sha256")}


def write_manifest(dumps: Path) -> Path:
    rows = [manifest_row(p) for p in sorted(dumps.glob("*.jsonl"))]
    out = dumps / "MANIFEST.tsv"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            fh.write("\t".join("" if r[c] is None else str(r[c]) for c in COLUMNS) + "\n")
    return out


if __name__ == "__main__":
    print(write_manifest(Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "dumps")))
