"""The documentation gate: docs/**/*.md, readme.adoc and the short directory READMEs.

  uv run --offline --no-project --with markdown-it-py==4.2.0 python -X utf8 tools/docs_check.py

The rules are docs/reference/documentation-style.md; the how-to is docs/how-to/write-documentation.md.
Checks (the name in brackets is what a finding prints):

  (a) [link]     a relative link resolves to a file in the git index or an untracked file under docs/,
                 compared case-sensitively: with core.ignorecase a filesystem check cannot see a case mismatch
  (b) [anchor]   a link's anchor resolves to a heading of the target
  (c) [index]    every page is linked from docs/index.md, exactly once
  (d) [path]     a code span that starts with a known top directory names a path that exists
  (e) [wording]  outside fences and code spans: no task id, package label, wave name or dating word
  (f) [opening]  a paragraph comes right after the title
  (g) [tutorial] the tutorial's inputs match their SHA-256 and its jq line matches the committed JSON

It reads the git index (paths only), the pages and the three tutorial inputs: no other file under client/ or packets/.
Exit status: 0 no finding, 1 findings, 3 not run (markdown-it-py missing).
"""

import argparse
import dataclasses
import hashlib
import json
import posixpath
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None

REPO = Path(__file__).resolve().parent.parent
TOP_DIRECTORIES = ("client", "packets", "research", "binaries", "patches", "tools", "specs", "docs")

# The directory READMEs held to the page rules. A package that shortens a README adds it here.
SHORT_READMES = (
    "research/scripts/README.md",
    "research/prompts/README.md",
    "research/03040008/notes/README.md",
)

# Untracked trees of other work a code span may name while they are not committed; on disk, exact case. Never links.
OTHER_WORK = ("research/knowledge-graph",)

# x86 R8 and R9 go in code spans, like every other exact name (the contract says so).
LABELS = re.compile(r"\b(?:T\d{3}[a-z]?|TC\d+|R\d[a-z]?|P\d{1,2}[a-z]?)\b|\b[Ww]aves?[ -]\d+\b|\b[Bb]atch(?:es)? B\d\b")
# The list documentation-style.md prints under "Terms"; a test keeps the two equal.
DATING_WORDS = ("currently", "now", "nowadays", "today", "recently", "new", "newly", "old", "existing", "yet",
                "no longer", "so far", "at present")
DATING = re.compile(r"\b(?:" + "|".join(DATING_WORDS) + r")\b", re.IGNORECASE)
URL_IN_TEXT = re.compile(r"https?://\S+")

