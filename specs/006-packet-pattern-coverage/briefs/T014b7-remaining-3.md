006 T014b7: continue T014b, name the last open unknown fields from PC consumers (evidence)

Objective (build 03040008, seed PS4 02020005; spec § "Naming unknown fields by inference", bases 1
and 3): settle, from PC code, every row of `specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.tsv`
still marked open as "consumer not traced" or "not traced within the budget" (60 rows, 57
struct.field pairs after T014b6). Read the md's method and parts 1, 2, 4, 5 and 6 first;
do not redo them.

Scope: Gacha/BoxGacha, Instance REPOP/gathering, Stage attributes, STAMP, nNetMsg, ContentsPlay*,
QuestContents, CDataQuestUnkU32*, GP, and the single-pattern rows (Part 6 lists partial leads). Start
with `CDataGachaSettlementInfo.unk_u32` (element `0x768830`, +36). Also confirm or reject the T014a
candidates (`research/T014a-value-correlation.{md,tsv}`) among these rows.

"Not traced" is not a valid open reason here. Where a handler or getter is not a function in the
database, read it instruction by instruction, or find its registration or caller by a raw byte or
data xref search (T014b5 found the JoinLobby callback that way). A row stays open only with a concrete
reason (e.g. stored but never read: name the store and say no reader exists).

Per field: follow the value from the reader to where the client stores or uses it; name it from a PC
property registration (`research/pc-property-names.tsv`, 7,347 rows: match object + offset), a
debug/assert/UI string at that member, the PS4 DWARF member reached by the same code path, a known
structure's reader, or a DWARF enum. Mark V (data flow read in full) or I (consumer / value / hint),
with VAs; a server name may only be confirmed (`lead agrees`), never be the basis.

Work economically: one `execute_python` script per struct or include for all its lookups. Write rows
with `research/T014b4-upd.py`, one update file per include (`research/T014b7-<include>.json`), and a
short md note (new section "Part 7") after each include, so progress survives a stop. Stay under 170
tool calls; if the scope does not fit, end `cut short:` with the next field after writing the rows done.

Owns: only those TSV rows, the `T014b7-*.json` update files and the md's Part 7. Never touch patterns,
packets/, client/. Private copies: `bash research/ida/private-copy.sh <pc|ps4> t014b7`.
Libraries: ida-mcp `execute_python`.
Done: every row in scope settled or open with its concrete reason; Part 7 with counts (V / I / open).
Final message: report path + at most 15 lines. Past 300k context: write what is settled, end
`cut short:` with the next field.
Stop: budget 240 min of work time; finish the scope.
Base: the head when you start.
