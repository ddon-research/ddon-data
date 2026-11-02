# 006 T010: groups 28 GP, 31 CLAN (+ StatusInfo check)

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T010-gp-clan.md`; the 39 rows of groups 28 and 31 in
`research/T001-triage.tsv` (25 + 14 ids, 792 captures). Base `cc8ae567fc` (HEAD was `c4c7129016`
when the report was written; that commit only adds a brief, no input of this report changed). Marks:
**V** verified in code (or by capture for walk results), **I** inferred, **C** contradicted. All
addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t010/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t010/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays, `ida_ua.decode_insn`
  for linear decoding, `ida_typeinf` for DWARF structs); nothing renamed, retyped, commented, patched or
  reanalysed.
- PC primitives as T003/T005/T009 § 0 (`nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32
  0x8bc480`, `Read_u32 0x8bc4d0`, `Read_MtString 0x8bc5b0`, `Read_s64 0x8bc660`, `Read_u64 0x8bc6a0`,
  `Read_bool 0x8bc6e0`; `Write_u32 0x8bc920`, `Write_bool 0x8bcb80`; `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` -> group 28 `{0x212c8b0, 36}`, group 31 `{0x212b560, 63}`;
  stride 0x18, key `(sub<<16)|id` at +0x10; entry +0 filled by the initializer (`mov [esp], offset X` +
  `movq` store, e.g. `0x1a2ce6f` -> 28.23.2 `0x7d84e0`, `0x1a295e1` -> 31.9.2 `loc_7CB02F+1` = `0x7cb030`).
  Every S2C `pc_va` of the triage equals its table handler (V, 20/20).
- **Not functions in the PC database** (decoded linearly, no database change): handlers `0x7d8700`
  (28.7.2), `0x7d8590` (28.9.2), `0x7d7980` (28.17.2), `0x7cb030` (31.9.2); readers `0x809a00` (28.7.2),
  `0x809380` (28.17.2); list readers `0x767d00` (CDataGPShopDisplayType), `0x75d430`
  (CDataClanJoinRequest), `0x75e2a0` (CDataClanShopInfo, called as `loc_75E29C+4`); the 28.9.1 writer
  `0x829f00-0x829fe5` (bytes at `0x829f00` start `83 ec 1c 56 8b f1`; the previous function
  `Send_C2S_GP_GP_SHOP_CAN_BUY_REQ` ends at `0x829ef1`; the triage `0x829f73` is its `WritePacket` call).
  The PC database carries hand-given names on some items (e.g. `sGame::setChargeCourse 0xb60b50`,
  `nUserSession::CPacket_S2C_OnPacket_GP_GP_SHOP_CAN_BUY_RES::ReadPacket 0x809810`); they are treated as
  leads, every conclusion below rests on the code.
- PC writers (C2S): `WritePacket(p, group, id, 1, -1)` with group/id read from the call (V each, 19/19).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, behaviour), never by PS4
  id. RES header (V, every PC RES reader here): `Read_s32` Error (+16); non-zero -> return; else `Read_s32`
  Result, body. PS4 reads `u16 m_usError` + `u32 m_unResult` (GP) or `s32 m_nResult` (CLAN). PC NTC
  readers read **no** header (V: 28.24.16, 28.25.16, 28.26.16); PS4 NTCs start with `Read_u16 m_usError`.
  PS4 C2S writers start with `Write_u16 0, Write_u16 <flat id>, Write_u16 0` (PS4 framing); PC C2S bodies
  hold only the fields listed.
- **Walk**: `specs/006-packet-pattern-coverage/research/T010-walk.py` (stdlib; run from `D:/ddon-data` with
  `python -X utf8 -I specs/006-packet-pattern-coverage/research/T010-walk.py`; sha256 prefix
  `d1d81e54d2615e64`; holds every PC layout below, the PS4 counter-test variants, `tally` fields and the
  StatusInfo dump). Input `packets/decrypted_raw/*/`, every file whose suffix is `.<g>_<id>_<sub>` of the
  39 ids (each suffix carries exactly one packet name). Header check: group, u16 id, sub, source (0x00 C2S,
  0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun. **Totals: 792 files, header
  792/792, fit 792/792, no RES with Error != 0.** Samples: file (relative to `packets/decrypted_raw/`),
  size, sha256 first 16 hex digits, body end offset.
- Recompilation cross-check: `D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/S2C.cpp`
  implements only `CPacket_S2C_GET_GP_RES::ReadPacket` (u16 Error, u32 Result, u32 GP, s64 UseLimit,
  u64 RealTime, u16 Milliseconds: agrees with PS4 and PC) and `GP_COURSE_START_PARTY_NTC` (out of scope);
  `GP_SHOP_DISPLAY_BUY_RES`, `CLAN_BASE_GET_INFO_RES`, `CLAN_SHOP_GET_BUFF_ITEM_LIST_RES` are `DDON_STUB`;
  `C2S.cpp` has no group-28/31 writer of this package; `PacketData/GP.cpp`, `Clan.cpp` hold only DTI
  boilerplate (no readers). Nothing contradicts the PS4 DWARF.

Field-name sources: PS4 DWARF member (`m_`/type prefix dropped) **V**; other names **I** with the basis
stated; a Season 3 field without code backing is `unk_*` (server names only as leads in comments).

## 1. Shared structures

### 1.1 GP (group 28)

| Struct | PC reader | PS4 02020005 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataGPPeriod` | list `0x7678e0` | `Read_CDataGPPeriod_ 0x1a12b20` {u32 m_unGP, b8 m_bIsFreeGP, u64 m_ullPeriod} | u32 GP, bool IsFreeGP, u64 Period (V, = PS4) |
| `CDataGPShopDisplayType` | list `0x767d00` (not a function) | `0x1a0fc00` {u32 m_unID, MtString m_wstrName, u32 m_unInGameUrlID} | u32 ID, MtString Name, u32 InGameUrlID (V, = PS4) |
| `CDataGPShopDisplayLineup` | list `0x767b20`, element `0x767be0` | `0x1a0f8e0` {u32 ID, u32 Category, u8 IconId, u32 GP, u32 DiscountType, u32 DiscountGP, MtString Name, MtString Comment, u32 LineupID, u32 BackIconID, u32 FrameIconID, u32 BehaviorAfterBuyingType} | u32 ID, u32 Category, u8 IconId, u32 GP, u32 DiscountType, u32 DiscountGP, MtString Name, MtString Comment, u32 LineupID, **MtString unk_MtString**, u32 x4 (S3: 14 reads vs 12; V shape). The four trailing u32: PS4 has three (BackIconID, FrameIconID, BehaviorAfterBuyingType); which of them survive and where the new u32 sits is not settled (`unk_u32_0..3`, I) |
| `CDataGPCourseAvailable` | list `0x7670a0`, element `0x7671a0` | `0x1a113c0` {u32 ID, MtString Name, u64 UseLimitTime, u32 CourseID, u32 LineupID, u32 BackIconID, u32 FrameIconID} | u32 ID, MtString Name, u64 UseLimitTime, u32 CourseID, u32 LineupID, **MtString unk_MtString** (S3: the two icon u32 replaced by one MtString, V shape; same change as `CDataGPCourseValid` in `GP.hexpat`; names of the u32 pair I by position) |
| `CDataEditParam` | list `0x764b20` | `0x1a10090` {CEditParamPalette {u32 m_unParamTypeId, u32 m_unUID}, b8 m_bIsValid, b8 m_bIsGp, b8 m_bIsPitchEnable} | u32 ParamTypeId, u32 UID, bool IsValid, bool IsGp, bool IsPitchEnable (V, = PS4) |
| `CDataCommonU32` | list `0x75e8e0` | — | `Packet.hexpat` (V) |

### 1.2 CLAN (group 31)

| Struct | PC reader | PS4 02020005 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataClanJoinRequest` | list `0x75d430` (not a function), element at `0x75d4e2` | `Read_CDataClanJoinRequest__0` {u32 m_unClanID, MtString m_wstrClanName, CCommunityCharacterBaseInfo, s64 m_llCreated} | u32 ClanID, MtString ClanName, CDataCommunityCharacterBaseInfo (`0x75ecf0`, `Character.hexpat`), s64 Created (V, = PS4) |
| `CDataClanHistoryElement` | list `0x75d280`, element `0x75d390` | {s64 m_llDate, u8 m_ucType, CCharacterName {MtString FirstName, MtString LastName}, u32 m_unValue1..3, MtString m_wstrFreeText} | s64 Date, u8 Type, CDataCharacterName (2 MtString, `Character.hexpat`), u32 Value1, Value2, Value3, MtString FreeText (V, = PS4) |
| `CDataClanPawnExpeditionInfo` (inline) | `0x771e80` | `m_PawnExpeditionInfo` {u8 SallyStatus, u8 GoldenSallyPrice, u8 ChargeSallyPrice} | 3 x u8 (V, = PS4) |
| `CDataClanPartnerPawnInfo` (inline) | `0x75d770` | {list MyPartnerPawnList, list MemberPartnerPawnList} | 2 x list CDataCommonU32 (V) |
| `CDataClanConciergeInfo` (inline) | `0x75d120`, list `0x75d160` | {u32 m_unNpcId, list CDataClanConciergeNpc {u32 NpcId, u32 Price, b8 IsInit, u32 SortId}} | same (V) |
| `CDataClanShopLineupName` | list `0x75e2f0` | {u32 LineupID, MtString Name} | same (V) |
| `CDataClanValueInfo` | list `0x75e500` | {u8 Type, u32 Value} | same (V) |
| `CDataFurnitureLayout` | list `0x766f90` | `Read_CDataFurnitureLayout_ 0x19e8890` {u32 m_unItemID, u32 m_unOmID, u8 m_ucLayoutID} | u32 ItemID, u32 OmID, u8 LayoutID (V: the PC MY_ROOM_FURNITURE_LIST_GET_RES reader `0x80fa00` (handler `0x7e5a90`, string "OnPacket_MY_ROOM_FURNITURE_LIST_GET_RES") reads `0x766f90` where PS4 `CPacket_S2C_FURNITURE_LIST_GET_RES::ReadPacket 0x19df920` reads `CDataFurnitureLayout`; names V by that identity) |
| `CDataClanShopBuffItem` | list `0x75de20`, element `0x75dee0` | {u32 LineupId, u32 RequireClanPoint, u8 RequiredLevel, u32 IconID, MtString Name, list CDataClanShopBuffInfo {u32 BuffID, u8 BuffType} (`0x75dd30`), list CDataCommonU32 RequireLineupId} | same (V) |
| `CDataClanShopInfo` (inline) | `0x75e2a0` (not a function) | {u32 m_unClanPoint, list CurrentFunctionList, list CurrentBuffList} | same (V) |
| `CDataNoraPawnInfo` (inline) | `0x76f790` | `CNoraPawnInfo` {u32 m_unVersion, MtString m_wstrName, CEditInfo m_EditInfo, u8 m_ucJob, list CDataCharacterEquipData} | u32 Version, MtString Name, CDataEditInfo (`0x764550`, 122 B), u8 Job, list CDataCharacterEquipData (`0x75c190`), **list CDataCharacterEquipData** (S3, V shape; name `CharacterEquipViewDataList` I, by the same pair in CDataCharacterInfo) |

## 2. 28.0.1 GET_GP_REQ / 28.0.2 GET_GP_RES

- PC writer `0x829630` (empty body, V); PS4 `Send_C2S_GET_GP_REQ 0x19bc1b0` (empty, V).
- PC handler `0x7d73b0` -> reader `0x808f70`: header, u32 GP, s64 UseLimit, u64 RealTime, u16 Milliseconds.
  PS4 `CPacket_S2C_GET_GP_RES::ReadPacket 0x19d7af0` {u32 m_unGP, s64 m_llUseLimit, u64 m_ullRealTime,
  u16 m_usMilliseconds}: **= PS4 (V)**; recompilation agrees.
- Walk: 4/4 + 4/4; sample `stream5-marked.pcapng_tcp-stream-9/1173_S2C_GP_GET_GP_RES_…28_0_2` (48 B,
  `6bb8a0d9f5a61d04`) end 0x27.

## 3. 28.2.1 GET_GP_PERIOD_REQ / 28.2.2 …_RES

- REQ `0x829570` empty (V; PS4 `0x19bc7d0` empty). RES handler `0x7d72b0` -> `0x808ef0`: list
  CDataGPPeriod. PS4 `OnPacket_S2C_GET_GP_PERIOD_RES 0x30a6b0` reads `m_GPPeriodList`: **= PS4 (V)**.
- Walk: 42/42 + 42/42; lists up to 5; sample `stream21-failedlogin-marked.pcapng_tcp-stream-48/12344_…28_2_2`
  (96 B, `6b0fb5de7e39f33f`) end 0x56.

## 4. 28.3.1 GET_CAP_REQ / 28.3.2 GET_CAP_RES

- REQ `0x829310` empty (V; PS4 `0x19bc2e0` empty). RES `0x7d7080` -> `0x808d70`: u32. PS4
  `CPacket_S2C_GET_CAP_RES` {u32 m_unCAP}: **= PS4 (V)**, field `CAP`.
- Walk: 2/2 + 2/2; sample `stream5-marked.pcapng_tcp-stream-9/1177_…28_3_2` (32 B, `69199fcb8ab78b01`) end 0x15.

## 5. 28.6.1 COG_GET_ID_REQ / 28.6.2 COG_GET_ID_RES

- REQ `0x829250` empty (V; PS4 `0x19bc080` empty). RES `0x7d6ef0` -> `0x808cf0`: MtString. PS4
  `CPacket_S2C_COG_GET_ID_RES` {MtString m_wstrCogId}: **= PS4 (V)**, field `CogId`.
- Walk: 2/2 + 2/2; sample `stream5-marked.pcapng_tcp-stream-9/1187_…28_6_2` (80 B, `3b2bb8c4818403c3`) end 0x43.

## 6. 28.7.1 GP_SHOP_DISPLAY_GET_TYPE_REQ / 28.7.2 …_RES

- REQ `0x82a0d0` empty (V; PS4 `0x19bcf00` empty). RES handler `0x7d8700` (not a function) -> reader
  `0x809a00` (not a function; header, then list `0x767d00`). PS4 `0x30ae80` reads `m_Items`
  (CDataGPShopDisplayType list): **= PS4 (V)**. The triage read-seq ratio 0.07 is an artefact of the
  undefined code.
- Walk: 2/2 + 2/2; lists up to 12; sample `stream5-marked.pcapng_tcp-stream-9/1181_…28_7_2` (448 B,
  `af81e07b21527518`) end 0x1b7.

## 7. 28.8.1 GP_SHOP_DISPLAY_GET_LINEUP_REQ / 28.8.2 …_RES

- REQ `0x829ff0`: u32 (V). PS4 `Send_C2S_GP_SHOP_DISPLAY_GET_LINEUP_REQ 0x19bd030(u32 in_DisplayID)`: field
  `DisplayID` (V). Captured values 1-11.
- RES `0x7d8650` -> `0x809980`: list CDataGPShopDisplayLineup (§ 1.1, **S3: +MtString after LineupID,
  +1 u32**). PS4 `0x30b000` reads `m_Items` (12-field element).
- Counter-test: PS4 element fails **38/38**. Walk 38/38 + 38/38; lists up to 24; sample
  `stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/2019_…28_8_2` (7952 B, `50cd1c0365996ccf`) end 0x1f04.

## 8. 28.9.1 GP_SHOP_DISPLAY_BUY_REQ / 28.9.2 …_RES

- REQ writer `0x829f00` (undefined code, § 0): `WritePacket(28, 9, 1)`, `Write_u32 [esp+24h]`,
  `Write_u32 [esp+28h]` (V). PS4 `Send_C2S_GP_SHOP_DISPLAY_BUY_REQ 0x19bd170(u32 in_DisplayLineupId)`:
  one u32. **S3: + u32**. First = `DisplayLineupId` (I by position), second `unk_u32` (values 1, 3, 5, 7-10:
  the same value set as the third u32 of 28.23.1).
- Counter-test: PS4 body (one u32) fails **9/9** (the PC body ends 4 bytes later, slack 15 vs 19).
- RES handler `0x7d8590` (not a function) -> `0x8098d0`: u32, list CDataCommonU32, u32, MtString. PS4
  `CPacket_S2C_GP_SHOP_DISPLAY_BUY_RES::ReadPacket 0x19d7ed0` {u32 m_unLineupId, m_CommonIdList, u32
  m_unBalance, MtString m_wstrLineupName}: **= PS4 (V)**.
- Walk: 9/9 + 9/9 (CommonIdList always empty); sample `stream86-…-stream-9/2287_…28_9_2` (80 B,
  `ff068bb429128217`) end 0x43; REQ sample `…/2053_…28_9_1` (32 B, `96d5fc7a77428cce`) end 0x11.

## 9. 28.17.1 GP_COURSE_GET_AVAILABLE_LIST_REQ / 28.17.2 …_RES

- REQ `0x829a10` empty (V; PS4 `0x19bc900` empty). RES handler `0x7d7980` (not a function) -> reader
  `0x809380` (not a function; header, list `0x7670a0`). PS4 `0x30bc70` reads `m_Items`
  (CDataGPCourseAvailable). **S3 element: u32 x2 icons -> MtString** (§ 1.1, V by code).
- Counter-test: none possible: every capture holds an empty list (PS4 variant fails 0/10). Code-only.
- Walk: 10/10 + 10/10; sample `stream5-marked.pcapng_tcp-stream-9/1184_…28_17_2` (32 B, `249a2b807feb4046`) end 0x15.

## 10. 28.22.1 GP_EDIT_GET_VOICE_LIST_REQ / 28.22.2 …_RES

- REQ `0x829d30` empty (V; PS4 `Send_C2S_GP_EDIT_GET_VOICE_LIST_REQ 0x19bb4b0` empty). RES `0x7d8230` ->
  `0x809710`: list CDataEditParam. PS4 `CPacket_S2C_GP_EDIT_GET_VOICE_LIST_RES` {m_VoiceList}: **= PS4 (V)**.
- Walk: 2/2 + 2/2; lists up to 22; sample `stream86-…-stream-9/1479_…28_22_2` (272 B, `00ba8e94179d90e4`) end 0x107.

## 11. 28.23.1 GP_SHOP_CAN_BUY_REQ / 28.23.2 …_RES (Season 3-exclusive, confirmed)

- REQ `0x829df0`: `WritePacket(28, 23, 1)`, 3 x `Write_u32` (V). RES handler `0x7d84e0` -> `0x809810`:
  header, bool, u32 x4 (V).
- PS4: no `GP_SHOP_CAN_BUY` packet: no function name, no DWARF `CPacket_*` type (searched all named types for
  `CAN_BUY`). PS4 has only `GP_SHOP_CAN_BUY_PAWN` and `…_PAWN_VOICE` (REQ u32 m_unLineupId; RES b8 m_bCanBuy,
  u32 m_unLineupId); the PC binary has neither string (only "OnPacket_GP_GP_SHOP_CAN_BUY_RES"). Exclusive
  **confirmed (V)**; Season 3 plausibly merged the two PAWN checks into one generic check (I).
- Field names: RES bool `CanBuy` and u32 `LineupId` (I: PS4 PAWN analogue's leading pair, and capture: RES
  field 2 echoes REQ field 1, values 23-463); REQ field 1 `LineupId` (I, echo); the rest `unk_u32` (RES fields
  4-5 always 0; REQ field 3 shares the value set of 28.9.1 field 2).
- Counter-test: the PS4 PAWN bodies fail 9/9 on both directions. Walk 9/9 + 9/9. Capture (RES
  `stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/2045_…28_23_2`, 48 B, `62e60d682b768a03`, end
  0x22): `…0x09 00000000 | 00000000 | 01 | 0000007f | 00000008 | 00000000 | 00000000`; its REQ `…/2043_…28_23_1`
  (32 B, `6836fdaaf0fca3a1`, end 0x15): `0000007f 00000009 00000008`.

## 12. 28.24.16 S2C_GP_28_24_16_NTC (unresolved -> Season 3-exclusive, I)

- PC handler `0x7d6fd0` reads **u32** inline (no reader object, no header) and passes it to `0xb86860`
  (`this[211] = a2`, i.e. a store to `+0x34c` of the object at `n3_0 + 0x4ad0`); `0x419ee0` resets the same
  field to 0 in its state 0. No notice class, no name string.
- PS4: the five PS4 GP notice handlers map to PC 28.25-28.29.16 by code: 25 = START (§ 13), 26 = EXTEND
  (§ 14), 27 = END (`0x7d7770` -> `0x809230` u32, u32 + `setChargeCourse`, = PS4 `OnPacket_S2C_GP_COURSE_END_NTC
  0x30c2a0` u32 CourseID, u32 announceType + `sGame::setChargeCourse`), 28/29 = START_PARTY/END_PARTY (readers
  `0x809620`, `0x8092a0`; their mapping rests on the database names, I). No PS4 GP notice is left for 24.16;
  the u32-only shape is shared by 32 PS4 bodies with unrelated behaviour (triage). Settled as **Season
  3-exclusive (I)**; meaning of the u32 not settled (values 3 (83x), 4 (1x)): `unk_u32`.
- Counter-test: none discriminating (PS4 u16 framing fits in slack, 0/84 fails). Walk 84/84; sample
  `stream1-marked.pcapng_tcp-stream-34/11895_…28_24_16` (16 B, `9d1327afbdf1a9c9`) end 0xd: body `00000003`.

## 13. 28.25.16 S2C_GP_COURSE_START_NTC (unresolved -> matched, V by behaviour)

- PC handler `0x7d8010` -> reader `0x8095a0`: u32, u64, u32 (no header); then
  `0xb60b50(sGame, u32_0, 1, u64, isChargeAnnounce(u32_2), 0, 0)`.
- PS4 `OnPacket_S2C_GP_COURSE_START_NTC 0x30c0a0`: u16 Error, u32, u64, u32 then
  `sGame::setChargeCourse(sGame, id, true, time, isChargeAnnounce(type), false, 0)`. DWARF
  `CPacket_S2C_GP_COURSE_START_NTC` {u32 m_unCourseID, u64 m_ullFinishDateTime, u32 m_unannounceType}.
  Same reader shape, same callee pattern and constants: **matched (V)**; fields `CourseID`,
  `FinishDateTime`, `AnnounceType` (V).
- Walk 22/22 (CourseID 1 x21, 15 x1; AnnounceType always 1); sample
  `stream51-marked.pcapng_tcp-stream-10/10057_…28_25_16` (32 B, `76d6adf2c15510f9`) end 0x19.

## 14. 28.26.16 S2C_GP_COURSE_EXTEND_NTC (unresolved -> matched, V by behaviour)

- PC handler `0x7d78f0` -> reader `0x809310`: u32, u64; then `0xb60b50(sGame, u32, 1, u64, 0, 1, 0)`.
- PS4 `OnPacket_S2C_GP_COURSE_EXTEND_NTC 0x30c1c0`: `setChargeCourse(sGame, id, true, endTime, false, true,
  0)`; DWARF {u32 m_unCourseID, u64 m_ullFinishDateTime}: **matched (V)**.
- Walk 21/21; sample `stream51-marked.pcapng_tcp-stream-11/10146_…28_26_16` (32 B, `755b5152bf304c84`) end 0x15.

## 15. 28.34.1 GET_UPDATE_APP_COURSE_BONUS_FLAG_REQ / 28.34.2 …_RES (Season 3-exclusive, confirmed)

- REQ `0x8296f0` empty (V). RES handler `0x7d74c0` -> `0x809020`: header, bool; the handler stores the bool
  into a `sGame` byte when Error == 0 (V). PC strings "OnPacket_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES" and
  "…GP_UPDATE_APP_COURSE_BONUS_RES" (V).
- PS4: no function or DWARF type with `APP_COURSE` / `BONUS_FLAG`: exclusive **confirmed (V)**. Field name
  `unk_bool` (I: "flag" of the packet name; value always 0 in 42 captures).
- Walk 42/42 + 42/42; sample `stream1-marked.pcapng_tcp-stream-35/12115_…28_34_2` (32 B, `10679f121676eabc`) end 0x12.

## 16. Group-31 requests: 31.4.1, 31.9.1, 31.17.1, 31.30.1, 31.31.1, 31.34.1, 31.53.1

| id | PC writer | body | PS4 |
| --- | --- | --- | --- |
| 31.4.1 GET_MY_MEMBER_LIST_REQ | `0x822c70` | empty (V) | `0x19c4600` empty (V) |
| 31.9.1 GET_JOIN_REQUESTED_LIST_REQ | `0x822950` | empty (V) | `0x19c4110` empty (V) |
| 31.17.1 SETTING_UPDATE_REQ | `0x823a80` | bool `IsMemberNotice` (V; PS4 `in_IsMemberNotice`) | `0x19c5af0` (V) |
| 31.30.1 GET_HISTORY_REQ | `0x8227b0` | empty (V) | `0x19cf460` empty (V) |
| 31.31.1 BASE_GET_INFO_REQ | `0x822200` | empty (V) | `0x19c44d0` empty (V) |
| 31.34.1 SHOP_GET_BUFF_ITEM_LIST_REQ | `0x823e30` | empty (V) | `0x19cf0b0` empty (V) |
| 31.53.1 GET_FURNITURE_REQ | `0x824090` | empty (V) | none: no function or DWARF type for a clan furniture packet; exclusive **confirmed (V)** |

Walks: 41/41, 21/21, 42/42 (bool 0 x22, 1 x20), 1/1, 27/27, 25/25, 27/27; samples in the script output
(e.g. 31.17.1 `stream1-marked.pcapng_tcp-stream-34/11897_…31_17_1`, 16 B, `0ee589f4d75be317`, end 0xa).

## 17. 31.9.2 CLAN_GET_JOIN_REQUESTED_LIST_RES

- Handler `0x7cb030` (not a function) -> reader `0x803350`: header, list `0x75d430` CDataClanJoinRequest
  (§ 1.2). PS4 `0x317f20` reads `m_JoinReqList` (`Read_CDataClanJoinRequest__0`): **= PS4 (V)**.
- Code-only: every capture holds an empty list. Walk 21/21; sample
  `stream21-failedlogin-marked.pcapng_tcp-stream-48/12382_…31_9_2` (32 B, `45583158081fb163`) end 0x15.

## 18. 31.30.2 CLAN_GET_HISTORY_RES

- Handler `0x7cae70` -> `0x803250`: header, list CDataClanHistoryElement. PS4 `0x31d170` reads
  `m_ClanHistoryList`: **= PS4 (V)**.
- Walk 1/1 (87 elements); sample `stream4-friendinvites-mail-revival-marked.pcapng_tcp-stream-47/15339_…31_30_2`
  (4912 B, `285746c7d17ca673`) end 0x1322.

## 19. 31.31.2 CLAN_BASE_GET_INFO_RES

- Handler `0x7ca610` -> `0x802de0`: header, list U32 (FunctionInfo.ReleaseIdList), list U32
  (DungeonInfo.ReleaseIdList), PawnExpeditionInfo (3 u8), PartnerPawnInfo, ConciergeInfo, list
  ShopLineupName, list ClanValueInfo, **list CDataFurnitureLayout `0x766f90`** (S3, V).
- PS4 `CPacket_S2C_CLAN_BASE_GET_INFO_RES::ReadPacket 0x19dbe20` reads the first eight members in the same
  order (V) and ends there. Trailing list name: `ClanFurnitureList` (I: furniture by reader identity, § 1.2;
  Arrowgene `ClanFurnitureInfo` is the lead).
- Counter-test: PS4 body fails **27/27**. Walk 27/27; lists up to: function 9, shop lineup names 50, values 2,
  furniture 8; sample `stream69-epi-2-2-marked.pcapng_tcp-stream-11/10819_…31_31_2` (2384 B, `dfac6ce267cef473`) end 0x950.

## 20. 31.34.2 CLAN_SHOP_GET_BUFF_ITEM_LIST_RES

- Handler `0x7cd8f0` -> `0x8046f0`: header, list CDataClanShopBuffItem, u32, CDataClanShopInfo (`0x75e2a0`,
  called through `loc_75E29C+4`; § 1.2). PS4 `ReadPacket 0x19dc020` {m_BuffItemList, u32 m_unClanPoint,
  m_ShopInfo {u32 m_unClanPoint, m_CurrentFunctionList, m_CurrentBuffList}}: **= PS4 (V)**. (The triage
  ratio 0.50 counts only the defined part of the reader.)
- Walk 25/25 (buff items up to 8, CurrentFunctionList up to 26); sample
  `stream21-failedlogin-marked.pcapng_tcp-stream-48/13532_…31_34_2` (688 B, `7713443d8100eec4`) end 0x2a4.

## 21. 31.40.1 CLAN_PARTNER_PAWN_DATA_GET_REQ / 31.40.2 …_RES (31.40.1 "exclusive" -> matched; C)

- REQ `0x823090`: `WritePacket(31, 40, 1)`, `Write_u32` (V). PS4 has no `Send_` function for it, but the
  DWARF type `nUserSession::CPacket_C2S_CLAN_PARTNER_PAWN_DATA_GET_REQ` {u16 m_usError, u32 m_unPawnID}
  exists: the triage "exclusive" mark is **contradicted (C)**; body u32 `PawnID` (V by DWARF; the PS4
  writer was not located, likely inlined, not searched further).
- RES handler `0x7cc210` -> `0x803c00`: header, u32, CDataNoraPawnInfo `0x76f790` (§ 1.2, **S3: second
  CDataCharacterEquipData list**). PS4 `OnPacket_S2C_CLAN_PARTNER_PAWN_DATA_GET_RES 0x338a30`: s32 Result,
  u32, u32, MtString, CDataEditInfo, u8, list CDataCharacterEquipData; DWARF {u32 m_unPawnID, CNoraPawnInfo
  m_PawnInfo}.
- Counter-test: PS4 body fails **22/28** (it fits only when the extra list's trailing bytes stay inside the
  slack). Walk 28/28 (slack 0-15); sample `stream69-epi-2-2-marked.pcapng_tcp-stream-11/10924_…31_40_2`
  (672 B, `c2ae98435453f62d`) end 0x296; REQ sample `stream3-party-experiments-marked.pcapng_tcp-stream-47/13005_…31_40_1`
  (16 B, `a29e2b22e7e2e706`) end 0xd.

## 22. 31.53.2 S2C_CLAN_GET_FURNITURE_RES (unresolved -> Season 3-exclusive, V)

- PC handler `0x7cdd80` (string "OnPacket_CLAN_GET_FURNITURE_RES", V) -> reader `0x8048c0`: header, list
  `0x766f90` CDataFurnitureLayout {u32 ItemID, u32 OmID, u8 LayoutID} (§ 1.2).
- The triage candidate PS4 `OnPacket_S2C_RELEASED_EDIT_PARTS_LIST_GET_RES 0x3354b0` reads
  `Read_CDataUnlockEditParam_ 0x19e8440` {CEditParamPalette {u32, u32}, u8 m_ucUnlockType}: the same wire
  shape, but a different struct. **Rejected (V)**: the PC reader is the one the PC MY_ROOM furniture list
  uses where PS4 reads `CDataFurnitureLayout`, and the PC handler carries the CLAN_GET_FURNITURE name; PS4
  has no clan furniture packet (no name, no DWARF type). No capture counter-test can separate the two (same
  shape).
- Walk 27/27 (lists up to 8); sample `stream21-failedlogin-marked.pcapng_tcp-stream-48/13393_…31_53_2` (96 B,
  `b55ca76f1cc24026`) end 0x5d; first element `00005289 00000000 32` (ItemID 21129, OmID 0, LayoutID 50).

## 23. StatusInfo (T009b extra item): order and names hold; MaxHp is the base, not the cap

Question: 2.0.2 sample 10055 decodes `Hp 4507, MaxHp 760` with `Character.hexpat:136-152`.

- **PC reader `0x77a810` (V)**: stores u32 +4, u32 +8, u8 +0xc, u32 +0x10, +0x14, +0x18, +0x1c, +0x20, +0x24,
  +0x28, +0x2c, +0x30 (wire order = offset order). It sits at CDataCharacterInfo +0x98 (`0x75c315 lea eax,
  [esi+98h]`).
- **PC consumer `0x84eaf0` (V)**, called from the 2.0.2 path (`0x84dea4 lea eax, [ebp+98h]; …; call
  0x84eaf0`, inside the copy routine starting `0x84d710`, called by handler `0x7c7f20`): converts each field
  to float and calls a setter of the human base-info object: +4 -> `0x4055b0` (writes `this+4`), +0x10 ->
  `0x405910` and `0xa296f0` (two setters), +0x18 -> `0x405730` (`this+20`), +8 -> `0x405bf0` (`this+24`),
  +0x14 -> `0x405970` (`this+28`) and `0x405350` (`this+32`), +0x1c -> `0x405490`, +0x20 -> `0x405520`, +0x24
  -> `0x405430` (`this+68`), +0x28, +0x2c, … (setters are obfuscated thunks; the targets named are those
  readable). The RevivePoint byte (+0xc = CharacterInfo +0xa4) is copied separately (`0x84df9f`).
- **PS4 consumer `cNetGameServer::copyRecvCharacterData 0x36e7a0` (V)**: into `nJobParam::cHumanBaseInfo`
  {f32 mHP@8, mMaxHP@12, mFinalMaxHP@16, u32 CheatCheck@20, f32 mLogInHpWhite@24, mStamina@28,
  mMaxStamina@32, mFinalMaxStamina@36, …, mGainHp@64, mGainStamina@68, u32 mGainAtk..mGainMDef@72-87}:
  m_unHp -> mHP, **m_unMaxHp -> mMaxHP and `setFinalMaxHP`**, m_unWhiteHp -> mLogInHpWhite, m_unStamina ->
  mStamina, m_unMaxStamina -> mMaxStamina (+Final), m_unGainHp/Stamina -> mGain*, Gain Atk..MDef as a 16-byte
  copy, m_ucRevivePoint byte separately.
- PC and PS4 agree once the 32-bit vptr shift (-4) is applied: Hp -> +4 (mHP), WhiteHp -> +20
  (mLogInHpWhite), Stamina -> +24, MaxStamina -> +28/+32 (Max/FinalMax), GainAtk -> +68; the 4th field
  (MaxHp) goes to two setters exactly where PS4 sets mMaxHP and calls setFinalMaxHP (I for the obfuscated
  `0x405910`/`0xa296f0` targets). **Order and PS4 names are right for PC (V for order and roles of Hp,
  Stamina, WhiteHp, MaxStamina, Gain*; I for MaxHp's two setter targets).**
- The values are consistent, not a misparse: across all 42 2.0.2 captures MaxHp is 760 and MaxStamina 450
  for every character and job, while Hp, WhiteHp and Gain* vary with job (walk script, last block):
  Kendra job 1 `Hp 1710 = 760 + GainHp 950`; Diana job 10 `760` (Gain 0); Rumi job 5 `Hp 4507, WhiteHp 4589,
  GainHp 2575`. MaxHp/MaxStamina are the base values; the effective cap is recomputed by the client from base
  + gains + equipment (I; Arrowgene `CharacterManager.cs:421` states the same as a lead: "the game wants MaxHP
  to always be 760 and MaxStamina to be 450", then adds Gain and gear). `Hp > MaxHp` is therefore expected.
  No change to `Character.hexpat` is needed; a comment "base value (760/450 in all captures)" would help.

## 24. Summary

PS4 mark: V = confirmed by code (symbol + body, DWARF type, or behaviour); X = no PS4 counterpart
(confirmed by code); X(I) = no counterpart found, inferred. Body bytes for Error == 0 (lists as `+kn`).

| id | name (file) | PS4 | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 28.0.1 | C2S_GP_GET_GP_REQ | V | 0 | 1172 | 4/4 |
| 28.0.2 | S2C_GP_GET_GP_RES | V | 8+22 | 1173 | 4/4 |
| 28.2.1 | C2S_GP_GET_GP_PERIOD_REQ | V | 0 | 12040 | 42/42 |
| 28.2.2 | S2C_GP_GET_GP_PERIOD_RES | V | 8+4+13n | 12344 | 42/42 |
| 28.3.1 | C2S_GP_GET_CAP_REQ | V | 0 | 1175 | 2/2 |
| 28.3.2 | S2C_GP_GET_CAP_RES | V | 8+4 | 1177 | 2/2 |
| 28.6.1 | C2S_GP_COG_GET_ID_REQ | V | 0 | 1186 | 2/2 |
| 28.6.2 | S2C_GP_COG_GET_ID_RES | V | 8+str | 1187 | 2/2 |
| 28.7.1 | C2S_GP_GP_SHOP_DISPLAY_GET_TYPE_REQ | V | 0 | 1179 | 2/2 |
| 28.7.2 | S2C_GP_GP_SHOP_DISPLAY_GET_TYPE_RES | V | 8+4+var | 1181 | 2/2 |
| 28.8.1 | C2S_GP_GP_SHOP_DISPLAY_GET_LINEUP_REQ | V | 4 | 1189 | 38/38 |
| 28.8.2 | S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES | V (S3 element +str +u32) | 8+4+var | 2019 | 38/38 |
| 28.9.1 | C2S_GP_GP_SHOP_DISPLAY_BUY_REQ | V (S3 +u32) | 8 | 2053 | 9/9 |
| 28.9.2 | S2C_GP_GP_SHOP_DISPLAY_BUY_RES | V | 8+var | 2287 | 9/9 |
| 28.17.1 | C2S_GP_GP_COURSE_GET_AVAILABLE_LIST_REQ | V | 0 | 1183 | 10/10 |
| 28.17.2 | S2C_GP_GP_COURSE_GET_AVAILABLE_LIST_RES | V (S3 element, code-only) | 8+4+var (always empty) | 1184 | 10/10 |
| 28.22.1 | C2S_GP_GP_EDIT_GET_VOICE_LIST_REQ | V | 0 | 1478 | 2/2 |
| 28.22.2 | S2C_GP_GP_EDIT_GET_VOICE_LIST_RES | V | 8+4+11n | 1479 | 2/2 |
| 28.23.1 | C2S_GP_GP_SHOP_CAN_BUY_REQ | X | 12 | 2043 | 9/9 |
| 28.23.2 | S2C_GP_GP_SHOP_CAN_BUY_RES | X | 8+17 | 2045 | 9/9 |
| 28.24.16 | S2C_GP_28_24_16_NTC | X(I) | 4 | 11895 | 84/84 |
| 28.25.16 | S2C_GP_COURSE_START_NTC | V (behaviour) | 16 | 10057 | 22/22 |
| 28.26.16 | S2C_GP_COURSE_EXTEND_NTC | V (behaviour) | 12 | 10146 | 21/21 |
| 28.34.1 | C2S_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_REQ | X | 0 | 12114 | 42/42 |
| 28.34.2 | S2C_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES | X | 8+1 | 12115 | 42/42 |
| 31.4.1 | C2S_CLAN_CLAN_GET_MY_MEMBER_LIST_REQ | V | 0 | 12068 | 41/41 |
| 31.9.1 | C2S_CLAN_CLAN_GET_JOIN_REQUESTED_LIST_REQ | V | 0 | 12381 | 21/21 |
| 31.9.2 | S2C_CLAN_CLAN_GET_JOIN_REQUESTED_LIST_RES | V (code-only) | 8+4+var (always empty) | 12382 | 21/21 |
| 31.17.1 | C2S_CLAN_CLAN_SETTING_UPDATE_REQ | V | 1 | 11897 | 42/42 |
| 31.30.1 | C2S_CLAN_CLAN_GET_HISTORY_REQ | V | 0 | 15334 | 1/1 |
| 31.30.2 | S2C_CLAN_CLAN_GET_HISTORY_RES | V | 8+4+var | 15339 | 1/1 |
| 31.31.1 | C2S_CLAN_CLAN_BASE_GET_INFO_REQ | V | 0 | 13370 | 27/27 |
| 31.31.2 | S2C_CLAN_CLAN_BASE_GET_INFO_RES | V (S3 +furniture list) | var | 10819 | 27/27 |
| 31.34.1 | C2S_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_REQ | V | 0 | 13531 | 25/25 |
| 31.34.2 | S2C_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_RES | V | var | 13532 | 25/25 |
| 31.40.1 | C2S_CLAN_CLAN_PARTNER_PAWN_DATA_GET_REQ | V (DWARF; triage "exclusive" C) | 4 | 13005 | 28/28 |
| 31.40.2 | S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES | V (S3 +equip list) | var | 10924 | 28/28 |
| 31.53.1 | C2S_CLAN_GET_FURNITURE_REQ | X | 0 | 13391 | 27/27 |
| 31.53.2 | S2C_CLAN_GET_FURNITURE_RES | X (candidate rejected) | 8+4+9n | 13393 | 27/27 |

Triage corrections: `recompiled_body` "yes" for 28.0.2 holds; for 28.9.2, 31.31.2, 31.34.2 the recompilation
body is a `DDON_STUB` (no body). 31.40.1 exclusive -> matched (C). 28.24.16 -> exclusive (I); 28.25.16,
28.26.16 -> matched (V); 31.53.2 -> exclusive (V).

## 25. Shared types for pattern authors

Reuse: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`), `Character.hexpat`
(`CDataCommunityCharacterBaseInfo`, `CDataCharacterName`), `Context.hexpat` (`CDataEditInfo`), `Pawn.hexpat`
(`CDataCharacterEquipData`), `Clan.hexpat` as is. Framing as T003 § 18 (inline RES header; NTCs without
header).

Add to `include/GP.hexpat` (names PS4 DWARF unless marked I):

| Struct | PC reader | Wire |
| --- | --- | --- |
| `CDataGPPeriod` | `0x7678e0` | u32 GP, bool IsFreeGP, u64 Period |
| `CDataGPShopDisplayType` | `0x767d00` | u32 ID, MtString Name, u32 InGameUrlID |
| `CDataGPShopDisplayLineup` | `0x767be0` | § 1.1 (S3: `unk_MtString` after LineupID, then `unk_u32_0..3`) |
| `CDataGPCourseAvailable` | `0x7671a0` | u32 ID, MtString Name, u64 UseLimitTime, u32 CourseID, u32 LineupID, MtString unk_MtString |
| `CDataEditParam` | `0x764b20` element | u32 ParamTypeId, u32 UID, bool IsValid, bool IsGp, bool IsPitchEnable |

Add to `include/Clan.hexpat`:

| Struct | PC reader | Wire |
| --- | --- | --- |
| `CDataClanJoinRequest` | `0x75d430` | u32 ClanID, MtString ClanName, CDataCommunityCharacterBaseInfo, s64 Created |
| `CDataClanHistoryElement` | `0x75d390` | s64 Date, u8 Type, CDataCharacterName, u32 Value1..3, MtString FreeText |
| `CDataClanPawnExpeditionInfo` | `0x771e80` | u8 SallyStatus, u8 GoldenSallyPrice, u8 ChargeSallyPrice |
| `CDataClanPartnerPawnInfo` | `0x75d770` | MtTypedArray<CDataCommonU32> MyPartnerPawnList, MemberPartnerPawnList |
| `CDataClanConciergeNpc` / `CDataClanConciergeInfo` | `0x75d160` / `0x75d120` | {u32 NpcId, u32 Price, bool IsInit, u32 SortId} / {u32 NpcId, list} |
| `CDataClanShopLineupName` | `0x75e2f0` | u32 LineupID, MtString Name |
| `CDataClanValueInfo` | `0x75e500` | u8 Type, u32 Value |
| `CDataFurnitureLayout` | `0x766f90` | u32 ItemID, u32 OmID, u8 LayoutID (also MY_ROOM furniture; could live in a shared include) |
| `CDataClanShopBuffInfo` / `CDataClanShopBuffItem` | `0x75dd30` / `0x75dee0` | {u32 BuffID, u8 BuffType} / § 1.2 |
| `CDataClanShopInfo` | `0x75e2a0` | u32 ClanPoint, list CurrentFunctionList, list CurrentBuffList |
| `CDataNoraPawnInfo` | `0x76f790` | § 1.2 (S3 second equip list, name I); could live in `Pawn.hexpat` |

Packet bodies (after the header): 28.24.16 `u32 unk_u32`; 28.25.16 `u32 CourseID, u64 FinishDateTime, u32
AnnounceType`; 28.26.16 `u32 CourseID, u64 FinishDateTime`; 28.23.1 `u32 LineupId (I), u32 unk_u32_0, u32
unk_u32_1`; 28.23.2 `bool CanBuy (I), u32 LineupId (I), u32 unk_u32_0, u32 unk_u32_1, u32 unk_u32_2`; 28.34.2
`bool unk_bool`; 28.9.1 `u32 DisplayLineupId, u32 unk_u32`; 31.40.2 `u32 PawnID, CDataNoraPawnInfo PawnInfo`;
31.31.2 PS4 members + `MtTypedArray<CDataFurnitureLayout> ClanFurnitureList (I)`.

## 26. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`:

1. `CDataGPCourseAvailable` writes `ID, CourseName, UseLimitTime, CourseID, LineupID, BackIconID, FrameIconID`
   (PS4 layout); PC 03040008 reads `u32, MtString, u64, u32, u32, MtString` (§ 1.1). Misplacement (C),
   invisible in captures (lists always empty).
2. Agree with PC: `S2CGpGetGpRes`, `S2CGpGetGpPeriodRes` / `CDataGPPeriod`, `S2CGpGpEditGetVoiceListRes` /
   `CDataEditParam`, `S2CGPCourseStartNtc` (u32, u64, u32), `S2CGPCourseExtendNtc` (u32, u64),
   `S2CClanClanBaseGetInfoRes` (incl. trailing `ClanFurnitureInfo` list), `S2CClanClanShopGetBuffItemListRes`
   / `CDataClanShopBuffItem` / `CDataClanShopInfo`, `CDataClanHistoryElement`, `CDataClanJoinRequest`,
   `C2SClanClanPartnerPawnDataGetReq` (u32 PawnId), `S2CClanClanPartnerPawnDataGetRes` / `CDataNoraPawnInfo`
   (two equip lists), `S2CClanGetFurnitureRes` / `CDataFurnitureLayout` (ItemID, OmID, LayoutID).
3. `S2C_GP_COURSE_END_NTC` = 28.27.16 in `PacketId.cs` agrees with the code mapping (§ 12). Arrowgene has no
   structure for 28.7, 28.8, 28.9, 28.23, 28.24.16, 28.34 (ids only).

## 27. Open items and checks not run

- Names without code backing (I): the four trailing u32 and the MtString of `CDataGPShopDisplayLineup`; the
  MtString of `CDataGPCourseAvailable`; 28.9.1 second u32; 28.23.x fields beyond CanBuy/LineupId; 28.24.16
  u32; 28.34.2 bool; the 31.31.2 furniture list and 31.40.2 second equip list names.
- 28.24.16: meaning of the stored u32 (object `n3_0+0x4ad0`, field `+0x34c`) not traced to a reader.
  28.28/28.29.16 mapping to PS4 START/END_PARTY rests on database names (outside this package's ids).
- 31.40.1: the PS4 writer of `CPacket_C2S_CLAN_PARTNER_PAWN_DATA_GET_REQ` was not located (DWARF type only).
- Code-only (never non-empty in captures): 28.17.2 list, 31.9.2 list, 28.9.2 CommonIdList.
- 31.53.2 vs `CDataUnlockEditParam`: same wire shape; settled by code, not by capture.
- StatusInfo: the PC setters `0x405910`/`0xa296f0` are obfuscated thunks; their target offsets were not
  resolved (I by parallel with PS4).
- ImHex not run (not on `PATH`); no pattern written (outside this package).
