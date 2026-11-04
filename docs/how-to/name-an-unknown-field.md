# Name an unknown field

This page is for anyone who wants to replace an `unk_*` field of a packet pattern of client 03040008 with a name that states its basis. You collect value candidates, pick the strongest basis, write the mark and re-export. You need to know the [marks](../reference/packet-marks.md), and `packets/decrypted_json/` on disk.

## Choose the basis

Take the strongest that holds, in this order:

1. **Consumer and property names (PC code).** Trace the field from the reader to where the client stores or uses it, until a `createProperty` name, a debug, assert or UI string, or a PS4 DWARF member on the same code path names it. The mark is `V` when the data flow was read in full, else `I (consumer)`.
2. **Value correlation (captures).** Its values match, in the same session or stream, a code-backed field (`PawnId`, `CharacterId`, `ItemId`, `StageId`, `QuestId`, UID, timestamp). The mark is `I (value: n/m match <field> in <packet>)`, with the counts and the coincidence ruled out. Count distinct values and apply [the chance rule](../reference/packet-marks.md#value-bases).
3. **Other binary hints.** Strings or constants near the reader or consumer, the same reader used by a known structure, DWARF enum ranges. The mark is `I (binary hint)`.
4. **Server leads (Arrowgene).** Corroboration only. A server name becomes the field name only when a basis from 1-3 agrees: `I (<basis>; lead agrees)`. A lead alone keeps `unk_*` with the lead in a comment, or is at most `G (lead)`.

## Find value candidates

`packets/tools/unk_correlate.py` compares, per session, the values of every unknown leaf field in the JSON with the value sets of the named fields of that session. It names nothing: its output is a list of candidates with counts. It uses the standard library only. From the repository root:

```sh
python -X utf8 -I packets/tools/unk_correlate.py --tsv <out>.tsv --md <out>.md
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--patterns` | `packets/patterns/03040008` | the patterns that name the packets |
| `--json` | `packets/decrypted_json` | the JSON tree |
| `--group` | `capture` | session unit: `capture` (one capture file, all its TCP streams) or `stream` (one TCP stream) |
| `--tsv` | required | one row per unknown (packet, key path) |
| `--md` | none | the Markdown report |

Its output of record is `specs/006-packet-pattern-coverage/research/T014a-value-correlation.tsv`. Integers below 256 in magnitude, sentinels and strings under 3 characters count as uninformative. The tool's tests:

```sh
python -X utf8 -I -m unittest discover -s packets/tools -p "test_*.py" -v
```

## Write the name

1. Rename the field in the pattern or include, and put the mark in the comment above it, in a [form the marks page lists](../reference/packet-marks.md#comment-forms).
2. If the role is known and the name is not, keep `unk_*` and give the role in the comment. If the basis fails, keep `unk_*` with `open (<reason>)`.
3. Re-export every pattern that reaches the structure: [After changing an include](export-packets-to-json.md#after-changing-an-include). Success is that only the renamed key differs in the JSON, with the same values, shapes and fits.
