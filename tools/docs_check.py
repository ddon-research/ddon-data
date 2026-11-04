"""The documentation gate: docs/**/*.md, readme.adoc and the short directory READMEs.

  uv run --offline --no-project --with markdown-it-py==4.2.0 python -X utf8 tools/docs_check.py

The rules are docs/reference/documentation-style.md; the how-to is docs/how-to/write-documentation.md.
Checks (the name in brackets is what a finding prints):

  (a) [link]     a relative link resolves to a file in the git index or an untracked file under docs/, compared
                 case-sensitively (with core.ignorecase a filesystem check cannot see a case mismatch), and that file
                 is on disk. Only http, https and mailto are external. HTML href and src, undefined reference links and
                 adoc link:, xref:, image:, include: and <<...>> count as links. readme.adoc must exist and link
                 docs/index.md
  (b) [anchor]   a link's anchor resolves to a heading of the target
  (c) [index]    every page is linked from docs/index.md, exactly once; a Markdown or adoc file under docs/ is `.md`
  (d) [path]     in a code span, every word that starts with a known top directory (`./` and `../` too) names a path in
                 this case that exists, a trailing slash a directory; an absolute spelling of the repository is refused.
                 In a fence, the first word of each line
  (e) [wording]  outside fences and code spans, across line breaks, in image alt and HTML text and all of readme.adoc:
                 no task id, package label, wave name or dating word
  (f) [opening]  a paragraph comes right after the title
  (g) [tutorial] the tutorial's inputs match their SHA-256 and its jq line matches the committed JSON
  (h) [packet-ids] docs/reference/packet-ids.md has one row per packet pattern; id, name and every tag's marks equal the
                 pattern's; the Report column names a report label, the one of the pattern's `// Evidence:` where it has
                 one; a pattern file is named `<name>-pattern.cpp`

It reads the git index (paths only), the pages, the three tutorial inputs and the packet patterns: nothing else under
client/ or packets/.
Exit status: 0 no finding, 1 findings, 3 not run (markdown-it-py missing).

A separate mode compares the table's `n/m fit` with the JSON tree, which takes seconds, so the gate runs it only when
the table or the JSON changed; `--write` corrects the rows and the recount date, and nothing else:

  python -X utf8 tools/docs_check.py --packet-counts [--write]

Its exit status: 0 no difference (or all written), 1 differences left, 3 not run (rg or the JSON tree missing).
"""

import argparse
import dataclasses
import datetime
import hashlib
import json
import posixpath
import re
import shutil
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None

REPO = Path(__file__).resolve().parent.parent
TOP_DIRECTORIES = ("client", "packets", "research", "binaries", "patches", "tools", "specs", "docs")
EXTERNAL_SCHEMES = ("http", "https", "mailto")
README = "readme.adoc"
INDEX = "docs/index.md"
ABSOLUTE_REPOSITORY = re.compile(r"^(?:[a-zA-Z]:[\\/]|/[a-zA-Z]/|/mnt/[a-zA-Z]/)ddon-data[\\/]")
# Page extensions the docs tree must not hold under another spelling; `.md` itself is the one that is checked.
PAGE_EXTENSION = re.compile(r"\.(?:md|markdown|mdown|mkd|mkdn|mdwn|mdtext|adoc|asciidoc)$", re.IGNORECASE)

# The directory READMEs held to the page rules. A package that shortens a README adds it here.
SHORT_READMES = (
    "research/README.md",
    "research/scripts/README.md",
    "research/prompts/README.md",
    "research/03040008/dumps/README.md",
    "research/03040008/notes/README.md",
    "research/03040008/xfs/README.md",
    "tools/README.md",
    "packets/README.md",
    "packets/patterns/03040008/README.md",
    "packets/plbatch/README.md",
    "packets/wireshark/README.md",
    "patches/README.md",
    "research/03040008/protections/README.md",
    "research/pharos/README.md",
    "research/rng-race/README.md",
    "research/textures/README.md",
)

# Untracked trees of other work a code span may name while they are not committed; on disk, exact case. Never links.
OTHER_WORK = ("research/knowledge-graph",)

