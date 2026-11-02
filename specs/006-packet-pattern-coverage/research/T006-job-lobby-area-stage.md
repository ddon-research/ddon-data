# 006 T006: groups 33 JOB, 3 LOBBY, 23 AREA, 12 STAGE

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T006-job-lobby-area-stage.md`; the 23 rows of groups 33, 3,
23 and 12 in `research/T001-triage.tsv` (9 + 7 + 4 + 3 ids). Base given `d378fe0a88`; head at start
`f7fd1b3ba0` (adds only the T007 brief). Marks: **V** verified in code (or by capture for walk
results), **I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t006/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t006/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `ida_ua.decode_insn`
  for linear decoding, `ida_typeinf` for DWARF structs); nothing renamed, retyped, commented, patched
  or reanalysed.
- PC primitives as T003/T005 § 0 (`nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32 0x8bc480`,
  `Read_u32 0x8bc4d0`, `Read_MtString 0x8bc5b0`, `Read_bool 0x8bc6e0`; `Write_* 0x8bc790-0x8bcb80`;
  `Write_cstr 0x8bca30` writes u16 BE length + bytes, i.e. an MtString on the wire; `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` -> group 3 `{0x212d720, 5}` (0.2, 1.2, 2.2, 2.16,
  4.16), group 12 `{0x212fbe0, 14}` (0.2-8.2, 9.16, 10.16, 11.2-13.2), group 23 `{0x212ad38, 16}`,
  group 33 `{0x212d3a8, 23}`; stride 0x18, key `(sub<<16)|id` at +0x10, handler stored by the
  initializers (`mov [esp], offset handler` before each `movq` into the entry). Every S2C `pc_va` of the
  triage equals its table handler (V). 33.20.16's handler `0x7e2770` also builds its packet object with
  group 33, id 20, sub 16 (V).
- **Not functions in the PC database** (decoded linearly, no database change): writer `0x82ede0`
  (3.0.1; the triage `pc_va 0x82ee53` is its `WritePacket` call), handlers `0x7e2e00` (3.1.2) and
  `0x7e29b0` (3.2.16), list reader `0x76d6f0` (IDA's function starts at `0x76d6ee`), list reader
  `0x77246d` (IDA's function starts one byte early at `0x77246c`, so Hex-Rays fails on it). The 12.5.1
  writer `0x842930` decompiles without its second argument (a list writer `0x77fd30`): read linearly.
- PS4 match by code only (symbol + body, DWARF members, or behaviour), never by PS4 id.
- RES header (V, every PC RES reader here: `0x80d9b0`, `0x80ea20`, `0x80eab0`, `0x80e8e0`, `0x81ca00`,
  `0x81ce40`, `0x800020`): `Read_s32` Error (+16); non-zero -> return; else `Read_s32` Result, body.
  PS4 reads `u16 m_usError, s32 m_nResult`. PC NTC readers read **no** header (V: `0x80d2b0`,
  `0x80d3a0`, `0x80d330`, `0x80e1c0`, `0x80e2d0`, `0x80e250`, `0x80e740`, `0x80e840`, `0x81d070`); PS4
  NTCs start with `Read_u16 m_usError`. PS4 writers start with u16 0, u16 id, u16 0 (PS4 framing only).
- **Walk**: stdlib Python run from stdin (no script saved; the role writes only this report) over
  `packets/decrypted_raw/`, every file whose suffix is `.<g>_<id>_<sub>` of the 23 ids. **3.0.1/3.0.2
  suffixes also match 41 + 41 login-server files** (`C2L_GET_ERROR_MESSAGE_LIST_REQ`, …), so those two
  are selected by suffix *and* the name `LOBBY` (41 + 41). Header check: group, u16 id, sub, source
  (0x00 C2S, 0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun. **Totals: 3,712
  files, header 3,712/3,712, fit 3,712/3,712, no RES with Error != 0.** Counter-tests: the PS4 body with
  PC framing, and PS4 framing (u16 error first) on the PC NTCs. Samples: file, size, sha256 first 16
  hex digits, body end offset.

Field-name sources: PS4 DWARF member (`m_` prefix dropped) **V**; Season 3 additions carry Arrowgene
names, **I**.

## 1. Group 33 JOB

### 1.1 33.0.1 C2S_JOB_GET_JOB_CHANGE_LIST_REQ / 33.0.2 S2C_…_RES

- PC writer `0x82e020` (33,0,1): no body (V). PS4 `Send_C2S_GET_JOB_CHANGE_LIST_REQ 0x19c84d0`: no body (V).
- PC handler `0x7e05e0` ("cSeedGameSvConnection::OnPacket_JOB_GET_JOB_CHANGE_LIST_RES"), reader
  `0x80d9b0`: RES header, list `0x76b1d0`, list `0x76b1d0`, list `0x77246d`, list `0x76c670` (V).
  PS4 `CPacket_S2C_GET_JOB_CHANGE_LIST_RES::ReadPacket 0x19dc300` (V): `m_JobChangeInfo`,
  `m_JobReleaseInfo` (`Read_CDataJobChangeInfo_ 0x19fe620`), `m_PawnJobChangeInfoList`
  (`Read_CDataPawnJobChangeInfo_ 0x19fe870`), `m_PlayPointList` (`Read_CDataJobPlayPoint_ 0x19e4880`).
- Elements (PC reader -> PS4 DWARF):

| Struct | PC | Wire (PC) | PS4 02020005 |
| --- | --- | --- | --- |
| `CDataJobChangeInfo` | `0x76b1d0` element | u8 JobID; list `0x765fb0` of `CDataEquipItemInfo` (`0x766070`) | `u8 m_ucJobID, MtTypedArray<CDataEquipItemInfo> m_EquipItemList` (V) |
| `CDataPawnJobChangeInfo` | `0x77246d` element (linear) | u8, u32, list `0x76b1d0`, list `0x76b1d0` | `u8 m_ucSlotNo, u32 m_unPawnId, m_JobChangeInfoList, m_JobReleaseInfoList` (V) |
| `CDataJobPlayPoint` | `0x76c670` element | u8 Job, u8, u32 | `u8 m_ucJob, CPlayPointData m_Data {u8 m_ucExpMode, u32 m_unPlayPoint}` (V) |

- Season 3: only `CDataEquipItemInfo` differs (the Login.hexpat type, PC `0x766070`; PS4 `{u8, u8, u32,
  u8, u8, list {u8,u32}}`). Counter-test: PS4 element body fails **42/42** (every capture carries
  equipment).
- Wire REQ empty. RES `s32 Error; if (Error == 0) { s32 Result; MtTypedArray<CDataJobChangeInfo>
  JobChangeInfo; MtTypedArray<CDataJobChangeInfo> JobReleaseInfo; MtTypedArray<CDataPawnJobChangeInfo>
  PawnJobChangeInfoList; MtTypedArray<CDataJobPlayPoint> PlayPointList; }`.
- Walk: REQ 42/42 slack 7, `stream1-marked.pcapng_tcp-stream-35/12049_C2S_JOB_GET_JOB_CHANGE_LIST_REQ_…33_0_1`
  (16 B, `6a54016856d76b56`), end 0x9. RES 42/42 slack 0-12, lists up to 19 elements;
  `stream1-…-35/12050_S2C_JOB_GET_JOB_CHANGE_LIST_RES_…33_0_2` (416 B, `b3c1a0fefd5191d2`): 3 job-change
  entries (first Job 2, 6 equipment items, first ItemID 21765), end 0x1a0; largest capture 2944 B
  (`0365c9635e34487e`), end 0xb74.

### 1.2 33.11.16 S2C_JOB_CHARACTER_JOB_EXP_UP_NTC

- PC handler `0x7df610`, reader `0x80d2b0`: u8, u32, u32, u32, u8 (V). PS4
  `CPacket_S2C_CHARACTER_JOB_EXP_UP_NOTICE::ReadPacket 0x19d7fd0`: `u8 m_ucJob, u32 m_unAddExp,
  u32 m_unExtraBonusExp, u32 m_unTotalExp, u8 m_ucType` (V; same body, PS4 u16 error first).
- Wire `u8 Job; u32 AddExp; u32 ExtraBonusExp; u32 TotalExp; u8 Type;` (14 B).
- Walk 417/417 slack 9; `stream1-…-35/13402_S2C_JOB_CHARACTER_JOB_EXP_UP_NTC_…33_11_16` (32 B,
  `020e18fb71fd3b3c`): Job 10, AddExp 63000, Extra 0, Total 84764112, Type 3, end 0x17. PS4 framing also
  fits 417/417 (slack 9 > 2): not discriminating; the no-header framing rests on the PC reader (V).

### 1.3 33.12.16 S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC

- PC handler `0x7dfa50`, reader `0x80d3a0`: u8, u32, u32, u32, `0x75cb00` (10 x u16) (V). PS4
  `…CHARACTER_JOB_LEVEL_UP_NOTICE::ReadPacket 0x19d8080`: `u8 m_ucJob, u32 m_unLevel, u32 m_unAddJobPoint,
  u32 m_unTotalJobPoint, CDataCharacterLevelParam` (V). `CDataCharacterLevelParam` (PS4
  `Read_CDataCharacterLevelParam_`, PC `0x75cb00`): u16 Attack, MagAttack, Defence, MagDefence,
  Strength, DownPower, ShakePower, StunPower, Constitution, Guts (V, same widths and count).
- Wire `u8 Job; u32 Level; u32 AddJobPoint; u32 TotalJobPoint; CDataCharacterLevelParam
  CharacterLevelParam;` (33 B).
- Walk 1/1 slack 6; `stream85-marked.pcapng_tcp-stream-11/77091_…33_12_16` (48 B, `a331710f7c928db7`):
  Job 9, Level 100, AddJobPoint 0, Total 444600, Attack 327 …, end 0x2a. PS4 framing fits (slack 6).

### 1.4 33.13.16 S2C_JOB_CHARACTER_JOB_LEVEL_UP_MEMBER_NTC

- PC handler `0x7df800`, reader `0x80d330`: u32, u8, u32, `0x75cb00` (V). PS4 `0x19d8130`:
  `u32 m_unCharacterID, u8 m_ucJob, u32 m_unLevel, CDataCharacterLevelParam` (V).
- Wire `u32 CharacterID; u8 Job; u32 Level; CDataCharacterLevelParam CharacterLevelParam;` (29 B).
- Walk 1/1 slack 10; `stream85-…-11/77092_…33_13_16` (48 B, `e2652eafee753467`): CharacterID 2184603,
  Job 9, Level 100, end 0x26.

### 1.5 33.15.16 S2C_JOB_PAWN_JOB_EXP_UP_NTC

- PC handler `0x7e15b0`, reader `0x80e1c0`: u32, u8, u32, u32, u32, u8 (V). PS4 `0x19d81e0`:
  `u32 m_unPawnID, u8 m_ucJob, u32 m_unAddExp, u32 m_unExtraBonusExp, u32 m_unTotalExp, u8 m_ucType` (V).
- Wire (18 B) in that order.
- Walk 1245/1245 slack 5; `stream85-…-11/100898_…33_15_16` (32 B, `057f8a0d90f7aee0`): PawnID 14454766,
  Job 6, AddExp 4461, Extra 0, Total 126636004, Type 1, end 0x1b.

### 1.6 33.16.16 S2C_JOB_PAWN_JOB_LEVEL_UP_NTC

- PC handler `0x7e1890`, reader `0x80e2d0`: u32, u8, u32, u32, u32, `0x75cb00` (V). PS4 `0x19d82a0`:
  `u32 m_unPawnID, u8 m_ucJob, u32 m_unLevel, u32 m_unAddJobPoint, u32 m_unTotalJobPoint,
  CDataCharacterLevelParam` (V).
- Wire (37 B) in that order.
- Walk 3/3 slack 2; `stream85-…-11/76621_…33_16_16` (48 B, `9a390682f7c60d8c`): PawnID 14455514, Job 8,
  Level 100, end 0x2e.

### 1.7 33.17.16 S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC

- PC handler `0x7e17b0`, reader `0x80e250`: u32, u32, u8, u32, `0x75cb00` (V). PS4 `0x19d8360`:
  `u32 m_unCharacterID, u32 m_unPawnID, u8 m_ucJob, u32 m_unLevel, CDataCharacterLevelParam` (V).
- Wire (33 B) in that order.
- Walk 3/3 slack 6; `stream85-…-11/76621_…33_17_16` (48 B, `e1b96f777badab76`): CharacterID 2184603,
  PawnID 14455514, Job 8, Level 100, end 0x2a.

### 1.8 33.20.16 S2C_JOB_PLAY_POINT_NTC (unresolved -> matched `UPDATE_PLAY_POINT_NOTICE`, V by behaviour)

- PC handler `0x7e2770` (packet object group 33/id 20/sub 16), reader `0x80e740`: u8, u32, u32, u32, u8
  (V). Behaviour: `switch (Type)`: 1/3/4 -> `sub_B67B60(gui, 7, UpdatePoint, ExtraBonusPoint)`, chat
  message index `0xF6`, `sub_B5E460`; 2/5/6 -> chat message `0xF8`; then
  `sub_5B2D60(sGamePointer[37], Job, TotalPoint)`.
- PS4 `cSeedGameSvConnection::OnPacket_S2C_UPDATE_PLAY_POINT_NOTICE 0x30ec00` /
  `CPacket_S2C_UPDATE_PLAY_POINT_NOTICE::ReadPacket 0x19d8560`: `u8 m_ucJob, u32 m_unUpdatePoint,
  u32 m_unExtraBonusPoint, u32 m_unTotalPoint, u8 m_ucType`; Type 3/4 and 1 ->
  `sGUIExt::addGainInfoQueue(7, UpdatePoint, ExtraBonusPoint)` + message `0xF6`; Type 2 -> message
  `0xF8`; then `cPlayPointInfo::updaptePlayPointValue(mpPlayPointInfo, Job, TotalPoint)`. Same body, same
  gain-info type 7, same two messages, same final update (V).
- Rejected candidate: the other PS4 body with this shape, `CHARACTER_JOB_EXP_UP_NOTICE`, belongs to
  33.11.16 (own PC handler `0x7df610`, exp behaviour) (V).
- Season 3: the Type switch adds 5 and 6 (to the 0xF8 branch) and moves 3/4 in with 1 (V; values only,
  no width change).
- Wire `u8 Job; u32 UpdatePoint; u32 ExtraBonusPoint; u32 TotalPoint; u8 Type;` (14 B).
- Walk 14/14 slack 9; `stream51-marked.pcapng_tcp-stream-11/24163_S2C_JOB_PLAY_POINT_NTC_…33_20_16`
  (32 B, `a353f53e67a9f590`), end 0x17:

```
00000000: 2100 1410 3400 0000 9505 0000 0024 0000  !...4........$..
00000010: 0000 0000 0213 0400 0000 0000 0000 0000  ................
```

  Job 5, UpdatePoint 36, Extra 0, Total 531, Type 4.

## 2. Group 3 LOBBY

Spec 005 covers 3.3.16 / 3.4.16 (nNetMsg); none of the ids below carries an nNetMsg.

### 2.1 3.0.1 C2S_LOBBY_LOBBY_JOIN_REQ / 3.0.2 S2C_…_RES

- PC writer `0x82ede0` (undefined code; `WritePacket(p, 3, 0, 1, -1)` at `0x82ee53`, then `Write_u32`
  stack arg 1, `Write_u32` stack arg 2, `retn 8`) (V). PS4 `Send_C2S_LOBBY_JOIN_REQ 0x19b0ec0`:
  `u32 in_CharacterID, u32 in_UserListMaxNum` (V).
- PC handler `0x7e2ce0` (`cSeedGameSvConnection__OnPacket_LOBBY_LOBBY_JOIN_RES`), reader `0x80ea20`:
  RES header, u32, list `0x76d6f0` (linear) of element `0x76d7f0` {u32, MtString x3, u32, u8, u8, u8}
  (V). PS4 `OnPacket_S2C_LOBBY_JOIN_RES 0x2de4d0` (inline): `u32 m_unCharacterID,
  MtTypedArray<CDataLobbyMemberInfo>` with `Read_CDataLobbyMemberInfo__0 0x1a2f460`:
  `CCommunityCharacterBaseInfo {u32, FirstName, LastName, ClanName}, u32 m_unPawnId, u8 m_ucPlatform,
  u8 m_ucClientVersion, u8 m_ucSessionStatus, u8 m_ucOnlineStatus` (V).
- **Season 3: `CDataLobbyMemberInfo` has 3 u8, PS4 4 (V by code).** Which PS4 member is gone is not
  settled: the PC handler reads only CharacterID (+8) and PawnId (+28). Counter-test: the PS4 4-u8 body
  also fits 41/41 (one member per capture, slack 7-9): not discriminating, code only.
- Wire REQ `u32 CharacterID; u32 UserListMaxNum;` (8 B). RES `… s32 Result; u32 CharacterID;
  MtTypedArray<CDataLobbyMemberInfo> LobbyMemberInfoList; }` with element `CDataCommunityCharacterBaseInfo
  BaseInfo; u32 PawnId; u8 unk_u8_0; u8 unk_u8_1; u8 unk_u8_2;` (I names: Arrowgene `Unk0` "most likely
  Platform", `Unk1`, `OnlineStatus`).
- Walk (name-filtered): REQ 41/41 slack 15, `stream1-…-35/11969_C2S_LOBBY_LOBBY_JOIN_REQ_…3_0_1` (32 B,
  `ed61292d677442e9`): 2144504, 100, end 0x11. RES 41/41 slack 7-9, every capture 1 member;
  `stream1-…-35/11972_S2C_LOBBY_LOBBY_JOIN_RES_…3_0_2` (64 B, `3713d9c43dee6d42`), end 0x38:

```
00000000: 0300 0002 3400 0000 0000 0000 0000 0000  ....4...........
00000010: 0000 20b8 f800 0000 0100 20b8 f800 0544  .. ....... ....D
00000020: 6961 6e61 0006 5365 656c 6978 0003 533b  iana..Seelix..S;
00000030: 5200 0000 0001 0001 0046 ee45 b7c1 0c68  R........F.E...h
```

  CharacterID 2144504; member 2144504 "Diana" "Seelix" clan "S;R", PawnId 0, u8 1, 0, 1.

### 2.2 3.1.1 C2S_LOBBY_LOBBY_LEAVE_REQ / 3.1.2 S2C_…_RES

- PC writer `0x82eed0` (3,1,1): no body (V); PS4 `Send_C2S_LOBBY_LEAVE_REQ 0x19b1020`: none (V).
- PC handler `0x7e2e00` (undefined code; builds group 3/id 1/sub 2, calls reader `0x80eab0`): RES header
  only (V). PS4 `OnPacket_S2C_LOBBY_LEAVE_RES 0x2de900`: u16 error, s32 result only (V).
- Wire REQ empty; RES `s32 Error; if (Error == 0) { s32 Result; }`.
- Walk REQ 41/41 slack 7 (`26544_…3_1_1`, 16 B, `be9c3428e6ba5402`, end 0x9); RES 41/41 slack 15
  (`26545_…3_1_2`, 32 B, `1472ca0ddcb6aa6c`, end 0x11).

### 2.3 3.2.1 C2S_LOBBY_LOBBY_CHAT_MSG_REQ / 3.2.2 S2C_…_RES

- PC writer `0x841ad0` (3,2,1): u8, u32, u8, u32, u32, `Write_cstr` (MtString) (V, decompiled and linear).
  PS4 `CPacket_C2S_LOBBY_CHAT_MSG_REQ::WritePacket 0x1a3a680`: `u8 in_Type, u32 in_TargetID,
  MT_CSTR in_strMessage` (V).
- **Season 3: u8 + u32 + u32 inserted before the message (V).** Counter-test: PS4 body fails **328/328**.
- PC handler `0x7e2a40`, reader `0x80e8e0`: RES header only (V). PS4 `OnPacket_S2C_LOBBY_CHAT_MSG_RES
  0x2dec90`: header only (V).
- Wire REQ `u8 Type; u32 TargetID; u8 unk_u8; u32 unk_u32_0; u32 unk_u32_1; MtString Message;`
  (Arrowgene names for the three: `MessageFlavor`, `PhrasesCategory`, `PhrasesIndex`, I). RES header only.
- Walk REQ 328/328 slack 3-15; `stream21-failedlogin-marked.pcapng_tcp-stream-48/12450_…3_2_1` (64 B,
  `a27c0204d6dcca6e`), end 0x35:

```
00000000: 0300 0201 0000 0000 3a0d 0000 0000 0000  ........:.......
00000010: 0000 0000 0000 0000 1c52 756d 6920 416d  .........Rumi Am
00000020: 6573 7472 6973 2068 6173 206c 6f67 6765  estris has logge
00000030: 6420 696e 2e00 0000 0000 0000 0000 0000  d in............
```

  Type 13, 0, 0, 0, 0, "Rumi Amestris has logged in.". RES 382/382 slack 15 (`12452_…3_2_2`, 32 B,
  `7be7b30ec3a0871b`, end 0x11).

### 2.4 3.2.16 S2C_LOBBY_LOBBY_CHAT_MSG_NTC

- PC handler `0x7e29b0` (undefined code; calls reader `0x80e840`): u8, u32, `0x75ecf0`
  (CDataCommunityCharacterBaseInfo {u32, MtString x3}), u8, u32, u32, MtString (V). PS4
  `CPacket_S2C_LOBBY_CHAT_MSG_NOTICE::ReadPacket 0x19d49f0`: `u8 m_ucType, u32 m_unHandleId,
  m_CharacterBaseInfo {u32 m_unCharacterID, FirstName, LastName, ClanName}, MtString m_wstrMessage` (V).
- **Season 3: the same u8 + u32 + u32 as 3.2.1, before the message (V).** Counter-tests: PS4 body fails
  **463/463**; PS4 framing fails 463/463.
- Wire `u8 Type; u32 HandleId; CDataCommunityCharacterBaseInfo CharacterBaseInfo; u8 unk_u8; u32
  unk_u32_0; u32 unk_u32_1; MtString Message;`.
- Walk 463/463 slack 0-15; `stream1-…-35/12231_…3_2_16` (272 B, `840c09f30acd97ba`): Type 9, HandleId 0,
  empty base info, 0, 0, 0, a login-bonus system message, end 0x10f.

## 3. Group 12 STAGE

### 3.1 12.0.1 C2S_STAGE_GET_STAGE_LIST_REQ

- PC writer `0x83eca0` (12,0,1): no body (V). PS4 `Send_C2S_GET_STAGE_LIST_REQ 0x19bb1f0`: none (V).
  The RES 12.0.2 already has a pattern.
- Walk 42/42 slack 7; `stream1-…-34/11898_…12_0_1` (16 B, `e5263390a77eb17b`), end 0x9.

### 3.2 12.1.1 C2S_STAGE_AREA_CHANGE_REQ / 12.1.2 S2C_…_RES

- PC writer `0x83e9f0` (12,1,1): u32, u32 (V). PS4 `Send_C2S_AREA_CHANGE_REQ 0x19bb320`: `u32 in_StageId,
  u32 in_JumpType` (V).
- PC handler `0x7fd690`, reader `0x81ca00`: RES header, u32, bool, list `0x75e8e0` (CDataCommonU32), list
  `0x766640` {u32, u8, u32, u32, u8}, list `0x766540` {u32, bool, bool} (V). PS4
  `CPacket_S2C_AREA_CHANGE_RES::ReadPacket`: `u32 m_unStageNo, b8 m_bIsBase,
  MtTypedArray<CDataCommonU32> m_StageFeatureList` (V).
- **Season 3: two trailing lists (V).** Counter-test: PS4 body fails **79/150**.
- Wire REQ `u32 StageId; u32 JumpType;` (8 B). RES `… s32 Result; u32 StageNo; bool IsBase;
  MtTypedArray<CDataCommonU32> StageFeatureList; MtTypedArray<unk {u32, u8, u32, u32, u8}> unk_List0;
  MtTypedArray<unk {u32, bool, bool}> unk_List1; }` (Arrowgene `CDataStageAreaChangeResUnk0/1`, I).
- Walk REQ 150/150 slack 15 (`12126_…12_1_1`, 32 B, `e8e16487b8544a8e`: StageId 2, JumpType 0, end 0x11).
  RES 150/150 slack 0-14, lists up to 8 elements (105 non-empty);
  `stream85-…-11/65690_S2C_STAGE_AREA_CHANGE_RES_…12_1_2` (80 B, `58afe1942a0ef618`), end 0x4c:

```
00000000: 0c00 0102 3400 0000 0000 0000 0000 0000  ....4...........
00000010: 0000 0002 3000 0000 0000 0000 0003 0000  ....0...........
00000020: 0230 0000 0000 8300 0000 0000 0000 0230  .0.............0
00000030: 0000 0000 8400 0000 0000 0000 0230 0000  .............0..
00000040: 0000 8800 0000 0000 0000 0000 0004 0901  ................
```

  StageNo 560, IsBase 0, StageFeatureList 0, unk_List0 3 x {560, 0, 131/132/136, 0, 0}, unk_List1 0.

### 3.3 12.5.1 C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ / 12.5.2 S2C_…_RES (Season 3-exclusive, confirmed)

- PC writer `0x842930` (12,5,1), linear: `Write_u32 [esp+0xc]`, list writer `0x77fd30` {MtString, u32},
  `Write_u32`, `Write_cstr` (V). Hex-Rays drops the list argument.
- PC handler `0x7fdce0`, reader `0x81ce40`: RES header only (V).
- PS4: no symbol, no DWARF type and no string containing `UNISON`, `SP_AREA`, `TICKET_DUNGEON` or
  `DUNGEON_START` (full symbol list and `idautils.Strings()` of the PS4 database), and its only
  `OnPacket_S2C` stage handlers are `GET_STAGE_LIST_RES`, `AREA_CHANGE_RES` and the `RANDOM_STAGE_*` pair
  (V: no counterpart in 02020005).
- Wire REQ `u32 unk_u32_0; MtTypedArray<{MtString, u32}> unk_List; u32 unk_u32_1; MtString unk_str;`
  (Arrowgene `ContentId`, `EntryFeeList` of `CDataStageTicketDungeonItemInfo {ItemUid, Num}`,
  `EntranceId`, `Unk2String`, I). RES header only.
- Walk REQ 3/3 slack 15; `stream85-…-11/13597_…12_5_1` (80 B, `7ce8cde7aad56161`), end 0x41: 19, list 0,
  1111, "第4区画 メガドシスの記憶 山道" (list never non-empty: element shape code-only). RES 3/3 slack 15
  (`13599_…12_5_2`, 32 B, `64836d94a8aae138`, end 0x11).

### 3.4 12.9.16 S2C_STAGE_DUNGEON_START_NTC (unresolved -> Season 3-exclusive, I)

- PC handler `0x7fdff0` (table entry 9.16, V) allocates a 64-byte packet (`0x78d830`: group 12, id 9,
  sub 16), reader `0x81d070` -> `0x779a90`: u32, MtString, u32, u32, bool, list `0x779b10` {u32, u16}
  (V). The handler keeps the packet at connection +0x4d4; getter `0x782090` feeds `0x5cf2d0`, which
  returns its 3rd and 4th fields (u32 +28, +32); `0x5f4360` (talk-manager flow) clears it, then sends
  12.2.1 (`0x83eae0`, GET_SP_AREA_CHANGE_ID_FROM_NPC_ID, u32 NpcId) (V).
- PS4: no reader in 02020005 reads `u32, MtString, u32, u32, bool` in sequence (search over all 7,660
  PS4 functions named `*Packet*`/`*CData*`/`OnPacket*`/`Send_*`), no DWARF struct with that member
  sequence, no `DUNGEON_START`/`UNISON` string (§ 3.3). Exclusive rests on absence: **X(I)**. The triage's
  "no PC name string" stands (the handler logs none).
- Capture context (I): every 12.9.16 follows a 12.5.1/12.5.2 pair (13597, 13599 -> 13600) and its first
  u32 (19) equals the 12.5.1 first u32 and Arrowgene's `ContentId`.
- Wire `u32 unk_u32_0; MtString unk_str; u32 StageId; u32 StartPos; bool unk_bool;
  MtTypedArray<{u32, u16}> unk_List;` (names Arrowgene `S2CStageDungeonStartNtc`, I; list element
  `CDataBattleContentUnk5`/`EntryCostList`, I).
- Walk 3/3 slack 4; `stream85-…-11/13600_…12_9_16` (32 B, `c9368c7229a13f8d`), end 0x1c:

```
00000000: 0c00 0910 3400 0002 0000 0000 1300 0000  ....4...........
00000010: 0002 2f00 0000 0501 0000 0000 783e c491  ../.........x>..
```

  19, "", 559, 5, true, list 0 (list never non-empty: element shape code-only). PS4 framing fits 2/3.

## 4. Group 23 AREA

| id | PC | PS4 02020005 | Wire | Walk |
| --- | --- | --- | --- | --- |
| 23.3.1 C2S_AREA_GET_AREA_SUPPLY_INFO_REQ | writer `0x81e680` (23,3,1): u32 (V) | `Send_C2S_GET_AREA_SUPPLY_INFO_REQ 0x19c1e10`: `u32 in_AreaID` (V) | `u32 AreaId;` (4 B) | 13/13 slack 3; `stream61-remarked.pcapng_tcp-stream-11/11276_…23_3_1` (16 B, `b183bd1516ced16d`): AreaId 14, end 0xd |
| 23.4.2 S2C_AREA_GET_AREA_SUPPLY_RES | handler `0x7c4570`, reader `0x800020`: RES header only (V) | `OnPacket_S2C_GET_AREA_SUPPLY_RES 0x302c90`: header only (V) | `s32 Error; if (Error == 0) { s32 Result; }` | 12/12 slack 15; `stream61-…-11/11286_…23_4_2` (32 B, `77a0220d7e5fa058`), end 0x11 |
| 23.8.1 C2S_AREA_GET_LEADER_AREA_RELEASE_LIST_REQ | writer `0x81e870` (23,8,1): no body (V) | `Send_… 0x19c1ce0`: none (V) | empty | 131/131 slack 7; `stream1-…-35/12142_…23_8_1` (16 B, `f0cfb5c85c125d84`), end 0x9 |
| 23.12.1 C2S_AREA_GET_AREA_BASE_INFO_LIST_REQ | writer `0x81e400` (23,12,1): no body (V) | `Send_… 0x19c2200`: none (V) | empty | 72/72 slack 7; `stream1-…-35/12058_…23_12_1` (16 B, `69b4baf4a0f3199f`), end 0x9 |

## 5. Summary

PS4 mark: V = confirmed by code (symbol + body, or behaviour); X = no PS4 counterpart (confirmed by
code); X(I) = none found, inferred. Body bytes for Error == 0 (lists `+kn`; var = nested/strings).

| id | name (file) | PS4 | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 3.0.1 | C2S_LOBBY_LOBBY_JOIN_REQ | V | 8 | 11969 | 41/41 |
| 3.0.2 | S2C_LOBBY_LOBBY_JOIN_RES | V (S3 member: 3 u8, PS4 4; code-only) | 16+var | 11972 | 41/41 |
| 3.1.1 | C2S_LOBBY_LOBBY_LEAVE_REQ | V | 0 | 26544 | 41/41 |
| 3.1.2 | S2C_LOBBY_LOBBY_LEAVE_RES | V | 8 | 26545 | 41/41 |
| 3.2.1 | C2S_LOBBY_LOBBY_CHAT_MSG_REQ | V (S3 u8+u32+u32) | 16+var | 12450 | 328/328 |
| 3.2.2 | S2C_LOBBY_LOBBY_CHAT_MSG_RES | V | 8 | 12452 | 382/382 |
| 3.2.16 | S2C_LOBBY_LOBBY_CHAT_MSG_NTC | V (S3 u8+u32+u32) | var | 12231 | 463/463 |
| 12.0.1 | C2S_STAGE_GET_STAGE_LIST_REQ | V | 0 | 11898 | 42/42 |
| 12.1.1 | C2S_STAGE_AREA_CHANGE_REQ | V | 8 | 12126 | 150/150 |
| 12.1.2 | S2C_STAGE_AREA_CHANGE_RES | V (S3 two lists) | 25+4n+14m+6k | 65690 | 150/150 |
| 12.5.1 | C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ | X | var | 13597 | 3/3 |
| 12.5.2 | S2C_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_RES | X | 8 | 13599 | 3/3 |
| 12.9.16 | S2C_STAGE_DUNGEON_START_NTC | X(I) | 19+var | 13600 | 3/3 |
| 23.3.1 | C2S_AREA_GET_AREA_SUPPLY_INFO_REQ | V | 4 | 11276 | 13/13 |
| 23.4.2 | S2C_AREA_GET_AREA_SUPPLY_RES | V | 8 | 11286 | 12/12 |
| 23.8.1 | C2S_AREA_GET_LEADER_AREA_RELEASE_LIST_REQ | V | 0 | 12142 | 131/131 |
| 23.12.1 | C2S_AREA_GET_AREA_BASE_INFO_LIST_REQ | V | 0 | 12058 | 72/72 |
| 33.0.1 | C2S_JOB_GET_JOB_CHANGE_LIST_REQ | V | 0 | 12049 | 42/42 |
| 33.0.2 | S2C_JOB_GET_JOB_CHANGE_LIST_RES | V (S3 EquipItemInfo) | var | 12050 | 42/42 |
| 33.11.16 | S2C_JOB_CHARACTER_JOB_EXP_UP_NTC | V | 14 | 13402 | 417/417 |
| 33.12.16 | S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC | V | 33 | 77091 | 1/1 |
| 33.13.16 | S2C_JOB_CHARACTER_JOB_LEVEL_UP_MEMBER_NTC | V | 29 | 77092 | 1/1 |
| 33.15.16 | S2C_JOB_PAWN_JOB_EXP_UP_NTC | V | 18 | 100898 | 1245/1245 |
| 33.16.16 | S2C_JOB_PAWN_JOB_LEVEL_UP_NTC | V | 37 | 76621 | 3/3 |
| 33.17.16 | S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC | V | 33 | 76621 | 3/3 |
| 33.20.16 | S2C_JOB_PLAY_POINT_NTC | V behaviour `UPDATE_PLAY_POINT_NOTICE` | 14 | 24163 | 14/14 |

Triage corrections: 33.20.16 unresolved -> matched `UPDATE_PLAY_POINT_NOTICE` (V; the shape-sharing
`CHARACTER_JOB_EXP_UP_NOTICE` rejected, it is 33.11.16); 12.9.16 unresolved -> Season 3-exclusive (X(I));
12.5.1/12.5.2 exclusive confirmed. The 3.0.1 `pc_va 0x82ee53` is the `WritePacket` call inside the
undefined writer `0x82ede0`. The triage's 3.0.1/3.0.2 capture counts (41) are right only with the
`LOBBY` name filter: the suffixes also match 41 + 41 login-server files.

Capture-tested discrimination (PS4 body, PC framing): fails 42/42 (33.0.2), 328/328 (3.2.1), 463/463
(3.2.16), 79/150 (12.1.2). PS4 framing on PC NTCs fails 463/463 (3.2.16); it fits the 33.x NTCs (slack
2-10) and 2/3 of 12.9.16: not discriminating there, the no-header framing rests on the PC readers (V).
Code-only: the 3.0.2 member u8 count (PS4 4-u8 fits 41/41), the 12.5.1 list element, the 12.9.16 list
element. No RES with Error != 0 captured.

Recompilation (`D:/ddon-data-s2/recompilation/.../UserSession/{C2S,S2C}.cpp`): bodies only for
`CPacket_S2C_CHARACTER_JOB_EXP_UP_NOTICE::ReadPacket` (S2C.cpp:747) and
`CPacket_S2C_UPDATE_PLAY_POINT_NOTICE::ReadPacket` (S2C.cpp:12352); both agree with PS4 and PC (33.11.16,
33.20.16). T001's `recompiled_body yes` is a `DDON_STUB` for 3.2.1 (C2S.cpp:217), 33.0.2 (S2C.cpp:4782),
33.12.16 (791), 33.16.16 (8851), 33.17.16 (8822): overstated. `PacketData/{Lobby,JobMaster,Character}.cpp`
hold DTI stubs, no reader bodies.

## 6. Shared types for pattern authors

Reuse: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`), `Character.hexpat`
(`CDataCommunityCharacterBaseInfo` = PC `0x75ecf0` / `0x76d7f0` prefix, V), `Login.hexpat`
(`CDataEquipItemInfo`, PC `0x766070`; it uses `Context.hexpat`'s `EquipElementParam`, `AddStatusParam`,
`EquipStatParam`), `nNetMsg.hexpat` `ONLINE_STATUS` (only if the third LobbyMember u8 is OnlineStatus, I).
Framing as T003 § 18 (inline RES header; NTCs without header).

