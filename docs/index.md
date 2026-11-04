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
- [Write a packet pattern](how-to/write-a-packet-pattern.md): go from a packet id to a pattern, its marks, a re-export and a fit count.
- [Name an unknown field](how-to/name-an-unknown-field.md): give an `unk_*` field a name with a stated basis.
- [Verify a regeneration](how-to/verify-a-regeneration.md): check a re-export of many files by a prediction and a stratified sample.
- [Build plbatch](how-to/build-plbatch.md): build the batch engine of the export.
- [Inspect captures in Wireshark](how-to/inspect-captures-in-wireshark.md): load the postdissector and the display filters.
- [Query an IDA database read-only](how-to/query-ida-read-only.md): make a private copy, read it, delete it.
- [Write to an IDA database](how-to/write-to-an-ida-database.md): run a write as a headless batch, check the save, keep the undo.
- [Transfer annotations from PS4 to PC](how-to/transfer-annotations-ps4-to-pc.md): repair, extract, match, transfer, apply, verify, undo.

## Reference: look something up

- [Documentation writing contract](reference/documentation-style.md): the rules every page follows.
- [Glossary](reference/glossary.md): the terms pages share, the evidence marks among them.
- [Status](reference/status.md): the dated counts, and what was not run.
- [Packet wire format](reference/packet-wire-format.md): framing, cipher, header, RES header, lists, strings and padding.
- [Packet handler tables](reference/packet-handler-tables.md): where the PC client keeps handlers, senders and names.
- [Packet ids](reference/packet-ids.md): every packet pattern of client 03040008, its report and its fit.
- [Packet pattern includes](reference/packet-includes.md): the shared pattern files and their users.
- [Packet evidence marks](reference/packet-marks.md): the marks, their comment forms and the value-basis rules.
- [Packet pattern format](reference/packet-pattern-format.md): header lines, JSON shape, exported checks, raw file names.
- [Packet open questions](reference/packet-open-questions.md): what the patterns leave unsettled, by group.
- [imhex-export CLI](reference/imhex-export-cli.md): options, filter forms, environment and summary line of the export.
- [plbatch CLI](reference/plbatch-cli.md): flags, output lines and exit codes of the batch engine.
- [Arrowgene CLI patches](reference/arrowgene-cli-patches.md): what the patched CLI changes, and its build identity.
- [IDA transfer tools](reference/ida-transfer-tools.md): the transfer's scripts, flags, extractor records, manifest columns, rules and published results.

## Explanation: understand why

- [Evidence model](explanation/evidence-model.md): why authority goes by fact type and the PC decides Season 3 layouts.
- [Wire protocol](explanation/wire-protocol.md): transport, keys, framing, nNetMsg and why the RES guard exists.
- [Packet decoding method](explanation/packet-decoding-method.md): reader first, what a fit proves, value bases, PS4 numbers, stack arguments.
- [Two packet decodings](explanation/two-packet-decodings.md): the annotated dumps against the JSON, and who decides what.
- [plbatch design](explanation/plbatch-design.md): why a batch driver, why its pin, what it costs per file.
- [IDA transfer method](explanation/ida-transfer-method.md): why pairs are proved by code shape, what each gate prevents, what the results mean.

## Other work

These projects keep their own documents:

- [`ddon-flags`](../research/03040008/flags/README.md): the quest and layout flag investigation.
- `ddon-knowledge-graph`, in `research/knowledge-graph/README.md`: the provenance-bound evidence graph.