# x86 R8 and R9 go in code spans, like every other exact name (the contract says so).
# Lower case only for the T ids: `r2` is radare2 and `p1` a parameter, while `t009` can only be the id.
LABELS = re.compile(r"\b(?:[Tt]\d{3}[a-z]?|TC\d+|R\d[a-z]?|P\d{1,2}[a-z]?)\b|\b[Ww]aves?[\s-]\d+\b|\b[Bb]atch(?:es)?\s+B\d\b")
# The list documentation-style.md prints under "Terms"; a test keeps the two equal.
DATING_WORDS = ("currently", "now", "nowadays", "today", "recently", "new", "newly", "old", "existing", "yet",
                "no longer", "so far", "at present")
DATING = re.compile(r"\b(?:" + "|".join(w.replace(" ", r"\s+") for w in DATING_WORDS) + r")\b", re.IGNORECASE)
UNDEFINED_REFERENCE = re.compile(r"(?<![\w\]])\[[^\]\n]+\]\[[^\]\n]*\]")
URL_IN_TEXT = re.compile(r"https?://\S+")

ADOC_LINK = re.compile(r"\b(?:link|xref|image|include)::?([^\s\[]+)\[")
ADOC_XREF = re.compile(r"<<([^>,\n]+)(?:,[^>\n]*)?>>")
ADOC_ID = re.compile(r"\[\[([^\]\n]+)\]\]|\[#([^\]\n,]+)")
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
        ("packets/patterns/03040008/S2C_WARP_WARP_RES-pattern.cpp",
         "0e8e3f859a7d1b2988054ed97be3c83cdc597850ab0856a124cc37a68b63c044"),
    ),
    json_path=f"packets/decrypted_json/{_WARP}.json",
    jq_line='{"packet":{"group":14,"id":3,"subId":2,"source":52,"packetcounter":0,"sourceOk":true,"Error":0,'
            '"Result":0,"WarpPointID":66,"Rim":39109,"paddingSize":7,"fits":true}}',
)


PACKET_IDS = "docs/reference/packet-ids.md"
PATTERNS = "packets/patterns/03040008"
JSON_TREE = "packets/decrypted_json"
TABLE_HEADING = "## The table"
ROW = re.compile(r"^\| (?P<id>\d+\.\d+\.\d+) \| `(?P<name>\w+)`(?: \(was [^|]*\))? \| (?P<report>[^|]*) \| (?P<status>.*) \|$")
FIT = re.compile(r"^(?:(\d+)/(\d+) fit|no capture)")
RECOUNT = re.compile(r"^Fit counts .*$", re.MULTILINE)
PATTERN_ID = re.compile(r"^// packet-id: (\S+)", re.MULTILINE)
PATTERN_SELECT = re.compile(r"^// packet-select: (\S+)", re.MULTILINE)
PATTERN_EVIDENCE = re.compile(r"^// Evidence: (\S+)", re.MULTILINE)
# Every report tag that carries marks; the patterns hold T003, T004, T005 and T014b (`T007 from T006 F2` is provenance).
PATTERN_MARK = re.compile(r"\b(T\d{3}[a-z]?) (V|I|G|open)\b")
ROW_MARKS = re.compile(r"\b(T\d{3}[a-z]?) marks: ([^;)]*)")
MARK_LIST = re.compile(r"(?:V|I|G|open) \d+(?:, (?:V|I|G|open) \d+)*")
REPORT_LABEL = re.compile(r"(?:\d{3} )?[A-Z]+\d+[a-z]*")
LABEL_ROW = re.compile(r"^\| (`[^|]*`) \| (`[^|]*`) \|")
JSON_ID = re.compile(r"\.(\d+)_(\d+)_(\d+)\.json$")


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

    def on_disk(self, path, directory=False):
        target = self.root / path
        return target.is_dir() if directory else target.is_file() or target.is_dir()

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