Add (V from the PC readers named; names PS4 DWARF unless marked I):

| Include | Struct | PC reader | Wire |
| --- | --- | --- | --- |
| `Character.hexpat` | `CDataCharacterLevelParam` | `0x75cb00` | u16 Attack, MagAttack, Defence, MagDefence, Strength, DownPower, ShakePower, StunPower, Constitution, Guts |
| `Character.hexpat` (or new `Lobby.hexpat`) | `CDataLobbyMemberInfo` | `0x76d7f0` | CDataCommunityCharacterBaseInfo, u32 PawnId, u8 x3 (S3; names I) |
| new `Job.hexpat` (includes `Login.hexpat`) | `CDataJobChangeInfo` | `0x76b1d0` element | u8 JobID, MtTypedArray<CDataEquipItemInfo> EquipItemList |
| `Job.hexpat` | `CDataPawnJobChangeInfo` | `0x77246d` element | u8 SlotNo, u32 PawnId, MtTypedArray<CDataJobChangeInfo> JobChangeInfoList, JobReleaseInfoList |
| `Job.hexpat` | `CDataPlayPointData` / `CDataJobPlayPoint` | `0x76c670` element | {u8 ExpMode, u32 PlayPoint} / u8 Job, CDataPlayPointData Data |
| new `Stage.hexpat` | AREA_CHANGE extra elements | `0x766640` / `0x766540` | {u32, u8, u32, u32, u8} / {u32, bool, bool} (S3, I names) |
| `Stage.hexpat` | 12.5.1 list element | `0x77fd30` (writer) | MtString, u32 (S3, I names) |
| `Stage.hexpat` | 12.9.16 body / element | `0x779a90` / `0x779b10` | § 3.4 / {u32, u16} (S3, I names) |

