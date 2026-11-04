# Packet evidence marks

What the marks in the comments of the packet patterns of client 03040008 say, in which forms they appear and what rules a value basis follows, for a reader weighing a decoded field. The [glossary](glossary.md#evidence-marks) defines the marks in brief; [Name an unknown field](../how-to/name-an-unknown-field.md) gives the steps to earn one. A label in a code span names a report: [the key](packet-ids.md#report-labels).

## The marks

| Mark | Meaning |
| --- | --- |
| `V` | Read in IDA: the PC code decides. A field name is code-backed. |
| `I (<basis>)` | Inferred, with its basis stated. |
| `G (<basis>)` | Guess: a server lead alone, the capture shape alone, or a name from context. A `G` may name a field. `G (lead)` is a server-only name. |
| `open` | Rejected or unsettled: the field keeps `unk_*`, with any leads in the comment. |

A field name is code-backed (`V`), inferred and marked (`I`) with its basis, guessed and marked (`G`), or `unk_*`.

- A field whose role is known but whose name is not keeps `unk_*`, and the comment gives the role.
- A Season 3 field with no PS4 counterpart is labelled that way.
- Outside the `G (lead)` form, a server name alone never becomes a field or type name, not even as the suffix of `unk_` (`unk_u32x5`, `unk_List_0`, `CDataPawnInfo_unk_0`, never `unk_TrainingProfile`). It goes in a `server: <name> (lead)` comment.

## Comment forms

| Where | Form |
| --- | --- |
| Structure comment | names the PC reader or writer VA (PC 03040008 database, image base 0x400000) and the PS4 02020005 DWARF type, and carries a mark |
| A field named in the consumer sweep | `// T014b <mark>: <basis>` |
| A field of the later reports | `// T003 <mark>: <basis>`, `// T004 <mark>: <basis>` or `// T005 <mark>: <basis>`, with `<mark>` one of `V`, `I (<basis>)`, `G (<basis>)` or `open` |
| An open field | `// T014b open (<reason>), kept unk: ...`, for example `open (never read by the client)`, `open (no reader found)`, `open (value only)` |
| A server lead | `server: <name> (lead)` |

The `T014b` marks are the verdicts of `specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.tsv`, for example `V (consumer)`, `V (consumer); I (name; lead agrees)`, `I (consumer, member order)` and `V (role)`.

- `V (role); I (name)` splits the data flow from the name: the code role is read in IDA and the name is inferred from it.
- `(...)` ends a basis shortened in the comment. The row of that TSV (struct, field, packet) holds it in full.
- Where a report and the patterns plus that TSV differ, the patterns and the TSV are authoritative.

## Value bases

The rule for a mark that rests on values seen in captures; [Value bases](../explanation/packet-decoding-method.md#value-bases) gives the reasons. `specs/008-remaining-packets/research/t007/` holds the counts and the rewrite that applied it (`marks.py`, `marks-before.tsv`, `mark-changes.tsv`); `specs/008-remaining-packets/research/T006-adversarial.md` holds the review behind it.

- **Distinct counts.** A value basis, `I (value, <n> distinct: ...)`, counts distinct values, not captures. Repeated captures of one value are one observation, and a headline like "294/294" may be one list repeated in every capture; the comment says so.
- **The chance rule.** Where the basis is "the value is an item id" (`base/etc/itemlist.ipa.json`) or a stage id (`base/scr/stage_list.slt.json`), it also gives the chance that every distinct value would be such an id by luck: the table's density over the observed range to the power of the distinct count (`chance 0.21`). The item table fills 0.83 of 1..25768 and 0.92-1.00 of the ranges the captures use.
- **When it is only a guess.** A value-only basis with 3 or fewer distinct values, or with a chance above 0.05, is `G (lead; value consistent: <n> distinct; ...)`, or `G (context; ...)` without a server name. It is not `I`.
- **When it keeps `I`.** A mark keeps `I` when an independent structural basis comes first (`same structure`, `same reader`, `width parallel`), or when a stage id also matches the stage name the packet carries.

## Evidence rules of the patterns

[Evidence model](../explanation/evidence-model.md) gives the reasons.

- PC code comes first: the PC 03040008 reader (S2C) or writer (C2S) decides the layout. Captures confirm a layout; they do not prove it.
- PS4 02020005 is matched to PC by code (handler and reader structure, strings), never by packet number: PS4 packet numbers do not identify PC packets.
- The PS4 recompilation C++ is the baseline wherever it has a ReadPacket or WritePacket body. For the 36 patterns of the `P11a` and `P11b` reports it has none (stubs or no body, `R2`), so only its class layouts were compared.
- The server's C# (Arrowgene) is a lead only. Its names appear as `server: <name> (lead)`.
- Enums come from PS4 DWARF only. A value with no DWARF name is `UNK_<value>`.
- Every inferred position or name is marked, or stays `unk_*`.
