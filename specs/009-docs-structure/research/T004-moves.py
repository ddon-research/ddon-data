"""009 T004: write T004-moves.md, one row per classified section of the packet README and the adoc.

    python -X utf8 -I specs/009-docs-structure/research/T004-moves.py
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = "research/03040008/packets/README.md"
ADOC = "packets/README-decrypt-annotate-streams.adoc"
R = "docs/reference/"
H = "docs/how-to/"
OPEN = R + "packet-open-questions.md"
NEXT = "; the why is for the explanation page of the next package"

HEADINGS = {
    "Packet patterns, client 03040008": (R"packets/patterns/03040008/README.md", "short README; spec history lines 4-6 cut, spec 005 keeps them"),
    "How the patterns are built": ("see the [sub] rows", ""),
    "How to export": (f"{H}export-packets-to-json.md, {R}imhex-export-cli.md", ""),
    "Evidence rules": (f"{R}packet-marks.md § Evidence rules", "the rules whole" + NEXT),
    "Patterns": ("see the [sub] rows", ""),
    "Open items": ("see the [sub] rows", ""),
    "Parallel CLI Runner README": ("packets/README.md", "stale title dropped"),
    "Purpose": (f"{H}reannotate-streams.md", ""),
    "Requirements": (f"{H}reannotate-streams.md", "stale: `flock` and `grep`, which the script does not use, are cut; gawk's `match` added"),
    "Configuration": (f"{H}reannotate-streams.md § Variables", ""),
    "Usage": (f"{H}reannotate-streams.md", "stale `./run-parallel-packet.sh` corrected to `decrypt-annotate-streams.sh`; the script does not cd, so the page says run it from packets/"),
    "Concurrency tuning": (f"{H}reannotate-streams.md § Variables", ""),
    "Required Arrowgene CLI patches": (f"{H}patch-the-arrowgene-cli.md, {R}arrowgene-cli-patches.md", "reasons on the reference page" + NEXT + "; export comparisons cut, see below"),
    "Splitting large dumps": (f"{H}reannotate-streams.md § Split large dumps", ""),
    "Exporting raw packets": (f"{H}reannotate-streams.md § Export raw packets, {R}packet-pattern-format.md § Raw file names", "export history cut, see below"),
    "Exporting packet structures with ImHex": (f"{H}export-packets-to-json.md, {R}imhex-export-cli.md, {R}packet-pattern-format.md", "measurements to docs/reference/status.md"),
    "Packet statistics": (f"{H}refresh-packet-statistics.md", "`unknown` file, `-k`, `-f` and `ANNOTATED_DIR` added from the script"),
}
SUBS = {
    "Include table": (f"{R}packet-includes.md", "history wording cut; `CharacterData.hexpat` row added"),
    "Structure comment and marks": (f"{R}packet-marks.md", ""),
    "Naming unknown fields by inference": (f"{H}name-an-unknown-field.md, {R}packet-marks.md § Comment forms", "the count of T014c's application is in 006 tasks"),
    "Header comment": (f"{R}packet-pattern-format.md § Header comment", "reason history in 005 R2 F2, 006 T002c"),
    "JSON conventions": (f"{R}packet-pattern-format.md § JSON conventions", ""),
    "RES error guard": (f"{R}packet-pattern-format.md § RES error guard", "rule and 18.0.2 exception" + NEXT),
    "Exported checks": (f"{R}packet-pattern-format.md § Exported checks", ""),
    "What a fit proves": (f"{R}packet-pattern-format.md § Exported checks", "the rule" + NEXT),
    "Patterns: status meaning and report key": (f"{R}packet-ids.md § Report labels, § Reading the table; {R}packet-marks.md", "dated recount prose reduces to one date"),
    "Patterns: how value bases are counted": (f"{R}packet-marks.md § Value bases", "rule, density formula and item density" + NEXT),
    "Patterns: the per-id table": (f"{R}packet-ids.md § The table", "595 rows intact; 31 counts corrected in their own commit"),
}
HISTORY = {
    "Code-backed renames": f"{R}arrowgene-cli-patches.md § Names from code holds the eight renames; the `(was ...)` notes stay on packet-ids.md",
    "14.10.16 name": f"{R}arrowgene-cli-patches.md § Names from code holds the call-site evidence (`0x840160`)",
}


def row_target(row):
    if row[1].startswith("[sub] Open item: "):
        name = row[1][len("[sub] Open item: "):]
        if row[4] == OPEN:
            return OPEN, "history wording cut; re-checked by `T004-names.py`"
        for key, note in HISTORY.items():
            if name.startswith(key):
                return "cut (history)", note
        if "not patterned" in name:
            return "cut (stale)", "every id listed has a pattern; spec 006 reports keep the PC readers"
        return "cut (history)", "the named report and spec 006 tasks hold it"
    if row[1].startswith("[sub] "):
        return SUBS[row[1][len("[sub] "):]]
    return HEADINGS[row[1]]


def main():
    with (HERE / "T001-sections.tsv").open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.reader(handle, delimiter="\t", quoting=csv.QUOTE_NONE) if r[0] in (README, ADOC)]
    out = [(HERE / "T004-moves-head.txt").read_text(encoding="utf-8"), "| Source | Section | Lines | Went to | Note |", "| --- | --- | --- | --- | --- |"]
    for row in rows:
        target, note = row_target(row)
        source = "README" if row[0] == README else "adoc"
        out.append(f"| {source} | {row[1].replace('|', '/')} | {row[2]} | {target} | {note} |")
    out.append((HERE / "T004-moves-tail.txt").read_text(encoding="utf-8"))
    (HERE / "T004-moves.md").write_bytes("\n".join(out).encode("utf-8"))
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
