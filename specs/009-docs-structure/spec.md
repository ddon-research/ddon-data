# 009 Documentation and file structure (Diataxis)

**Status: open** (opened 2026-11-04; follows specs 005-008, whose doc points stayed open)

## Goal

Sam, 2026-11-04: "Go ahead and improve documentation and structuring of files, this was an open point for a few specs
now. Follow Diataxis best practices."

A peer reverse engineer who knows x86 and ELF but not this project's specs can find, in one place, how to do each
workflow, how to look up each fact, and why the evidence model and methods are what they are; and can find each file
by the directory it sits in. Knowledge now buried in specs, chat receipts, version-by-version READMEs and `AGENTS.md`
reaches a page of the right type.

## Target structure

```text
readme.adoc              what this is, the layout in brief, where to go next (short)
docs/
  index.md               the map: every page, by type
  tutorials/             learn by doing one thing guaranteed to work, on a fixed input
  how-to/                reach one goal: steps, decisions, success vs failure
  reference/             look up: tables of paths, fields, marks, ids, hashes, flags, plus the writing contract and glossary
  explanation/           understand why: evidence model, wire protocol, decoding and transfer methods, protections
```

- Markdown under `docs/`; no site build. GitHub renders it; a local link check is the gate.
- A directory holding data or code keeps a short `README` that says what the directory holds, who produces it, and
  links to the pages. It holds no method and no history.
- The writing contract is `docs/reference/documentation-style.md`, adapted from
  `C:/ddon-dwarf-reconstructor-rust/docs/reference/documentation-style.md` (one purpose per page; opening paragraph;
  altitude by page type; facts checked against the source; no history or task ids on pages, no words that date a page;
  a build number on every client fact).

## Rules

- **Nothing is lost by moving it.** A fact cut from a page lands on another page, or stays in the spec it came from
  when it is history. The packets README's per-id rows move intact.
- **Closed specs are records**: never rewritten, so their old paths may go stale. Every live pointer follows a move:
  `AGENTS.md`, `CLAUDE.md`, `.claude/`, `tools/`, scripts, READMEs, and this machine's other repositories, reported
  to Sam where they are not ours to edit here.
- **Paths outside readers use stay put** unless their reader is updated in the same package: `client/03040008`,
  `client/03040008/quest` (DDON-translation), `research/02030004/` (DDOn-Tools), `research/03040008/protections/README.md`
  and `research/external-references.*` (ddon-hook `AGENTS.md`), plus whatever the census finds.
- **Moves use `git mv`** and preserve history; no JSON, raw or `client/` file moves. `client/` and `packets/decrypted_*`
  layout is out of scope.
- **Other work is dirty in this tree** (`research/03040008/flags/**`, `research/knowledge-graph/`, `binaries/PS4_02020005/DDOORBIS.elf.h`,
  `packets/decrypt-annotate-streams.sh`, `research/external-references.jsonl`, `research/external/*`, `patches/2026_10_17_*`,
  `specs/*-1.md`): those files are not moved or edited; a page may describe them and link to them.
- **Facts come from the source**: a page states what the code or data shows at the commit it is written on; a
  disagreement between a spec and the code goes in the report, and the page follows the code.

## Deliverables

`docs/` populated; the short directory READMEs; loose files in their directories; the packets table in its own
reference file (retro finding of 008: every README edit echoed about 29k tokens); a `docs` section in `tools/check.sh`
(local links, every page reachable from `docs/index.md`); `AGENTS.md` shortened to point at the pages for workflows;
an `editor` role for later specs.
