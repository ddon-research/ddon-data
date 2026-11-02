# 006 T012: groups 19 SKILL, 20 SHOP, 25 ORB_DEVOTE, 27 ACHIEVEMENT, 29 EQUIP, 39 GACHA, 43 LOADING_INFO

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T012-achievement-equip-skill.md`; the 40 rows of groups 19, 20,
25, 27, 29, 39 and 43 in `research/T001-triage.tsv` (groups 27, 29, 19, 39, 25, 43, 20: 14 + 10 + 4 + 4 + 2 +
2 + 4 = 40 ids; 688 captures). Base `89fcfbb03e`. Marks: **V** verified in code (or
by capture for walk results), **I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t012/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t012/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays; `ida_ua.decode_insn` with
  `GENDSM_FORCE_CODE` for linear decoding; `ida_typeinf` for DWARF members). Nothing renamed, retyped,
  commented, patched or reanalysed.
- PC primitives and framing as T003/T005/T011 § 0 (`nPacket::Read_*`, `Write_*`, `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` (`{table, count}` per group): 19 `{0x212f718, 51}`, 20
  `{0x212f6e8, 2}`, 25 `{0x212da08, 7}`, 27 `{0x212ac30, 11}`, 29 `{0x212c478, 30}`, 39 `{0x212c880, 2}`, 43
  `{0x212d708, 1}`; stride 0x18, key `(sub<<16)|id` at +0x10; entry +0 is stored by the initializer
  (`mov [esp+var], <handler>`, `movq xmm0`, `movq <entry>, xmm0`; e.g. `0x1a2757d` stores `0x7c3370` into
  27.0.2 `0x212ac30`, `0x1a2775d` stores `0x7c2f80` into 27.8.16). Every S2C `pc_va` of the triage equals its
  traced table handler (**V, 21/21**).
- **Not functions in the PC database** (decoded linearly, no change): handlers 27.0.2 `0x7c3370`, 27.1.2
  `0x7c3500`, 27.2.2 `0x7c3280`, 27.4.2 `0x7c3690` (misaligned decoding at the IDA function boundary; the
  read path is `0x7c36db call 0x7ff8d0`, string at `0x1bd2ca0`), 25.5.2 `0x7e64d0` (reader `0x810120`, also
  not a function), 39.0.2 `0x7d6cf0`; list readers `0x758810` (achievement progress), `0x768430` (gacha
  list), `0x76d550` (loading schedule), `0x769330` (goods list).
- PC writers (C2S): `WritePacket(p, group, id, 1, -1)`, group/id read from the call (V each, 19/19).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, behaviour), never by PS4 id.
  RES header (V, every PC RES reader here): `Read_s32` Error; non-zero -> return; else `Read_s32` Result, body.
  PS4 reads `u16 m_usError` + `s32/u32 Result`. PC NTC readers read **no** header (V: 27.8.16, 27.9.16,
  29.17.16). PS4 C2S writers start with three `Write_u16` (PS4 framing). The DWARF `bool m_bIsReceived`
  member of every PS4 packet is a client flag, never read from the wire (V: no PS4 reader reads it).
- **Walk**: `specs/006-packet-pattern-coverage/research/T012-walk.py` (stdlib; run from `D:/ddon-data`
  with `python -X utf8 -I specs/006-packet-pattern-coverage/research/T012-walk.py`; sha256 prefix
  `f092ce191801bb83`; holds every PC layout below, the PS4 counter-test variants, `tally` fields and an
  extra block of value sets). Input `packets/decrypted_raw/*/`, every file whose suffix is `.<g>_<id>_<sub>`
  of the 40 ids (each suffix carries exactly one packet name). Header check: group, u16 id, sub, source
  (0x00 C2S, 0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun. **Totals: 688 files,
  header 688/688, fit 688/688, no RES with Error != 0.** Samples: file (relative to `packets/decrypted_raw/`),
  size, sha256 first 16 hex digits, body end offset.
- Recompilation cross-check (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`): `UserSession/
  S2C.cpp` implements **no** `ReadPacket` of this package (none of the 19 RES/NTC classes has a body there);
  `C2S.cpp` has `CPacket_C2S_BUY_SHOP_GOODS_REQ::WritePacket(u32 in_GoodsIndex, u32 in_Num, u8 in_StorageType,
  u32 in_Price)` as a `DDON_STUB` (signature only) and no `C2S_GACHA_BUY_REQ`. `PacketData/` (`Gacha.h`
  CDataGachaSettlementInfo, `Shop.h` CDataGoodsParam, `Skill.h` CDataNormalSkillParam, `Achievement.h`
  CDataAchievementProgress, `Loading.h` CDataLoadingInfoSchedule) declares the same members and offsets as
  the PS4 DWARF. Triage `recompiled_body` "yes" (20.1.1) is overstated: the writer is a stub.

Field-name sources: PS4 DWARF member (`m_`/type prefix dropped) **V**; other names **I** with the basis
stated; a Season 3 field without code backing is `unk_*` (server names only as leads in comments).

## 1. Shared structures

Reused from the includes, readers re-read here (no change): `CDataEquipJobItem` (`0x766120`, `Pawn.hexpat`),
`CDataEquipItemInfo` (S3, element `0x766070`, list `0x765fb0`, `Login.hexpat`), `EquipElementParam`
(`0x765a90` {u8, u32, u16}), `AddStatusParam` (`0x765ba0`), `EquipStatParam` (shape {u8, u16}, list `0x766210`),
`CDataOrbGainExtendParam` (`0x7701c0`, 13 x u16, `Pawn.hexpat`), `CDataAchievementIdentifier` ({u32, u32},
`Pawn.hexpat`).

New (PS4 = PS4 02020005 reader; V = same widths and order read in both):

| Struct | PC reader | PS4 02020005 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataAchievementProgress` | list `0x758810` (loc) | `Read_CDataAchievementProgress_ 0x19f0970` {CAchievementIdentifier m_AchieveIdenfier, u32 m_unCurrentNum, u32 m_unSeqence, s64 m_llCompleteDate} | {u32, u32}, u32, u32, s64 (V, = PS4) |
| `CDataAchievementRewardProgress` | list `0x758960` | `0x19f05f0` {u32 m_unRewardId, u32 m_unCurrentNum, u32 m_unTargetNum, b8 m_bIsRecieved} | same (V) |
| `CDataAchievementFurnitureReward` | list `0x7585a0`, element `0x7586a0` | `0x19e6bd0` {u32 m_unRewardId, u32 m_unSortId, CAchievementIdentifier m_AchieveIdenfier, u32 m_unFurnitureItemId, b8 m_bIsRecieved} | u32 x5, bool (V) |
| `CDataAchieveRewardCommon` | list `0x7584b0`; writer `0x77d160` | `0x19e6810` {u8 m_ucType, u32 m_unRewardId} | same (V) |
| 27.8.16 element (S3) | list `0x758720` | PS4 uses `CDataCommonU32` | u32 AchievementId, **u8** (S3, § 9) |
| `CDataS2CCharacterEquipInfo` | list `0x7776e0`; C2S writer `0x77d2d0` | `0x19fdbc0` {MtString m_wstrEquipItemUID, u8 m_ucEquipCategory, u8 m_ucEquipType}; C2S twin `CDataC2SChangeCharacterEquipInfo` (`Write_ 0x1a37960`, same members) | same (V) |
| `CDataPawnEquipInfo` | list `0x7777e0` | `CDataS2CPawnEquipInfo` `0x1a0ea50` {u32 m_unPawnID, m_CharacterEquipList, m_EquipJobItemList} | same (V) |
| `CDataItemEquipElement` | list `0x76aad0` | `0x19e4070` {MtString m_wstrItemUID, list CDataEquipElementParam {u8, u32}} | MtString, list `EquipElementParam` (**S3 u16 per param**, V) |
| S3 equip-change tail | `0x765f70` (12 callers: 29.1.2, 29.2.2, 29.1.16, 29.4.2, 29.4.16, 29.5.2, four group-7 readers) | none | u8, list `0x766210` {u8, u16} (V shape; § 13) |
| `CDataNormalSkillParam` | list `0x76f820` | `0x19f1cc0` {u8 m_ucJob, u32 m_unSkillNo, u32 m_unIndex, u32 m_unPreSkillNo} (reader stores +0xc, +0x10, +0x14 in that order) | same (V) |
| `CDataSetAcquirementParam` | list `0x777f10` | `0x19f1f40` {u8 m_ucJob, u8 m_ucType, u8 m_ucSlotNo, u32 m_unAcquirementNo, u8 m_ucAcquirementLv} | same (V) |
| goods element (S3) | list `0x769330` (loc), element `0x769450` | `CDataGoodsParam` `0x1a085c0` {u32 x6} | u32, u32, u32, u8 (1-byte read `0x8bc3e0`), bool, s64, s64, list requirement (§ 6) |
| goods requirement (S3) | list `0x778770`, element `0x7788a0` | none | u32, u32, bool, u32, bool, u32 x5, s64, s64 |
| `CDataGachaItemInfo` | list `0x7685e0` | `0x19ef190` {u32 m_unItemId, m_unItemNum, m_unRank, m_unEffect, f64 m_dProbability} | same (V) |
| `CDataGachaSettlementInfo` | list `0x768720`, element `0x768830` | `0x19efae0`/`0x19effe0` {u32 m_unDrawGroupId, m_unId, m_unPrice, m_unBasePrice, m_unPurchaseNum, m_unPurchaseMaxNum, m_unSpecialPriceNum, m_unSpecialPriceMaxNum} | the 8 PS4 u32 + **S3 trailing u32** (V width) |
| `CDataGachaDrawInfo` | list `0x768310` | `0x19efcf0` {u32 m_unNum, b8 m_bIsBonus, list CDataGachaItemInfo} | same (V) |
| `CDataGachaDrawGroupInfo` | list `0x7681e0` | `0x19ef860` {m_GachaSettlementList, m_GachaDrawList} | same, S3 settlement (V) |
| `CDataGachaInfo` | list `0x768430` (loc), element `0x7684f0` | `0x19ef760` {u32 m_unId, s64 m_llBegin, s64 m_llEnd, MtString m_wstrName, m_wstrDescription, m_wstrDetail, u8 m_ucWeightDispType, MtString m_wstrWeightDispTitle, m_wstrWeightDispText, m_wstrListAddr, m_wstrImageAddr, m_DrawGroups} | same, S3 settlement (V) |
| `CDataLoadingInfoSchedule` | list `0x76d550` (loc) | `0x19ee8a0` {MtString m_wstrText, u32 m_unImageId, u32 m_unPriority, s64 m_llBeginDateTime, s64 m_llEndDateTime} | same (V) |

## 2. 19.1.1 GET_ACQUIRABLE_SKILL_LIST_REQ / 19.2.1 GET_ACQUIRABLE_ABILITY_LIST_REQ

- PC writers `0x83ccf0` (19, 1, 1) and `0x83cc00` (19, 2, 1): `Write_u32 a3`, `Write_u8 a4` (V). Caller
  `0x8683e0`/`0x868350` (via `0x4ec740`): the u8 is the lowest set bit 1-11 of a job mask (a job id), the u32
  is a2[2] of the request record.
- PS4 `Send_C2S_GET_ACQUIRABLE_SKILL_LIST_REQ 0x19bf470(u8 in_Job)` / `…_ABILITY_LIST_REQ 0x19bf5c0(u8
  in_Job)`: **match V (symbol pair with the PC RES strings, same u8)**. **S3: + leading u32.**
- Names: `Job` (V, PS4); the u32 `unk_CharacterId` (I: every capture holds 0x0020b8f8 = 2144504, the player's
  CharacterID in the same stream (T011 § 7); server lead `CharacterId`).
- Counter-test: the PS4 body (u8 only) fits 4/4 and 16/16 (slack 2 + 4 < 15): inconclusive, the writer decides.
- Walk 4/4 + 16/16; Job 10 (19.1.1), 0/2/3/10 (19.2.1). xxd 19.1.1
  `stream1-marked.pcapng_tcp-stream-35/26337_…19_1_1` (16 B, `dee3867534fcf4f1`):
  `1300 0101 00 | 00 0001 88 | 00 20b8 f8 | 0a` end 0x0e. 19.2.1 sample `…/26341_…19_2_1` (16 B,
  `800eca809893a578`) end 0x0e.

## 3. 19.28.1 GET_CURRENT_SET_SKILL_LIST_REQ / 19.28.2 …_RES

- REQ `0x83cde0`: `WritePacket(19, 28, 1)`, empty (V; PS4 `0x19c10a0` empty).
- RES `0x7fae10` (string "…OnPacket_SKILL_GET_CURRENT_SET_SKILL_LIST_RES") -> `0x81b3b0`: header, list
  `0x76f820` (CDataNormalSkillParam), list `0x777f10`, list `0x777f10` (CDataSetAcquirementParam). PS4
  `CPacket_S2C_GET_CURRENT_SET_SKILL_LIST_RES::ReadPacket 0x19da530` {m_NormalSkillList, m_SetCustomSkillList,
  m_SetAbilityList}: **= PS4 (V)**.
- Walk 41/41 + 41/41; lists up to 4/8/10; sample `stream51-marked.pcapng_tcp-stream-11/10281_…19_28_2`
  (224 B, `b6125ddad19779b3`) end 0xd4.

## 4. 20.0.1 GET_SHOP_GOODS_LIST_REQ

- PC `0x83c950`: `WritePacket(20, 0, 1)`, `Write_u32` (V). PS4 `Send_C2S_GET_SHOP_GOODS_LIST_REQ 0x19c1440(u32
  in_ShopID)`: **= PS4 (V)**, field `ShopID` (V). Walk 18/18 (ShopID 223 x17, 230 x1); sample
  `stream1-marked.pcapng_tcp-stream-35/13014_…20_0_1` (16 B, `716f050b9bc7ec3a`) end 0x0d.

## 5. 20.1.1 BUY_SHOP_GOODS_REQ

- PC `0x842670`: `WritePacket(20, 1, 1)`, u32, u32, u8, u32 (V). PS4 `CPacket_C2S_BUY_SHOP_GOODS_REQ::WritePacket
  0x1a34e30` {u32 m_unGoodsIndex, u32 m_unNum, u8 m_ucStorageType, u32 m_unPrice}: **= PS4 (V)**.
- Walk 17/17 (StorageType 19 always); xxd `stream1-marked.pcapng_tcp-stream-35/13398_…20_1_1` (32 B,
  `63dcc936b10dcaea`): `1400 0101 00 | 00 0000 ae | 00 0000 03 | 00 0000 01 | 13 | 00 0000 09` -> GoodsIndex 3,
  Num 1, StorageType 19, Price 9, end 0x16.

## 6. 20.0.2 GET_SHOP_GOODS_LIST_RES (Season 3 body)

- PC `0x7fa010` (string "…OnPacket_SHOP_GET_SHOP_GOODS_LIST_RES") -> `0x81adc0`: header, then `0x778710`:
  `Read_u32`, `Read_u8`, `Read_u8`, list `0x769330`; element `0x769450`: u32, u32, u32, 1-byte read
  `0x8bc3e0`, `Read_bool`, `Read_s64`, `Read_s64`, list `0x778770`; requirement element `0x7788a0`: u32, u32,
  bool, u32, bool, u32 x5, s64, s64 (V widths and order).
- PS4 `OnPacket_S2C_GET_SHOP_GOODS_LIST_RES 0x301ac0`: header + `m_GoodsParamList` of CDataGoodsParam {u32
  x6}. **Match V (symbol pair, string), body Season 3**: the PS4 body fails **18/18**.
- Names (I, none code-backed): top u32 `ShopID` (echoes the 20.0.1 ShopID in 18/18 pairs), first u8
  `unk_u8` (always 0), second u8 `unk_PointType` (always 11, the value 20.1.2 returns, § 7). Element: u32
  `Index` (0, 1, 2, ...; bit 15 set on some, e.g. 0x800d), u32 `ItemId` (values 18828-18832 are item ids
  by range; I), u32 `Price` (5-24), u8 `Stock` (255 or small counts), bool, s64 x2 (always 0 in
  captures; server lead SalesPeriodStart/End), requirement list (0 or 1 entries). Keep `unk_` names unless
  the implementer accepts these bases; server leads in § 19.
- Walk 18/18; lists up to 44 goods; sample `stream76-marked.pcapng_tcp-stream-11/11635_…20_0_2` (2928 B,
  `4007375fd514a2fb`) end 0xb6b.

## 7. 20.1.2 BUY_SHOP_GOODS_RES (Season 3: no u32)

- PC `0x7f9f70` (string "…OnPacket_SHOP_BUY_SHOP_GOODS_RES") -> `0x81ad40`: header, `Read_u8` only (V).
- PS4 `OnPacket_S2C_BUY_SHOP_GOODS_RES 0x301c40`: header, `Read_u8 m_ucPointType`, `Read_u32 m_unPoint`.
  **Match V (symbol pair), S3 drops m_unPoint.** Field `PointType` (I: first PS4 member, same width).
- Counter-test: the PS4 body fits 17/17 by length (slack 14), but its u32 reads padding: 10 distinct values in
  17 captures (`46be641f`, `f496a0bd`, ...) besides 7 zeros: supports the PC reader (I, capture).
- Walk 17/17 (value 11 always); xxd `stream1-marked.pcapng_tcp-stream-35/13405_…20_1_2` (32 B,
  `59cb187f0e468790`): `1400 0102 34 | 0000 0000 | 0000 0000 | 0b` end 0x12, then padding.

## 8. 25.5.1 GET_ORB_GAIN_EXTEND_PARAM_REQ / 25.5.2 …_RES

- REQ `0x830dd0`: `WritePacket(25, 5, 1)`, empty (V; PS4 `0x19c2c20` empty).
- RES `0x7e64d0` (string at `0x1bcdf70` "…OnPacket_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_RES") -> `0x810120`:
  header, `0x7701c0` (13 x u16). PS4 `0x305320`: header, `Read_CDataOrbGainExtendParam_ 0x1a04c60`
  (m_ExtendParam): **= PS4 (V)**.
- Walk 43/43 + 43/43; sample `stream1-marked.pcapng_tcp-stream-35/12047_…25_5_2` (48 B, `f5576cdd57ae280b`)
  end 0x2b.

## 9. 27.0.x - 27.4.x ACHIEVEMENT lists

| id | PC | PS4 02020005 | Body (after header) |
| --- | --- | --- | --- |
| 27.0.1 | `0x81de30` empty | `Send_… 0x19cb0f0` empty | none (V) |
| 27.0.2 | `0x7c3370` -> `0x7ff750`: list `0x758810` | `0x309020` m_AchievementProgressList | `MtTypedArray<CDataAchievementProgress> AchievementProgressList` (V) |
| 27.1.1 | `0x81dfb0` empty | `0x19cb220` empty | none (V) |
| 27.1.2 | `0x7c3500` -> `0x7ff850`: list `0x758960` | `0x309590` m_BackgroundProgressList | `MtTypedArray<CDataAchievementRewardProgress> BackgroundProgressList` (V) |
| 27.2.1 | `0x81dd70` empty | `0x19cb350` empty | none (V) |
| 27.2.2 | `0x7c3280` -> `0x7ff6d0`: list `0x7585a0` | `0x309710` m_RewardList | `MtTypedArray<CDataAchievementFurnitureReward> RewardList` (V) |
| 27.3.1 | `0x81def0` empty | `0x19cb480` empty | none (V) |
| 27.3.2 | `0x7c3450` -> `0x7ff7d0`: list `0x7584b0` | `0x309890` m_RewardList | `MtTypedArray<CDataAchieveRewardCommon> RewardList` (V) |
| 27.4.1 | `0x81e070`: writer `0x77d160` (count + {u8, u32}) | `Send_C2S_ACHIEVEMENT_REWARD_RECEIVE_REQ 0x19cb5b0(const MtTypedArray<CDataAchieveRewardCommon>* in_RewardList)` | `MtTypedArray<CDataAchieveRewardCommon> RewardList` (V) |
| 27.4.2 | `0x7c3690` (linear) -> `0x7ff8d0`: list `0x7584b0` x2 | `0x309b80` m_RecievedRewardList, m_RewardList | two `MtTypedArray<CDataAchieveRewardCommon>`: `RecievedRewardList` (DWARF spelling), `RewardList` (V) |

All **= PS4 (V)**; each PC RES handler carries its "…OnPacket_ACHIEVEMENT_ACHIEVEMENT_…_RES" string. After
27.4.2 the PC sets `[dword_21C08C4+0x30]` (the same flag 27.9.16 sets, § 11).

Walk: 27.0.1 1/1, 27.0.2 1/1 (678 entries; `stream65-epi1-4-marked.pcapng_tcp-stream-9/1885_…27_0_2`, 16304 B,
`2926e7038f18edc1`, end 0x3fa5); 27.1.x 1/1 + 1/1 (50 entries; `…/1888_…27_1_2`, 672 B, `66b4ecdeb78e3e48`,
end 0x29f); 27.2.x 2/2 + 2/2 (136 entries; `…/1894_…27_2_2`, 2880 B, `72c0a0c574d338d2`, end 0xb3d); 27.3.x
42/42 + 42/42 (0, 1 or 3 entries; `stream1-marked.pcapng_tcp-stream-35/12106_…27_3_2`, 48 B,
`798959996d326825`, end 0x24); 27.4.1 1/1 (1 entry; `stream65-…/1956_…27_4_1`, 32 B, `e8c2680d906faa38`, end
0x12); 27.4.2 1/1 (both lists empty: code-only; `…/1958_…27_4_2`, 32 B, `5fef010c31e6b4e2`, end 0x19).

## 10. 27.8.16 ACHIEVEMENT_COMPLETE_NTC (unresolved -> matched, V; Season 3 element)

- PC handler `0x7c2f80` (packet object tagged group 27, id 8, sub 16): `0x758720` = count + elements {`Read_u32`
  +4, `Read_u8` +8}; **no header**. Per element: name lookup `sub_B77340(id)`, chat line
  `getMsgFromIdxInfo(…, 5)` gated by an option byte of sGame, a banner (`getMsgFromIdxInfo(…, 0xEC)`,
  `MtString::format`), `sub_B67C50(6, id, 1)` **if the u8 == 6**, then `sub_BE6B90(sQuestManagerExt)`.
- PS4 `OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTC 0x3091a0`: `Read_u16` error, `Read_CDataCommonU32_`
  (m_AchievementIdList); per id `sGUIExt::getAchievementData`, skip when `mCategory == 6`,
  `getAchievementName`, chat message gated by `mIsAchievementDispAnnounce`, banner, then
  `sQuestManagerExt::notifyGetAchievement`: the same flow, **match V (behaviour)**. Field
  `AchievementIdList` (V).
- **S3**: element {u32 AchievementId, u8}; the client now takes the category-6 test from the wire. Name the u8
  `unk_Category` (I: PS4 tests `mCategory == 6` where PC tests the u8 == 6; capture values 1-4; 27.10.1 sends
  category 6 too).
- Counter-tests: PS4 framing (u16 first) fails **8/8**; the PS4 element (u32 only) fits 8/8 (one element, the
  u8 within slack): inconclusive, the reader decides.
- Walk 8/8; one element each; u8 in {1, 2, 3, 4}. xxd `stream65-epi1-4-marked.pcapng_tcp-stream-9/1492_…27_8_16`
  (32 B, `f23fa0e462cde0be`): `1b00 0810 34 | 0000 009b | 0000 0001 | 0000 09e4 | 04` -> id 2532, u8 4, end 0x12.

## 11. 27.9.16 ACHIEVEMENT_RECEIVABLE_REWARD_NTC (unresolved -> matched, V)

- PC handler `0x7c35b0` (object tagged 27, 9, 16): `0x7584b0` = list CDataAchieveRewardCommon; no header;
  on success sets byte `[dword_21C08C4+48] = 1`.
- PS4 `OnPacket_S2C_ACHIEVEMENT_RECEIVABLE_REWARD_NTC 0x309a10`: `Read_u16` error,
  `Read_CDataAchieveRewardCommon_` (m_RewardList), on success `mIsAvailableAchieve = true`: **match V (list
  type + behaviour)**. Field `RewardList` (V).
- Counter-test: PS4 framing fails **3/3**. Walk 3/3; xxd `stream65-…/1493_…27_9_16` (32 B,
  `7ccc4f192e38d2ec`): `1b00 0910 34 | 0000 009c | 0000 0001 | 02 | 0000 003f` -> Type 2, RewardId 63, end 0x12.

## 12. 27.10.1 / 27.10.2 GET_CATEGORY_PROGRESS_LIST (exclusive, confirmed V)

- REQ `0x81dc90`: `WritePacket(27, 10, 1)`, `Write_u8` (V). RES `0x7c31d0` (string
  "…OnPacket_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES") -> `0x7ff650`: header, list `0x758810`,
  **the reader of 27.0.2** (V): body `MtTypedArray<CDataAchievementProgress>`.
- PS4: no symbol, string or `nUserSession` packet containing `CATEGORY_PROGRESS` (name search over all
  PS4 02020005 names: 0 hits). **Exclusive (V)**; only the packet is new, its element type is shared.
- Names: REQ u8 `unk_Category` (I: 5/5 captures send 6; server lead `Category`); RES list
  `AchievementProgressList` (I, by the shared reader with 27.0.2).
- Walk 5/5 + 17/17 (19 entries each); xxd 27.10.1 `stream85-marked.pcapng_tcp-stream-11/100006_…27_10_1`
  (16 B, `2c746dbe35b22e79`): `1b00 0a01 00 | 0000 f29f | 06` end 0x0a. 27.10.2 sample `…/100008_…27_10_2`
  (480 B, `1a1676c29f0cd39a`) end 0x1dd.

## 13. 29.0.x, 29.1.x, 29.2.x, 29.15.x EQUIP lists

- 29.0.1 `0x827f20`, 29.15.1 `0x827fe0`: empty (V; PS4 `0x19b6770`, `0x19be950` empty).
- 29.0.2 `0x7d5340` (string "…OnPacket_EQUIP_GET_CHARACTER_EQUIP_LIST_RES") -> `0x808020`: header, list
  `0x7776e0`, list `0x766120`, list `0x7777e0`. PS4 `CPacket_S2C_GET_CHARACTER_EQUIP_LIST_RES::ReadPacket
  0x19d8610` {m_CharacterEquipList, m_EquipJobItemList, m_PawnEquipItemList}: **= PS4 (V)**.
- 29.1.1 `0x8278e0` / 29.2.1 `0x8279c0`: `WritePacket(29, 1|2, 1)`, writer `0x77d2d0` (count + {MtString, u8,
  u8}). PS4 `Send_C2S_CHANGE_CHARACTER_EQUIP_REQ 0x19b69e0` / `…_STORAGE_EQUIP_REQ 0x19b6b20`
  (`MtTypedArray<CDataC2SChangeCharacterEquipInfo> in_ChangeCharacterEquipList`): **= PS4 (V)**.
- 29.1.2 `0x7d47e0` / 29.2.2 `0x7d4870` (strings "…OnPacket_EQUIP_CHANGE_CHARACTER_EQUIP_RES",
  "…_STORAGE_EQUIP_RES") -> `0x807910` / `0x8079a0`: header, list `0x7776e0`, **then `0x765f70`: `Read_u8`,
  list `0x766210` {u8, u16}**. PS4 `0x30f1a0` / `0x30f450`: header, `m_CharacterEquipList` only. **S3: +
  tail struct.** Consumer `0x7d4760`: when the list is non-empty, if the u8 equals the current job
  (`sGamePointer[3142]`) the list goes to `sub_468CA0`, and `sub_B9E8C0(myPlayerContext, u8, list, 1)`. Names:
  `unk_Job` (I: compared with the current job; captures 10 = the job of 19.1.1 in the same session),
  `unk_List` (shape EquipStatParam; server lead `CDataJobChangeJobResUnk0 {Unk0, List<CDataCharacterItemSlotInfo>}`).
  Counter-test: the PS4 body fits 5/5 and 2/2 (the tail is 5 bytes, inside slack): inconclusive, the reader
  decides.
- 29.15.2 `0x7d5480` (string "…OnPacket_EQUIP_GET_CRAFT_LOCKED_ELEMENT_LIST_RES") -> `0x8080c0`: header, list
  `0x76aad0` {MtString, list `0x765a90`}. PS4 `0x338280` m_LockedElementList (CDataItemEquipElement):
  **match V, S3 via EquipElementParam's u16**; captures hold empty lists only (counter-test 0/2: code-only).
- Walk: 29.0.1 41/41; 29.0.2 41/41 (CharacterEquipList up to 19, EquipJobItemList 2, pawns 1 or 3; sample
  `stream51-marked.pcapng_tcp-stream-11/10269_…29_0_2`, 880 B, `a7a4b4c65ab17c37`, end 0x369); 29.1.1 5/5
  (`stream6-annilot-hobo-marked.pcapng_tcp-stream-2/25119_…29_1_1`, 32 B, `d081016f0fe58814`, end 0x19); 29.2.1
  2/2 (`stream1-marked.pcapng_tcp-stream-35/26381_…29_2_1`, 32 B, `b9bd6988daaabe63`, end 0x19); 29.2.2 2/2
  (`…/26389_…29_2_2`, 48 B, `1cff743dcaa0e00a`, end 0x26); 29.15.1 2/2, 29.15.2 2/2
  (`stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/3298_…29_15_2`, 32 B, `9c1b08f6f3de31ca`, end
  0x15). xxd 29.1.2 `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/26527_…29_1_2` (48 B,
  `d99f0ce7329a1a30`): `1d00 0102 34 | 0000 0000 | 0000 0000 | 0000 0002 | 0000 04 01 | 0008 "B0AAED5A" 05 01
  | 0a | 0000 0000` -> two entries (an unequip with empty UID), tail Job 10 + empty list, end 0x2a; tail
  always (10, empty) in 7/7.

## 14. 29.17.16 CHANGE_CHARACTER_EQUIP_LOBBY_NTC

- PC handler `0x7d4470` -> `0x807830`: `Read_u32`, `Read_u8`, list `0x765fb0`, list `0x765fb0`
  (CDataEquipItemInfo S3); no header; consumer checks `sAreaExt::isLobby`.
- PS4 `OnPacket_S2C_CHANGE_CHARACTER_EQUIP_LOBBY_NOTICE 0x310870` -> `ReadPacket 0x19d89c0`: u16 error, u32
  m_unCharacterID, u8 m_ucJob, m_EquipItemList, m_VisualEquipItemList: **match V (shape + lobby)**, S3 via the
  element. Fields `CharacterID`, `Job`, `EquipItemList`, `VisualEquipItemList` (V).
- Counter-tests: PS4 element fails **23/23**; PS4 framing fails **23/23**.
- Walk 23/23; both lists 15 entries always; Job 1/2/6/8/9/11; sample
  `stream85-marked.pcapng_tcp-stream-11/138031_…29_17_16` (896 B, `887f07b34962e122`) end 0x374.

## 15. 29.23.16 (unresolved -> settled: the PC client ignores the body, V)

- Table entry 29.23.16 (`0x212c478 + 29*0x18`) holds `0x7d5730`: `mov eax, 1; retn 4` (8 bytes; its only xref
  is the initializer `0x1a2c53b`). The handler reads **nothing**; 29.19.2, 29.20.2, 29.20.16, 29.21.2, 29.22.2,
  29.22.16 are the same stub shape (`0x7d56e0`-`0x7d5720`). No PC string names the packet.
- PS4: no code match is possible (no PC reader to compare). The nearest PS4 EQUIP notice,
  `CPacket_S2C_CHANGE_CHARACTER_EQUIP_JOB_ITEM_NOTICE` {u32 m_unCharacterID, list CDataEquipJobItem {u32, u8}},
  does not fit the capture shape (element 18 bytes, not 5): **rejected**.
- Capture shape (I, capture only; no code backing): u32, count, elements {u32, u32, u32, u8, u32, u8}. In the
  same stream 0x0021559b occurs in lobby chat and community-status notices (another player's CharacterID, I)
  and 0x00dc8fee/0x00dc92da/0x00dcb1d3 in pawn lists and pawn-exp notices (PawnIDs, I); the first element's
  id is 0. Pattern recommendation: the body as `unk_` fields with this shape and a comment that the client
  ignores it, or as raw bytes.
- Walk 2/2 (identical bodies); xxd `stream85-marked.pcapng_tcp-stream-11/139323_…29_23_16` (96 B,
  `63d945003505d175`): `1d00 1710 34 | 0000 16f3 | 0021 559b | 0000 0004 | 0000 0000 0000 0002 0000 0000 01
  0000 0000 02 | 00dc 8fee …` end 0x59.

## 16. 39.0.x / 39.1.x GACHA

- 39.0.1 `0x8290b0`: empty (V; PS4 `Send_C2S_GACHA_LIST_REQ 0x19ccc60` empty).
- 39.0.2 `0x7d6cf0` (linear; string "…OnPacket_GACHA_GACHA_LIST_RES") -> `0x808bd0`: header, list `0x768430`
  (CDataGachaInfo, § 1). PS4 `OnPacket_S2C_GACHA_LIST_RES 0x32f1b0` m_GachaList: **match V; S3 via the
  settlement's ninth u32**. Counter-test: the PS4 settlement (8 u32) fails **26/26**. The ninth u32 is 0 in
  all 520 settlements: `unk_u32` (no code use traced).
- 39.1.1 `0x841020`: `WritePacket(39, 1, 1)`, u32 x4 (V). PS4 `CPacket_C2S_GACHA_BUY_REQ::WritePacket
  0x1a328b0` {m_unId, m_unDrawGroupId, m_unSettlementId, m_unPrice}: **= PS4 (V)**.
- 39.1.2 `0x7d6c30` (string "…OnPacket_GACHA_GACHA_BUY_RES") -> `0x808b40`: header, u32, list `0x7685e0`.
  PS4 `0x32f330` {m_unId, m_GachaItemList}: **= PS4 (V)**.
- Walk 26/26 + 26/26 (5 gachas, up to 146 items per draw; `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/
  10440_…39_0_2`, 38128 B, `599b344475cc0312`, end 0x94e7); 21/21 + 21/21 (1 or 11 items;
  `…/17572_…39_1_2`, 304 B, `7bc26ae672e95894`, end 0x121; 39.1.1 `…/17562_…39_1_1`, 32 B,
  `d12c78b852e26d71`, end 0x19).

## 17. 43.0.1 LOADING_GET_INFO_REQ / 43.0.2 …_RES

- REQ `0x82eb70`: empty (V; PS4 `Send_C2S_LOADING_GET_INFO_REQ 0x19cca00` empty).
- RES `0x7e28d0` (string "…OnPacket_LOADING_INFO_LOADING_GET_INFO_RES") -> `0x80e7c0`: header, list
  `0x76d550`. PS4 `0x330180`: `Read_CDataLoadingInfoSchedule_` into `m_Info.m_LoadingInfoScheduleList`:
  **= PS4 (V)**; the CDataLoadingInfoSchedules wrapper is only the list on the wire.
- Walk 42/42 + 42/42 (34, 35 or 100 entries); sample `stream31-loginfail-marked.pcapng_tcp-stream-12/10158_…43_0_2`
  (30544 B, `2e548bc5f1e8832a`) end 0x7741.

## 18. Summary

| id | name | PS4 mark | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 19.1.1 | C2S_SKILL_GET_ACQUIRABLE_SKILL_LIST_REQ | V (S3 + u32) | 5 | 26337 | 4/4 |
| 19.2.1 | C2S_SKILL_GET_ACQUIRABLE_ABILITY_LIST_REQ | V (S3 + u32) | 5 | 26341 | 16/16 |
| 19.28.1 | C2S_SKILL_GET_CURRENT_SET_SKILL_LIST_REQ | V | 0 | 12052 | 41/41 |
| 19.28.2 | S2C_SKILL_GET_CURRENT_SET_SKILL_LIST_RES | V | 8+var | 10281 | 41/41 |
| 20.0.1 | C2S_SHOP_GET_SHOP_GOODS_LIST_REQ | V | 4 | 13014 | 18/18 |
| 20.0.2 | S2C_SHOP_GET_SHOP_GOODS_LIST_RES | V (S3 body) | 8+6+var | 11635 | 18/18 |
| 20.1.1 | C2S_SHOP_BUY_SHOP_GOODS_REQ | V | 13 | 13398 | 17/17 |
| 20.1.2 | S2C_SHOP_BUY_SHOP_GOODS_RES | V (S3 - u32) | 8+1 | 13405 | 17/17 |
| 25.5.1 | C2S_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_REQ | V | 0 | 12046 | 43/43 |
| 25.5.2 | S2C_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_RES | V | 8+26 | 12047 | 43/43 |
| 27.0.1 | C2S_ACHIEVEMENT_ACHIEVEMENT_GET_PROGRESS_LIST_REQ | V | 0 | 1865 | 1/1 |
| 27.0.2 | S2C_ACHIEVEMENT_ACHIEVEMENT_GET_PROGRESS_LIST_RES | V | 8+4+24n | 1885 | 1/1 |
| 27.1.1 | C2S_ACHIEVEMENT_ACHIEVEMENT_GET_REWARD_LIST_REQ | V | 0 | 1887 | 1/1 |
| 27.1.2 | S2C_ACHIEVEMENT_ACHIEVEMENT_GET_REWARD_LIST_RES | V | 8+4+13n | 1888 | 1/1 |
| 27.2.1 | C2S_ACHIEVEMENT_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_REQ | V | 0 | 1890 | 2/2 |
| 27.2.2 | S2C_ACHIEVEMENT_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_RES | V | 8+4+21n | 1894 | 2/2 |
| 27.3.1 | C2S_ACHIEVEMENT_ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_REQ | V | 0 | 12105 | 42/42 |
| 27.3.2 | S2C_ACHIEVEMENT_ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_RES | V | 8+4+5n | 12106 | 42/42 |
| 27.4.1 | C2S_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_REQ | V | 4+5n | 1956 | 1/1 |
| 27.4.2 | S2C_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_RES | V | 8+8+5n | 1958 | 1/1 |
| 27.8.16 | S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC | V (behaviour; S3 element) | 4+5n | 1492 | 8/8 |
| 27.9.16 | S2C_ACHIEVEMENT_ACHIEVEMENT_RECEIVABLE_REWARD_NTC | V (behaviour) | 4+5n | 1493 | 3/3 |
| 27.10.1 | C2S_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_REQ | X (exclusive) | 1 | 100006 | 5/5 |
| 27.10.2 | S2C_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES | X (exclusive; 27.0.2 type) | 8+4+24n | 100008 | 17/17 |
| 29.0.1 | C2S_EQUIP_GET_CHARACTER_EQUIP_LIST_REQ | V | 0 | 12043 | 41/41 |
| 29.0.2 | S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES | V | 8+var | 10269 | 41/41 |
| 29.1.1 | C2S_EQUIP_CHANGE_CHARACTER_EQUIP_REQ | V | 4+var | 25119 | 5/5 |
| 29.1.2 | S2C_EQUIP_CHANGE_CHARACTER_EQUIP_RES | V (S3 tail) | 8+var+5+3n | 26527 | 5/5 |
| 29.2.1 | C2S_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_REQ | V | 4+var | 26381 | 2/2 |
| 29.2.2 | S2C_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_RES | V (S3 tail) | 8+var+5+3n | 26389 | 2/2 |
| 29.15.1 | C2S_EQUIP_GET_CRAFT_LOCKED_ELEMENT_LIST_REQ | V | 0 | 3297 | 2/2 |
| 29.15.2 | S2C_EQUIP_GET_CRAFT_LOCKED_ELEMENT_LIST_RES | V (S3 via param; always empty) | 8+4 | 3298 | 2/2 |
| 29.17.16 | S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC | V (S3 via element) | 5+var | 138031 | 23/23 |
| 29.23.16 | S2C_EQUIP_29_23_16_NTC (raw name) | rejected (no PC reader) | 8+18n (capture) | 139323 | 2/2 (I shape) |
| 39.0.1 | C2S_GACHA_GACHA_LIST_REQ | V | 0 | 10395 | 26/26 |
| 39.0.2 | S2C_GACHA_GACHA_LIST_RES | V (S3 settlement) | 8+var | 10440 | 26/26 |
| 39.1.1 | C2S_GACHA_GACHA_BUY_REQ | V | 16 | 17562 | 21/21 |
| 39.1.2 | S2C_GACHA_GACHA_BUY_RES | V | 8+4+4+24n | 17572 | 21/21 |
| 43.0.1 | C2S_LOADING_INFO_LOADING_GET_INFO_REQ | V | 0 | 11919 | 42/42 |
| 43.0.2 | S2C_LOADING_INFO_LOADING_GET_INFO_RES | V | 8+var | 10158 | 42/42 |

Total 40 ids, 688/688 fit. Triage corrections: 27.8.16, 27.9.16 unresolved -> matched (V); 29.23.16
unresolved -> settled as a no-op handler (V), layout capture-only (I); 27.10.1/2 exclusive confirmed (V).
`recompiled_body` "yes" for 20.1.1 is a `DDON_STUB`. Read-seq ratios below 1.0 in the triage are explained:
27.0.2/27.10.2 share a `loc_` list reader, 20.0.2 is a Season 3 body, 20.1.2 drops a u32, 29.x via the
S3 equip types, 39.0.2 via the settlement u32.

## 19. Shared types for pattern authors

Reuse unchanged: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`), `Context.hexpat`
(`EquipElementParam`, `AddStatusParam`, `EquipStatParam`), `Login.hexpat` (`CDataEquipItemInfo`), `Pawn.hexpat`
(`CDataEquipJobItem`, `CDataOrbGainExtendParam`, `CDataAchievementIdentifier`). Framing as T003 § 18 (inline
RES header; NTCs without header).

Add (names PS4 DWARF unless marked):

- `include/Achievement.hexpat` (new): `CDataAchievementProgress` {CDataAchievementIdentifier AchieveIdenfier
  (DWARF spelling), u32 CurrentNum, u32 Seqence (DWARF spelling), s64 CompleteDate}; `CDataAchievementRewardProgress`
  {u32 RewardId, u32 CurrentNum, u32 TargetNum, bool IsRecieved}; `CDataAchievementFurnitureReward` {u32
  RewardId, u32 SortId, CDataAchievementIdentifier AchieveIdenfier, u32 FurnitureItemId, bool IsRecieved};
  `CDataAchieveRewardCommon` {u8 Type, u32 RewardId}; `CDataAchievementCompleteElement` (struct name I) {u32
  AchievementId (I, PS4 list of ids), u8 unk_Category (I, § 10)}.
- `include/Item.hexpat`: `CDataS2CCharacterEquipInfo` {MtString EquipItemUID, u8 EquipCategory, u8 EquipType}
  (also the C2S element of 29.1.1/29.2.1, PS4 `CDataC2SChangeCharacterEquipInfo`, same members);
  `CDataPawnEquipInfo` {u32 PawnID, MtTypedArray<CDataS2CCharacterEquipInfo> CharacterEquipList,
  MtTypedArray<CDataEquipJobItem> EquipJobItemList}; `CDataItemEquipElement` {MtString ItemUID,
  MtTypedArray<EquipElementParam> EquipElementList}; `CDataEquipChangeUnk` (struct name I) {u8 unk_Job,
  MtTypedArray<EquipStatParam> unk_List} (PC `0x765f70`, Season 3).
- `include/Skill.hexpat`: `CDataNormalSkillParam` {u8 Job, u32 SkillNo, u32 Index, u32 PreSkillNo};
  `CDataSetAcquirementParam` {u8 Job, u8 Type, u8 SlotNo, u32 AcquirementNo, u8 AcquirementLv}.
- `include/Shop.hexpat` (new; all names I or `unk_`, § 6): `CDataGoodsRequirement` {u32 unk_u32_0, u32
  unk_u32_1, bool unk_bool_0, u32 unk_u32_2, bool unk_bool_1, u32 unk_u32_3..7, s64 unk_s64_0, s64 unk_s64_1};
  `CDataGoodsParam` (Season 3) {u32 Index, u32 ItemId, u32 Price, u8 Stock, bool unk_bool, s64 unk_s64_0, s64
  unk_s64_1, MtTypedArray<CDataGoodsRequirement> unk_RequirementList}.
- `include/Gacha.hexpat` (new): `CDataGachaItemInfo`, `CDataGachaSettlementInfo` (8 PS4 members + `u32
  unk_u32`), `CDataGachaDrawInfo` {u32 Num, bool IsBonus, MtTypedArray<CDataGachaItemInfo> GachaItemInfo},
  `CDataGachaDrawGroupInfo` {GachaSettlementList, GachaDrawList}, `CDataGachaInfo` (§ 1).
- `CDataLoadingInfoSchedule` {MtString Text, u32 ImageId, u32 Priority, s64 BeginDateTime, s64 EndDateTime}
  (in `Server.hexpat` or a new `Loading.hexpat`).

Packet bodies (after the header): 19.1.1/19.2.1 `u32 unk_CharacterId, u8 Job`; 19.28.2 `MtTypedArray<
CDataNormalSkillParam> NormalSkillList, MtTypedArray<CDataSetAcquirementParam> SetCustomSkillList,
SetAbilityList`; 20.0.1 `u32 ShopID`; 20.0.2 `u32 ShopID (I), u8 unk_u8, u8 unk_PointType (I),
MtTypedArray<CDataGoodsParam> GoodsParamList`; 20.1.1 `u32 GoodsIndex, u32 Num, u8 StorageType, u32 Price`;
20.1.2 `u8 PointType (I)`; 25.5.2 `CDataOrbGainExtendParam ExtendParam`; 27.0.2 and 27.10.2
`MtTypedArray<CDataAchievementProgress> AchievementProgressList`; 27.1.2 `MtTypedArray<
CDataAchievementRewardProgress> BackgroundProgressList`; 27.2.2 `MtTypedArray<CDataAchievementFurnitureReward>
RewardList`; 27.3.2 and 27.4.1 and 27.9.16 `MtTypedArray<CDataAchieveRewardCommon> RewardList`; 27.4.2
`RecievedRewardList, RewardList`; 27.8.16 `MtTypedArray<CDataAchievementCompleteElement> AchievementIdList`;
27.10.1 `u8 unk_Category`; 29.0.2 `CharacterEquipList, EquipJobItemList, MtTypedArray<CDataPawnEquipInfo>
PawnEquipItemList`; 29.1.1/29.2.1 `MtTypedArray<CDataS2CCharacterEquipInfo> ChangeCharacterEquipList`;
29.1.2/29.2.2 `MtTypedArray<CDataS2CCharacterEquipInfo> CharacterEquipList, CDataEquipChangeUnk unk_0`;
29.15.2 `MtTypedArray<CDataItemEquipElement> LockedElementList`; 29.17.16 `u32 CharacterID, u8 Job,
MtTypedArray<CDataEquipItemInfo> EquipItemList, VisualEquipItemList`; 29.23.16 capture shape (§ 15); 39.0.2
`MtTypedArray<CDataGachaInfo> GachaList`; 39.1.1 `u32 Id, u32 DrawGroupId, u32 SettlementId, u32 Price`;
39.1.2 `u32 Id, MtTypedArray<CDataGachaItemInfo> GachaItemList`; 43.0.2 `MtTypedArray<CDataLoadingInfoSchedule>
LoadingInfoScheduleList`. Empty REQ bodies: 19.28.1, 25.5.1, 27.0.1, 27.1.1, 27.2.1, 27.3.1, 29.0.1, 29.15.1,
39.0.1, 43.0.1.

## 20. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`:

1. `S2CAchievementCompleteNtc` writes `List<CDataCommonU32> AchievementIdList` (the PS4 shape); PC 27.8.16 reads
   {u32, u8} per element (§ 10). Misplacement (C, by the PC reader; the captures carry the u8).
2. `CDataNormalSkillParam` writes Job, **Index, SkillNo**, PreSkillNo; PS4 DWARF and reader store SkillNo (+0xc)
   before Index (+0x10), recompilation `Skill.h` agrees: the two u32 names are swapped (C against PS4; same
   bytes).
3. `S2CShopBuyShopGoodsRes` writes only `PointType` (u8): agrees with PC (PS4 has an extra u32).
4. No structure for 29.23.16 (`PacketId` entry only) and none for 39.x GACHA.
5. Agree with PC (shape): `C2SSkillGetAcquirableSkillListReq` / `…AbilityListReq` {CharacterId, Job},
   `S2CShopGetShopGoodsListRes` {Unk0, Unk1, WalletType, CDataGoodsParam} / `CDataGoodsParam` /
   `CDataGoodsParamRequirement`, `C2SShopBuyShopGoodsReq`, `S2CEquipChangeCharacterEquipRes` (+
   `CDataJobChangeJobResUnk0 {u8, List<CDataCharacterItemSlotInfo {u8, u16}>}`), `S2CEquipGetCharacterEquipListRes`,
   `S2CEquipGetCraftLockedElementListRes` / `CDataItemEquipElement`, `CDataEquipElementParam` {u8, u32, u16},
   `CDataEquipItemInfo`, `S2CEquipChangeCharacterEquipLobbyNtc`, `S2CAchievementReceivableRewardNtc`,
   `C2SAchievementGetCategoryProgressListReq` {Category}, `S2CAchievementGetCategoryProgressListRes`,
   `CDataAchievementProgress`, `CDataAchievementRewardProgress`, `CDataAchievementFurnitureReward`,
   `CDataAchieveRewardCommon`, `CDataSetAcquirementParam`, `CDataLoadingInfoSchedule`.

## 21. Open items and checks not run

- Names without code backing (I): 19.x.1 u32 (CharacterId by capture), 20.0.2 top fields and the goods and
  requirement elements (§ 6), 20.1.2 PointType, 27.8.16 / 27.10.1 Category, the 29.1.2 tail `0x765f70`, the
  39.0.2 settlement ninth u32, all of 29.23.16 (§ 15).
- Consumers not traced: the 20.0.2 goods and requirement fields (`0x769450`, `0x7788a0` use sites), the tail
  list of `0x765f70` beyond `sub_B9E8C0`, the gacha settlement ninth u32.
- Counter-tests that cannot separate PC from PS4 (code decides): 19.1.1/19.2.1 (slack), 20.1.2 (by length;
  the PS4 u32 reads padding), 27.8.16 element (single elements), 29.1.2/29.2.2 tail (slack).
- Code-only (never non-empty in captures): 27.4.2 lists, 29.15.2 list, the 29.1.2/29.2.2 tail list, 20.0.2
  s64 pairs (always 0).
- ImHex not run (not on `PATH`); no pattern written (outside this package).
