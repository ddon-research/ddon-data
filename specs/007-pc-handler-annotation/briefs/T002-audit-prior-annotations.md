007 T002: audit the earlier packet annotations in the accepted PC database (evidence)

Question (PC 03040008, seed PS4 02020005): which of the earlier agent's packet-area annotations hold,
and is the PS4 database ready to supply prototypes, types and locals? Read
`specs/007-pc-handler-annotation/spec.md` (method) and `research/T001-prior-method.md` (what was done,
its weak points) first.

Databases (private copies, read-only in substance; never save_database):
- PC accepted: `bash research/ida/private-copy.sh pc-accepted t002` (lands with T003; if that target
  is missing, stop and say so).
- PS4: `bash research/ida/private-copy.sh ps4 t002`.

Work:
1. **Identity**: confirm the PC copy is the accepted database (input sha256 against
   `CURRENT-RECOVERY.json`, `idc.get_idb_path()`), and that the 107 method views T001 counts exist.
2. **Inventory** (one execute_python per step): every non-default name, prototype, local type/name,
   struct/enum and function comment in the packet area: the 1,041 handler-table entries (table at
   `0x1bc0110`, `{table,count}` x 74, entry stride 0x18, key `(sub<<16)|id` at +0x10; the handler
   pointers come from the initializers `0x1a27560`-`0x1a343b0`, see 006 `research/T001-triage.md`
   § Method), the senders and the read/write helpers they call (one level). Write
   `research/T002-prior-annotations.tsv`: pc_va, kind, value, origin guess (earlier work / IDA
   propagation / default), and in step 3 a verdict.
3. **Check** each earlier handler name (50) and the sender (`0x833670`) independently: the function is
   the table entry's; it references the `OnPacket_` string its name repeats, and only that one; the
   PS4 symbol with the same `<NAME>` exists once and its body has the same reader/sender call shape.
   Check every earlier prototype in that set against PC code (ecx `this`, argument count from `ret N`
   and callers' pushes, return use). Check the two packet structs and nine peer types against the PC
   member accesses. For the three byte-identical helper pairs (`0x8BC480`/`0x8BC4D0`,
   `0x8BC410`/`0x8BC6E0`, `0x8BC660`/`0x8BC6A0`): confirm byte identity, count callers, and say whether
   any PC evidence tells the names apart. Verdict per row: holds / wrong (what is right) / unproved.
4. **Tier-0 feasibility** (counts only, the extractor comes later): how many table entries reference
   exactly one `OnPacket_` string, several, or none; any string referenced from several functions.
5. **PS4 readiness**: for 10 handlers and 10 `CPacket_*::ReadPacket`/`CData*` readers spread over
   groups, does the PS4 database have the DWARF prototype (parameter names and types), local variable
   names and types, and the struct types? Say what IDA imported and what only the DWARF dump
   (`binaries/PS4_02020005/elf-dumps/dwarf/`) has.

Owns: `specs/007-pc-handler-annotation/research/T002-audit.md` and `T002-prior-annotations.tsv`. Never
touch patterns, packets/, client/, ddon-hook, the original databases.
Libraries: ida-mcp `execute_python` (IDAPython, ida_hexrays for local variables).
Done: report with the five sections and counts, the TSV; final message with the path and at most 15
lines. Past 300k context: write what is settled and end `cut short:` with the next step.
Stop: budget 120 min of work time; batch lookups (one script per step), stay under 120 tool calls.
Base: the head when you start.
