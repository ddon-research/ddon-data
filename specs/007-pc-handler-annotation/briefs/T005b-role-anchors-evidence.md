007 T005b: anatomy of handlers, readers, codecs and senders on both sides (evidence for role anchors)

Question (PC 03040008, PS4 02020005): T005 (499f7c701d, `research/03040008/ida-transfer/manifest/`)
pairs 467 handlers (PC `OnPacket_` string + PS4 symbol of the same name and connection class) but
propagation adds nothing: a handler pair's bodies have uneven call gaps (typically 2 PC calls vs 4 PS4),
so no callee pair is forced. Spec 007 will add **role anchors** that pair callees by what they do, proved
by code. This package gathers the facts to define them. Read `specs/007-pc-handler-annotation/spec.md`,
`research/T002-audit.md` (§ codec pairs: 298 aligned handler pairs) and the T005 summary.

Databases: `bash research/ida/private-copy.sh pc-accepted t005b` and `... ps4 t005b`, ida-mcp,
read-only (the work copy `ddon-data-007work` is never opened in ida-mcp). Dumps for counts:
`research/03040008/ida-transfer/dumps/*.jsonl`.

Answer, each with VAs on both sides and counts over all 467 seed pairs where a count is asked:
1. **Handler anatomy**: for 6 seed pairs (2 RES, 2 NTC, 1 login, 1 with Season 3 extra fields), list each
   side's call sites in order with what each callee is (packet object ctor/dtor, the reader
   `CPacket_<DIR>_<NAME>::ReadPacket` on PS4, the PC reader or inlined read, the listener dispatch such as
   `callOnPacketFunc`, error paths). Then over all seeds: how many PC handlers have exactly one callee that
   itself calls codec read functions (directly or one level down), and how many PS4 handlers call exactly
   one `CPacket_*::ReadPacket` whose class name matches the handler's packet.
2. **Codecs**: the PS4 codec read/write functions (symbols, e.g. the `Read_u32`-style functions T002 used)
   and the PC codec functions (T002's `0x8BC4xx`-`0x8BC6xx` set and any others), with how the width (1/2/4/
   8 bytes, string, array count) is determined from each PC body's instructions (load width, byte swap),
   since names and signedness are not visible on PC. Is width alone enough to align a reader's call
   sequence? How often do PC and PS4 readers of a seed pair have equal codec width sequences, and how often
   the PC one extends the PS4 one (Season 3 additions)?
3. **Element readers**: inside readers, calls to `CData*` element readers: how they appear on each side
   (call vs inline), and whether aligning on codec-width anchors would leave 1:1 gaps for them (count over
   the readers reached in question 1).
4. **Senders**: how a PC request sender passes its packet id to the write path (`0x8bcbb0` or the entry
   T004 found): constants, registers, a key `(sub<<16)|id`; for 5 REQ ids whose RES is a seed, the PC
   sender and the PS4 `Send_C2S_*_REQ` (or `CPacket_C2S_*::WritePacket`) with their write width sequences.
   Over all seeds: how many PC senders can be identified by their packet id with a RES seed of the same
   group.id.
5. **REQ/RES convention**: on PS4, do `C2S_X_REQ` and `S2C_X_RES` symbols pair by code (e.g. the RES
   handler consumes what the REQ sender's caller waits for, or table positions)? On PC, does the table key
   pair `g.id.1` with `g.id.2`? State what proves "the request of the same `g.id` as a named RES is
   `<NAME>_REQ`", or that it is only a convention (then such names stay I).

End with a proposal: each role anchor rule in one or two sentences, its evidence, the expected count, and
the near-misses that must be refused.

Owns: `specs/007-pc-handler-annotation/research/T005b-role-anchors.md` only. Never touch scripts, dumps,
the work copy, the original or accepted databases, ddon-hook, client/, packets/.
Libraries: ida-mcp `execute_python`; stdlib Python/jq over the dumps.
Done: the report; final message with the path and at most 15 lines. Past 300k context: write what is
settled, end `cut short:` with the next question.
Stop: budget 120 min of work time; batch lookups, under 120 tool calls.
Base: the head when you start.
