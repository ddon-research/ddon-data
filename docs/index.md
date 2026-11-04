# DDON data documentation

The map of this repository's documentation, for peers who know x86, ELF and DWARF but not this project: every page, by what you want to do. Start with the tutorial if the repository is unfamiliar; `readme.adoc` gives the overview. `AGENTS.md` is the canonical guide for coding agents.

## Tutorials: learn by doing

- [Read one packet by hand](tutorials/read-one-packet.md): decode one committed packet of client 03040008 and match its JSON.

## How-to: reach a goal

- [Run the gate](how-to/run-the-gate.md): run `tools/check.sh` and read its lines.
- [Write documentation](how-to/write-documentation.md): change a page and pass its check.

## Reference: look something up

- [Documentation writing contract](reference/documentation-style.md): the rules every page follows.
- [Glossary](reference/glossary.md): the terms pages share, the evidence marks among them.
- [Status](reference/status.md): the dated counts, and what was not run.

## Other work

These projects keep their own documents:

- [`ddon-flags`](../research/03040008/flags/README.md): the quest and layout flag investigation.
- `ddon-knowledge-graph`, in `research/knowledge-graph/README.md`: the provenance-bound evidence graph.
