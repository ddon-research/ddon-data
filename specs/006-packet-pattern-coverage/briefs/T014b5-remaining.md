006 T014b5: continue T014b, name unknown fields from PC consumers and binary hints (evidence)

Objective (build 03040008, seed PS4 02020005; spec § "Naming unknown fields by inference", bases 1
and 3): for the `unk_*` fields of the PS4-matched packet patterns, settle names from PC code, and
confirm or reject the value-correlation candidates of `specs/006-packet-pattern-coverage/research/T014a-value-correlation.{md,tsv}`.

Continuation: T014b part 1 (3ea5fa4399, `research/T014b-consumer-property-names.{md,tsv}`) settled 24
of 244 distinct fields and found no property tables naming packet data (read its method and that
finding; do not redo it). This part covers the open rows of: every open row not in T014b4's scope (Shop, Pawn, Craft, Mandragora, Character, Instance, EntryBoard, Dispel, Stage, Item, Gacha and the remaining single patterns). Run after T014b4; start with `include/Shop.hexpat`. Then also every row any part marked "not traced
within the budget" (36 rows, 19 fields from T014b4: GP lineup and buy request, STAMP, nNetMsg,
ContentsPlay*, JoinLobby lists; start with `CDataQuestJoinLobbyUnkOrderList.unk_u32`, element +384,
from the consumer of the cQuestSvNotJoinLobbyQuestInfo notice). "Not traced within the budget" is
not a valid open reason in this part; where a handler or getter is not a function in the database,
read it instruction by instruction or find its caller by xref to the data, as earlier parts did.
T014b3 (201ad9a587) saved the PC property table `research/pc-property-names.tsv` (7,347 rows: every
`MtPropertyList::insert` call; function VA, owner vtable, name, type, offset) and then hit its
200-turn limit without writing any row. Reuse that table; do not re-extract it. Work economically:
one `execute_python` script per struct or include that looks up all its fields' readers, stores and
property matches at once (not one call per lookup), and write the TSV rows and a short md note after
each include, so progress survives a stop. Stay under 170 tool calls; if the scope does not fit, end `cut short:` with the next field
after writing the rows done.

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
`bash research/ida/private-copy.sh <pc|ps4> t014b5`.
Libraries: ida-mcp `execute_python`.
Done: every row in scope settled or open with its reason; the md section with counts (V / I / open). Final message: report path + at most 15 lines. Large: if
your context passes 300k tokens, write what is settled, end `cut short:` with the next field.
Stop: budget 240 min of work time; finish the scope.
Base: the head when you start.
