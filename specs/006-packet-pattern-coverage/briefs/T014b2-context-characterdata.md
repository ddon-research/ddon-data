006 T014b2: continue T014b, name unknown fields from PC consumers and binary hints (evidence)

Objective (build 03040008, seed PS4 02020005; spec § "Naming unknown fields by inference", bases 1
and 3): for the `unk_*` fields of the PS4-matched packet patterns, settle names from PC code, and
confirm or reject the value-correlation candidates of `specs/006-packet-pattern-coverage/research/T014a-value-correlation.{md,tsv}`.

Continuation: T014b part 1 (3ea5fa4399, `research/T014b-consumer-property-names.{md,tsv}`) settled 24
of 244 distinct fields and found no property tables naming packet data (read its method and that
finding; do not redo it). This part covers the open rows of: `include/Context.hexpat` and `include/CharacterData.hexpat`. Start with `CDataContextEquipData_unk_0.unk_u16_0` (PC reader 0x765ba0, copied by 0x880210), where part 1 stopped.
Update those rows of the TSV in place (proposed name, mark, basis, VAs) and append a dated section
to the md for this part; do not touch other rows. A row stays open only with a concrete reason
(e.g. the value is never read by the client: say which reader discards it).

Order of work inside the scope: first the T014a strong candidates (confirm the meaning by code, or reject), then the
remaining unknowns by how often they occur in captures. Per field:
- From the reader (the report that settled its layout names the PC VA), follow the value to where the
  client stores or uses it: the member offset of the receiving object, the setter, the UI/message call.
- Name it from what the code shows: a PC `createProperty` registration (MtPropertyList name strings)
  or debug/assert/printf/UI string at that member; the PS4 DWARF member at the same storage by the
  same code path (match the PC consumer to its PS4 counterpart by code); a known structure's reader
  reused for it; a DWARF enum for its range.
- Mark V (data flow read in full) or I (consumer / value / hint), with VAs; a server name may only be
  confirmed (`lead agrees`), never be the basis.
Also look first for PC `createProperty` / property-name tables of the classes the packet data lands
in (cQuestTask, cContext*, pawn/character data, …): one table can name many fields at once.

Owns: only the rows named above of `specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.tsv`
and a new section of its `.md`. Never touch patterns, packets/, client/. Private copies:
`bash research/ida/private-copy.sh <pc|ps4> t014b2`.
Libraries: ida-mcp `execute_python`.
Done: every row in scope settled or open with its reason; the md section with counts (V / I / open). Final message: report path + at most 15 lines. Large: if
your context passes 300k tokens, write what is settled, end `cut short:` with the next field.
Stop: budget 240 min of work time; finish the scope.
Base: the head when you start.
