"""Print one section of a Markdown file, so an agent reads what it needs, not the whole file.

Usage: python -X utf8 -I tools/orchestration/section.py <file.md> '<heading text>'   one section
       python -X utf8 -I tools/orchestration/section.py <file.md> --list             its headings

A section runs from the first heading whose text contains <heading text> (case ignored) to
the next heading of the same or a higher level. Copied from the reconstructor
(C:/ddon-dwarf-reconstructor-rust), where a spec's `tasks.md` is about 110 KB: read whole, it
stays in an agent's context for every later turn (2026-10-17 there: spec documents were 10% of
what subagents re-read).
"""

import re
import sys

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def headings(lines):
    fence = False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fence = not fence
        match = None if fence else HEADING.match(line)
        if match:
            yield number, len(match.group(1)), match.group(2).strip()


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    path, wanted = sys.argv[1], sys.argv[2]
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError as why:
        print(f"section.py: {why}", file=sys.stderr)
        return 1
    found = list(headings(lines))
    if wanted == "--list":
        for number, level, text in found:
            print(f"{number:6}  {'  ' * (level - 1)}{text}")
        return 0
    for i, (number, level, text) in enumerate(found):
        if wanted.lower() in text.lower():
            end = next((n for n, lvl, _ in found[i + 1 :] if lvl <= level), len(lines) + 1)
            print(f"[{path} lines {number}-{end - 1}]")
            print("\n".join(lines[number - 1 : end - 1]))
            return 0
    print(f"section.py: no heading containing {wanted!r} in {path}; --list shows them", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
