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
- [x] T001c (done: evidence 3ef33ecaff; patterns + JSON a564bde7f0: 193 re-exported, renames only, all fit) Spec 005's other parked static items, finished, not listed (Sam's rule 2026-11-01): the
  35.12.16 tail (second structure via `0x760480`), the 35.0.2/35.1/35.2/35.4 readers, the start/end
  pairing of 13.44-13.47 (callers `0x8a2670`, `0x8a1d5a`), the CaughtResult/GameEasy sender check,
  the QuestEnemyInfo u32 position (P11a § 1.3); one IDA package, then the pattern fixes.
- [x] T002 (done: evidence d7f0cebbf2; patterns + JSON 5421fdf867: 21 patterns, 20 ids exported, 1,235/1,235 fit; 1.0.1 pattern unexported until T002c) Login group (C2L/L2C, all directions): evidence + patterns (`evidence-researcher-ida`,
  then `implementer`), extending `C2L_LOGIN_REQ`/`L2C_LOGIN_RES`.
- [x] T001d (done: 7565aa6383 pin PatternLanguage 300d7388, b2646372c2 JSON: 117,101 exported, 110,872 changed strings only, 157/157 samples equal, 0 invalid UTF-8) Plain UTF-8 JSON strings (Sam, 2026-11-01): plbatch's PatternLanguage pin `fb6ea061`
  percent-encodes strings (110,872 JSON files); upstream master writes UTF-8. Bump the pin, rebuild,
  re-export everything, verify by sample (`implementer`, brief `briefs/T001d-utf8-json-strings.md`);
  runs right after T003's evidence.
- [ ] T003+ One evidence + one implementer package per group, by captured count (13 instance,
  0 connection, 11 quest, 33 job, 62 season dungeon, 23 area, 14, 8 pawn, 10 item, ...), PS4-matched
  ids only; a reviewer after every few groups.
- [ ] Tn List of Season 3-exclusive ids for the later spec; README table; close.

## Running

- T002c/T002d done (report 83ce3403dd; fix 40f80dc80f + 20a4617cd4; 250 raws re-decrypted).
- T003 evidence done (d6692cf3b9, `research/T003-connection-server-cert.md`: 27/27 ids V, all
  captures fit; 0.10.16 = SESSION_STATUS_NTC; PC `Send` 0x9d6a20 strips the header of the
  handshake packet; the 304 B first-packet files are 44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC (PS4
  `S2C_GAME_SERVER_CERT_NOTICE`) and 1.1.16 L2C_LOGIN_SERVER_CERT_NTC, filed by the CLI under
  44.0.1/1.0.1; IDA copies deleted). Running: T002e. Next: T003 patterns (incl. the
  two CERT_NTC patterns), Sam (2026-11-01): rename the 304 B files
  to their code-backed ids/names: T002e, brief `briefs/T002e-cert-ntc-rename.md`, after T001d.
  Tn: `tests/imhex-export-select.sh` is not run by check.sh.
- Coordinator housekeeping until 002 T021 lands: after each IDA package, stop its `idat.exe` workers
  (`scratchpad/idaprocs.ps1` lists them) and delete its `ddon-data-<name>` copies.

## Next step (2026-11-01)

T001 (triage) running, brief `briefs/T001-triage.md`. Inventory input: the raw ids by suffix (`fd -t f . packets/decrypted_raw | awk
-F. '{print $NF}' | sort | uniq -c`, bounded with `| wc -l` by the guard: write it to a file) minus
the `// packet-id:` lines of `research/03040008/packets/*-pattern.cpp`.
