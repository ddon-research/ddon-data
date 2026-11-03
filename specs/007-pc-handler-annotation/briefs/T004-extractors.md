007 T004: fact extractors for the PC and PS4 databases and the PS4 DWARF

Objective (PC 03040008, PS4 02020005): the inputs of the matcher (spec 007 § Method, step 1). Read
`specs/007-pc-handler-annotation/spec.md` and `research/T002-audit.md` (table layout, tier-0 counts,
PS4 readiness: IDA lacks most DWARF locals) first.

Build a new uv project `research/03040008/ida-transfer/` (CPython 3.14, `pyproject.toml`, pytest, ruff),
with:
1. `extract_ida.py`: an IDAPython script run inside ida-mcp (`execute_python` will `exec` it with
   `OUT` (path) and `SIDE` ("pc" | "ps4") set; it must also run headless the same way). It writes one
   JSONL dump with a header line (database path, input sha256 via `ida_nalt.retrieve_input_file_sha256`,
   idb path, bitness, image base, script version) and one line per function in scope:
   va, size, instruction count, name (and whether it is a default `sub_` name), prototype string if
   set, ordered call sites (site va, target va or `indirect`, for PC the bytes pushed before the call
   and whether ecx is loaded; for PS4 the argument registers written), referenced strings (text) and
   data addresses, immediate constants that are not addresses and not in 0..255, `ret N` immediates,
   whether ecx is read before written (PC), callers (count and up to 20 vas), and for PC the
   function's non-default local names/types and comments (so apply can preserve them).
   Scope: PC: the 1,041 handler-table records (table `0x1bc0110`, `{table,count}` x 74, stride 0x18,
   key `(sub<<16)|id` at +0x10; callbacks come from the 74 initializers `0x1a27560`-`0x1a36540`;
   reuse the reading logic of `C:/Users/morph/CLionProjects/ddon-hook/scripts/ida_packet_dispatch.py`
   (copy with attribution, check it against T002's 1,041/1,040 counts) written as a separate
   `table` record per entry (group, id, sub, callback va, record va); every function referencing an
   `OnPacket_` string; the callers of the packet write entry `0x8bcbb0`; then their callees to depth 3.
   PS4: every function whose symbol is `cSeed*Connection::OnPacket_*` or `Send_*` or
   `CPacket_*::{ReadPacket,WritePacket}`, then callees to depth 3. Depth and roots are parameters.
2. The PS4 DWARF facts per in-scope function (by address): prototype, parameter names and types,
   local variables with their lexical block and DWARF location expression, inlined subroutine calls
   (callee, call site, ranges), and the DWARF definition of every struct/class/enum/typedef they reach
   (members with offset, size, type; base classes; vtable). **Libraries first**: before writing a
   parser, check what the DWARF reconstructor already emits (`C:/ddon-dwarf-reconstructor-rust`,
   its `output_*.signatures.json`, `*.layout.json`, `*.inlined.json`, its README/docs; clones are not
   built or run unless its docs give a release binary) and the existing dumps
   (`binaries/PS4_02020005/elf-dumps/dwarf/inline-chains.orbis-addr2line.tsv`); else use
   `pyelftools` (`uv add pyelftools`) on the staged ELF
   `binaries/PS4_02020005/elf-dumps/.staging/input/DDOORBIS.elf` (verify its sha256 equals the
   `elf_sha256` in the inline-chains header). Write `extract_dwarf.py` producing a JSONL dump with
   the same header discipline (ELF sha256, tool, version). Run it yourself and report time and size.
3. Tests: the pure parts (scope closure, record parsing, constant filter, JSONL writer, DWARF record
   shaping) with fakes; one fixture test of the DWARF dump for two known functions
   (`cSeedGameSvConnection::OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTC` and one `CPacket_*::ReadPacket`)
   against `llvm-dwarfdump` text or the reconstructor output.
4. Dumps go to `research/03040008/ida-transfer/dumps/` (gitignored; a committed `dumps/MANIFEST.tsv`
   lists file, sha256, source sha256, script version). Wire the project's tests into `tools/check.sh`
   like the other projects.
The IDA script is run in T004b by an `evidence-researcher-ida`; make it runnable with one
`exec(open(path).read(), {"OUT": ..., "SIDE": ...})` call and fast (no decompilation; batch, no
per-function round trips).

Owns: `research/03040008/ida-transfer/**`, the `tools/check.sh` lines for it, `.gitignore` line for the
dumps. Never touch ddon-hook (read only), the databases, client/, packets/, other specs.
Libraries: IDAPython (ida_funcs, idautils, ida_ua, ida_bytes, ida_nalt), pyelftools or the reconstructor
output, pytest, ruff.
Done: `uv run pytest`, `uv run ruff check --no-fix .`, `bash tools/check.sh --since <base>`; the DWARF dump
run with counts (functions, params, locals, types) and time; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 150 min of work time; stop and ask if the DWARF
source needs more than 30 GB or an hour of run time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
