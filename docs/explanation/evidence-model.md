# Evidence model

Why this repository decides who is right by the kind of fact and not by the tool that reported it, for a reader weighing a layout or a name or about to add one. The rules themselves are in `AGENTS.md`, the constitution `.specify/memory/constitution.md` and, for packets, [Packet evidence marks](../reference/packet-marks.md#evidence-rules-of-the-patterns). This page gives their reasons.

## Observations and conclusions

An address, a layout or a packet's bytes is an observation: it belongs to one client build and one producer, and it does not change. A statement about what a field means is a conclusion, which may well change. Keeping the two apart is what lets a conclusion be revised without damaging the evidence under it, so an observation is never overwritten by an inference, and a conclusion cites what it rests on and says when it is only inferred. The [marks](../reference/glossary.md#evidence-marks) `V`, `I` and `G` are this distinction applied to one field at a time.

## Authority goes by fact type

No source is good at everything, and each has a kind of fact it cannot get wrong by construction.

- **DWARF and ELF decide declared structure:** the PS4 02020005 symbols state class members as compiled.
- **Pinned disassembly decides what an instruction does:** it is the program, not a reconstruction of it.
- **Decrypted traffic decides wire bytes:** what was sent is what was captured.
- **Extractor JSON corroborates a layout.** It is written by a tool that fits resources, so it supports a layout and does not prove one.

Each is weak outside its kind. DWARF says nothing about the bytes a Season 3 PC client reads; a capture shows the bytes and not what they mean; a decompiler's pseudocode is a reconstruction whatever its source. So IDA, Ghidra and the reconstructors stay separate observations, cross-checked. Missing decompiler output is a gap in coverage and never evidence that something is absent.

A peer would propose a single merged database with one answer per fact. It reads more easily, but merging discards which source said what. When two sources later disagree, that disagreement is the finding, and it can only be seen while both survive.

## The PC decides Season 3 layouts

The packets here are those of the PC client 03040008, so its readers and writers are the format: a field the PC reader does not consume is not part of what the client understands. The PS4 02020005 build has the symbols but is older, and Season 3 changed widths and added fields. A layout from PS4 stands on the PC only once it is checked there, per format.

A peer would start from PS4 and adjust, since that is where the names are. That is how names are found, and it is why a PS4 structure on the same code path is good evidence for a name. It is not how a width is settled.

PS4 still earns its place by code. A PC function is matched to a PS4 one through what the code does (its callers, strings, the data it reads), and then its symbols apply. Packet numbers do not do that matching, for the reasons on [Packet decoding method](packet-decoding-method.md#why-ps4-numbers-never-name-pc-packets).

## Server names are leads

The server emulator (Arrowgene) is handwritten by people who played against the client, and that makes it valuable and unreliable in distinct ways. Its names often come from behaviour seen in play, which no binary states. Its layouts need only be good enough for the client to accept them, and a wrong order of two same-width fields, or a field it never reads, survives that test. So a server name is a candidate, marked as such, and a server layout never settles a width or an order. [Two packet decodings](two-packet-decodings.md) works this out on real packets.

The stricter alternative, ignoring the server, would leave many Season 3 fields with no name at all. The looser one, trusting it, would put errors in sizes and order into the patterns. The marks allow the middle: a `G (lead)` field carries the server's name and says so.

## A check that did not run

"Not run" is a result. A report that says a check passed when it was skipped costs a later reader more than a missing check does, since nobody goes back to verify what is written as verified. So every check is stated with its command, input identity and counts, and a check not run is named as not run, as on [Status](../reference/status.md#not-run). The same honesty applies to the fit flag: the export reports it for every packet, and it is still weak evidence.

## Limits

The model does not make a conclusion true. A `V` means the code was read, and a reading can be wrong: review finds such errors, which is why marks are revised and never treated as settled. It also costs effort: many fields sit at `G` or `unk_*`, because writing down what is not known takes the place of a plausible name.
