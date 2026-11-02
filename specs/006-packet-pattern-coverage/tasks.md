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
- [x] T003 Groups 0/1/44 (done: evidence d6692cf3b9; patterns 383373ed28 + JSON 5bc4846af8: 27 patterns, 5,359/5,359 fit).
- [x] T004 Group 13 (done: evidence f7efade6c6; patterns + JSON d7d48b68f6: 27 patterns, 5,567/5,567 fit; 13.16.x/13.17.x/13.23.16 Season 3-exclusive, not patterned).
- [x] T005 Group 11 (done: evidence 1159abe264; patterns + JSON d6c1a1f061: 67 patterns, 3,505/3,505 fit over the 73 captured in-scope ids; 4 shared types moved into Quest.hexpat, older JSON byte-identical).
- [x] T006 Groups 33/3/23/12 (done: evidence 722283dcf1; patterns + JSON bc9279f6c0: 23 patterns, 3,675/3,675 fit; the report's total 3,712 exceeds the per-id sum by 28 files, per-id counts agree).
- [x] T007 Groups 8/58/53 (done: evidence d5da913504; patterns + JSON 441febe4f2: 43 patterns, 1,569/1,569 fit; 8.30.2 JSON byte-identical).
- [x] T008 Groups 14/10/50 (done: evidence dcf19a90eb; patterns + JSON 4abc0b4b80: 32 patterns, 1,848/1,848 fit; no older pattern used the PS4 item list; 10.9.2 byte-identical).
- [x] T009 Groups 37/45/2 (done: evidence d941b4e255; patterns + JSON 9d69024f34: 43 patterns, 1,258/1,258 fit; 5 list-element users 174/174 byte-identical; StatusInfo Hp > MaxHp queued in T010).
- [x] T010 Groups 28/31 (done: evidence 9e24b3b0f3; patterns + JSON ff9f166af7: 32 patterns, 552/552 fit; `CDataFurnitureLayout` moved to Furniture.hexpat, 52.1.2 key `unOmID`->`OmID` 20/20; 207 other files byte-identical).
- [ ] T011+ One evidence + one implementer package per group, by captured count (13 instance,
  0 connection, 11 quest, 33 job, 62 season dungeon, 23 area, 14, 8 pawn, 10 item, ...), PS4-matched
  ids only; a reviewer after every few groups.
- [ ] Tn List of Season 3-exclusive ids for the later spec; README table; close.

## Running

- Landed: T002c/T002d (83ce3403dd; 40f80dc80f + 20a4617cd4: 250 first-packet raws re-decrypted);
  T002e (70201832e1: the 304 B first packets renamed byte-identical to 1.1.16
  L2C_LOGIN_SERVER_CERT_NTC / 44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC, 2 patterns 42/42 + 83/83 fit);
  T003 (d6692cf3b9; 383373ed28 + 5bc4846af8: 0.10.16 = SESSION_STATUS_NTC; PC `Send` 0x9d6a20 strips
  the handshake packet's header); T004 (f7efade6c6; d7d48b68f6).
- R1 review done (2026-11-02: no wrong-data defects; 8 smaller findings: Arrowgene names as field
  names in `Server.hexpat`, comment/README slips, report errata). R1b fixes done (45d29a2c57, 7ef48a26de: 1.1.2
  server-lead keys now `unk_*`, 42/42 re-exported; errata appended to T002/T002c/T003). T005 evidence done (1159abe264: 79 ids,
  4,352/4,352 fit; Season 3 `CDataQuestList`; 9/11 unresolved settled; 11.7.16, 11.68.16 (I) exclusive;
  11.88.16, 11.118.16 unresolved: empty PC handlers). T005 patterns done (d6c1a1f061). T006 evidence
  done (722283dcf1: 23 ids, 3,712/3,712 fit; 33.20.16 = UPDATE_PLAY_POINT_NOTICE; 12.5.x, 12.9.16
  exclusive). T006 patterns done (bc9279f6c0). T007 evidence done
  (d5da913504: 43 ids, 1,569/1,569 fit; 8.37.16, 53.9.16 settled). T007 patterns done (441febe4f2).
  T008 evidence done (2,038/2,038 fit; 14.10.16 = C2S_WARP_END_NTC,
  raw name WARP_START wrong: add to the Tn rename list). T008 patterns done (4abc0b4b80). Running: R2 reviewer over T005-T008\n  (`briefs/R2-review-T005-T008.md`); next T009 (`briefs/T009-mail-stamp-character.md`); then T010 28 GP + 31 CLAN (`briefs/T010-gp-clan.md`); T011 6 PARTY + 26 PROFILE +
  16 FRIEND + 17 BLACK + 5 + 24; T012 27 ACHIEVEMENT + 29 EQUIP + 19 SKILL + 39 GACHA + 25 ORB + 43
  LOADING + 20; T013 the small rest (30, 34, 63, 9, 18, 52, 15, 41, 54, 57, 51); all-exclusive groups
  (70, 72, 60, 71, 61, 64, 59, 65, 62) go to the Tn list. Earlier plan:
  8+58 PAWN + 53 PARTNER; 14 WARP + 10/50 ITEM; 37 MAIL + 45 STAMP + 2 CHARACTER; then the rest by count
  (62 SEASON is all Season 3-exclusive: out of scope). Was: then groups 33, 3, 8, 14, 10, 37 by the triage order.
- Tn: `tests/imhex-export-select.sh` is not run by check.sh; the u64 OM `Key` (13.20.x/13.22.2) exceeds
  2^53 in JSON (README note).
- Tn naming sweep (README rule after R2b: an `unk_` name carries no server name): `unk_SpSkillList` / type
  `SpSkill` (Context, Pawn), 13.6.2 `unk_RestrictionList`, `CDataDeliveredItem.ItemNum/NeedNum`
  (Quest.hexpat:456); grep all includes for server-derived names before close; F2 bool order open.
- Tn: raws whose names are placeholders but code names them (0.10.16 = SESSION_STATUS_NTC, T003 § 9;
  14.10.16 = C2S_WARP_END_NTC, T008): one CLI `PacketId` relabel + rename package at spec end (Sam 2026-11-01 chose renaming
  for code-backed names).
- Sam is away 2026-11-01 evening for ~8 h: keep coordinating; park decisions with a recommendation.
- Coordinator housekeeping until 002 T021 lands: after each IDA package, stop its `idat.exe` workers
  (`scratchpad/idaprocs.ps1` lists them) and delete its `ddon-data-<name>` copies.

## Next step (2026-11-01)

T001 (triage) running, brief `briefs/T001-triage.md`. Inventory input: the raw ids by suffix (`fd -t f . packets/decrypted_raw | awk
-F. '{print $NF}' | sort | uniq -c`, bounded with `| wc -l` by the guard: write it to a file) minus
the `// packet-id:` lines of `research/03040008/packets/*-pattern.cpp`.
