# Write documentation

This page is for anyone adding or changing a page under `docs/` or a short directory README: you place the text, pass the check and leave the map correct. Read the [writing contract](../reference/documentation-style.md) first. You need `uv`; the check fetches nothing when `markdown-it-py` is in its cache.

## Change a page

1. Decide the type by what the reader wants: learn by doing (tutorial), reach a goal (how-to), look up a fact (reference), understand why (explanation). If the text serves two, split it.
2. Check every fact in the source at the commit you are on. A client fact names its build. A count goes on [Status](../reference/status.md) with its date.
3. Start the page with a `#` title and one paragraph: who it is for, what they get, what they need first.
4. Add one line for the page to [`docs/index.md`](../index.md), under its type. An empty type has no heading.
5. Add a term that two pages use to the [glossary](../reference/glossary.md), and link it on first use.
6. Run the check:

   ```sh
   uv run --offline --no-project --with markdown-it-py==4.2.0 python -X utf8 tools/docs_check.py
   ```

7. Success is the last line with `0 findings` and exit status 0. Exit status 3 means the check did not run. If `uv` reports that it cannot resolve the package offline, drop `--offline` once to fill the cache.

## Add a directory README to the check

A README that follows the contract joins the check through `SHORT_READMES` in `tools/docs_check.py`. Add it there in the change that shortens it.

## Fix a finding

A finding reads `<path>:<line>: [<check>] <message>`.

| Check | It means | Fix |
| --- | --- | --- |
| `link` | the target is not in the git index with this exact spelling, or not on disk; `case differs` means the disk hides the mismatch; only `http`, `https` and `mailto` count as external; a `[x][y]` with no definition; `readme.adoc` missing, or not linking `docs/index.md` | correct the spelling; `git add` a file outside `docs/` before linking it; link a directory's README, not the directory; write links relative |
| `anchor` | the target has no heading with that slug | use GitHub's spelling: lower case, punctuation dropped, spaces as hyphens |
| `index` | the page is missing from `docs/index.md`, or listed twice; a Markdown or adoc file under `docs/` with an extension other than `.md` | list it once; rename it |
| `path` | a word of a code span, or the first word of a fence's line, starts with a top directory (also `./`, `../`) and names no path in this case; a trailing slash names no directory; an absolute spelling of this repository | correct it, write it from the root, write a glob or a `<placeholder>` when it is a shape, or prefix the other repository's name |
| `wording` | a task id, package label or dating word in prose, also split over a line break, in image alt or HTML text, or in `readme.adoc` | state the fact without it; give a date; put an exact name in a code span |
| `opening` | no paragraph right after the title | write it |
| `tutorial` | a pinned input, its hash or the expected `jq` line changed | see below |
| `packet-ids` | a row of [Packet ids](../reference/packet-ids.md) disagrees with its pattern (id, the marks of any tag, the report of its `// Evidence:` line), its Report column is empty or unknown, a pattern has no row, or a pattern file is not `<name>-pattern.cpp` | correct the row by script, not the whole table with an editor; the pattern is the authority |

## Correct the packet fit counts

The fit counts in [Packet ids](../reference/packet-ids.md) come from the JSON tree. After a re-export, this rewrites the differing rows and the date beside the table, and touches nothing else:

```sh
python -X utf8 tools/docs_check.py --packet-counts --write
```

Without `--write` it only lists the differences, and the exit status is 1 when there are any. With `--write` the exit status is 1 when a difference could not be written, a row with no count to replace. The gate's `packet-counts` section runs the form without `--write`.

## Change a tutorial input

A `tutorial` finding means the page and its data disagree, usually after a re-export. Run the tutorial's commands again. Then change the page and the `TUTORIAL` constant in `tools/docs_check.py` together, with the date of the run.

## Change the check

Each check has a failing fixture in `tools/test_docs_check.py`. Run the tests with:

```sh
uv run --offline --no-project --with markdown-it-py==4.2.0 python -X utf8 -m unittest discover -s tools -p test_docs_check.py
```