ADOC_LINK = re.compile(r"\b(?:link|xref):([^\s\[]+)\[")
ADOC_SPAN = re.compile(r"`([^`\n]+)`")
ADOC_HEADING = re.compile(r"^={1,6} +(.+?) *$", re.MULTILINE)
ADOC_FENCE = re.compile(r"^(----|```)[^\n]*\n.*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)


@dataclasses.dataclass(frozen=True)
class Tutorial:
    page: str
    inputs: tuple  # (path, sha256) pairs
    json_path: str
    jq_line: str  # what `jq -c .` prints for json_path


_WARP = "stream3-party-experiments-marked.pcapng_tcp-stream-47/12863_S2C_WARP_WARP_RES_2019-07-08T10_35_53.3199119-07_00.14_3_2"
TUTORIAL = Tutorial(
    page="docs/tutorials/read-one-packet.md",
    inputs=(
        (f"packets/decrypted_raw/{_WARP}", "4a693d40ba70f74a7b2af3b43ee028e96a5cb9f298abb533d5ba1dd27ac8759f"),
        (f"packets/decrypted_json/{_WARP}.json", "d93d890bc91a8c758d322f28b344fbd84044b979d0cebfd0ca3ce76786c79b1b"),
        ("research/03040008/packets/S2C_WARP_WARP_RES-pattern.cpp",
         "0e8e3f859a7d1b2988054ed97be3c83cdc597850ab0856a124cc37a68b63c044"),
    ),
    json_path=f"packets/decrypted_json/{_WARP}.json",
    jq_line='{"packet":{"group":14,"id":3,"subId":2,"source":52,"packetcounter":0,"sourceOk":true,"Error":0,'
            '"Result":0,"WarpPointID":66,"Rim":39109,"paddingSize":7,"fits":true}}',
)


@dataclasses.dataclass(frozen=True)
class Finding:
    check: str
    path: str
    line: int
    message: str

    def __str__(self):
        return f"{self.path}:{self.line}: [{self.check}] {self.message}"


class Tree:
    """The paths git knows, without touching the working tree. Case-sensitive on every platform."""

    def __init__(self, root):
        self.root = Path(root)
        self.files = set(self._git("ls-files", "-z"))
        self.files.update(self._git("ls-files", "-z", "--others", "--exclude-standard", "--", "docs"))
        self._folded = None
        self.dirs = set()
        for path in self.files:
            parent = path.rpartition("/")[0]
            while parent and parent not in self.dirs:
                self.dirs.add(parent)
                parent = parent.rpartition("/")[0]

    def _git(self, *args):
        out = subprocess.run(["git", "-C", str(self.root), "-c", "core.quotepath=off", *args], check=True,
                             capture_output=True).stdout
        return [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]

    def case_variant(self, path):
        """The tracked file that differs from `path` only in case, or None."""
        if self._folded is None:
            self._folded = {f.lower(): f for f in self.files}
        return self._folded.get(path.lower())

    def exists_local(self, path):
        """A path that a code span may name without git tracking it, on disk with this exact case: gitignored local
        data (binaries/PS4_02020005/elf-dumps/local/) or an OTHER_WORK tree."""
        if not any(path == w or path.startswith(w + "/") for w in OTHER_WORK):
            ignored = subprocess.run(["git", "-C", str(self.root), "check-ignore", "-q", path], capture_output=True)
            if ignored.returncode != 0:
                return False
        here = self.root
        for part in path.split("/"):
            if not here.is_dir() or part not in {e.name for e in here.iterdir()}:
                return False
            here = here / part
        return True


def github_slug(title):
    slug = re.sub(r"[^\w\- ]", "", title.strip().lower())
    return slug.replace(" ", "-")


def with_duplicates(slugs):
    seen, out = Counter(), set()
    for slug in slugs:
        out.add(slug if not seen[slug] else f"{slug}-{seen[slug]}")
        seen[slug] += 1
    return out


class Page:
    """A Markdown file parsed once."""

    parser = None

    def __init__(self, root, path):
        self.path = path
        self.text = (Path(root) / path).read_text(encoding="utf-8")
        if Page.parser is None:
            Page.parser = MarkdownIt("commonmark").enable("table")
        self.tokens = Page.parser.parse(self.text)

    def inline(self):
        """(line, inline child) outside fences and blocks of code; a child of a link is a child too."""
        for token in self.tokens:
            if token.type != "inline":
                continue
            line = (token.map[0] if token.map else 0) + 1
            for child in token.children or ():
                if child.type in ("softbreak", "hardbreak"):
                    line += 1
                yield line, child

    def links(self):
        for line, child in self.inline():
            if child.type == "link_open":
                yield line, child.attrs.get("href", "")
            elif child.type == "image":
                yield line, child.attrs.get("src", "")

    def code_spans(self):
        return ((line, c.content) for line, c in self.inline() if c.type == "code_inline")

    def anchors(self):
        titles = []
        for index, token in enumerate(self.tokens):
            if token.type == "heading_open":
                inline = self.tokens[index + 1]
                titles.append("".join(c.content for c in inline.children
                                      if c.type in ("text", "code_inline")))
        return with_duplicates(github_slug(t) for t in titles)


def split_link(page_path, href):
    """(repository path or None for a same-page link, anchor), or None for an external link."""
    parts = urlsplit(href)
    if parts.scheme or parts.netloc:
        return None
    anchor = unquote(parts.fragment)
    if not parts.path:
        return None, anchor
    if parts.path.startswith("/"):
        return "/", anchor  # never resolves: absolute paths mean nothing on GitHub or on disk
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page_path), unquote(parts.path)))
    return target, anchor


def check_link(root, tree, pages, path, line, href):
    split = split_link(path, href)
    if split is None:
        return
    target, anchor = split
    if target is not None and target not in tree.files:
        hint = ""
        variant = tree.case_variant(target)
        if variant:
            hint = f" (the index has {variant}: case differs)"
        elif target in tree.dirs:
            hint = " (a directory: link its README)"
        yield Finding("link", path, line, f"{href} resolves to {target}, not in the git index{hint}")
        return
    if not anchor:
        return
    target = target or path
    anchors = target_anchors(root, pages, target)
    if anchors is None:
        yield Finding("anchor", path, line, f"{href}: {target} has no headings to anchor to")
    elif anchor not in anchors:
        yield Finding("anchor", path, line, f"{href}: no heading #{anchor} in {target}")


def target_anchors(root, pages, target):
    if not (Path(root) / target).is_file():
        return None
    if target.endswith(".md"):
        if target not in pages:
            pages[target] = Page(root, target)
        return pages[target].anchors()
    if target.endswith(".adoc"):
        text = (Path(root) / target).read_text(encoding="utf-8")
        return with_duplicates(github_slug(t) for t in ADOC_HEADING.findall(ADOC_FENCE.sub("", text)))
    return None


def span_path(span):
    """The repository path a code span names, or None. The first word counts: `tools/check.sh --all`."""
    words = span.strip().split()
    if not words:
        return None
    word = words[0].rstrip(",.;")
    if "/" not in word or word.split("/", 1)[0] not in TOP_DIRECTORIES:
        return None
    if any(c in word for c in "*?[]{}<>$…|\\") or "..." in word:
        return None
    return re.sub(r":\d+(-\d+)?$", "", word).split("#")[0].rstrip("/")


def check_span(tree, path, line, span):
    target = span_path(span)
    if target and target not in tree.files and target not in tree.dirs and not tree.exists_local(target):
        yield Finding("path", path, line, f"`{span}`: {target} is not in the git index")


