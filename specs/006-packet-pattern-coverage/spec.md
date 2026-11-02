# 006 Packet pattern coverage (every PS4-matched packet in the captures)

**Status: active** (opened 2026-11-01, Sam's request; follows spec 005)

## Goal

An ImHex pattern for every packet id in `packets/decrypted_raw` (client build **03040008**) whose
PC handler, reader or writer matches a PS4 02020005 handler by code, built and verified the way
spec 005 built its 67 patterns (`research/03040008/packets/README.md`). After 005: 575 distinct
ids in the raws, 67 with a pattern, about 508 without (of the 551 uncovered at 2026-11-01:
223 REQ, 225 RES, 103 NTC; 32,733 packets).

Out of scope: Season 3-exclusive handlers (no PS4 counterpart). They are listed with their PC VA,
not patterned; a later spec handles them with context from the new Season 3 client files.

## Order and batching (Sam, 2026-11-01)

1. Triage: per uncovered id, the PC handler VA and whether a PS4 match exists (by code: reader body,
   callers, strings; never by packet number), with its captured count.
2. One batch per packet group as `PacketId.cs` numbers them (grouping only; never layouts): login
   first (C2L/L2C, every direction), then groups by captured count. A batch's packets share data
   classes: one include per group.

## Evidence rules (from 005, binding)

- PC 03040008 code decides Season 3 layouts (headless ida-mcp on private copies).
- PS4 packets are matched by code, never by packet number (flat u16 numbering differs).
- The PS4 recompilation C++ (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`) is the
  PS4 baseline where it has a body: IDA can misread stack-argument order. Disagreements go back to IDA.
- The server's C# (Arrowgene) is a community lead, never evidence. Enums from PS4 DWARF only.
- Verification by prediction + stratified sample, never per-file diffs over the JSON trees.
- Every package lists its JSON changes for Sam's inspection.

## Naming unknown fields by inference (Sam, 2026-11-02)

Deductive naming of `unk_*` fields in the PS4-matched packets is permitted when it states its basis.
Bases, strongest first:

1. **Consumer and property names (PC code).** Trace the field from the reader to where the client
   stores or uses it. A PC `createProperty` registration, debug/assert/printf string or UI message
   at that storage member names it; a store into a member a PS4 DWARF type names, by the same code
   path, names it too. Mark `V` when the data flow is read in full, else `I (consumer)`.
2. **Value correlation (captures).** The field's values match, within the same session or stream,
   the values of a field whose meaning is code-backed (e.g. a `PawnId`, `CharacterId`, `ItemId`,
   `StageId`, `QuestId`, UID, timestamp in a known PS4 structure). Mark `I (value: n/m match <field>
   in <packet>)`; state the counts and rule out coincidence (constants, 0/1, small enums need more).
3. **Other binary hints:** strings or constants near the reader or consumer, the same reader used by
   a known structure, enum ranges from DWARF.
4. **Server leads (Arrowgene):** corroboration only. A server name may become the field name only
   when a basis from 1-3 agrees with it; mark `I (<basis>; lead agrees)`. A lead alone keeps the
   field `unk_*` with the lead in a comment.

## Deliverables

Patterns and includes in `research/03040008/packets/`, JSON in `packets/decrypted_json/`, per-batch
evidence reports in `specs/006-packet-pattern-coverage/research/`, the README table extended, and a
list of the Season 3-exclusive ids for the later spec.
