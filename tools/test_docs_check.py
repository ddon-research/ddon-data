"""Tests for docs_check.py:
uv run --offline --no-project --with markdown-it-py==4.2.0 python -X utf8 -m unittest discover -s tools -p test_docs_check.py

Each check has a fixture that fails it; `setUpClass` proves the same tree passes before a test breaks it, so a removed
check fails its test.
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import docs_check  # noqa: E402

JQ_LINE = '{"packet":{"fits":true}}'
RAW = b"\x0e\x00\x03\x02"


def sha(data):
    return hashlib.sha256(data).hexdigest()


TUTORIAL_PAGE = f"""# A tutorial

Who it is for.

| Input | SHA-256 |
| --- | --- |
| `packets/raw/p` | {sha(RAW)} |
| `packets/json/p.json` | {sha(JQ_LINE.encode())} |

```sh
{JQ_LINE}
```
"""

INDEX = """# Map

Every page, by type.

- [A tutorial](tutorials/one.md)
- [A how-to](how-to/two.md)
"""

HOW_TO = """# A how-to

For peers. See the [tutorial](../tutorials/one.md#a-tutorial) and the [section](#steps).

## Steps

Run `tools/run.sh --all`, read `research/notes/`, skip `research/<build>/x.cpp`, `specs/*-1.md` and `git status`.
"""


def git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "core.autocrlf=false", *args], check=True, capture_output=True)


def remove_tree(root):
    for path in Path(root).rglob("*"):
        with contextlib.suppress(OSError):
            os.chmod(path, 0o700)  # git's objects are read-only, which Windows refuses to delete
    shutil.rmtree(root, ignore_errors=True)


class DocsCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = Path(tempfile.mkdtemp(prefix="docs-check-template-"))
        cls.addClassCleanup(remove_tree, cls.template)
        cls.tutorial = docs_check.Tutorial(
            page="docs/tutorials/one.md",
            inputs=(("packets/raw/p", sha(RAW)), ("packets/json/p.json", sha(JQ_LINE.encode()))),
            json_path="packets/json/p.json",
            jq_line=JQ_LINE,
        )
        probe = cls()
        probe.root = cls.template
        git(probe.root, "init", "-q", "--template=")
        git(probe.root, "config", "core.ignorecase", "true")
        probe.write("docs/index.md", INDEX)
        probe.write("docs/tutorials/one.md", TUTORIAL_PAGE)
        probe.write("docs/how-to/two.md", HOW_TO)
        probe.write("research/notes/README.md", "# Notes\n\nWhat this directory holds.\n")
        probe.write("research/Readme.adoc", "= Title\n\n== A section\n")
        probe.write("tools/run.sh", "#!/bin/sh\n")
        probe.write("readme.adoc", "See link:research/Readme.adoc[it] and `tools/run.sh`.\n\n----\n`tools/inafence.sh`\n----\n")
        probe.write_bytes("packets/raw/p", RAW)
        probe.write_bytes("packets/json/p.json", JQ_LINE.encode())
        # docs/ stays untracked: pages must count without a commit.
        git(probe.root, "add", "--", "research", "tools", "readme.adoc", "packets")
        found = probe.findings()
        if found:
            raise AssertionError(f"the fixture must pass before a test breaks it: {found}")

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="docs-check-")) / "repo"
        self.addCleanup(remove_tree, self.root.parent)
        shutil.copytree(self.template, self.root)

    def write(self, path, text):
        self.write_bytes(path, text.encode("utf-8"))

    def write_bytes(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def findings(self, short_readmes=("research/notes/README.md",)):
        found, _counts = docs_check.run(self.root, short_readmes=short_readmes, tutorial=self.tutorial)
        return [str(f) for f in found]

    def assert_finding(self, check, text):
        found = self.findings()
        self.assertTrue(any(f"[{check}]" in f and text in f for f in found), found)

    def assert_page_finding(self, body, check, text):
        self.write("docs/how-to/two.md", f"# A how-to\n\nFor peers.\n\n{body}\n")
        self.assert_finding(check, text)

    # (a) links

    def test_broken_link_fails(self):
        self.assert_page_finding("[x](../missing.md)", "link", "not in the git index")

    def test_case_mismatch_fails_where_the_filesystem_would_pass(self):
        # On a case-insensitive disk research/README.adoc opens; the index holds research/Readme.adoc.
        self.assert_page_finding("[x](../../research/README.adoc)", "link", "case differs")

    def test_file_on_disk_but_not_in_git_fails(self):
        self.write("research/untracked.md", "x\n")
        self.assert_page_finding("[x](../../research/untracked.md)", "link", "not in the git index")

    def test_untracked_page_under_docs_counts(self):
        self.write("docs/how-to/three.md", "# Three\n\nFor peers.\n")
        self.write("docs/index.md", INDEX + "- [Three](how-to/three.md)\n")
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers. See [three](three.md).\n")
        self.assertEqual(self.findings(), [])

    def test_absolute_link_fails(self):
        self.assert_page_finding("[x](/docs/index.md)", "link", "not in the git index")

    def test_directory_link_fails(self):
        self.assert_page_finding("[x](../../research/notes/)", "link", "a directory")

    def test_external_link_is_not_checked(self):
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers. [x](https://example.org/missing#nope).\n")
        self.assertEqual(self.findings(), [])

    def test_short_readme_is_checked(self):
        self.write("research/notes/README.md", "# Notes\n\nWhat. [x](missing.md)\n")
        self.assert_finding("link", "missing.md")

    def test_listed_short_readme_that_does_not_exist_fails(self):
        found = self.findings(short_readmes=("research/none/README.md",))
        self.assertTrue(any("does not exist" in f for f in found), found)

    def test_adoc_link_and_path_fail(self):
        self.write("readme.adoc", "See link:research/readme.adoc[it].\n\nRun `tools/gone.sh`.\n")
        found = self.findings()
        self.assertTrue(any("readme.adoc:1: [link]" in f and "case differs" in f for f in found), found)
        self.assertTrue(any("readme.adoc:3: [path]" in f for f in found), found)

    # (b) anchors

    def test_missing_anchor_fails(self):
        self.assert_page_finding("[x](../tutorials/one.md#no-such-heading)", "anchor", "no heading")

    def test_same_page_anchor_fails(self):
        self.assert_page_finding("[x](#no-such-heading)", "anchor", "no heading")

    def test_anchor_into_a_file_without_headings_fails(self):
        self.assert_page_finding("[x](../../tools/run.sh#L1)", "anchor", "no headings")

    def test_adoc_anchor_resolves(self):
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers. [x](../../research/Readme.adoc#a-section).\n")
        self.assertEqual(self.findings(), [])

    def test_slug_follows_github(self):
        self.assertEqual(docs_check.github_slug("The `fit` rule: what it proves!"), "the-fit-rule-what-it-proves")
        self.assertEqual(docs_check.with_duplicates(["a", "a"]), {"a", "a-1"})

    # (c) index

    def test_orphan_page_fails(self):
        self.write("docs/how-to/orphan.md", "# Orphan\n\nFor peers.\n")
        self.assert_finding("index", "not reachable")

    def test_page_listed_twice_fails(self):
        self.write("docs/index.md", INDEX + "- [Again](how-to/two.md)\n")
        self.assert_finding("index", "lists it 2 times")

    def test_missing_index_fails(self):
        (self.root / "docs/index.md").unlink()
        self.assert_finding("index", "does not exist")

    # (d) code-span paths

    def test_missing_path_in_code_span_fails(self):
        self.assert_page_finding("See `research/nothing/here.md`.", "path", "research/nothing/here.md")

    def test_command_with_a_missing_path_fails(self):
        self.assert_page_finding("Run `tools/gone.sh --all`.", "path", "tools/gone.sh")

    def test_case_mismatch_in_code_span_fails(self):
        self.assert_page_finding("See `research/README.adoc`.", "path", "research/README.adoc")

    def test_globs_placeholders_and_commands_are_skipped(self):
        self.assertEqual(self.findings(), [])
        for span in ("research/<build>/x.cpp", "specs/*-1.md", "git status", "research/03040008/…/x", "nothing/x"):
            self.assertIsNone(docs_check.span_path(span), span)
        self.assertEqual(docs_check.span_path("tools/run.sh:12"), "tools/run.sh")

    def test_ignored_local_path_counts_with_its_exact_case(self):
        self.write(".gitignore", "research/local/\n")
        self.write("research/local/x.txt", "x\n")
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers. See `research/local/x.txt`.\n")
        self.assertEqual(self.findings(), [])
        self.assert_page_finding("See `research/LOCAL/x.txt`.", "path", "research/LOCAL/x.txt")

    def test_other_work_tree_counts_in_a_code_span_but_never_as_a_link(self):
        self.write("research/knowledge-graph/README.md", "x\n")  # untracked, not ignored
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers. See `research/knowledge-graph/README.md`.\n")
        self.assertEqual(self.findings(), [])
        self.assert_page_finding("See `research/KNOWLEDGE-graph/README.md`.", "path", "KNOWLEDGE")
        self.assert_page_finding("[x](../../research/knowledge-graph/README.md)", "link", "not in the git index")

    # (e) wording

    def test_process_labels_fail(self):
        for label in ("T002", "T014a", "TC1", "R2", "R3b", "P11", "wave 2", "batch B5"):
            with self.subTest(label=label):
                self.assertTrue(list(docs_check.check_wording("p", 1, f"As {label} found.")), label)
        self.assert_page_finding("As T002 found.", "wording", "T002")

    def test_dating_words_fail(self):
        for word in docs_check.DATING_WORDS:
            with self.subTest(word=word):
                self.assertTrue(list(docs_check.check_wording("p", 1, f"The tool {word} does this.")), word)

    def test_dating_word_in_heading_and_link_text_fails(self):
        self.write("docs/how-to/two.md", "# The new tool\n\nFor peers.\n")
        self.assert_finding("wording", "new")
        self.assert_page_finding("[the old page](../tutorials/one.md)", "wording", "old")

    def test_code_fences_urls_and_longer_words_pass(self):
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers. Know `T002` and `now`; renew the oldest knowledge, "
                                         "see https://example.org/T002/now.\n\n```text\nT002 new now\n```\n")
        self.assertEqual(self.findings(), [])

    # (f) opening

    def test_no_paragraph_after_title_fails(self):
        self.write("docs/how-to/two.md", "# A how-to\n\n## At once a section\n")
        self.assert_finding("opening", "no paragraph")

    def test_table_after_title_fails(self):
        self.write("docs/how-to/two.md", "# A how-to\n\n| a |\n| --- |\n| b |\n")
        self.assert_finding("opening", "no paragraph")

    def test_no_title_fails(self):
        self.write("docs/how-to/two.md", "For peers.\n")
        self.assert_finding("opening", "title")

    # (g) tutorial

    def test_changed_input_fails(self):
        self.write_bytes("packets/raw/p", RAW + b"\x00")
        self.assert_finding("tutorial", "SHA-256")

    def test_missing_input_fails(self):
        (self.root / "packets/raw/p").unlink()
        self.assert_finding("tutorial", "input missing")

    def test_hash_cut_from_the_page_fails(self):
        self.write("docs/tutorials/one.md", TUTORIAL_PAGE.replace(sha(RAW), "cut"))
        self.assert_finding("tutorial", "does not state")

    def test_jq_line_cut_from_the_page_fails(self):
        self.write("docs/tutorials/one.md", TUTORIAL_PAGE.replace(JQ_LINE, "cut"))
        self.assert_finding("tutorial", "jq line")

    def test_json_that_prints_another_line_fails(self):
        other = json.dumps({"packet": {"fits": False}}, separators=(",", ":")).encode()
        self.write_bytes("packets/json/p.json", other)
        self.tutorial = docs_check.Tutorial(self.tutorial.page, (("packets/raw/p", sha(RAW)),),
                                            self.tutorial.json_path, JQ_LINE)
        self.assert_finding("tutorial", "jq -c prints")

    def test_missing_tutorial_page_fails(self):
        (self.root / "docs/tutorials/one.md").unlink()
        self.write("docs/index.md", "# Map\n\nEvery page.\n\n- [A how-to](how-to/two.md)\n")
        self.write("docs/how-to/two.md", "# A how-to\n\nFor peers.\n")
        self.assert_finding("tutorial", "does not exist")

    # The contract and the code

    def test_contract_prints_the_dating_words_the_code_refuses(self):
        contract = (HERE.parent / "docs/reference/documentation-style.md").read_text(encoding="utf-8")
        for word in docs_check.DATING_WORDS:
            self.assertIn(f"`{word}`", contract)

    def test_main_reports_not_run_without_the_library(self):
        saved = docs_check.MarkdownIt
        docs_check.MarkdownIt = None
        self.addCleanup(setattr, docs_check, "MarkdownIt", saved)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(docs_check.main(["--root", str(self.root)]), 3)
        self.assertIn("not run", out.getvalue())
        self.assertNotIn("passed", out.getvalue())


if __name__ == "__main__":
    unittest.main()
