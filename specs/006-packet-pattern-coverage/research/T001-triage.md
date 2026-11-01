# 006 T001: triage of every uncovered packet id

Client build **03040008** (PC, IDA 9.5 private copy `ddon-data-t001/2022_01_29_DDO_DUMP_FIX.exe.i64`,
32-bit, image base `0x400000`); seed **PS4 02020005** (`ddon-data-t001/DDOORBIS.elf.i64`, 64-bit,
base `0`). Address basis: IDA VA in each database. Run 2026-11-01, base `ae52337e2d`, read-only
(no rename/comment/retype/reanalysis; nothing saved).

Outputs (this directory):

- `T001-inventory.tsv`: 526 uncovered ids (id, raw name, captured count).
- `T001-triage.tsv`: one row per inventory id: id, raw name, captured, group, direction, PC VA,
  PS4 symbol @VA (or `-`), mark, recompiled body, basis. **All 526 ids, every group done.**

## Result

| Mark | ids | captured packets |
| --- | --- | --- |
| matched | 355 | 23,407 |
| exclusive (Season 3, no PS4 counterpart) | 94 | 4,254 |
| unresolved | 77 | 3,406 |

54 matched ids have a PS4 recompilation body (`CPacket_<name>::ReadPacket/WritePacket` in
`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`, 158 bodies in total).

## Method

1. **Inventory** (stdlib Python, `os.scandir`, run as `python -X utf8 -I inventory.py <out>` from the
   session scratch dir; not kept in the repo): 146,891 files in 125 stream dirs of
   `packets/decrypted_raw/`, keyed by the `.<g>_<id>_<sub>` suffix **and the server side** (raw name
   prefix `C2L`/`L2C` = login server, else game server: the two servers reuse the same g.id.sub, e.g.
   `0_0_1` is both `C2L_PING_REQ` and `C2S_CONNECTION_PING_REQ`, `1_0_1` both `C2L_CLIENT_CHALLENGE_REQ`
   and `C2S_SERVER_GET_SERVER_LIST_REQ`). 585 distinct (side, id); the 67 `// packet-id:` values of
   `research/03040008/packets/*-pattern.cpp` (side from the pattern file prefix) cover 59 of them;
   **526 uncovered** (221 REQ, 204 RES, 101 NTC; 31,067 packets). Login ids are written `L:g.id.sub`.
   Spec 005's "about 508" did not split the login ids from the game ids.
2. **PC S2C handlers** (V): the per-group table directory at PC `0x1bc0110` = `{table, count}` x 74,
   indexed by group 0-73 (checked: group 11 entry `0x1bc0168` -> `0x212e638`/146, group 23 `0x1bc01c8`
   -> `0x212ad38`/16, group 35 `0x1bc0228` -> `0x212bc68`/18, the bases P4/P11 found). Entries
   stride 0x18, key `(sub<<16)|id` at +0x10; handler pointers come from the 73 initializers at
   `0x1a27560`-`0x1a343b0` (`mov [esp], offset handler` / `movq table_entry, xmm0`). 1,041 game S2C
   handlers. Login: the static `{handler, key}` list at `0x1bd6270` with a trailing count per group
   (groups 0-5, 20 handlers). Every S2C inventory id has a PC handler.
3. **PC C2S writers** (V): the 658 `nUserSession::CPacket::WritePacket` (`0x8bcbb0`) call sites;
   group/id/sub from the pushed immediates (all 658 decoded, 651 distinct keys). Login writers are
   the sites in `0x889e00`-`0x88ac00` (`0x889f40`..`0x88a980`; e.g. `0x88a390` = `WritePacket(0,1,1)`,
   P11b's C2L login writer). Every C2S inventory id has a PC writer.
4. **PC names from code** (V): the 675 `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>` strings in
   `.rdata`, each assigned to the handler whose code references it (xref or raw `push imm32`). The
   login server has no such strings on PC. A REQ (g.id.1) takes the name of its RES (g.id.2) handler
   string (pairing: **I**).
5. **Body shape** (V, automated): the flattened sequence of `nPacket::Read_*`/`Write_*` primitive calls,
   following callees recursively (depth 5), on both sides. PC: from the handler (linear decode up to
   the next handler when IDA has no function) or the writer function. PS4: from
   `cSeed{Game,Login}SvConnection::OnPacket_*` (802), `Send_*` (404),
   `CPacket_*::ReadPacket` (149) / `::WritePacket` (100). Normalised: PS4 drops its leading `u16`
   (RES/NTC) or three `u16` (C2S header); PC RES drops its leading `s32`. Ratio =
   `difflib.SequenceMatcher` over the two sequences. Loops collapse to one element, so this is a shape
   check, not a layout proof.
6. **Match** (never by packet number):
   - `pc-name`: the PC handler string (or paired RES string), minus 0-3 leading group words, `_NTC`
     also as `_NOTICE`, names a PS4 symbol (case-insensitive) -> **matched**; the basis column gives
     the shape ratio. 310 rows; 271 of them ratio >= 0.8.
   - `shape-unique`: no name, but exactly one PS4 body has the identical normalised sequence and it has
     >= 6 primitives -> **matched**; shorter unique shapes stay unresolved (three short ones hit wrong
     PS4 bodies, e.g. 13.20.16 -> `S2C_GP_COURSE_START_NTC`).
   - `raw-name-lead`: the raw (Arrowgene, community) name finds a PS4 symbol; **matched** only when
     the PC body has >= 4 primitives and the ratio is >= 0.6; otherwise unresolved with the PS4
     candidate listed.
   - **exclusive**: the PC string names the packet but no PS4 symbol carries the name and no PS4 body
     has a unique matching shape (**I**). Group-level (I): the 12 unnamed NTC ids of groups 62 and 72, where none of
     the group's PC-named S2C handlers (23 and 3) has a PS4 symbol (the rule also covers groups 59, 61,
     64, 65, 71, which had no unnamed ids).
   - **unresolved**: everything else (mostly NTCs and login packets with no PC name string and an
     empty or short body).
