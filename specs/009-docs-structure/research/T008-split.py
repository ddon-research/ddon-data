"""009 T008: move research/wikis-and-resources.adoc to docs/reference/community-resources.md by script.

    python -X utf8 -I specs/009-docs-structure/research/T008-split.py <base sha>

Headings and URLs move whole. The chat-log section becomes one block per backed-up site. The cut lines are named in
T008-moves.md.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SOURCE = "research/wikis-and-resources.adoc"
TARGET = REPO / "docs/reference/community-resources.md"

OPENING = """# Community resources

Outside material on Dragon's Dogma Online: archived official pages, wikis, spreadsheets, playthrough videos and repositories, for a researcher who wants evidence of what the live service showed. Nothing here is needed to use this repository, and none of it is evidence of a client layout. For the repositories and documents the research relies on, see [`research/external-references.md`](../../research/external-references.md).

**Status:** not run. The URLs were not checked when this page was written (2026-11-04); some were already archived copies, and any may be gone.
"""

BACKUP_INTRO = """Website backups beyond the Wayback Machine, as standalone WACZ archives made with [Browsertrix](https://crawler.docs.browsertrix.com/user-guide/). It packages a site in the web archive format the Internet Archive uses and rewrites all links and resources. The wget and Python alternatives failed on sitemaps, went too far or not far enough, and left links to fix by hand.

| Do this | With |
| --- | --- |
| Replay a WACZ in the browser | <https://replayweb.page/> |
| Replay a WACZ on the desktop | <https://github.com/webrecorder/replayweb.page/releases/tag/v2.2.5> |
| Reach the HTML pages | <https://github.com/chfoo/warcat-rs>, examples at <https://warcat-rs.readthedocs.io/en/latest/usage_examples.html#extract-everything> |

Unpack the WACZ with 7-zip or unzip, then extract the `warc.gz` of its `archive` folder:

```sh
warcat extract --input "archive\\rec-06e7f4f19938-20250122204822175-0.warc.gz"
```

The wget form that was tried, for the record:

```sh
{wget}
```

Each backup below names its site, its WACZ, any note and the crawl command.
"""


def adoc_lines(text):
    """The list sections of the page as Markdown, up to the backup section."""
    out = []
    seen = set()
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith(":") or line.startswith("toc::") or line == "'''":
            continue
        heading = re.match(r"^(=+) (.+?):?$", line)
        if heading:
            if heading[2] == "Wikis and other resources":
                continue
            out.append("")
            out.append("#" * max(len(heading[1]), 2) + " " + heading[2])
            out.append("")
            continue
        bullet = re.match(r"^(\s*)\* (.*)$", line)
        if bullet:
            depth = "  " if bullet[1] else ""
            body = autolink(bullet[2].replace(" * Lv", " Lv"))
            key = body.strip()
            if key.startswith("<") and key in seen:  # the one URL the source lists twice
                continue
            seen.add(key)
            if out and out[-1] and not out[-1].startswith(("- ", "  - ")):
                out.append("")
            out.append(f"{depth}- {body}")
            continue
        if line:
            if out and out[-1].startswith(("- ", "  - ")):
                out.append("")
            out.append(autolink(line))
    return out


def autolink(text):
    return re.sub(r"(?<![<(])(https?://[^\s<>]+)", r"<\1>", text)


def backups(text):
    blocks, block = [], None
    wget = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("wget "):
            wget = line
        if line.startswith("Site: "):
            block = {"site": line[6:].strip()}
            blocks.append(block)
        elif block is not None:
            for key, label in (("wacz", "WACZ: "), ("note", "Notes: "), ("note", "Note: "), ("command", "Command: ")):
                if line.startswith(label):
                    block[key] = line[len(label):].strip()
    return blocks, wget


def main():
    text = subprocess.run(["git", "show", f"{sys.argv[1]}:{SOURCE}"], cwd=REPO, capture_output=True, check=True,
                          ).stdout.decode("utf-8")
    head, rest = text.split("=== Backing up old wikis", 1)
    body = "\n".join(adoc_lines(head))
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    blocks, wget = backups(rest)
    out = [OPENING, body, "", "## Wiki backups", "", BACKUP_INTRO.replace("{wget}", wget)]
    for block in blocks:
        out.append(f"### {block['site']}")
        out.append("")
        out.append(f"- WACZ: <{block['wacz']}>")
        if "note" in block:
            out.append(f"- Note: {block['note']}")
        out.append("")
        out.append("```sh")
        out.append(block["command"])
        out.append("```")
        out.append("")
    TARGET.write_bytes(("\n".join(out).rstrip() + "\n").encode("utf-8"))
    print(f"{TARGET.relative_to(REPO)}: {len(blocks)} backups")


if __name__ == "__main__":
    main()
