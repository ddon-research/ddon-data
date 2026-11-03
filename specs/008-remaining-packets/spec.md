# 008 Remaining packets: decode every captured packet id (Season 3 and unresolved)

**Status: open** (opened 2026-11-03; follows specs 006 and 007)

## Goal

An ImHex pattern for **every** packet id in `packets/decrypted_raw` (client **03040008**) that still has none
(spec 006 left 115: `specs/006-packet-pattern-coverage/research/season3-exclusive.tsv`; recount, TC3 recovered more
raws), and JSON for every capture. Sam, 2026-11-03: "Decode all remaining packets, even if you have to infer and
guess a lot. Consider knowledge uncovered in ddon-extractor's season 3 client dumps and the server's leads while
of course keeping in mind there might be errors in sizes and order and that the names might not be canonical, if
you can derive better names from the context and knowledge built-up from the other decodings go ahead."

## Sources, strongest first

1. **PC 03040008 code** (layouts and handler names): the handler table and the PC's own
   `cSeed*Connection::OnPacket_<GROUP>_<NAME>` strings (spec 007 tier 0: names Season 3 handlers too); readers'
   codec call trees with widths in `research/03040008/ida-transfer/dumps/pc-ida.jsonl` (v6); senders found by their
   `WritePacket` constant key `(g,id,sub)`; the annotated database
   `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/` (names, prototypes, partial types).
2. **Captures**: every file of an id must fit (body ends within the last 15 bytes, as 006); value correlation with
   known fields in the same session (006 T014a method).
3. **ddon-extractor Season 3 client data** (`client/03040008/` JSON): ids and enums that values match (item, quest,
   stage, NPC, job, ...), and resource layouts of shared structures.
4. **PS4 02020005** (DWARF) for structures Season 3 kept; the recompilation C++ for argument order.
5. **Server leads** (Arrowgene `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline`, `PacketId.cs`, `Entity/` structures):
   names and field order as candidates; sizes and order may be wrong.

## Marks (extends the 006 rule; Sam 2026-11-03 allows inference and guesses)

Every field carries one: `V` (read in PC code), `I (<basis>)` (inferred from code shape, capture fit plus value
correlation, extractor data, PS4 structure on the same path), `G (<basis>)` (guess: a server lead alone, capture
shape alone, or a name from context). A server name may now become the field name, marked `G (lead)` unless a
stronger basis agrees (`I (<basis>; lead agrees)`); names that later decodings contradict are corrected. A layout
the PC reader proves is `V` even when its field names are guesses. Packet names: the PC string (V) where the
handler has one; else the server name `G (lead)` or a name from context.

## Evidence rules

- PC code decides Season 3 layouts where a reader/writer exists; captures must all fit; a check not run is "not run".
- PS4 flat packet numbers never name PC packets.
- Verify by prediction plus stratified sample, never per-file diffs over the JSON trees.
- Every package lists its JSON changes for Sam's inspection.

## Deliverables

Patterns and includes in `research/03040008/packets/` (README table extended, mark legend with `G`), JSON in
`packets/decrypted_json/`, per-batch reports in `specs/008-remaining-packets/research/`, and a final list of ids
whose layout stays partly unknown with what would settle it.