7. **Recompiled body**: `yes` when the PS4 candidate's `CPacket_<name>::ReadPacket/WritePacket` is
   defined in the recompilation's `Protocol/` sources.

## Caveats

- The name bridge (`pc-name`) relies on the PC handler string plus the PS4 symbol of the same name
  stem; 22 of these have a shape ratio below 0.5 (e.g. 3.0.2 LOBBY_JOIN_RES 130 vs 12 primitives,
  27.0.2, 28.7.2, 34.1.2, 34.2.2, 50.0.2): the PC side follows non-reader callees too, or Season 3
  changed the data class (10.3.2 `CDataItemList` differs). Each batch must read these by hand.
- 157 matched REQs rest on the REQ/RES pairing plus an empty or short body: pairing is **I**.
- Login (L0-L5): no PC strings; only 6 of 21 ids reach "matched" (shape); the rest are unresolved
  with the PS4 candidate named. T002 must decide them by reading the code.
- 60.0.2 NPC_GET_NPC_EXTENDED_FACILITY_RES is "exclusive" (PC string, no PS4 symbol), though spec 005
  patterned 60.0.1; 64.0.1 MANDRAGORA likewise (P11a read its PC handler only).
- Group 63 (8 NTC ids) and group 15 have no PC name strings at all; left unresolved.
- Not run: caller comparison, string comparison inside bodies, capture walks against the PC readers.

## Per group (PacketId.cs group numbers and names only)

