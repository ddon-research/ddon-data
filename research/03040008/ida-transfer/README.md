# ddon-ida-transfer (spec 007)

Fact extractors for the PC 03040008 and PS4 02020005 IDA databases and the PS4 DWARF, plus the PC
handler function repair. Spec: `specs/007-pc-handler-annotation/`. Gates: `uv run pytest`,
`uv run ruff check --no-fix .`.

## Function repair (`repair_functions.py`, T004c)

`extract_ida.py` (script version 2) writes a `missing_root` record for each root that is not a
function start (`missing`: `no-function` or `inside-function`, `enclosing`, `root` reason) and never
expands the enclosing function in its place; the summary gives `missing_roots`,
`missing_roots_by_kind`, `depth0_expected` (= roots - missing), `depth0_functions` and
`onpacket_orphan_ref_count` beside the `onpacket_orphan_refs` list.

`repair_functions.py` repairs the PC handler-table callbacks that are not function starts. Run it in
ida-mcp `execute_python` on a writable work copy only, dry run first:

    exec(open("D:/ddon-data/research/03040008/ida-transfer/repair_functions.py").read(),
         {"OUT": "D:/ddon-data/research/03040008/ida-transfer/dumps/repair-dryrun.jsonl", "APPLY": False})

The callbacks come from the handler table (`extract_ida._ida_pc_table`; the run aborts unless the
table matches the T002 audit). Per callback it decodes the body linearly to its closing `ret`/`jmp`,
checks the gap before the callback (unreferenced; padding or the tail of an instruction crossing
the callback), that the enclosing function ends at the body end and that no other function overlaps.
`OUT` holds a header, one `result` per callback (`already-ok`, `would-repair`, `repaired`,
`refused` + `check`, `failed` + read-back `check`), an `undo` record written and flushed before each
applied repair (items, function chunks, names, comments of the range), and a `summary`. With
`APPLY: True` it undefines only the conflicting items, then `set_func_start` or `add_func` (IDA picks
the end), waits for auto-analysis and reads the bounds back. Names are not moved: a name left at a
moved enclosing start is in the undo record.