def check_wording(path, line, text):
    text = URL_IN_TEXT.sub("", text)
    for match in LABELS.finditer(text):
        yield Finding("wording", path, line, f"process label {match.group(0)!r}: state the fact, or cite the file in a code span")
    for match in DATING.finditer(text):
        yield Finding("wording", path, line, f"dating word {match.group(0)!r}: give a date or cut it")


def check_opening(page):
    tokens = page.tokens
    if not tokens or tokens[0].type != "heading_open" or tokens[0].tag != "h1":
        yield Finding("opening", page.path, 1, "the page does not start with a # title")
    elif len(tokens) < 4 or tokens[3].type != "paragraph_open":
        line = (tokens[3].map[0] + 1) if len(tokens) > 3 and tokens[3].map else 1
        yield Finding("opening", page.path, line, "no paragraph right after the title (who it is for, what they get, what they need)")


def check_index(root, tree, pages, docs_pages, index="docs/index.md"):
    if index not in tree.files or index not in pages:
        yield Finding("index", index, 1, "docs/index.md does not exist")
        return
    listed = Counter()
    for _line, href in pages[index].links():
        split = split_link(index, href)
        if split and split[0] and split[0] in docs_pages:
            listed[split[0]] += 1
    for page in sorted(docs_pages):
        if page != index and listed[page] == 0:
            yield Finding("index", page, 1, "not reachable: docs/index.md does not list it")
        elif page != index and listed[page] > 1:
            yield Finding("index", page, 1, f"docs/index.md lists it {listed[page]} times")


def check_tutorial(root, tutorial):
    page_file = Path(root) / tutorial.page
    if not page_file.is_file():
        yield Finding("tutorial", tutorial.page, 1, "the tutorial page does not exist")
        return
    page_text = page_file.read_text(encoding="utf-8")
    for path, sha in tutorial.inputs:
        data = Path(root) / path
        if not data.is_file():
            yield Finding("tutorial", tutorial.page, 1, f"input missing: {path}")
            continue
        actual = hashlib.sha256(data.read_bytes()).hexdigest()
        if actual != sha:
            yield Finding("tutorial", tutorial.page, 1, f"{path}: SHA-256 {actual}, the tutorial pins {sha}")
        if sha not in page_text:
            yield Finding("tutorial", tutorial.page, 1, f"the page does not state the SHA-256 of {path}")
    if tutorial.jq_line not in page_text:
        yield Finding("tutorial", tutorial.page, 1, "the page does not show the expected jq line")
    data = Path(root) / tutorial.json_path
    if data.is_file():
        printed = json.dumps(json.loads(data.read_text(encoding="utf-8")), separators=(",", ":"), ensure_ascii=False)
        if printed != tutorial.jq_line:
            yield Finding("tutorial", tutorial.page, 1, f"{tutorial.json_path}: jq -c prints {printed}")


def check_adoc(root, tree, pages, path):
    text = ADOC_FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), (Path(root) / path).read_text(encoding="utf-8"))
    for number, line in enumerate(text.splitlines(), 1):
        for href in ADOC_LINK.findall(line):
            yield from check_link(root, tree, pages, path, number, href)
        for span in ADOC_SPAN.findall(line):
            yield from check_span(tree, path, number, span)


def run(root=REPO, short_readmes=SHORT_READMES, tutorial=TUTORIAL, adoc=("readme.adoc",)):
    """(findings, summary counts). `adoc` and the READMEs that do not exist are findings, not skips."""
    root = Path(root)
    tree = Tree(root)
    findings = []
    docs_pages = {f for f in tree.files if f.startswith("docs/") and f.endswith(".md") and (root / f).is_file()}
    checked = sorted(docs_pages | set(short_readmes))
    pages = {}
    counts = Counter(pages=0, links=0, paths=0)
    for path in checked:
        if not (root / path).is_file():
            findings.append(Finding("link", path, 1, "a listed short README does not exist"))
            continue
        pages[path] = page = pages.get(path) or Page(root, path)
        counts["pages"] += 1
        findings.extend(check_opening(page))
        for line, href in page.links():
            counts["links"] += 1
            findings.extend(check_link(root, tree, pages, path, line, href))
        for line, span in page.code_spans():
            counts["paths"] += 1 if span_path(span) else 0
            findings.extend(check_span(tree, path, line, span))
        for line, child in page.inline():
            if child.type == "text":
                findings.extend(check_wording(path, line, child.content))
    findings.extend(check_index(root, tree, pages, docs_pages))
    findings.extend(check_tutorial(root, tutorial))
    for path in adoc:
        if (root / path).is_file():
            findings.extend(check_adoc(root, tree, pages, path))
    return findings, counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(REPO))
    args = parser.parse_args(argv)
    if MarkdownIt is None:
        print("docs_check: not run (markdown-it-py is not installed; run it through uv as the module docstring says)")
        return 3
    findings, counts = run(args.root)
    for finding in findings:
        print(finding)
    print(f"docs_check: {counts['pages']} pages, {counts['links']} links, {counts['paths']} code-span paths, "
          f"{len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