| Group | Name | ids | captured | matched (captured, recompiled) | exclusive | unresolved |
| --- | --- | --- | --- | --- | --- | --- |
| L0 | login (ping/login/logout) | 4 | 234 | 0 (0, 0) | 0 | 4: 0.0.1 0.0.2 0.2.1 0.2.2 |
| L1 | login (challenge) | 2 | 126 | 0 (0, 0) | 0 | 2: 1.0.1 1.0.2 |
| L2 | login (session/settings) | 5 | 208 | 2 (83, 0) | 0 | 3: 2.1.1 2.1.2 2.2.1 |
| L3 | login (error messages) | 3 | 492 | 1 (410, 0) | 0 | 2: 3.0.1 3.0.2 |
| L4 | login (GP course) | 2 | 82 | 1 (41, 1) | 0 | 1: 4.0.1 |
| L5 | login (character list) | 5 | 177 | 2 (84, 1) | 0 | 3: 5.0.1 5.1.2 5.5.16 |
| 0 | CONNECTION | 15 | 4765 | 14 (4763, 3) | 0 | 1: 0.10.16 |
| 1 | SERVER | 10 | 428 | 10 (428, 1) | 0 | 0 |
| 2 | CHARACTER | 23 | 397 | 15 (313, 0) | 0 | 8: 2.5.16 2.6.16 2.27.16 2.28.16 2.29.16 2.30.16 2.31.16 2.32.16 |
| 3 | LOBBY | 7 | 1337 | 7 (1337, 1) | 0 | 0 |
| 5 | USER | 2 | 310 | 0 (0, 0) | 0 | 2: 5.2.16 5.3.16 |
| 6 | PARTY | 11 | 271 | 8 (184, 1) | 0 | 3: 6.8.16 6.10.16 6.18.16 |
| 8 | PAWN | 20 | 936 | 19 (927, 0) | 0 | 1: 8.37.16 |
| 9 | BINARY | 1 | 47 | 1 (47, 0) | 0 | 0 |
| 10 | ITEM | 14 | 787 | 11 (725, 1) | 0 | 3: 10.0.16 10.10.16 10.14.16 |
| 11 | QUEST | 79 | 4352 | 60 (3066, 9) | 8: 11.5.1 11.5.2 11.121.1 11.121.2 11.122.1 11.122.2 11.123.1 11.123.2 | 11: 11.7.16 11.39.16 11.60.16 11.68.16 11.70.16 11.83.16 11.88.16 11.95.16 11.103.16 11.117.16 11.118.16 |
| 12 | STAGE | 6 | 351 | 3 (342, 0) | 2: 12.5.1 12.5.2 | 1: 12.9.16 |
| 13 | INSTANCE | 32 | 5617 | 21 (4279, 5) | 4: 13.16.1 13.16.2 13.17.1 13.17.2 | 7: 13.1.16 13.2.16 13.20.16 13.23.16 13.31.16 13.32.16 13.42.16 |
| 14 | WARP | 18 | 993 | 14 (790, 2) | 2: 14.14.1 14.14.2 | 2: 14.10.16 14.11.16 |
| 15 | (none) | 2 | 16 | 0 (0, 0) | 0 | 2: 15.0.16 15.1.16 |
| 16 | FRIEND | 4 | 164 | 4 (164, 0) | 0 | 0 |
| 17 | BLACK | 2 | 82 | 2 (82, 0) | 0 | 0 |
| 18 | GROUP | 1 | 41 | 1 (41, 0) | 0 | 0 |
| 19 | SKILL | 4 | 102 | 4 (102, 0) | 0 | 0 |
| 20 | SHOP | 4 | 70 | 4 (70, 1) | 0 | 0 |
| 23 | AREA | 4 | 228 | 4 (228, 0) | 0 | 0 |
| 24 | JOB_MASTER | 1 | 150 | 0 (0, 0) | 0 | 1: 24.6.16 |
| 25 | ORB | 2 | 86 | 2 (86, 0) | 0 | 0 |
| 26 | PROFILE | 6 | 174 | 6 (174, 2) | 0 | 0 |
| 27 | ACHIEVEMENT | 14 | 127 | 10 (94, 0) | 2: 27.10.1 27.10.2 | 2: 27.8.16 27.9.16 |
| 28 | GP | 25 | 451 | 18 (222, 2) | 4: 28.23.1 28.23.2 28.34.1 28.34.2 | 3: 28.24.16 28.25.16 28.26.16 |
| 29 | EQUIP | 10 | 125 | 9 (123, 0) | 0 | 1: 29.23.16 |
| 30 | CRAFT | 10 | 32 | 10 (32, 4) | 0 | 0 |
| 31 | CLAN | 14 | 341 | 11 (259, 2) | 2: 31.40.1 31.53.1 | 1: 31.53.2 |
| 33 | JOB | 9 | 1768 | 8 (1754, 5) | 0 | 1: 33.20.16 |
| 34 | ENTRY | 13 | 17 | 9 (13, 1) | 2: 34.0.1 34.0.2 | 2: 34.6.16 34.16.16 |
| 37 | MAIL | 17 | 533 | 17 (533, 0) | 0 | 0 |
| 39 | GACHA | 4 | 94 | 4 (94, 0) | 0 | 0 |
| 41 | CHARACTER_EDIT | 6 | 12 | 2 (2, 1) | 4: 41.5.1 41.5.2 41.8.1 41.8.2 | 0 |
| 43 | LOADING | 2 | 84 | 2 (84, 0) | 0 | 0 |
| 44 | CERT | 2 | 249 | 2 (249, 1) | 0 | 0 |
| 45 | STAMP | 8 | 412 | 4 (330, 2) | 4: 45.3.1 45.3.2 45.4.1 45.4.2 | 0 |
| 50 | ITEM | 5 | 258 | 4 (210, 1) | 0 | 1: 50.0.16 |
| 51 | DISPEL | 3 | 3 | 3 (3, 0) | 0 | 0 |
| 52 | MY | 1 | 20 | 1 (20, 0) | 0 | 0 |
| 53 | PARTNER | 9 | 265 | 8 (242, 0) | 0 | 1: 53.9.16 |
| 54 | CRAFT | 2 | 6 | 2 (6, 1) | 0 | 0 |
| 57 | BOX | 1 | 3 | 1 (3, 0) | 0 | 0 |
| 58 | PAWN | 14 | 368 | 14 (368, 3) | 0 | 0 |
| 59 | INFINITY | 8 | 10 | 0 (0, 0) | 8: 59.0.1 59.0.2 59.4.1 59.4.2 59.8.1 59.8.2 59.9.1 59.9.2 | 0 |
| 60 | NPC | 1 | 219 | 0 (0, 0) | 1: 60.0.2 | 0 |
| 61 | PAWN | 2 | 40 | 0 (0, 0) | 2: 61.2.1 61.2.2 | 0 |
| 62 | SEASON | 35 | 1508 | 0 (0, 0) | 35: 62.0.1 62.0.2 62.1.1 62.1.2 62.7.1 62.7.2 62.8.1 62.8.2 62.9.1 62.9.2 62.10.1 62.10.2 62.12.16 62.14.16 62.15.16 62.16.16 62.18.1 62.18.2 62.20.1 62.20.2 62.22.16 62.23.16 62.24.1 62.24.2 62.26.16 62.27.16 62.33.1 62.33.2 62.34.1 62.34.2 62.35.1 62.35.2 62.38.16 62.39.16 62.40.16 | 0 |
| 63 | (none) | 8 | 45 | 0 (0, 0) | 0 | 8: 63.0.16 63.1.16 63.2.16 63.3.16 63.5.16 63.6.16 63.7.16 63.10.16 |
| 64 | MANDRAGORA | 1 | 20 | 0 (0, 0) | 1: 64.0.1 | 0 |
| 65 | EQUIP | 2 | 4 | 0 (0, 0) | 2: 65.3.1 65.3.2 | 0 |
| 70 | ACTION | 2 | 624 | 0 (0, 0) | 2: 70.0.1 70.0.2 | 0 |
| 71 | BATTLE | 2 | 84 | 0 (0, 0) | 2: 71.22.1 71.22.2 | 0 |
| 72 | DAILY | 7 | 322 | 0 (0, 0) | 7: 72.0.1 72.0.2 72.1.16 72.2.1 72.2.2 72.3.1 72.3.2 | 0 |


