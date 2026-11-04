# DDON data documentation

This map is for peers who know x86, ELF and DWARF but not this project: it lists every page, by what you want to do. You need nothing first. Start with the tutorial if the repository is unfamiliar; [`readme.adoc`](../readme.adoc) gives the overview, and [`AGENTS.md`](../AGENTS.md) is the guide for coding agents.

## Tutorials: learn by doing

- [Read one packet by hand](tutorials/read-one-packet.md): decode one committed packet of client 03040008 and match its JSON.

## How-to: reach a goal

### Resources

- [Choose a resource target](how-to/choose-a-resource-target.md): list the extensions the extractor lacks and pick one.
- [Decode a resource format](how-to/decode-a-resource-format.md): from a class to a validated ImHex pattern, with rLandInfo as the example.
- [Extract client resources](how-to/extract-client-resources.md): re-extract `client/<build>/` and review the change.
- [Convert textures](how-to/convert-textures.md): extract a client's textures and convert them to PNG.

### Packets

- [Decrypt a capture](how-to/decrypt-a-capture.md): turn a pcapng into session keys and decrypted streams.
- [Re-annotate streams](how-to/reannotate-streams.md): re-run the CLI over known streams, split the dumps, export the raw files.
- [Patch the Arrowgene CLI](how-to/patch-the-arrowgene-cli.md): build the patched CLI those exports need.
- [Export packets to JSON](how-to/export-packets-to-json.md): run a pattern over its raw files and read the summary.
- [Refresh packet statistics](how-to/refresh-packet-statistics.md): regenerate the packet count files.
- [Write a packet pattern](how-to/write-a-packet-pattern.md): go from a packet id to a pattern, its marks, a re-export and a fit count.
- [Name an unknown field](how-to/name-an-unknown-field.md): give an `unk_*` field a name with a stated basis.
- [Verify a regeneration](how-to/verify-a-regeneration.md): check a re-export of many files by a prediction and a stratified sample.
- [Build plbatch](how-to/build-plbatch.md): build the batch engine of the export.
- [Inspect captures in Wireshark](how-to/inspect-captures-in-wireshark.md): load the postdissector and the display filters.

### IDA and binaries

- [Query an IDA database read-only](how-to/query-ida-read-only.md): make a private copy, read it, delete it.
- [Write to an IDA database](how-to/write-to-an-ida-database.md): annotate a database through a headless batch, check the save, keep the undo.
- [Transfer annotations from PS4 to PC](how-to/transfer-annotations-ps4-to-pc.md): repair, extract, match, transfer, apply, verify, undo.
- [Regenerate the ELF dumps](how-to/regenerate-elf-dumps.md): rebuild or verify the static dumps of the PS4 ELF.
- [Run Pharos](how-to/run-pharos.md): run OOAnalyzer on a large executable in Docker.

### Client executables

- [Apply a client patch](how-to/apply-a-client-patch.md): apply one `.r2` layer to a copy and check its hash.
- [Add a client patch layer](how-to/add-a-client-patch-layer.md): record a layer with its hash chain.
- [Triage a client crash](how-to/triage-a-client-crash.md): capture, classify and record a crash; what to try when a hook writes `.text`.

### This repository

- [Run the gate](how-to/run-the-gate.md): run `tools/check.sh` and read its lines.
- [Write documentation](how-to/write-documentation.md): change a page and pass its check.

## Reference: look something up

### The repository

- [Repository layout](reference/repository-layout.md): every top path, what it holds, who produces it and who reads it from outside.
- [Inputs and builds](reference/inputs-and-builds.md): builds, clients, IDA databases, the PS4 ELF, captures and videos.
- [Status](reference/status.md): the dated counts, and what was not run.
- [Glossary](reference/glossary.md): the terms pages share, the evidence marks among them.
- [Conventions](reference/conventions.md): naming and file formats.
- [Tools and shell](reference/tools-and-shell.md): the tools a human needs, with versions, and the shell's rules in brief.
- [Gate and hooks](reference/gate-and-hooks.md): each section of the gate and what each hook refuses.
- [Documentation writing contract](reference/documentation-style.md): the rules every page follows.

### Packets

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

### Binaries and client

- [IDA transfer tools](reference/ida-transfer-tools.md): the transfer's scripts, flags, extractor records, manifest columns, rules and published results.
- [Client patches](reference/client-patches.md): the hash chain, lineage, file offsets and `.r2` encoding of the PC executables.
- [Protection inventory](reference/protection-inventory.md): the mechanisms in the PC dumps, their sites and their state per executable.
- [ELF dumps](reference/elf-dumps.md): provenance, storage, verification and two file formats of the PS4 dump set.
- [Structure of the PS4 ELF](reference/ps4-elf-structure.md): what is unusual about `DDOORBIS.elf`, section by section.

### Game knowledge

- [Quest flag sources](reference/quest-flag-sources.md): where each flag command of a quest lives in client 03040008.
- [Community resources](reference/community-resources.md): archived pages, wikis, spreadsheets, videos, repositories and wiki backups.

## Explanation: understand why

- [Evidence model](explanation/evidence-model.md): why authority goes by fact type and the PC decides Season 3 layouts.
- [Wire protocol](explanation/wire-protocol.md): transport, keys, framing, nNetMsg and why the RES guard exists.
- [Packet decoding method](explanation/packet-decoding-method.md): reader first, what a fit proves, value bases, PS4 numbers, stack arguments.
- [Two packet decodings](explanation/two-packet-decodings.md): the annotated dumps against the JSON, and who decides what.
- [plbatch design](explanation/plbatch-design.md): why a batch driver, why its pin, what it costs per file.
- [IDA transfer method](explanation/ida-transfer-method.md): why pairs are proved by code shape, what each gate prevents, what the results mean.
- [Client lineage and protections](explanation/client-lineage-and-protections.md): what the PC executables are, what the layers do, why a code patch crashes the client.
- [RNG race](explanation/rng-race.md): why captures from long-running clients do not decrypt, and what is open.
- [PS4 ELF dump choices](explanation/ps4-elf.md): why inlined chains take one process per address, and why IDA only corroborates.

## Other work

These keep their own documents:

- [`ddon-flags`](../research/03040008/flags/README.md): the quest and layout flag investigation.
- `ddon-knowledge-graph`, in `research/knowledge-graph/README.md`: the provenance-bound evidence graph.
- [External references](../research/external-references.md): the outside repositories and documents the research relies on.
