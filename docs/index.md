# DDON data documentation

The map of this repository's documentation, for peers who know x86, ELF and DWARF but not this project: every page, by what you want to do. Start with the tutorial if the repository is unfamiliar; `readme.adoc` gives the overview. `AGENTS.md` is the canonical guide for coding agents.

## Tutorials: learn by doing

- [Read one packet by hand](tutorials/read-one-packet.md): decode one committed packet of client 03040008 and match its JSON.

## How-to: reach a goal

- [Run the gate](how-to/run-the-gate.md): run `tools/check.sh` and read its lines.
- [Write documentation](how-to/write-documentation.md): change a page and pass its check.
- [Decrypt a capture](how-to/decrypt-a-capture.md): turn a pcapng into session keys and decrypted streams.
- [Re-annotate streams](how-to/reannotate-streams.md): re-run the CLI over known streams, split the dumps, export the raw packets.
- [Patch the Arrowgene CLI](how-to/patch-the-arrowgene-cli.md): build the patched CLI those exports need.
- [Export packets to JSON](how-to/export-packets-to-json.md): run a pattern over its raw files and read the summary.
- [Refresh packet statistics](how-to/refresh-packet-statistics.md): regenerate the packet count files.
- [Name an unknown field](how-to/name-an-unknown-field.md): give an `unk_*` field a name with a stated basis.
- [Build plbatch](how-to/build-plbatch.md): build the batch engine of the export.
- [Inspect captures in Wireshark](how-to/inspect-captures-in-wireshark.md): load the postdissector and the display filters.

## Reference: look something up

- [Documentation writing contract](reference/documentation-style.md): the rules every page follows.
- [Glossary](reference/glossary.md): the terms pages share, the evidence marks among them.
- [Status](reference/status.md): the dated counts, and what was not run.
- [Packet ids](reference/packet-ids.md): every packet pattern of client 03040008, its report and its fit.
- [Packet pattern includes](reference/packet-includes.md): the shared pattern files and their users.
- [Packet evidence marks](reference/packet-marks.md): the marks, their comment forms and the value-basis rules.
- [Packet pattern format](reference/packet-pattern-format.md): header lines, JSON shape, exported checks, raw file names.
- [Packet open questions](reference/packet-open-questions.md): what the patterns leave unsettled, by group.
- [imhex-export CLI](reference/imhex-export-cli.md): options, filter forms, environment and summary line of the export.
- [plbatch CLI](reference/plbatch-cli.md): flags, output lines and exit codes of the batch engine.
- [Arrowgene CLI patches](reference/arrowgene-cli-patches.md): what the patched CLI changes, and its build identity.

## Explanation: understand why

- [plbatch design](explanation/plbatch-design.md): why a batch driver, why its pin, what it costs per file.

## Other work

These projects keep their own documents:

- [`ddon-flags`](../research/03040008/flags/README.md): the quest and layout flag investigation.
- `ddon-knowledge-graph`, in `research/knowledge-graph/README.md`: the provenance-bound evidence graph.