## Suggested batch order

1. **Login** (L0-L5, 21 ids, 1,319 packets): T002, every direction; 15 ids still need a code match.
2. Then the game groups by matched captured packets (group, name, matched ids, their packets):
   1. 0 CONNECTION (14 ids, 4763 pkts)
   2. 13 INSTANCE (21 ids, 4279 pkts)
   3. 11 QUEST (60 ids, 3066 pkts)
   4. 33 JOB (8 ids, 1754 pkts)
   5. 3 LOBBY (7 ids, 1337 pkts)
   6. 8 PAWN (19 ids, 927 pkts)
   7. 14 WARP (14 ids, 790 pkts)
   8. 10 ITEM (11 ids, 725 pkts)
   9. 37 MAIL (17 ids, 533 pkts)
   10. 1 SERVER (10 ids, 428 pkts)
   11. 58 PAWN (14 ids, 368 pkts)
   12. 12 STAGE (3 ids, 342 pkts)
   13. 45 STAMP (4 ids, 330 pkts)
   14. 2 CHARACTER (15 ids, 313 pkts)
   15. 31 CLAN (11 ids, 259 pkts)
   16. 44 CERT (2 ids, 249 pkts)
   17. 53 PARTNER (8 ids, 242 pkts)
   18. 23 AREA (4 ids, 228 pkts)
   19. 28 GP (18 ids, 222 pkts)
   20. 50 ITEM (4 ids, 210 pkts)
   21. 6 PARTY (8 ids, 184 pkts)
   22. 26 PROFILE (6 ids, 174 pkts)
   23. 16 FRIEND (4 ids, 164 pkts)
   24. 29 EQUIP (9 ids, 123 pkts)
   25. 19 SKILL (4 ids, 102 pkts)
   26. 27 ACHIEVEMENT (10 ids, 94 pkts)
   27. 39 GACHA (4 ids, 94 pkts)
   28. 25 ORB (2 ids, 86 pkts)
   29. 43 LOADING (2 ids, 84 pkts)
   30. 17 BLACK (2 ids, 82 pkts)
   31. 20 SHOP (4 ids, 70 pkts)
   32. 9 BINARY (1 ids, 47 pkts)
   33. 18 GROUP (1 ids, 41 pkts)
   34. 30 CRAFT (10 ids, 32 pkts)
   35. 52 MY (1 ids, 20 pkts)
   36. 34 ENTRY (9 ids, 13 pkts)
   37. 54 CRAFT (2 ids, 6 pkts)
   38. 51 DISPEL (3 ids, 3 pkts)
   39. 57 BOX (1 ids, 3 pkts)
   40. 41 CHARACTER_EDIT (2 ids, 2 pkts)

3. Unresolved ids join their group's batch and are decided there (or move to the exclusive list).
4. Exclusive list for the later spec: the 94 `exclusive` rows of `T001-triage.tsv` (groups 59-62,
   64, 65, 70-72 whole; plus 11.5, 11.121-123, 12.5, 13.16-17, 14.14, 27.10, 28.23, 28.34, 31.40,
   31.53.1, 34.0, 41.5, 41.8, 45.3-4, 60.0.2).
