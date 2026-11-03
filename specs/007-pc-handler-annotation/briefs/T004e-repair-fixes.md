007 T004e: fix the repair script; headless batch as the write path

Objective (PC 03040008): T004d (`research/T004d-repair.md`) applied `repair_functions.py` on the work copy:
116 repaired, 3 failed, 12 refused. Its writes were then lost: ida-mcp's `close_database` and
`save_database` are denied here, the worker was killed, and the next headless open chose "Restore packed
base (DISCARD unpacked)" (coordinator test 2026-11-03: 0/116 survived; an `idat -A -S<script>` run whose
script ends with `idc.qexit(0)` did save and pack the copy). Decision: **database writes run as headless
batch jobs** (`idat -A -L<log> -S"<script> <args>" <work copy .i64>`), never through an ida-mcp worker; ida-mcp
stays for reads.

1. `repair_functions.py`:
   - Defect: for an inside-function case it undefines the enclosing start's own first instruction, IDA
     then deletes the whole function and `set_func_start` returns `MOVE_FUNC_NOFUNC` (callbacks 0x7C3840,
     0x7D8590, 0x7F1790). Fix: when the enclosing function's body from the callback on equals the decoded
     body, delete that function (`del_func`, before-state in the undo record) and create it at the
     callback (`add_func`), or move the start without undefining; test the sequence with fakes.
   - Refusal `gap_not_padding` (9): accept when no code or data xref targets any address in
     [enclosing start, callback), the enclosing start is not a table callback, and nothing calls or jumps
     to it; the junk bytes become unexplored. Otherwise refuse as now.
   - Refusal `runs_into_function` (2, stray 3-byte functions at 0x7E13F4 and 0x7F4120 on the body's own
     `retn`): accept when the other function lies wholly inside the decoded body, has no xref, and is at
     most one instruction; delete it (undo record) before `add_func`.
   - Refusal `indirect_jump` (1, 0x7D1BE0 switch): accept when IDA has switch info for the jump
     (`ida_nalt.get_switch_info`) and every case target lies inside the decoded body.
   - Batch entry: runnable as `idat -A -S"repair_functions.py <OUT> --apply"` (args via `idc.ARGV`),
     ending with `idc.qexit(0)` after writing its output, and printing a final summary line to the log.
     Same for `extract_ida.py` (read-only batch run; it may exit without changes).
2. `research/03040008/ida-transfer/README.md`: the write path (batch only, on the work copy, never an
   ida-mcp worker), the read path (ida-mcp on private copies), and that a killed worker's writes are lost.
Each relaxation and the fix: a test with fakes that fails without it, and one that still refuses the
near-miss (an xref into the gap, a stray function with an xref, a switch target outside the body).

Owns: `research/03040008/ida-transfer/{repair_functions.py,extract_ida.py,tests/**,README.md}`. Never
touch the dumps, the databases, ddon-hook, client/, packets/.
Libraries: IDAPython (ida_funcs, ida_bytes, ida_ua, ida_nalt, ida_xref, ida_auto, idc), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 75 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