`CDataStageInfo` is defined locally in `S2C_STAGE_GET_STAGE_LIST_RES-pattern.cpp`; move it to
`Stage.hexpat` only if a second user appears (none in this package).

## 7. Arrowgene leads

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`.
No misplacement found: `C2SLobbyJoinReq`, `S2CLobbyJoinRes`, `CDataLobbyMemberInfo` (3 u8),
`C2SLobbyChatMsgReq` / `S2CLobbyChatMsgNotice` (MessageFlavor, PhrasesCategory, PhrasesIndex),
`C2SStageAreaChangeReq`, `S2CStageAreaChangeRes` (+`CDataStageAreaChangeResUnk0/1`),
`C2SStageUnisonAreaChangeBeginRecruitmentReq`, `S2CStageDungeonStartNtc`, `S2CJobGetJobChangeListRes`,
`CDataJobChangeInfo`, `CDataPawnJobChangeInfo`, `CDataJobPlayPoint`/`CDataPlayPointData`, the six job
NTCs and `S2CJobUpdatePlayPointNtc` (mapped to 33.20.16) agree with PC 03040008 in order and width. The
empty requests have no Arrowgene fields (agree). Note only: `PacketId.cs` gives 3.0.1/3.0.2 the same
`(group, id, sub)` triple as login-server packets; the capture files share the suffix (§ 0).

## 8. Open items and checks not run

- Names without code backing (I): the three Season 3 fields of 3.2.1/3.2.16, the three LobbyMember u8 and
  which PS4 u8 was dropped, the two 12.1.2 lists, every 12.5.1 and 12.9.16 field, the packet name of
  12.9.16 (no PC string).
- 12.9.16 exclusivity rests on absence in PS4 02020005 (X(I)).
- Never non-empty in captures (code-only): the 12.5.1 list, the 12.9.16 list. 12.1.2 per list (150 RES): StageFeatureList
  non-empty in 92 (max 2), {u32,u8,u32,u32,u8} in 13 (max 8), {u32,bool,bool} in 5 (max 3): all three
  element shapes are capture-exercised.
- PC code read linearly only: `0x82ede0`, `0x7e2e00`, `0x7e29b0`, `0x76d6f0`, `0x77246d`, `0x842930`.
- ImHex not run (not on `PATH`); no pattern written (outside this package).