class HtmlScan(HTMLParser):
    """The href and src targets and the text of a piece of HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.text = [], ""

    def handle_starttag(self, tag, attrs):
        self.links += [value for name, value in attrs if name in ("href", "src") and value]

    def handle_data(self, data):
        self.text += data

    @classmethod
    def of(cls, content):
        scan = cls()
        scan.feed(content)
        scan.close()
        return scan


class Page:
    """A Markdown file parsed once."""

    parser = None

    def __init__(self, root, path):
        self.path = path
        self.text = (Path(root) / path).read_text(encoding="utf-8")
        if Page.parser is None:
            Page.parser = MarkdownIt("commonmark").enable("table")
            Page.parser.validateLink = lambda url: True  # `file:` must stay a link, for check_link to refuse
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

    def html(self):
        """(line, scanned HTML) of each HTML block and inline tag."""
        for token in self.tokens:
            if token.type == "html_block":
                yield (token.map[0] if token.map else 0) + 1, HtmlScan.of(token.content)
        for line, child in self.inline():
            if child.type == "html_inline":
                yield line, HtmlScan.of(child.content)

    def links(self):
        for line, child in self.inline():
            if child.type == "link_open":
                yield line, child.attrs.get("href", "")
            elif child.type == "image":
                yield line, child.attrs.get("src", "")
        for line, scan in self.html():
            for href in scan.links:
                yield line, href

    def undefined_references(self):
        """`[x][nope]` with no definition renders as its own text."""
        for line, child in self.inline():
            if child.type == "text":
                for match in UNDEFINED_REFERENCE.finditer(child.content):
                    yield line, match.group(0)

    def prose(self):
        """(first line, text) of each block's words: line breaks kept as newlines, so a phrase split over two lines
        still matches, and a code span as NUL, so it joins nothing."""
        for token in self.tokens:
            if token.type != "inline":
                continue
            parts = []
            for child in token.children or ():
                if child.type in ("softbreak", "hardbreak"):
                    parts.append("\n")
                elif child.type in ("text", "image"):  # an image's content is its alt text
                    parts.append(child.content)
                elif child.type == "code_inline":
                    parts.append("\0")
            yield (token.map[0] if token.map else 0) + 1, "".join(parts)
        for line, scan in self.html():
            if scan.text.strip():
                yield line, scan.text

    def fence_lines(self):
        """(line, text) of each line of a fence."""
        for token in self.tokens:
            if token.type == "fence":
                for number, text in enumerate(token.content.splitlines(), (token.map[0] if token.map else 0) + 2):
                    yield number, text

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
    if parts.scheme in EXTERNAL_SCHEMES and (parts.netloc or parts.scheme == "mailto"):
        return None
    anchor = unquote(parts.fragment)
    if parts.scheme or parts.netloc:
        return "/", anchor  # `file:`, `D:/`, `//host`: not relative, and not a place on the web
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
        elif target == "/":
            hint = " (not relative: only http, https and mailto count as external)"
        yield Finding("link", path, line, f"{href} resolves to {target}, not in the git index{hint}")
        return
    if target is not None and not tree.on_disk(target):
        yield Finding("link", path, line, f"{href} resolves to {target}, in the git index but deleted from disk")
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


def word_path(word):
    """(repository path, wants a directory, relative spelling) that a word names, or None. The word may start `./` or
    `../`; its top directory counts in any case, so that `Tools/x` is a finding and not skipped."""
    word = word.strip("\"'(").rstrip(",.;:)\"'")
    core = re.sub(r"^(?:\.\.?/)+", "", word)
    if "/" not in core or core.split("/", 1)[0].lower() not in TOP_DIRECTORIES:
        return None
    if any(c in word for c in "*?[]{}<>$…|\\=") or "..." in word:
        return None
    core = re.sub(r":\d+(-\d+)?$", "", core).split("#")[0]
    return posixpath.normpath(core), core.endswith("/"), word if word != core else None


def span_targets(span):
    return [found for found in map(word_path, span.split()) if found]


def span_path(span):
    """The first repository path a code span names, or None."""
    targets = span_targets(span)
    return targets[0][0] if targets else None


def path_exists(tree, target, directory):
    if directory:
        return (target in tree.dirs and tree.on_disk(target, directory=True)) or (
            tree.exists_local(target) and tree.on_disk(target, directory=True))
    return ((target in tree.files or target in tree.dirs) and tree.on_disk(target)) or tree.exists_local(target)


def check_path_word(tree, path, line, text, found):
    target, directory, relative = found
    if path_exists(tree, target, directory):
        return
    if relative and path_exists(tree, posixpath.normpath(posixpath.join(posixpath.dirname(path), relative)), directory):
        return
    kind = "a directory" if directory else "a path"
    yield Finding("path", path, line, f"`{text}`: {target} is not {kind} in the git index and on disk")


def check_span(tree, path, line, span):
    for word in span.split():
        if ABSOLUTE_REPOSITORY.match(word):
            yield Finding("path", path, line, f"`{span}`: an absolute path of the repository; write {word} from its root")
    for found in span_targets(span):
        yield from check_path_word(tree, path, line, span, found)


def check_fence(tree, path, line, text):
    """The first word of a fence's line: a command, or a listed path. Later words may be output or arguments."""
    words = text.split()
    found = word_path(words[0]) if words else None
    if found:
        yield from check_path_word(tree, path, line, text.strip()[:80], found)


