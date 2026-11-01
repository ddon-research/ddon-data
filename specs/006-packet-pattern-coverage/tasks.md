# 006 tasks

Coordinator: main session. One subagent at a time. Method and rules: `spec.md`.

- [x] T001 Triage (2a3408b879: 526 ids; 355 matched / 94 exclusive / 77 unresolved; batch order login, 0, 13, 11, 33, 3, 8, 14, 10, 37; 157 REQs matched by RES pairing only, 22 low-ratio name matches to read by hand) (`evidence-researcher-ida`): for every uncovered packet id in the raws, the PC
  handler/reader/writer VA, PS4 match by code (yes / no = Season 3-exclusive / unresolved), captured
  count, `PacketId.cs` group. Output `research/T001-triage.md` + a machine-readable table
  (`research/T001-triage.tsv`). Large: may run in two or three parts by group range.
- [x] T001b (done: evidence 59e2475eba, patterns adda42cc98 + JSON 6ae1ba81e7; 47/47 captures equal the
  walk script field by field, 8,225 values; 9.0.2 checked on synthetic versions 0x19/0x13/0x0C) Save blob 9.1.1 (Sam, 2026-11-01: right after T001, before T002): `evidence-researcher-ida`
  reads `BitWriter` (bit order, `writeU32(val, nBits)`, bool packing, alignment/flush) and the PC
  `cCharacterData::serialize` (`sub_467790`, called from `0x87edd0`; PS4 `0x49740`) with every bit
  width, and walks 2-3 of the 47 captures bit by bit (the recompilation has only stubs for both);
  then an `implementer` turns it into ImHex bitfields in the 9.1.1/9.0.2 patterns and re-exports.
  Start from P4 § 3.1 (spec 005).
- [ ] T001c Spec 005's other parked static items, finished, not listed (Sam's rule 2026-11-01): the
  35.12.16 tail (second structure via `0x760480`), the 35.0.2/35.1/35.2/35.4 readers, the start/end
  pairing of 13.44-13.47 (callers `0x8a2670`, `0x8a1d5a`), the CaughtResult/GameEasy sender check,
  the QuestEnemyInfo u32 position (P11a § 1.3); one IDA package, then the pattern fixes.
- [ ] T002 Login group (C2L/L2C, all directions): evidence + patterns (`evidence-researcher-ida`,
  then `implementer`), extending `C2L_LOGIN_REQ`/`L2C_LOGIN_RES`.
- [ ] T003+ One evidence + one implementer package per group, by captured count (13 instance,
  0 connection, 11 quest, 33 job, 62 season dungeon, 23 area, 14, 8 pawn, 10 item, ...), PS4-matched
  ids only; a reviewer after every few groups.
- [ ] Tn List of Season 3-exclusive ids for the later spec; README table; close.

## Running

- T001c evidence done (3ef33ecaff, `research/T001c-parked-static-items.md`: 5 of 6 items V, item 6
  partly; P4 § 2.3, P5 item 7 actors and P11a § 1.3 contradicted; IDA copies deleted). Running: the
  T001c pattern implementer, brief `briefs/T001c2-pattern-fixes.md`. Next: T002 login.
- Coordinator housekeeping until 002 T021 lands: after each IDA package, stop its `idat.exe` workers
  (`scratchpad/idaprocs.ps1` lists them) and delete its `ddon-data-<name>` copies.

## Next step (2026-11-01)

T001 (triage) running, brief `briefs/T001-triage.md`. Inventory input: the raw ids by suffix (`fd -t f . packets/decrypted_raw | awk
-F. '{print $NF}' | sort | uniq -c`, bounded with `| wc -l` by the guard: write it to a file) minus
the `// packet-id:` lines of `research/03040008/packets/*-pattern.cpp`.
