007 T004c: report missing roots; repair the PC handler function starts

Objective (PC 03040008): T004b (`research/T004b-extract-run.md`) found 131 of the 1,040 handler-table
callbacks missing from `dumps/pc-ida.jsonl`: 119 are not functions in the accepted PC database (data or
misdecoded code, e.g. `0x7C3280` decoded inside `add eax, ...` at `0x7C327D`), 12 lie 1-4 bytes inside a
function that starts just before them (e.g. `0x7C5C90` in the function at `0x7C5C8D`). A callback
pointer stored by a proved table initializer is a code entry point: that is PC evidence. Two changes:

1. `extract_ida.py`: a root that is not a function start is never replaced by the enclosing function.
   Write one `missing_root` record per such root (va, kind: no-function | inside-function, enclosing
   start if any, root reason) and count them in the summary; depth-0 count = roots - missing. Same for
   `OnPacket_` string references from outside any function (`onpacket_orphan_refs`: list each). Tests.
2. `repair_functions.py`: an IDAPython script (same `exec(..., {"OUT":..., "APPLY": bool})` discipline,
   dry run by default) that, for each table callback that is not a function start (computed from the
   table, not from a list):
   - decodes linearly from the callback va to the first `ret`/`jmp` that ends the body without leaving
     decodable code and without running into another function's start; records the instructions;
   - for an inside-function case, checks that the bytes between the enclosing start and the callback
     are not referenced (no xref to them) and are padding or the tail of a misdecoded instruction;
   - only if all checks pass and APPLY: records the before-state (items, function chunks, names,
     comments over the affected range) in an undo JSONL, undefines exactly the conflicting items,
     moves the enclosing function's start (`ida_funcs.set_func_start`) or creates the function
     (`ida_funcs.add_func`), waits for auto-analysis of that range, and reads back: function starts at
     the callback, its end matches the decoded body, no other function changed bounds;
   - writes one result line per callback: repaired | refused (which check) | already-ok, and the
     undo record. Never forces a function; a refusal stays for the coordinator.
   Pure parts (decode-walk decision, check logic, undo record shape) tested with fakes.

Owns: `research/03040008/ida-transfer/{extract_ida.py,repair_functions.py,tests/**}` and its README
section. Never touch the dumps, the databases (the repair runs in T004d), ddon-hook, client/, packets/.
Libraries: IDAPython (ida_funcs, ida_bytes, ida_ua, ida_auto, idautils), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 90 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