def check_wording(path, line, text):
    """`line` is the first line of `text`, whose newlines count."""
    text = URL_IN_TEXT.sub("", text)
    def at(match):
        return line + text.count("\n", 0, match.start())
    for match in LABELS.finditer(text):
        yield Finding("wording", path, at(match), f"process label {match.group(0)!r}: state the fact, or cite the file in a code span")
    for match in DATING.finditer(text):
        yield Finding("wording", path, at(match), f"dating word {' '.join(match.group(0).split())!r}: give a date or cut it")


def check_opening(page):
    tokens = page.tokens
    if not tokens or tokens[0].type != "heading_open" or tokens[0].tag != "h1":
        yield Finding("opening", page.path, 1, "the page does not start with a # title")
    elif len(tokens) < 4 or tokens[3].type != "paragraph_open":
        line = (tokens[3].map[0] + 1) if len(tokens) > 3 and tokens[3].map else 1
        yield Finding("opening", page.path, line, "no paragraph right after the title (who it is for, what they get, what they need)")


def check_index(root, tree, pages, docs_pages, index=INDEX):
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


def packet_rows(text):
    """(line number, line) of the table under TABLE_HEADING: data rows only."""
    lines = text.split("\n")
    start = lines.index(TABLE_HEADING) if TABLE_HEADING in lines else len(lines)
    for number, line in enumerate(lines[start:], start + 1):
        if line.startswith("|") and not line.startswith(("| Id |", "| ---")):
            yield number, line


def row_marks(status):
    """{tag: {mark: count}} the row states, or None for a tag whose phrase cannot be read. An absent tag states nothing."""
    stated = {}
    for tag, words in ROW_MARKS.findall(status):
        words = words.strip()
        if words.startswith("none"):
            stated[tag] = {}
        elif MARK_LIST.fullmatch(words):
            stated[tag] = {m.group(1): int(m.group(2)) for m in re.finditer(r"\b(V|I|G|open) (\d+)\b", words)}
        else:
            stated[tag] = None
    return stated


def pattern_marks(text):
    counted = {}
    for tag, mark in PATTERN_MARK.findall(text):
        counted.setdefault(tag, Counter())[mark] += 1
    return {tag: dict(marks) for tag, marks in counted.items()}


def report_labels(text):
    """{label: {report paths}} from the table of labels above the packet table."""
    reports = {}
    for line in text.split("\n"):
        if line == TABLE_HEADING:
            break
        row = LABEL_ROW.match(line)
        if row:
            labels, paths = re.findall(r"`([^`]+)`", row.group(1)), re.findall(r"`([^`]+)`", row.group(2))
            for at, label in enumerate(labels):
                reports.setdefault(label, set()).update(paths if len(paths) != len(labels) else [paths[at]])
    return reports


def check_report(reports, name, number, report, text):
    labels = REPORT_LABEL.findall(report)
    if not labels:
        yield Finding("packet-ids", PACKET_IDS, number, f"{name}: the Report column names no report")
        return
    named = set().union(*(reports.get(label, set()) for label in labels))
    evidence = PATTERN_EVIDENCE.search(text)
    if not named:
        yield Finding("packet-ids", PACKET_IDS, number, f"{name}: {report.strip()!r} is not in the table of report labels")
    elif evidence and evidence.group(1).rstrip(".,;") not in named:
        yield Finding("packet-ids", PACKET_IDS, number,
                      f"{name}: the Report column says {report.strip()!r}, the pattern's Evidence says {evidence.group(1)}")


