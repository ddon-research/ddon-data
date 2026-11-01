# P11b: evidence for the old packet patterns, batch B (18 packets)

Brief: `specs/005-netmsg-patterns/briefs/P11-old-patterns-evidence.md` (committed at 007e296a9d), batch B.
Base c748cd3a53. This report edits nothing; it lists what P12 must fix. It reuses the method, marks and
common findings G1-G6 of `P11a-old-patterns.md` and extends its shared-structure table.

## What ran

- PC 03040008 (Season 3 truth): private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-p11b/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (`bash research/ida/private-copy.sh pc p11b`), ida-mcp instance `81556246c0f2`; `idc.get_idb_path()`
  returned that path, 32-bit, image base `0x400000`.
- PS4 02020005 (seed, symbols): private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-p11b/DDOORBIS.elf.i64`, instance
  `9178a58add91`; 64-bit, image base `0`. DWARF types and `nError::ERROR_CODE` read through `ida_typeinf`.
- Read-only: Hex-Rays, `ida_ua` decode of undefined bytes, xrefs, byte search. No rename, retype, comment,
  function creation or save. Address basis: IDA VA per database.
- Marks as P11a: **V** read in IDA (PC unless "PS4"), **I** inferred, **C** contradicts the pattern,
  **PC-cap** from 03040008 captures, **unresolved**.
- Method (PC). S2C: handler from its name string `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>`, or from
  a static handler table when the string has no xref (group 23 initializer `0x1a27840` writes 16 handlers
  into entries at `0x212AD38`, stride 0x18, key `(sub<<16)|id` at +0x10). Group/id/sub **V** from the
  immediates the handler or packet ctor stores (+4/+6/+8). Reader = function called with
  `(packetObj, CPacket*)`; wire order = order of `nPacket::Read_*` calls, traced recursively (undefined
  code decoded with `ida_ua`). C2S: Hex-Rays over the 642 functions containing the 658
  `nUserSession::CPacket::WritePacket` (`0x8bcbb0`) call sites, matched on `WritePacket(p, g, id, sub, -1)`.
- PS4 counterparts matched by code: the PS4 `OnPacket_*` / `ReadPacket` / `Send_*` read or write the same
  sequence; names then from PS4 symbols and DWARF.
- Captures: every `packets/decrypted_raw/*/*.<g>_<id>_<sub>` file of the 18 suffixes (for 0_1_1 / 0_1_2
  only the `C2L_` / `L2C_` files; the game-server `C2S/S2C_CONNECTION_LOGIN_*` share the suffix),
  1,098 files, walked in the ida-mcp Python session with the PC layouts. Framing as P11a: body from
  offset 9; ok = no read past the end and slack 0..15. Also walked: the pattern's layout where it differs.
- Server (`D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline`, `Arrowgene.Ddon.Shared/Entity/PacketStructure`)
  opened for 23.13.16, 23.11.2, 13.3.2 only; lead, never evidence.

## Common findings added by batch B

| # | Finding | Evidence | Mark |
| --- | --- | --- | --- |
| G1b | G1 holds for all 13 S2C RES of the batch (readers `0x8034d0`, `0x8035e0`, `0x8043c0`, `0x800150`, `0x7fff90`, `0x80c420`, `0x812500`, `0x80ad10`, `0x81b220`, `0x81b120`, `0x809d80`, L2C `0x889920`): `s32 Error`; if non-zero, copy to Result and stop. 14 of the batch patterns declare `u32 Error` (only 18.0.2 has `s32`). | PC readers | V |
| G2b | Unlike batch A, batch B captures **do exercise G1**: 63 files have Error != 0. 19.1.2 (4/4) and 19.2.2 (16/16): Error `0x3a9d`, file 16 B, nothing after Error; 13.3.2 (2/412): Error `0x3e90`, nothing after; 18.0.2 (41/41): Error `0xb79b`, but the server still writes Result and an empty list (the client ignores them, so slack is 19). PS4 `nError::ERROR_CODE` names: `0x3a9d` CHARACTER_PARAM_NOT_FOUND, `0x3e90` INSTANCE_AREA_ENEMY_NOT_CREATED, `0xb79b` GROUP_CHAT_NOT_IN_GROUP (V PS4; same meaning on PC is I). | walk; PS4 DWARF | PC-cap / V |
| G7 | The slack criterion (0..15) does not catch short layouts: the 23.13.16 pattern (13 bytes short) and the 23.11.2 pattern (fits because two lists are always empty) both "pass". A pattern-layout pass is not evidence of correctness. | walk | PC-cap |

## Per pattern

Items: (1) status; (2) PC reader/writer and how found; (3) wire and PS4 counterpart; (4) errors and gaps;
(5) shared structures; (6) capture walk; (7) raw name. "RES" = `s32 Error` + guarded `s32 Result`.

### 1. C2S_CLAN_GET_MY_INFO_REQ (31.29.1)

1. **finished**. V
2. Writer `0x822af0`: `WritePacket(0x1F, 29, 1, -1)`, no body. Name by pairing with handler `0x7cb2b0`
   (string `0x1bce704` "…OnPacket_CLAN_CLAN_GET_MY_INFO_RES", stores 31, 29, 2). V / I (pairing)
3. Wire: empty. PS4 `cSeedGameSvConnection::Send_C2S_CLAN_GET_MY_INFO_REQ` `0x19c43a0` writes only the
   u16 header triple; DWARF `CPacket_C2S_CLAN_GET_MY_INFO_REQ` has no wire member. V (PS4)
4. Errors: none (only G4). V
6. Walk: 41/41 ok. `stream1-marked.pcapng_tcp-stream-35/12064_C2S_CLAN_CLAN_GET_MY_INFO_REQ_...31_29_1`
   (16 B, SHA-256 prefix `b32e65d62e342fc9`): header only, end 0x9, slack 7.
7. Raw name: `C2S_CLAN_CLAN_GET_MY_INFO_REQ` (pattern file lacks the second `CLAN_`).

### 2. C2L_LOGIN_REQ (0.1.1, login server)

1. **finished**. V
2. Writer `0x88a390`: `WritePacket(0, 1, 1, -1)`, `Write_cstr`, `Write_u8`. A second (0, 1, 1) writer,
   `0x8243b0`, writes cstr, u8, **u32**: that is the game-server `C2S_CONNECTION_LOGIN_REQ`. `0x88a390`
   is the login-server one by code: PS4 `cSeedLoginSvConnection::Send_C2L_LOGIN_REQ` `0x1a3c1f0` writes
   `Write_MT_CSTR`, `Write_u8` (V PS4); it sits in the login packet block (`0x889f40`-`0x88a980`, groups
   0-5) beside the L2C reader of item 3 (class attribution I). `nPacket::Write_cstr` `0x8bca30` writes a
   u16 BE length + bytes, the MtString wire. V
3. Wire: MtString OnetimeToken, u8 Platform (PS4 DWARF `nLoginSession::CPacket_C2L_LOGIN_REQ`:
   `m_wstrOnetimeToken`, `m_ucPlatform`). V
4. Errors: none. V
6. Walk: 42/42 ok. `stream6-annilot-hobo-marked.pcapng_tcp-stream-0/9_C2L_LOGIN_REQ_...0_1_1` (48 B,
   `d6a00d2253eb7b19`): 0x09 token length 31 (content not reproduced), 0x2a Platform 1, end 0x2b, slack 5.
7. Raw name: `C2L_LOGIN_REQ`.

### 3. L2C_LOGIN_RES (0.1.2, login server)

1. **partial** (wrong header types, invented trailing pad). V
2. Reader `0x889920`, called at `0x8866a2` from handler code `0x886650` (not a function) that stores
   0, 1, 2. That handler is entry key `0x20001` of the table at `0x1bd6270` ({handler, key} pairs, group 0
   of the group directory `0x1bd67f4`, referenced from `0x88aae2` in the login block). V
   The game-server `CONNECTION_LOGIN_RES` reader (`0x804a50`, via `0x7ce490`) differs: s32, s32, **bool**,
   MtString. V
3. Wire: RES, MtString OnetimeToken. PS4 `cSeedLoginSvConnection::OnPacket_L2C_LOGIN_RES` `0x37c800`
   reads u16, s32, MtString (`nLoginSession::CPacket_L2C_LOGIN_RES`). V
4. Errors:
   - `u32 Error; u32 Result` unconditional: G1. V
   - **`u8 pad[14]` is not a field**: the client reads nothing after the token (`0x889920`). The 14 bytes
     are the 16-byte block padding; slack is 14 in all 42 captures only because the token length is
     constant (31). V (C)
6. Walk: 42/42 ok; slack 14 in every file. `stream1-marked.pcapng_tcp-stream-33/11762_L2C_LOGIN_RES_...0_1_2`
   (64 B, `10bab0530cbe264b`): Error 0, Result 0, 0x11 token length 31, end 0x32, slack 14.
7. Raw name: `L2C_LOGIN_RES`.

### 4. S2C_CLAN_GET_MY_INFO_RES (31.29.2)

1. **finished** (layout right). V
2. Handler `0x7cb2b0` (string `0x1bce704`; on-stack 31, 29, 2), reader `0x8034d0`. V
3. Wire (V): RES; CDataClanParam `0x75d730` = ClanUserParam `0x75e3e0` {MtString, MtString, u8 x4,
   u32 x4, bool, MtString, MtString, s64} + ClanServerParam `0x75dc60` {u32, u16, u16, ClanMemberInfo
   `0x75d640`, bool x3, u32 x3}; s64 LeaveTime. ClanMemberInfo {u32, s64 x3, u32,
   CDataCharacterListElement `0x75ccf0`}. PS4 `CPacket_S2C_CLAN_GET_MY_INFO_RES::ReadPacket` `0x19db590`:
   same sequence; PS4 CharacterListElement lacks the trailing u8. V (PS4)
4. Errors: G1 only. The pattern's trailing `u8 unknown` in CharacterListElement is right (S3). V
5. Shared: ClanMemberInfo, CharacterListElement, JobBaseInfo (table below).
6. Walk: 41/41 ok. `stream1-marked.pcapng_tcp-stream-35/12065_S2C_CLAN_CLAN_GET_MY_INFO_RES_...31_29_2`
   (176 B, `98a256b9d54e5d70`): Error 0, Result 0, UserParam 0x11→0x46, ServerParam 0x46→0x9d,
   LeaveTime 0 at 0x9d, end 0xa5, slack 11.
7. Raw name: `S2C_CLAN_CLAN_GET_MY_INFO_RES`.

### 5. S2C_CLAN_SETTING_UPDATE_RES (31.17.2)

1. **stub, does not compile**: the struct derives from undefined `CPacketDataBase` and there is no
   placement statement. V
2. Handler `0x7cd0e0` (string `0x1bceadc`; on-stack 31, 17, 2), reader `0x8043c0`. V
3. Wire: RES only. PS4 `OnPacket_S2C_CLAN_SETTING_UPDATE_RES` `0x31ab10` reads u16, s32. V (PS4)
4. Errors: base type `CPacketDataBase` (should be `CPacket`); no `@ 0x00` placement; G1. V (C)
6. Walk: 42/42 ok. `stream1-marked.pcapng_tcp-stream-34/11899_..._31_17_2` (32 B, `038605c2c0c79108`):
   Error 0, Result 0, end 0x11, slack 15.
7. Raw name: `S2C_CLAN_CLAN_SETTING_UPDATE_RES`.

### 6. S2C_CLAN_GET_MY_MEMBER_LIST_RES (31.4.2)

1. **finished**. V
2. Handler `0x7cb470` (string `0x1bce618`; on-stack 31, 4, 2), reader `0x8035e0`. V
3. Wire: RES; list (`0x75d580`) of ClanMemberInfo (`0x75d640`). PS4 `OnPacket_S2C_CLAN_GET_MY_MEMBER_LIST_RES`
   `0x317210`: u16, s32, `Read_CDataClanMemberInfo_`. V
4. Errors: G1 only. V
6. Walk: 41/41 ok, list non-empty in 41. `stream85-marked.pcapng_tcp-stream-11/10279_..._31_4_2` (96 B,
   `d8e33f31a336cf1e`): Error 0, Result 0, 0x11 n=1; 0x15 Rank 1, Created, LastLoginTime, LeaveTime 0,
   Permission 0x1ffe; CharacterID, names of length 6 and 4, clan name 3, ServerID 5, OnlineStatus 1,
   CurrentJob {9, 99}, EntryJob {0, 0}, profile length 0, S3 u8 0; end 0x56, slack 10.
7. Raw name: `S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES`.

### 7. S2C_AREA_23_13_16_NTC (23.13.16)

1. **stub / wrong** (2 of 6 fields). V
2. Handler `sub_7c38c0` (group-23 table entry key 16/13; on-stack 23, 13, 16), reader `0x7ffa60`. V
3. Wire (V): u32, u32, u32, u32, u32, bool. PS4 match by code: `CPacket_S2C_AREA_POINT_UP_NTC::ReadPacket`
   `0x19da9f0` reads u16 + 5 x u32 + bool; DWARF names m_unAreaID, m_unAddPoint, m_unAddPointByCharge,
   m_unTotalPoint, m_unWeekPoint, m_bCanRankUp (V PS4). PC handler behaviour agrees: it looks up the
   area by +16, formats +20 and +24 with "%d" into message 0xB6, and stores +28, +32 and the bool (V).
4. Errors: **missing AddPointByCharge, TotalPoint, WeekPoint, CanRankUp**; `AreaPoints` is AddPoint. No
   error field (G3 holds). Name should be `S2C_AREA_POINT_UP_NTC`. V (C)
6. Walk: PC layout 29/29 ok; pattern layout also "ok" 29/29 (G7: 13 bytes short, inside the 0..15 slack).
   `stream21-failedlogin-marked.pcapng_tcp-stream-48/13476_S2C_AREA_POINT_UP_NTC_...23_13_16` (32 B,
   `28766441ccb97d1d`): AreaID 0x10, AddPoint 0x5dc, ByCharge 0, Total 0x6338, Week 0x5dc, CanRankUp 0,
   end 0x1e, slack 2.
7. Raw name: `S2C_AREA_POINT_UP_NTC`. Server lead agrees with the PC reader.

### 8. C2S_AREA_GET_SPOT_INFO_LIST_REQ (23.11.1)

1. **finished**. V
2. Writer `0x81e930`: `WritePacket(0x17, 11, 1, -1)`, `Write_u32`. Pairs with 23.11.2 (I). V
3. Wire: u32 AreaID. PS4 `Send_C2S_GET_SPOT_INFO_LIST_REQ` `0x19c2330`: header + u32 (m_unAreaID). V
4. Errors: none; unused `SpotEnemyInfoVec`/`SpotItemInfoVec` defines and `b8`. V
6. Walk: 29/29 ok. `stream21-failedlogin-marked.pcapng_tcp-stream-48/13718_..._23_11_1` (16 B,
   `37b3fae07234c27c`): u32 0x11, slack 3.
7. Raw name: `C2S_AREA_GET_SPOT_INFO_LIST_REQ`.

### 9. C2S_AREA_GET_AREA_SUPPLY_REQ (23.4.1)

1. **finished**. V
2. Writer `0x81e760`: `WritePacket(0x17, 4, 1, -1)`, `Write_u32`, `Write_u8`, list writer `0x780ea0`
   (u32 count, {u32, u8}). Pairs with 23.4.2 (handler `0x7c4570`, string `0x1bcd8d0`
   "…OnPacket_AREA_GET_AREA_SUPPLY_RES", reader `0x800020`: RES only). V
3. Wire: u32 AreaID, u8 StorageType, list {u32 Index, u8 Num}. PS4
   `CPacket_C2S_GET_AREA_SUPPLY_REQ::WritePacket` `0x1a34990`: u32, u8, u32 count, {u32, u8}. V
4. Errors: none. V
6. Walk: 12/12 ok. `stream61-remarked.pcapng_tcp-stream-11/11338_..._23_4_1` (64 B, `85205bdaaed74130`):
   AreaID 0x11, StorageType 0x13, list n=8 0xe→0x3a, slack 6.
7. Raw name: `C2S_AREA_GET_AREA_SUPPLY_REQ`.

### 10. S2C_AREA_GET_AREA_SUPPLY_INFO_RES (23.3.2)

1. **finished**. V
2. Handler code `0x7c44c0` (group-23 table key 2/3; not a function) calls ctor `0x785d70` (0x17, 3, 2),
   reader `0x7fff90` (undefined bytes, decoded), and pushes string `0x1bcd87c`
   "…OnPacket_AREA_GET_AREA_SUPPLY_INFO_RES" at `0x7c454d`. V
3. Wire: RES; u8 SupplyGrade; list (`0x7773b0`) of {u32 Index, u32 ItemId, u8 Num}. PS4
   `OnPacket_S2C_GET_AREA_SUPPLY_INFO_RES` `0x302af0`: u16, s32, u8, `Read_CDataRewardItemInfo_`. V
4. Errors: G1 only. Note: the request 23.3.1 (writer `0x81e680`, one u32) has no pattern. V
6. Walk: 13/13 ok, list non-empty in 13. `stream69-epi-2-2-marked.pcapng_tcp-stream-11/11176_..._23_3_2`
   (112 B, `da655c0b60ccf5c3`): Error 0, Result 0, grade 1, list n=9 0x12→0x67, slack 9.
7. Raw name: `S2C_AREA_GET_AREA_SUPPLY_INFO_RES`.

### 11. S2C_AREA_GET_SPOT_INFO_LIST_RES (23.11.2)

1. **partial / wrong tail**. V
2. Handler `0x7c46b0` (string `0x1bcdb28`), ctor `0x785e70`, reader `0x800150`. V
3. Wire (V): RES; list (`0x779cf0`) of CDataSpotInfo (`0x779db0`: u32 SpotID, u32 TextIndex, u32 StageID,
   bool IsRelease, bool IsNew, list {u32, u8} (`loc_779c00`), list {u32, u8} (`0x779e50`), u32
   QuickPartyPopularity); **list {u32, u32, s64} (`0x7696e0`); list {u32, bool, s64} (`0x76d440`); list
   u32 (`0x75e8e0`)**. PS4 `OnPacket_S2C_GET_SPOT_INFO_LIST_RES` `0x303540` reads u16, s32,
   `Read_CDataSpotInfo_` only (same SpotInfo); the three bold lists are S3. V
4. Errors:
   - **`u32 Unknown1` is the count of list `0x7696e0`** {u32, u32, s64}, not a scalar. V (C)
   - `CDataSpotInfoS3` = list `0x76d440`: types right except **u64 → s64** (`R.s64`). V
   - **Trailing list u32 (`0x75e8e0`) missing.** V (C)
   - The two S3 lists `0x7696e0` / `0x76d440` are the same readers as 23.8.2 lists 2 and 3 (P11a §15). V
   - G1. Names of the S3 lists unresolved (server lead: MonsterGatheringSpots, PeriodicallyReleasedSpots,
     SpotAlertList).
6. Walk: PC 29/29 ok; pattern layout also "ok" 29/29 (G7) because list 2 and list 4 are empty in every
   capture (list 1 and list 3 non-empty in 29). `stream21-failedlogin-marked.pcapng_tcp-stream-48/13720_..._23_11_2`
   (512 B, `ae976f693eb028a5`): Error 0, Result 0, list n=16 0x11→0x1b5 (first element 0x15: SpotID 884,
   TextIndex 0, StageID 373, 1, 0, two empty lists, 0; next at 0x2f); list n=0 0x1b5→0x1b9; list n=4
   0x1b9→0x1f1 ({1068, 0, 1564084800}, {1070, …}, {1076, …}, {1080, …}, 13 B each); list n=0
   0x1f1→0x1f5; slack 11.
7. Raw name: `S2C_AREA_GET_SPOT_INFO_LIST_RES`. Server lead agrees with the PC reader (four lists).

### 12. C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ (60.0.1)

1. **finished**. V
2. Writer `0x830cf0`: `WritePacket(0x3C, 0, 1, -1)`, `Write_u32`. Pairs with the 60.0.2 handler code
   `0x7e6300` (ctor stores 0x3C, 0, 2; pushes string `0x1bca248`
   "…OnPacket_NPC_GET_NPC_EXTENDED_FACILITY_RES" at `0x7e6396`; reader `0x80ff90`, not traced). V / I
3. Wire: u32 (name NpcID from the pattern/server: I). PS4 counterpart: **none** (no symbol or DWARF type
   `*NPC_GET_NPC_EXTENDED_FACILITY*` in 02020005). V (PS4)
4. Errors: none in layout; field name not evidenced. V
6. Walk: 219/219 ok. `stream1-marked.pcapng_tcp-stream-35/12804_..._60_0_1` (16 B, `de019d19c31498c1`):
   u32 0x125e, slack 3.
7. Raw name: `C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ`.

### 13. S2C_ITEM_GET_ITEM_STORAGE_INFO_RES (10.9.2)

1. **finished**. V
2. Handler `0x7dd070` (string `0x1bd1f24`), ctor `0x789240`, reader `0x80c420`; list reader `0x7688e0`
   (mid-function, decoded): u32 count, {u8, u16, u16}. V
3. Wire: RES; list {u8 StorageType, u16 UsedSlotNum, u16 MaxSlotNum}. PS4 `OnPacket_S2C_GET_ITEM_STORAGE_INFO_RES`
   `0x3336a0`: u16, s32, `Read_CDataGameItemStorageInfo_`. V
4. Errors: G1 only; unused `MtString`, `f64`. V
6. Walk: 4/4 ok. `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/27180_..._10_9_2` (32 B,
   `2c360336d52ee832`): list n=1 0x11→0x1a, slack 6.
7. Raw name: `S2C_ITEM_GET_ITEM_STORAGE_INFO_RES`.

### 14. S2C_GET_NORA_PAWN_LIST_RES_RES (8.30.2)

1. **finished**. V
2. Handler `0x7eacd0` (string `0x1bc7990` "…OnPacket_PAWN_GET_NORA_PAWN_LIST_RES"; on-stack 8, 30, 2),
   reader `0x812500`. V
3. Wire: RES; list (`0x776610`) of CDataRegisterdPawnList (`0x7766d0`: s32, MtString, u8, u32, u64,
   PawnListData `0x772750` {u8, u32, u32, list {u8, u32} (`0x771c80`), u32, u64}). PS4
   `Read_CDataRegisterdPawnList_` (via `OnPacket_S2C_GET_NORA_PAWN_LIST_RES` `0x2e8a20`): identical. V
4. Errors: G1 only; file name has a doubled `_RES`. V
6. Walk: 41/41 ok, list non-empty in 41. `stream1-marked.pcapng_tcp-stream-35/12150_..._8_30_2`
   (4,432 B, `027e93d1c9f34320`): list n=100 0x11→0x1145, slack 11.
7. Raw name: `S2C_PAWN_GET_NORA_PAWN_LIST_RES`.

### 15. S2C_ENEMY_KILL_RES (13.3.2)

1. **finished** in layout; header wrong and the error case breaks it. V
2. Handler `0x7dac80` (string `0x1bc9b9c` "…OnPacket_INSTANCE_ENEMY_KILL_RES"; on-stack 13, 3, 2), reader
   `0x80ad10`. Request writer 13.3.1: `0x8413d0` (not in batch). V
3. Wire: RES; u32 EnemyID, u32 KillNum. PS4 `OnPacket_S2C_ENEMY_KILL_RES` `0x2f3f10`: u16, **u32**
   m_unResult, u32, u32. PC reads Result as s32. V
4. Errors: `u32 Error; u32 Result` unconditional (G1): **fails on the 2 error captures** (16 B files with
   only Error `0x3e90`; the pattern reads past the end). Result signedness: s32 on PC. V (C)
6. Walk: PC 412/412 ok (2 with Error != 0); pattern 410/412. `stream85-marked.pcapng_tcp-stream-11/100895_..._13_3_2`
   (32 B, `e2b3d3d218e01c4b`): Error 0, Result 0, EnemyID 0x10230, KillNum 1, end 0x19, slack 7.
   Error case: `.../146897_S2C_INSTANCE_ENEMY_KILL_RES_...13_3_2` (16 B): Error 0x3e90, end 0xd, slack 3.
7. Raw name: `S2C_INSTANCE_ENEMY_KILL_RES`. Server lead agrees.

### 16. S2C_GET_ACQUIRABLE_SKILL_LIST_RES (19.1.2)

1. **finished** in layout; header wrong; body never exercised. V
2. Handler `0x7fab30` (string `0x1bcc438` "…OnPacket_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES"), ctor `0x78cfa0`,
   reader `0x81b220`. V
3. Wire: RES; list (`0x778d30`) of {u32 SkillNo, u8 Job, u8 Type, list (`0x778c10`) {u8 Lv, u32, u32,
   bool}}. PS4 `OnPacket_S2C_GET_ACQUIRABLE_SKILL_LIST_RES` `0x2fbea0` + DWARF CDataSkillParam /
   CDataSkillLevelParam: identical. V
4. Errors: G1; **pattern fails on all 4 captures** (all are Error `0x3a9d`, 16 B, nothing after Error). V (C)
6. Walk: PC 4/4 ok (all errors); pattern 0/4. `stream1-marked.pcapng_tcp-stream-35/26339_..._19_1_2`
   (16 B, `5b6d16f6008ab39f`): Error 0x3a9d, end 0xd, slack 3. The list layout has no capture.
7. Raw name: `S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES`.

### 17. S2C_GET_ACQUIRABLE_ABILITY_LIST_RES (19.2.2)

1. **finished** in layout; error branch invented; body never exercised. V
2. Handler `0x7fa990` (string `0x1bcc4a0`), reader `0x81b120`; list reader `loc_758220` (not a function,
   decoded) → element `0x758320`. V
3. Wire: RES; list of {u32 AbilityNo, u8 Job, u8 Category, u8 SortCategory, u8 Type, u32 Cost, list
   (`0x758100`) {u8 Lv, u32, u32, bool}}. PS4 `OnPacket_S2C_GET_ACQUIRABLE_ABILITY_LIST_RES` `0x2fc020` +
   DWARF CDataAbilityParam: identical. V
4. Errors: **`if (Error != 0) s16 Result` has no source**: the client reads nothing after a non-zero
   Error (`0x81b120`); the pattern then reads a list count and **fails on all 16 captures**. V (C)
6. Walk: PC 16/16 ok (all Error `0x3a9d`); pattern 0/16. `stream1-marked.pcapng_tcp-stream-35/26342_..._19_2_2`
   (16 B, `ad15b57afb5b77ef`): Error 0x3a9d, end 0xd, slack 3.
7. Raw name: `S2C_SKILL_GET_ACQUIRABLE_ABILITY_LIST_RES`.

### 18. S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES (18.0.2)

1. **finished** (the only batch pattern with IDA evidence in its header; its claims re-verified). V
2. Handler `0x7d8d40` (string `0x1bd08e0`; on-stack 18, 0, 2), reader `0x809d80`. V
3. Wire: RES; list (`0x75cbd0`) of CDataCharacterListElement (`0x75ccf0`). PS4
   `OnPacket_S2C_GROUP_CHAT_GET_MEMBER_LIST_RES` `0x2fb0d0`: u16, s32, `Read_CDataCharacterListElement`;
   PS4 element ends at the MtString (no S3 u8). V
4. Errors: the pattern reads Result and the list unconditionally (it says so in a comment); P12 should
   guard them (G1) and keep the trailing `BlockPadding`. V
6. Walk: 41/41 read by the PC reader without overrun, all Error `0xb79b`; slack 19 (> 15) because the
   server writes Result + empty list after the error (G2b). The pattern's walk reaches the end by its
   `BlockPadding`. `stream1-marked.pcapng_tcp-stream-35/12082_..._18_0_2` (32 B, `a391bc160ca6898d`):
   Error 0xb79b, client stops at 0xd; server bytes 0xd Result 0xb79b, 0x11 count 0. No member element in
   any capture.
7. Raw name: `S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES`.

## Shared structures (extends P11a's table; PC 03040008)

| Structure | PC reader (element / list) | Wire | Used by | PS4 type | Mark |
| --- | --- | --- | --- | --- | --- |
| CDataCharacterListElement | `0x75ccf0` (`nPacket::Read_CDataCharacterListElement_`, earlier user name) | u32, MtString x3, u16, u8, JobBaseInfo x2, MtString, **u8** | 31.29.2, 31.4.2 (via ClanMemberInfo), 18.0.2 (list `0x75cbd0`); also called by login-block `0x8878c0` | same name, no trailing u8 | V |
| CDataJobBaseInfo | `0x76b190` | u8, u8 | CharacterListElement | same | V |
| CDataClanMemberInfo | element `0x75d640`; list `0x75d580` | u32, s64 x3, u32, CharacterListElement | 31.4.2, ClanServerParam | same | V |
| CDataClanParam | `0x75d730` = UserParam `0x75e3e0` + ServerParam `0x75dc60` | section 4 | 31.29.2 | same | V |
| CDataSpotInfo | list `0x779cf0`, element `0x779db0`; sublists `loc_779c00`, `0x779e50` {u32, u8} | section 11 | 23.11.2 | same | V |
| S3 list {u32, u32, s64} | `0x7696e0` | | 23.8.2 (list 2), 23.11.2 (list 2) | none | V |
| S3 list {u32, bool, s64} | `0x76d440` | | 23.8.2 (list 3), 23.11.2 (list 3) | none | V |
| CDataCommonU32 list | `0x75e8e0` | u32 | add 23.11.2 (list 4) to P11a's users | CDataCommonU32 | V |
| CDataRewardItemInfo | list `0x7773b0` | u32, u32, u8 | 23.3.2 | same | V |
| CDataSelectItemInfo (writer) | list writer `0x780ea0` | u32, u8 | 23.4.1 | same | V |
| CDataGameItemStorageInfo | list `0x7688e0` (mid-function) | u8, u16, u16 | 10.9.2 | same | V |
| CDataRegisterdPawnList / PawnListData / PawnCraftSkill | list `0x776610`, element `0x7766d0`, `0x772750`, list `0x771c80` | section 14 | 8.30.2 | same | V |
| CDataSkillParam / SkillLevelParam | list `0x778d30`, list `0x778c10` | section 16 | 19.1.2 | same | V |
| CDataAbilityParam / AbilityLevelParam | list `loc_758220`, element `0x758320`, list `0x758100` | section 17 | 19.2.2 | same | V |
| Skill/Ability level param shape | `0x778c10`, `0x758100` | u8, u32, u32, bool (same shape, separate readers) | 19.1.2, 19.2.2 | two DWARF types | V |
| MtString via `Write_cstr` | `0x8bca30` | u16 BE length + bytes | 0.1.1 | MtString | V |

## Server disagreements met (lead only)

- Checked 23.13.16, 23.11.2, 13.3.2: the server agrees with the PC client (six NTC fields; four RES lists
  after the header; Result + EnemyId + KillNum). The patterns disagree with both.
- Not checked: the other server structures of the batch.

## Summary

| Pattern | Status | Errors found (beyond G1 RES header, G4 no include) | Walk ok (PC layout) |
| --- | --- | --- | --- |
| C2S_CLAN_GET_MY_INFO_REQ (31.29.1) | finished | none | 41/41 |
| C2L_LOGIN_REQ (0.1.1) | finished | none | 42/42 |
| L2C_LOGIN_RES (0.1.2) | partial | `u8 pad[14]` is block padding, not a field | 42/42 |
| S2C_CLAN_GET_MY_INFO_RES (31.29.2) | finished | none | 41/41 |
| S2C_CLAN_SETTING_UPDATE_RES (31.17.2) | stub | undefined base `CPacketDataBase`, no placement | 42/42 |
| S2C_CLAN_GET_MY_MEMBER_LIST_RES (31.4.2) | finished | none | 41/41 |
| S2C_AREA_23_13_16_NTC (23.13.16) | stub/wrong | 4 of 6 fields missing; is AREA_POINT_UP_NTC | 29/29 (pattern also "ok", G7) |
| C2S_AREA_GET_SPOT_INFO_LIST_REQ (23.11.1) | finished | none | 29/29 |
| C2S_AREA_GET_AREA_SUPPLY_REQ (23.4.1) | finished | none | 12/12 |
| S2C_AREA_GET_AREA_SUPPLY_INFO_RES (23.3.2) | finished | none | 13/13 |
| S2C_AREA_GET_SPOT_INFO_LIST_RES (23.11.2) | partial | `Unknown1` is a list count; s64 not u64; last u32 list missing | 29/29 (pattern also "ok", G7) |
| C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ (60.0.1) | finished | none (no PS4 counterpart) | 219/219 |
| S2C_ITEM_GET_ITEM_STORAGE_INFO_RES (10.9.2) | finished | none | 4/4 |
| S2C_GET_NORA_PAWN_LIST_RES_RES (8.30.2) | finished | file name doubles `_RES` | 41/41 |
| S2C_ENEMY_KILL_RES (13.3.2) | finished | fails on error captures (G1) | 412/412 (pattern 410/412) |
| S2C_GET_ACQUIRABLE_SKILL_LIST_RES (19.1.2) | finished, unexercised | fails on all captures (G1) | 4/4 errors (pattern 0/4) |
| S2C_GET_ACQUIRABLE_ABILITY_LIST_RES (19.2.2) | finished, unexercised | invented `s16 Result` error branch | 16/16 errors (pattern 0/16) |
| S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES (18.0.2) | finished | body not guarded by Error | 41/41 read; slack 19 (server extra bytes) |

Totals: 1,098 capture files over 18 suffixes; the PC readers never overrun (0 failures); 41 files (18.0.2)
exceed the slack bound only because the server writes past the client's stopping point. 63 files carry
Error != 0. Raw-name mismatches with the pattern file names: 31.29.1, 31.29.2, 31.17.2, 31.4.2, 23.13.16,
8.30.2, 13.3.2, 19.1.2, 19.2.2.

## Left open

- Names of the S3 lists of 23.11.2 (shared with 23.8.2) and of the 60.0.1 field: no PS4 type, no PC
  string; need the PC consumers.
- 19.1.2, 19.2.2 bodies and the 18.0.2 member list have no successful capture: V from code only.
- Login-server class attribution of `0x88a390` / `0x889920` rests on code match with PS4 and their place
  in the login block (I); the group directory `0x1bd67f4` was not traced to `cSeedLoginSvConnection`.
- The 60.0.2 reader `0x80ff90` and the 13.3.1 writer `0x8413d0` were not read (outside the batch).
