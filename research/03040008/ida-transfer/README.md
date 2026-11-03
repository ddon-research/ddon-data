# ddon-ida-transfer (spec 007)

Fact extractors for the PC 03040008 and PS4 02020005 IDA databases and the PS4 DWARF, plus the PC
handler function repair. Spec: `specs/007-pc-handler-annotation/`. Gates: `uv run pytest`,
`uv run ruff check --no-fix .`.

## Read path and write path

- **Reads** (`extract_ida.py`, inspection): ida-mcp on a private copy
  (`bash research/ida/private-copy.sh <pc|ps4> <name>`), or a read-only headless batch:

      idat -A -L<log> -S"extract_ida.py <OUT> <pc|ps4>" <private copy .i64>

  The batch waits for auto-analysis, writes `OUT`, prints `extract_ida summary: {...}` to the log,
  discards the session (`DBFL_KILL`: the packed `.i64` is not rewritten) and exits (`idc.qexit`,
  1 after an error).
- **Writes** (`repair_functions.py --apply`): only as a headless batch job on the work copy, never
  through an ida-mcp worker:

      idat -A -L<log> -S"repair_functions.py <OUT> --apply" <work copy .i64>

  The script ends with `idc.qexit(0)`, which saves and packs the database; it prints
  `repair_functions summary: {...}` as the last line of the log. After an exception it prints the
  traceback and an error summary, marks the database not to be saved (`DBFL_KILL`) and exits with
  code 1; the partial `OUT.tmp` keeps the undo records written so far.
- **A killed worker's writes are lost.** ida-mcp's `close_database` and `save_database` are denied
  here, so an ida-mcp worker cannot save; when it is killed, the next open finds the unpacked files
  and offers "Restore packed base (DISCARD unpacked)" (T004d: 0 of 116 repairs survived). Check the
  `.i64` sha256 and mtime after every batch write.

## Function repair (`repair_functions.py`, script version 2)

`extract_ida.py` (script version 2) writes a `missing_root` record for each root that is not a
function start (`missing`: `no-function` or `inside-function`, `enclosing`, `root` reason) and never
expands the enclosing function in its place; the summary gives `missing_roots`,
`missing_roots_by_kind`, `depth0_expected` (= roots - missing), `depth0_functions` and
`onpacket_orphan_ref_count` beside the `onpacket_orphan_refs` list.

`repair_functions.py` repairs the PC handler-table callbacks that are not function starts. Dry run
first (no `--apply`; also possible in ida-mcp as
`exec(open(path).read(), {"OUT": ".../repair-dryrun.jsonl", "APPLY": False})`).

The callbacks come from the handler table (`extract_ida._ida_pc_table`; the run aborts unless the
table matches the T002 audit). Per callback it decodes the body linearly to its closing `ret`/`jmp`
and checks that no other function overlaps it and, inside a function, the gap before the callback
and that the enclosing function (one chunk) ends at the body end. Accepted since T004e:

- gap bytes that are neither padding nor the tail of an instruction crossing the callback, when no
  code or data xref targets any address in [enclosing start, callback) and the enclosing start is
  not itself a table callback (the junk items become unexplored);
- a stray function (one instruction, one chunk, no xref) lying wholly inside the decoded body, such
  as a nullsub on the body's own `retn`: deleted before the repair;
- an indirect jump with IDA switch info (`ida_nalt.get_switch_info`) whose case targets all lie in
  the body and whose jump table lies outside it.

The near misses stay refused (`gap_referenced`, `gap_not_padding`, `runs_into_function`,
`indirect_jump`, `switch_target_out_of_body`, `switch_table_in_body`, `enclosing_has_tails`).

`OUT` holds a header, one `result` per callback (`already-ok`, `would-repair`, `repaired`,
`refused` + `check`, `failed` + `check`), an `undo` record written and flushed before each applied
repair (items, the functions to delete with their chunks, names, comments of the range), and a
`summary`. Apply order: delete the enclosing function and any stray (`del_func`), then undefine the
conflicting items (and junk gap items), create the decoded instructions, `add_func` at the callback
(IDA picks the end), wait for auto-analysis and read the bounds back. Deleting first matters:
undefining a function's entry instruction deletes the function, which made the T004d
`set_func_start` repairs fail with `MOVE_FUNC_NOFUNC`. Names are not moved: a name left at a
deleted enclosing start is in the undo record.