def check_packet_ids(root):
    root = Path(root)
    page = root / PACKET_IDS
    if not page.is_file():
        yield Finding("packet-ids", PACKET_IDS, 1, "the page does not exist")
        return
    seen = set()
    patterns = {}
    for path in sorted((root / PATTERNS).glob("*.cpp")):
        if path.name.endswith("-pattern.cpp"):
            patterns[path.name[:-len("-pattern.cpp")]] = path
        else:
            yield Finding("packet-ids", PACKET_IDS, 1, f"{PATTERNS}/{path.name}: a pattern file is named <name>-pattern.cpp")
    text = page.read_text(encoding="utf-8")
    reports = report_labels(text)
    rows = list(packet_rows(text))
    if rows and not reports:
        yield Finding("packet-ids", PACKET_IDS, 1, "the table of report labels is missing")
    for number, line in rows:
        row = ROW.match(line)
        if not row:
            yield Finding("packet-ids", PACKET_IDS, number, f"not a table row: {line[:80]}")
            continue
        name = row["name"]
        if name in seen:
            yield Finding("packet-ids", PACKET_IDS, number, f"{name} has a second row")
            continue
        seen.add(name)
        if name not in patterns:
            yield Finding("packet-ids", PACKET_IDS, number, f"{name}: no {PATTERNS}/{name}-pattern.cpp")
            continue
        source = patterns[name].read_text(encoding="utf-8")
        declared = PATTERN_ID.search(source)
        if not declared or declared.group(1) != row["id"]:
            yield Finding("packet-ids", PACKET_IDS, number,
                          f"{name}: the row says {row['id']}, the pattern's packet-id says {declared and declared.group(1)}")
        if reports:
            yield from check_report(reports, name, number, row["report"], source)
        counted, stated = pattern_marks(source), row_marks(row["status"])
        for tag in sorted(set(counted) | set(stated)):
            if tag not in stated:
                yield Finding("packet-ids", PACKET_IDS, number, f"{name}: the row states no {tag} marks, the pattern has {counted[tag]}")
            elif stated[tag] != counted.get(tag, {}):
                yield Finding("packet-ids", PACKET_IDS, number, f"{name}: the row states {tag} marks {stated[tag]}, the pattern has {counted.get(tag, {})}")
    for name in sorted(set(patterns) - seen):
        yield Finding("packet-ids", PACKET_IDS, 1, f"{name}: a pattern with no row")


def fits_by_path(root):
    """{packet id: [(file name, fits)]} of the JSON tree, through rg: it reads each file once, in parallel."""
    def listing(*args):
        run = subprocess.run(["rg", *args, JSON_TREE, "-g", "*.json"], cwd=root, capture_output=True, encoding="utf-8")
        if run.returncode not in (0, 1):
            raise OSError(run.stderr.strip())
        return [line.replace("\\", "/") for line in run.stdout.splitlines()]
    fitting = set(listing("-l", "-F", '"fits": true'))
    tree = {}
    for path in listing("--files"):
        match = JSON_ID.search(path)
        if match:
            tree.setdefault(".".join(match.groups()), []).append((path.rpartition("/")[2], path in fitting))
    return tree


def packet_counts(root, write=False, unwritten=None):
    """(rows, differences). With `write`, the rows and the recount line take the JSON's counts; a difference that has no
    count to replace goes in `unwritten`."""
    unwritten = [] if unwritten is None else unwritten
    root = Path(root)
    page = root / PACKET_IDS
    text = page.read_text(encoding="utf-8")
    tree = fits_by_path(root)
    lines = text.split("\n")
    rows, differences = 0, []
    for number, line in packet_rows(text):
        row = ROW.match(line)
        if not row:
            differences.append(f"{PACKET_IDS}:{number}: not a table row")
            unwritten.append(differences[-1])
            continue
        rows += 1
        pattern = root / PATTERNS / f"{row['name']}-pattern.cpp"
        select = PATTERN_SELECT.search(pattern.read_text(encoding="utf-8")) if pattern.is_file() else None
        files = tree.get(row["id"], ())
        if select:
            files = [f for f in files if f"_{select.group(1)}_" in f[0]]
        total, fit = len(files), sum(1 for f in files if f[1])
        wanted = f"{fit}/{total} fit" if total else "no capture"
        fit_match = FIT.match(row["status"])
        stated = fit_match.group(0) if fit_match else None
        if stated != wanted:
            differences.append(f"{PACKET_IDS}:{number}: {row['id']} {row['name']}: table {stated}, JSON {wanted}")
            if write and stated:
                lines[number - 1] = line.replace(f"| {stated}", f"| {wanted}", 1)
            else:
                unwritten.append(differences[-1])
    if write:
        out = RECOUNT.sub(f"Fit counts recounted on {datetime.date.today().isoformat()} with `tools/docs_check.py --packet-counts`.",
                          "\n".join(lines), count=1)
        page.write_bytes(out.encode("utf-8"))
    return rows, differences


