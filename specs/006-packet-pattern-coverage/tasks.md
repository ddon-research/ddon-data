# 006 tasks

Coordinator: main session. One subagent at a time. Method and rules: `spec.md`.

- [ ] T001 Triage (`evidence-researcher-ida`): for every uncovered packet id in the raws, the PC
  handler/reader/writer VA, PS4 match by code (yes / no = Season 3-exclusive / unresolved), captured
  count, `PacketId.cs` group. Output `research/T001-triage.md` + a machine-readable table
  (`research/T001-triage.tsv`). Large: may run in two or three parts by group range.
- [ ] T001b Save blob 9.1.1 (Sam, 2026-11-01: right after T001, before T002): `evidence-researcher-ida`
  reads `BitWriter` (bit order, `writeU32(val, nBits)`, bool packing, alignment/flush) and the PC
  `cCharacterData::serialize` (`sub_467790`, called from `0x87edd0`; PS4 `0x49740`) with every bit
  width, and walks 2-3 of the 47 captures bit by bit (the recompilation has only stubs for both);
  then an `implementer` turns it into ImHex bitfields in the 9.1.1/9.0.2 patterns and re-exports.
  Start from P4 § 3.1 (spec 005).
- [ ] T002 Login group (C2L/L2C, all directions): evidence + patterns (`evidence-researcher-ida`,
  then `implementer`), extending `C2L_LOGIN_REQ`/`L2C_LOGIN_RES`.
- [ ] T003+ One evidence + one implementer package per group, by captured count (13 instance,
  0 connection, 11 quest, 33 job, 62 season dungeon, 23 area, 14, 8 pawn, 10 item, ...), PS4-matched
  ids only; a reviewer after every few groups.
- [ ] Tn List of Season 3-exclusive ids for the later spec; README table; close.

## Running

- (none)

## Next step (2026-11-01)

T001 (triage) running, brief `briefs/T001-triage.md`. Inventory input: the raw ids by suffix (`fd -t f . packets/decrypted_raw | awk
-F. '{print $NF}' | sort | uniq -c`, bounded with `| wc -l` by the guard: write it to a file) minus
the `// packet-id:` lines of `research/03040008/packets/*-pattern.cpp`.