def run_packet_counts(root, write):
    root = Path(root)
    if shutil.which("rg") is None:
        print("docs_check --packet-counts: not run (rg is not on PATH)")
        return 3
    if not (root / JSON_TREE).is_dir() or not (root / PACKET_IDS).is_file():
        print(f"docs_check --packet-counts: not run ({JSON_TREE} or {PACKET_IDS} missing)")
        return 3
    unwritten = []
    rows, differences = packet_counts(root, write, unwritten)
    for difference in differences:
        print(difference)
    written = f" ({len(differences) - len(unwritten)} written, {len(unwritten)} not)" if write else ""
    print(f"docs_check --packet-counts: {rows} rows, {len(differences)} differences{written}")
    return 1 if unwritten else 0


def check_adoc(root, tree, pages, path):
    raw = (Path(root) / path).read_text(encoding="utf-8")
    text = ADOC_FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), raw)
    ids = {a or b for a, b in ADOC_ID.findall(text)}
    ids |= {"_" + re.sub(r"\W+", "_", title.strip().lower()).strip("_") for title in ADOC_HEADING.findall(text)}
    links_index = False
    for number, line in enumerate(text.splitlines(), 1):
        for href in ADOC_LINK.findall(line):
            if "{" in href:
                continue  # an attribute: its value is not here
            split = split_link(path, href)
            links_index = links_index or (split is not None and split[0] == INDEX)
            yield from check_link(root, tree, pages, path, number, href)
        for target in ADOC_XREF.findall(line):
            if "#" in target or "/" in target or "." in target:
                yield from check_link(root, tree, pages, path, number, target)
            elif target not in ids:
                yield Finding("anchor", path, number, f"<<{target}>>: no such id in {path}")
        for span in ADOC_SPAN.findall(line):
            yield from check_span(tree, path, number, span)
    if path == README:
        if not links_index:
            yield Finding("link", path, 1, f"{README} does not link {INDEX}")
        words = ADOC_LINK.sub("[", ADOC_XREF.sub("", ADOC_SPAN.sub("\0", text)))
        yield from check_wording(path, 1, words)


def table_row_lines(page):
    """The lines of the packet id table: its rows move intact, so their report labels and notes are data, not prose."""
    if page.path != PACKET_IDS:
        return set()
    return {number for number, _line in packet_rows(page.text)}


def run(root=REPO, short_readmes=SHORT_READMES, tutorial=TUTORIAL,
        adoc=("readme.adoc", "binaries/PS4_02020005/elf-dumps/README.adoc")):
    """(findings, summary counts). `adoc` and the READMEs that do not exist are findings, not skips."""
    root = Path(root)
    tree = Tree(root)
    findings = []
    docs_pages = {f for f in tree.files if f.startswith("docs/") and f.endswith(".md") and (root / f).is_file()}
    for path in sorted(f for f in tree.files if f.lower().startswith("docs/")):
        if not path.startswith("docs/") or (PAGE_EXTENSION.search(path) and not path.endswith(".md")):
            findings.append(Finding("index", path, 1, "a page under docs/ is spelled docs/<...>.md, in this case"))
        if not (root / path).is_file():
            findings.append(Finding("link", path, 1, "in the git index but deleted from disk"))
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
            counts["paths"] += len(span_targets(span))
            findings.extend(check_span(tree, path, line, span))
        for line, text in page.undefined_references():
            findings.append(Finding("link", path, line, f"{text}: no such reference is defined"))
        for line, text in page.fence_lines():
            findings.extend(check_fence(tree, path, line, text))
        rows = table_row_lines(page)
        for line, text in page.prose():
            findings.extend(f for f in check_wording(path, line, text) if f.line not in rows)
    findings.extend(check_index(root, tree, pages, docs_pages))
    findings.extend(check_tutorial(root, tutorial))
    findings.extend(check_packet_ids(root))
    for path in adoc:
        if (root / path).is_file():
            findings.extend(check_adoc(root, tree, pages, path))
        else:
            findings.append(Finding("link", path, 1, "it does not exist"))
    return findings, counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(REPO))
    parser.add_argument("--packet-counts", action="store_true", help="compare the n/m fit of the packet id table with the JSON tree")
    parser.add_argument("--write", action="store_true", help="with --packet-counts: correct the rows and the recount date")
    args = parser.parse_args(argv)
    if args.write and not args.packet_counts:
        parser.error("--write needs --packet-counts")
    if args.packet_counts:
        return run_packet_counts(args.root, args.write)
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
