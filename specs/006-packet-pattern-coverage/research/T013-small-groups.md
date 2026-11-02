# 006 T013: small groups 9, 15, 18, 30, 34, 41, 51, 52, 54, 57, 63

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T013-small-groups.md`; the 48 rows of groups 30, 34, 63, 9, 18, 52,
15, 41, 54, 57 and 51 in `research/T001-triage.tsv` (242 captures). Base `9dfecfec62`. Marks: **V** verified
in code (or by capture for walk results), **I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t013/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t013/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays; `ida_ua.decode_insn`
  for linear decoding of code IDA has not made a function; `ida_typeinf` for DWARF members). Nothing
  renamed, retyped, commented, patched or reanalysed. Some PC functions already carry names from earlier
  annotation (`nPacket::Read_CDataEntryItem_`, `Send_S2C_63_5_16_NTC`, ...): used as labels only, every
  claim below rests on the code.
- PC primitives and framing as T003/T005/T012 § 0. `WritePacket 0x8bcbb0` writes u8 group, u16 id, u8 sub,
  u8 0, **u32** (0 from the client), so the header is 9 bytes and its bytes 5-8 are a u32 (V).
- **PC handler table (V)**: directory `0x1bc0110` (`{table, count}` per group): 9 `{0x212aff0, 2}`, 15
  `{0x212c748, 1}` (single entry, key `0xffffffff`: no S2C handler in group 15), 18 `{0x212cc10, 8}`, 30
  `{0x212be18, 27}`, 34 `{0x212c208, 26}`, 41 `{0x212b458, 9}`, 51 `{0x212c100, 5}`, 52 `{0x212d900, 10}`, 54
  `{0x212c0a0, 3}`, 57 `{0x212b068, 4}`, 63 `{0x2130cf0, 7}`; stride 0x18, key `(sub<<16)|id` at +0x10; entry
  +0 stored by the initializer (`mov [esp+var], <handler>` then a `movq` store, e.g. `0x1a2b2e3` stores
  `0x7d1ae0` for 63.0.16, store `0x1a2b2f7`). Every S2C `pc_va` of the triage equals its traced table
  handler (**V, 26/26**).
- **Not functions in the PC database** (decoded linearly, no change): handlers 30.13.2 `0x7d0bf0`, 63.0.16
  `0x7d1ae0`, 63.1.16 `0x7d1b80`, 63.2.16 `0x7d1be0`, 63.10.16 `0x7d1e60`; readers `0x8066b0` (63.10.16);
  list readers `0x760b60` (30.0.2), `0x7651d0` (34.0.2), `0x76e000` (54.0.2), `0x762b40` (63.2.16).
- PC writers (C2S): `WritePacket(p, group, id, sub, -1)`, group/id/sub read from the decompiled call (V each,
  22/22). 15.0.16, 15.1.16 and 63.5.16 are client-written notices (sub 16, source 0x00).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, behaviour), never by PS4 id.
  RES header (V, every PC RES reader here): `Read_s32` Error; non-zero -> return; else `Read_s32` Result, body.
  PS4 reads `u16 m_usError` + `s32 m_nResult`. PC NTC readers read **no** header (V: 34.6.16, 34.14.16,
  34.16.16, 63.x). PS4 C2S writers start with three `Write_u16` (PS4 framing). `bool m_bIsReceived` is a client
  flag, never on the wire.
- **Walk**: `specs/006-packet-pattern-coverage/research/T013-walk.py` (stdlib; run from `D:/ddon-data` with
  `python -X utf8 -I specs/006-packet-pattern-coverage/research/T013-walk.py`; sha256 prefix
  `986116d3e0a63ef3`). Input `packets/decrypted_raw/*/`, every file whose suffix is `.<g>_<id>_<sub>` of the
  48 ids (each suffix carries exactly one packet name). Header check: group, u16 id, sub, source (0x00 C2S,
  0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun. **Totals: 242 files, header
  242/242, fit 242/242, no RES with Error != 0.** Samples: file (relative to `packets/decrypted_raw/`), size,
  sha256 first 16 hex digits, body end offset.
- Recompilation cross-check (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/`): `UserSession/S2C.cpp`
  implements a real `ReadPacket` only for `CPacket_S2C_CRAFT_SKILL_UP_RES` (= PS4, § 3); `…GET_CRAFT_PROGRESS_LIST_RES`
  and `…GET_CRAFT_SETTING_RES` are `DDON_STUB`s; none of the other RES/NTC of this package has a body there.
  `C2S.cpp` has `CRAFT_SKILL_UP_REQ`, `ENTRY_BOARD_ITEM_CREATE_REQ`, `GET_CRAFT_RECIPE_REQ`,
  `UPDATE_PAWN_EDIT_PARAM_REQ` as `DDON_STUB` signatures only. `PacketData/` (`Craft.h`, `EntryBoard.h`,
  `DispelItem.h`) declares the PS4 DWARF members and offsets (e.g. `CDataEntryMemberData {m_usID 0x8,
  m_bIsReady 0xa, m_CharacterListElement 0x10}`, `CDataDispelCategoryInfo {u8 m_ucCategory}`). Triage
  `recompiled_body` "yes" for 30.0.2, 30.10.1, 30.13.2, 34.2.1, 41.3.1, 54.0.1 is overstated (stubs); only
  30.10.2 is implemented.

Field-name sources: PS4 DWARF member (`m_`/type prefix dropped) **V**; other names **I** with the basis stated;
Season 3 fields without code backing are `unk_*` (server names only as leads, § 16).

## 1. Shared structures

Reused from the includes, readers re-read here (no change): `CDataPawnCraftSkill` (`0x771c80`, `Pawn.hexpat`),
`CDataWalletPoint` (`0x77c5a0`, `Character.hexpat`), `CDataCharacterListElement` (S3 with trailing u8,
`0x75ccf0`, `Character.hexpat`), `CDataJobBaseInfo` (`0x76b190`), `CDataEditInfo` (PC writer
`Write_CDataEditInfo_ 0x77eb40`: u8, u8, u16, 18 x u8, 50 x u16 = 122 B, `Context.hexpat`; PS4
`Write_CDataEditInfo_ 0x1a38b40` same widths and order, V), `CDataStageLayoutId` (`Instance.hexpat`),
`CDataCommonU32`/`CDataCommonU8` (`Packet.hexpat`).

New (PS4 = PS4 02020005 reader/writer; "= PS4" = same widths and order):

| Struct | PC | PS4 02020005 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataCraftPawnInfo` | list `0x760870` | `Read_CDataCraftPawnInfo_ 0x1a0d5f0` {u32 m_unPawnID, MtString m_wstrName} | = PS4 (V) |
| `CDataCraftProgress` (S3) | list loc `0x760b60`, element `0x760c20` | `Read_CDataCraftProgress__0 0x1a0d500` {CCraftPawnInfo m_CraftMainPawnInfo, m_CraftSupportPawnInfoList, u32 m_unRecipeID, u32 m_unExp, s32 m_nNpcActionID, u32 m_unItemID, u32 m_unToppingID, u32 m_unRemainTime, b8 m_bExpBonus, u32 m_unCreateCount} | u32, MtString, list CDataCraftPawnInfo, **list {u32}**, u32, u32, s32, u32, u32, **u16**, u32, bool, u32 (§ 2) |
| `CDataCraftPawnList` | list `0x760960` | `Read_CDataCraftPawnList_ 0x1a0d260` {u32 m_unPawnID, m_unCraftExp, m_unCraftPoint, m_unCraftRankLimit} | = PS4 (V) |
| `CDataCraftTimeSaveCost` | list `0x7611f0` | `0x19e8e80` {u8 m_ucID, u8 m_ucType, u32 m_unPrice, u32 m_unSec} | = PS4 (V) |
| `CDataCraftSkillRate` | list `0x7610f0` | `0x19e8bb0` {u8 m_ucPawnType, u8 m_ucSkillType, u8 m_ucRate} | = PS4 (V) |
| S3 craft-setting pawn | list `0x77abd0`, element `0x77ace0` | none | u32, u8, u32, u32, MtString, u32, list CDataPawnCraftSkill |
| S3 craft-setting element | list `0x760db0`, element `0x760ea0` | none | u32 x5, bool |
| `CDataMDataCraftRecipe` | list loc `0x76e000`, element `0x76e130` | `0x19e7880` {u32 m_unRecipeID, m_unItemID, m_unTime, m_unNum, m_unCost, m_unExp, m_unNeedRank, s32 m_nNpcAct, b8 m_bIsHide, m_CraftMaterialList} | = PS4, S3 material |
| `CDataMDataCraftMaterial` (S3) | list `0x76dee0` | `0x19e72a0` {u32 m_unItemID, m_unNum, m_unSortNo} | 3 PS4 u32 + **bool** (V width) |
| `CDataEntryRecruitData` (S3) | list `0x765750`; C2S writer `0x77f340` | `0x19fc7c0` {u16 m_usID, list CDataEntryRecruitJob {u8 m_ucjob}} | u16, **u32**, list u8 (V) |
| `CDataEntryItemParam` | `0x7654b0`; writer `0x77f260` | `0x19fc370` / `Write_ 0x1a33da0` {b8 PasswordOn, b8 PawnOn, s32 BottomEntryJobLevel, s32 TopEntryJobLevel, u16 RequiredItemRank, u8 ItemRankType, u32 ItemRankCheckRoleType, u16 MinEntryNum, u16 MaxEntryNum, MtString Comment, EntryRecruitList} | = PS4, S3 recruit (V) |
| `CDataEntryMemberData` (S3) | list `0x765590`; element `0x7656f0` | `0x19fc460` {u16 m_usID, b8 m_bIsReady, CCharacterListElement} | u16, bool, **u32**, CDataCharacterListElement (S3) (V) |
| `CDataEntryItem` (S3) | list `0x765360`, element `0x765420` | `0x19fd460` {u32 m_unID, m_Param, m_EntryMemberList, u16 m_usBoardRequiredAvgItemRank, u16 m_usTimeOut, u32 m_unLeaderPartyId} | = PS4 + **trailing bool** (V) |
| `CDataEntryBoardItemSearchParameter` (S3) | writer `0x77f170` (list u8 `0x77e050`) | `Write_ 0x1a34100` {m_SearchGroups (CDataCommonU8), MtString FirstName, LastName, b8 RankSetting, u32 RankMin, RankMax, Job, b8 IsNoPassword, u32 RequiredItemRankMin, RequiredItemRankMax} | = PS4 + **u32 x2** (V) |
| entry-board list element | list loc `0x7651d0`, element `0x7652c0` | none (exclusive, § 5) | u64, u16 x5, bool, u32 |
| character-edit price | list `0x764d70` | none (exclusive, § 9) | u8, list CDataWalletPoint |
| `CDataDispelCategoryInfo` (S3) | list `0x763390` | `0x19eaf30` {u8 m_ucCategory, MtString m_wstrCategoryName} | **u32**, MtString (V) |
| 63 layout set | list `0x762c50` | none | u32, u8, u32, u32 (§ 13) |
| 63 announce element | list loc `0x762b40` | none | u8, u32, MtString (§ 13) |

## 2. 30.0.x GET_CRAFT_PROGRESS_LIST

- 30.0.1 `0x8255b0`: `WritePacket(30, 0, 1)`, empty (V; PS4 `Send_C2S_GET_CRAFT_PROGRESS_LIST_REQ 0x19bd530` empty).
- 30.0.2 `0x7d0b40` (string "…OnPacket_CRAFT_GET_CRAFT_PROGRESS_LIST_RES") -> `0x805b40`: header, list loc
  `0x760b60` (CDataCraftProgress S3), list `0x760960` (CDataCraftPawnList), list `0x75e8e0` {u32}. PS4
  `OnPacket_S2C_GET_CRAFT_PROGRESS_LIST_RES 0x313ec0` -> `ReadPacket 0x19d8e80` {m_CraftProgressList,
  m_CraftMyPawnList, m_CreatedReicpeList (CDataCommonU32)}: **match V (symbol pair, string), S3 via the
  progress element**.
- S3 element: after `CraftSupportPawnInfoList` a **list of u32** (`0x75e8e0`), and a **u16** among the trailing
  u32 run (PC: u32 +56, u32 +60, s32 +64, u32 +68, u32 +72, **u16 +76**, u32 +80, bool +84, u32 +88; PS4:
  RecipeID, Exp, NpcActionID, ItemID, ToppingID, RemainTime, ExpBonus, CreateCount). Names by position (I):
  RecipeID, Exp, NpcActionID, ItemID, ToppingID, `unk_u16`, RemainTime, ExpBonus, CreateCount (the u16 sits
  where the PS4 has no member; which side of it the PS4 u32s belong is inferred from order). The new list:
  `unk_u32_list`.
- Counter-test: the PS4 element fits 10/10 because the progress list is empty in every capture: **code-only**.
- Walk 10/10 + 10/10; progress list always empty, pawn list 1, created recipes 3; xxd
  `stream86-bonusdungeons-lastdays-marked.pcapng_tcp-stream-9/3219_…30_0_2` (64 B, `be9a9942429b3b75`):
  `1e00 0002 34 | 0000 0000 | 0000 0000 | 0000 0000 | 0000 0001 | 00db 3bcf 0000 0866 0000 0007 0000 0008 |
  0000 0003 …` end 0x39. 30.0.1 sample `…/3202_…30_0_1` (16 B, `f285f900a643c9ad`) end 0x09.

## 3. 30.10.x CRAFT_SKILL_UP, 30.12.x RESET_CRAFTPOINT, 30.15.x GET_CRAFT_IR_COLLECTION_VALUE_LIST

| id | PC | PS4 02020005 | Body | Mark |
| --- | --- | --- | --- | --- |
| 30.10.1 | `0x824f40`: u32 x3 | `CPacket_C2S_CRAFT_SKILL_UP_REQ::WritePacket 0x1a35c50` {u32 in_PawnID, in_SkillType, in_SkillLevel} | PawnID, SkillType, SkillLevel | V |
| 30.10.2 | `0x7d03d0` -> `0x805740`: u32 x5 | `0x315330` -> `0x19d96e0` {m_unPawnID, m_unSkillType, m_unSkillLevel, m_unUseCraftPoint, m_unRemainCraftPoint} (recompilation implements the same) | same names | V |
| 30.12.1 | `0x825a00`: u32 | `Send_C2S_RESET_CRAFTPOINT_REQ 0x19cdd90(u32 in_PawnID)` | PawnID | V |
| 30.12.2 | `0x7d1080` -> `0x805ed0`: u32, list `0x771c80`, u32 | `0x333e30` -> `0x19df770` {m_unPawnID, m_CraftSkillList (CDataPawnCraftSkill), m_unCraftPoint} | PawnID, CraftSkillList, CraftPoint | V |
| 30.15.1 | `0x8252f0`: empty | `0x19be820` empty | none | V |
| 30.15.2 | `0x7d0850` -> `0x8059b0`: list `0x7610f0` | `0x3346f0`: inline {m_usError, s32, `Read_CDataCraftSkillRate_`} | `MtTypedArray<CDataCraftSkillRate>` (name I: PS4 reads into a local `ar`, no member) | V |

Each PC RES handler carries its "…OnPacket_CRAFT_…_RES" string. Walk: 30.10.1 1/1
(`stream86-…-9/4543_…30_10_1`, 32 B, `52aa7d815b343fac`, end 0x15), 30.10.2 1/1 (`…/4545_…30_10_2`, 48 B,
`ecc5b8abaf2c7fee`, end 0x25), 30.12.1 1/1 (`…/4628_…30_12_1`, 16 B, `503258b66300223f`, end 0x0d), 30.12.2 1/1
(`…/4631_…30_12_2`, 64 B, `5a04ac776ba8f94c`: `1e00 0c02 34 | 0 | 0 | 00db 3bcf | 0000 0005 | 01 0000 0000 | 02
… | 0000 0007` -> PawnID 0x00db3bcf (= the 30.0.2 pawn), 5 skills, CraftPoint 7, end 0x36), 30.15.1 2/2, 30.15.2
2/2 (10 rates; `…/3295_…30_15_2`, 64 B, `be9cb0cbad82e74c`, end 0x33).

## 4. 30.13.x GET_CRAFT_SETTING (Season 3 tail)

- 30.13.1 `0x825670`: empty (V; PS4 `0x19be6f0` empty).
- 30.13.2 handler `0x7d0bf0` (not a function; string at `0x7d0cb7` "…OnPacket_CRAFT_GET_CRAFT_SETTING_RES") ->
  `0x805be0`: header, `0x760f20`: list `0x75e8e0` {u32}, list `0x7611f0` (CDataCraftTimeSaveCost), u32, u32,
  u8, **list `0x77abd0`, u32, u32, list `0x760db0`** (V). PS4 `0x334070` -> `0x19df830` {m_ColorRegulateItemList,
  m_TimeSaveCostList, m_unReasonableCraftLv, m_unCraftItemLv, m_ucCreateCountMax}: **match V; S3 adds four
  fields**. Counter-test: the PS4 body fails **2/2**.
- S3 names (all `unk_`; leads only): list of {u32, u8, u32, u32, MtString, u32, list CDataPawnCraftSkill}
  (captures: (309, 5, 1, 10000006, "Qualio", 100, 10 skills), (310, 5, 1, 10000002, "Arms", 100, 10): pawn
  records, I), u32 (49), u32 (30), list {u32 x5, bool} (7 elements, first u32 0 or 80xx).
- Walk 2/2 + 2/2; ColorRegulateItemList 993 entries; sample `stream86-…-9/3218_…30_13_2` (4336 B,
  `b9337d4d115f98bd`) end 0x10ef.

## 5. 34.0.x ENTRY_BOARD_LIST (exclusive, confirmed V)

- 34.0.1 `0x827580`: `WritePacket(34, 0, 1)`, writer `0x77dff0`: count + u64 per element (V).
- 34.0.2 `0x7d3f10` (string "…OnPacket_ENTRY_BOARD_ENTRY_BOARD_LIST_RES") -> `0x8075a0`: header, list loc
  `0x7651d0`, element `0x7652c0`: u64, u16 x5, bool, u32 (V).
- PS4: no symbol, string or DWARF packet with `ENTRY_BOARD_LIST` (the PS4 entry-board packets are the
  `…ITEM_…` set; name and string search: 0 hits); the element shape has no PS4 struct. **Exclusive (V)**.
- Names (I): request element `BoardId` (u64 0x0000000400_04d104 = the BoardID of 34.2.1/34.2.2 in the same
  stream); response u64 `BoardId` (same value), u16 #4 `unk_TimeOut` (3600 = the `TimeOut` of a 34.1.2 item),
  u16 #5 (120 = the 34.6.16 `TimeOut`), others `unk_`.
- Walk 1/1 + 1/1; xxd `stream85-marked.pcapng_tcp-stream-11/138924_…34_0_1` (32 B, `fc3bb7d1d6f443f8`):
  `2200 0001 00 | 0001 5b03 | 0000 0001 | 0000 0004 0004 d104` end 0x15; `…/138928_…34_0_2` (48 B,
  `14212a6f72714383`): `… | 0000 0001 | 0000 0004 0004 d104 | 0001 0004 0000 0e10 0078 | 01 | 0000 0000` end 0x2c.

## 6. 34.1.x ENTRY_BOARD_ITEM_LIST, 34.2.x ENTRY_BOARD_ITEM_CREATE (Season 3 elements)

- 34.1.1 `0x840ec0`: `WritePacket(34, 1, 1)`, u64, u32, u32, `0x77f170` (search parameter, S3 + u32 x2). PS4
  `CPacket_C2S_ENTRY_BOARD_ITEM_LIST_REQ::WritePacket 0x1a34040` {u64 m_ullID, u32 m_unOffset, u32 m_unNum,
  m_SearchParam}: **match V, S3 via the parameter**. Counter-test: the PS4 body fits 3/3 (the two u32 sit in
  slack): code decides. The two new u32 are 0 in 3/3: `unk_u32_0`, `unk_u32_1`.
- 34.1.2 `0x7d3880` -> `0x8072a0`: header, u64, list `0x765360` (CDataEntryItem S3). PS4
  `OnPacket_S2C_ENTRY_BOARD_ITEM_LIST_RES 0x321f30` {u64 m_ullID, m_EntryItemList}: **match V**. Counter-test:
  PS4 element fails 1/3 (the two others hold empty lists).
- 34.2.1 `0x826ae0`: `WritePacket(34, 2, 1)`, u64, `Write_cstr` (MtString wire), `0x77f260`
  (CDataEntryItemParam, S3 recruit). PS4 `CPacket_C2S_ENTRY_BOARD_ITEM_CREATE_REQ::WritePacket 0x1a34310`
  {u64 m_ullBoardID, MT_CSTR in_strPassword, m_Param}: **match V**. Counter-test: PS4 fails **1/1**.
- 34.2.2 `0x7d2bd0` -> `0x806c50`: header, u64, element `0x765420` (one CDataEntryItem). PS4
  `0x3220d0` {u64 m_ullBoardID, CEntryItem m_EntryItem} (read inline): **match V**. Counter-test: PS4 fails 1/1.
- S3 additions (all 0 in captures, names `unk_`): recruit u32 (12 entries), member u32 after IsReady (12),
  item trailing bool (2), search u32 x2.
- Walk 3/3, 3/3, 1/1, 1/1; samples `stream76-marked.pcapng_tcp-stream-11/11735_…34_1_1` (64 B,
  `b2b600407e50a1fb`, end 0x3f), `…/11828_…34_1_2` (544 B, `2ec9601eec517778`, end 0x220; 8 members),
  `stream85-marked.pcapng_tcp-stream-11/138931_…34_2_1` (144 B, `33dffc405ed2332e`, end 0x86; 4 recruit
  entries of 11 jobs), `…/138933_…34_2_2` (288 B, `28387c0bff878596`, end 0x112).

## 7. 34.6.x ITEM_READY, 34.7.x ITEM_FORCE_START, 34.6.16 READY_NTC (unresolved -> matched V)

- 34.6.1 `0x8273b0`, 34.7.1 `0x826dc0`: empty (V; PS4 `0x19c7170`, `0x19c72a0` empty).
- 34.6.2 `0x7d3a10` -> `0x8073a0`, 34.7.2 `0x7d2fe0` -> `0x806de0`: header only (V; strings "…ITEM_READY_RES",
  "…ITEM_FORCE_START_RES"; PS4 `0x3239a0`, `0x323e10` header only).
- 34.6.16 handler `0x7d3960` (packet object tagged 34, 6, 16) -> `0x807330`: `Read_u32`, `Read_u16`; no
  header; then `sNetworkExt::setEntryBoardReadyWait(1)`, a float = u16 * 30.0 (`0x1ae7070` holds 30.0),
  `sGUIExt::requestInfomation(…, 0xE, …)`, `requestSE_0(…, 0, 0x134)`. PS4
  `OnPacket_S2C_ENTRY_BOARD_ITEM_READY_NOTICE 0x323ab0`: u16 error, u32 m_unMaxMember, u16 m_usTimeOut, then
  `setEntryBoardReadyWait(true)`, `m_usTimeOut * 30.0`, `requestInfomation(INFO_FLAG_ENTRY_BOARD_READY)`,
  `requestSE_0(0, 0x134)`: **match V (behaviour, same SE id)**. Fields `MaxMember`, `TimeOut` (V).
- Counter-test: PS4 framing fails **1/1**. Walk 1/1; xxd `stream85-…-11/138947_…34_6_16` (16 B,
  `0542860a47fd78a8`): `2200 0610 34 | 0000 1687 | 0000 0001 | 0078` -> MaxMember 1, TimeOut 120, end 0x0f.
  34.6.1 `…/138967` (16 B, `f24bef777865da66`) end 0x09; 34.6.2 `…/138972` (32 B, `c34b0ba8f5aa19f8`) end 0x11;
  34.7.1 `…/138946` (16 B, `785639f61578b83f`) end 0x09; 34.7.2 `…/138950` (32 B, `fae8415da8471b51`) end 0x11.

## 8. 34.14.16 CHANGE_MEMBER_NTC (matched V) and 34.16.16 RESERVE_NTC (unresolved -> matched I)

- 34.14.16 `0x7d2b70` -> `0x806be0`: `Read_bool`, element `0x7656f0` (u16, bool, u32, CDataCharacterListElement
  S3; the same element as list `0x765590`); no header. PS4 `OnPacket_S2C_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NOTICE
  0x3236b0` {u16 error, b8 m_bEntryFlag, CEntryMemberData m_MemberData}; the only PS4 entry-board packet with
  bool + member data (all 22 PS4 `CPacket_S2C_ENTRY_BOARD_*` listed from DWARF): **match V**. Fields
  `EntryFlag`, `MemberData` (V). Counter-tests: PS4 element fails 1/1, PS4 framing fails 1/1. Walk 1/1; xxd
  `stream85-…-11/138932_…34_14_16` (64 B, `78cb5da07b8705b2`): `2200 0e10 34 | 0000 1682 | 01 | 0001 00 0000
  0000 | 0021 559b 0006 "Kendra" 0004 "Shaw" 0003 "BSP" 0005 0d 0964 0000 0000 00` -> EntryFlag 1, ID 1, not
  ready, CharacterID 2184603, end 0x32.
- 34.16.16 `0x7d3cf0` (object tagged 34, 16, 16) -> `0x807530`: `Read_u32`, `Read_u32`; the handler returns the
  read result and keeps nothing (local object). PS4 `OnPacket_S2C_ENTRY_BOARD_ITEM_RESERVE_NOTICE 0x323ca0`
  {u16 error, u32 m_unNowMember, u32 m_unMaxMember}, stored in `mpEntryBoardItemReservePacket`. Among the 22
  PS4 entry-board packets only RESERVE_NOTICE has the body {u32, u32}: **match I (unique shape within the
  group; no behaviour to compare, the PC handler discards the body)**. Fields `NowMember`, `MaxMember` (I).
  Counter-test: PS4 framing fits 1/1 (slack 15): inconclusive. Walk 1/1; xxd `…/138971_…34_16_16` (32 B,
  `e1b84842180fe29a`): `2200 1010 34 | 0000 168f | 0000 0001 | 0000 0001` end 0x11.

## 9. 41.x CHARACTER_EDIT

- 41.3.1 `0x840840`: `WritePacket(41, 3, 1)`, u8, u8, **writer `0x7812a0` {u8, u32}**, `Write_CDataEditInfo_`.
  PS4 `CPacket_C2S_UPDATE_PAWN_EDIT_PARAM_REQ::WritePacket 0x1a3a200` {u8 in_SlotNo, u8 in_UpdateType,
  CEditInfo}: **match V, S3 inserts {u8, u32}**. Name `unk_Price` as `CDataWalletPoint` (I: the capture
  holds (4, 200), an entry of the 41.8.2 price list for UpdateType 1 sent earlier in the stream). Counter-test:
  the PS4 body fits 1/1 (5 bytes inside slack 6+5): code decides.
- 41.3.2 `0x7c8c40` (string "…UPDATE_PAWN_EDIT_PARAM_RES") -> `0x802580`: header only. PS4 `0x32fc30` reads
  header + u32 (`m_unGP`). **Match V; S3 drops m_unGP.** Counter-test: PS4 fits 1/1 (slack 15): inconclusive.
- 41.5.1 `0x8406b0` (exclusive): `WritePacket(41, 5, 1)`, u8, u8 (+4), u32 (+8), `Write_CDataEditInfo_`,
  `Write_MtString` (V). 41.5.2 `0x7c8420` (string "…UPDATE_CHARACTER_EDIT_PARAM_EX_RES") -> `0x8022d0`: header
  only (V). PS4 has `UPDATE_CHARACTER_EDIT_PARAM_REQ/RES` (`Send_ 0x19b1ea0` u8 UpdateType + EditInfo;
  `0x32fa90` header + u32) and PC keeps a separate string for that non-EX RES (`0x1bd14a8`); no PS4 symbol or
  string `EDIT_PARAM_EX`: **exclusive (V)**. Names (I): u8 `unk_UpdateType` (position of the PS4 non-EX
  UpdateType), {u8, u32} `unk_Price` as CDataWalletPoint (capture (5, 20) = the 41.8.2 entry of UpdateType 2),
  MtString `unk_String` (empty in capture).
- 41.8.1 `0x821440` (exclusive): empty. 41.8.2 `0x7c81e0` (string "…GET_SHOP_PRICE_RES") -> `0x802130`:
  header, list `0x764d70` {u8, list CDataWalletPoint}. No PS4 symbol/string `SHOP_PRICE`: **exclusive (V)**.
  Names (I): u8 `UpdateType` (values 1, 2 = the 41.3.1 UpdateType), list `Prices`.
- Walk: 41.3.1 1/1 (`stream86-…-9/1748_…41_3_1`, 144 B, `cf9198fb97821915`: `2900 0301 00 | 0001 7701 | 01 | 01 |
  04 0000 00c8 | 02 07 a410 …` -> SlotNo 1, UpdateType 1, price (4, 200), end 0x8a); 41.3.2 1/1 (`…/1752`, 32 B,
  `6c5a37b78f6d330b`, end 0x11); 41.5.1 1/1 (`…/1529_…41_5_1`, 144 B, `90ad2210e9f783f4`: `… | 03 | 05 0000
  0014 | 01 07 7530 …` end 0x8b); 41.5.2 1/1 (`…/1532`, 32 B, `2474c1d2b7fbda29`, end 0x11); 41.8.1 4/4 (`…/1429`,
  16 B, `1cd780aad58b7906`, end 0x09); 41.8.2 4/4 (`…/1431_…41_8_2`, 48 B, `dc90d918676b86fe`: `… | 0000 0002 |
  01 0000 0002 05 0000 0005 04 0000 00c8 | 02 0000 0001 05 0000 0014` end 0x2e).

## 10. 51.x DISPEL

- 51.0.1 `0x826670`: `WritePacket(51, 0, 1)`, u8 (V). PS4 `Send_C2S_GET_DISPEL_ITEM_LIST_REQ 0x19cdb00(u8
  in_Category)`: **= PS4 (V)**, `Category` (V). Walk 1/1 (152; `stream85-…-11/159324_…51_0_1`, 16 B,
  `580e6c76b7a09c95`, end 0x0a).
- 51.2.1 `0x826750`: `WritePacket(51, 2, 1)`, **u32** (V). PS4 `Send_C2S_GET_DISPEL_ITEM_SETTING_REQ 0x19cd9d0`:
  empty. **Match V (RES string pair), S3 adds u32**: `unk_u32` (capture 23). Counter-test: empty PS4 body fits
  (slack): code decides. Walk 1/1 (`…/159320_…51_2_1`, 16 B, `a87af68ba53d8cdf`: `3300 0201 00 | 018f 7b00 |
  0000 0017` end 0x0d).
- 51.2.2 `0x7d24b0` (string "…DISPEL_GET_DISPEL_ITEM_SETTING_RES" at `0x7d2587`) -> `0x8068b0`: header, list
  `0x763390` {**u32**, MtString}, **bool** (V). PS4 `0x337ac0`: header, `m_DispelCategoryInfo`
  (CDataDispelCategoryInfo {u8 m_ucCategory, MtString m_wstrCategoryName}). **Match V; S3 widens Category to
  u32 and adds a bool.** Counter-test: PS4 fails **1/1**. Names: `Category` (V by member; values 152-156 = the
  51.0.1 Category), `CategoryName` (V), bool `unk_bool` (0). Walk 1/1 (`…/159322_…51_2_2`, 160 B,
  `c569b9ce507ec223`: `… | 0000 0005 | 0000 0098 0013 "武器(Lv60～80）" | …` end 0x93).

## 11. 9.1.2, 18.0.1, 52.1.1, 57.0.1 (headers and simple requests)

- 9.1.2 `0x7c6a00` (string "…OnPacket_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES") -> `0x8015b0`: header only.
  PS4 `OnPacket_S2C_SET_CHARACTER_BIN_SAVEDATA_RES 0x2e9060`: header only. **= PS4 (V)**. Walk 47/47
  (`stream1-marked.pcapng_tcp-stream-35/26535_…9_1_2`, 32 B, `dc48a57a8c0f063f`: `0900 0102 34 | 0000 0000 |
  0000 0000 | 0000 0000` end 0x11).
- 18.0.1 `0x82a310`: `WritePacket(18, 0, 1)`, `Write_u64` (V). PS4 `Send_C2S_GROUP_CHAT_GET_MEMBER_LIST_REQ
  0x19ca2d0(u64 in_GroupID)`: **= PS4 (V)**, `GroupID` (V). Walk 41/41 (GroupID 0 in all;
  `stream1-…-35/12081_…18_0_1`, 32 B, `27baef51d022f192`, end 0x11).
- 52.1.1 `0x830630`: `WritePacket(52, 1, 1)`, empty (V; PS4 `Send_C2S_FURNITURE_LIST_GET_REQ 0x19bbb00` empty).
  Walk 20/20 (`stream21-failedlogin-marked.pcapng_tcp-stream-48/12968_…52_1_1`, 16 B, `b8ee90c8471a10c6`, end 0x09).
- 57.0.1 `0x820870`: `WritePacket(57, 0, 1)`, empty (V; PS4 `Send_C2S_BOX_GACHA_LIST_REQ 0x19ccb30` empty). Walk
  3/3 (`stream6-annilot-hobo-marked.pcapng_tcp-stream-2/10018_…57_0_1`, 16 B, `5e93892a355074c6`, end 0x09).

## 12. 15.0.16 EVENT_START_NTC / 15.1.16 EVENT_END_NTC (unresolved -> matched V)

- PC `0x828920`: `WritePacket(15, 0, 16)`, empty; `0x828860`: `WritePacket(15, 1, 16)`, empty (V).
- PS4 `Send_C2S_EVENT_START_NTC 0x19c5da0` / `Send_C2S_EVENT_END_NTC 0x19c5ed0`: empty bodies.
- Behaviour (call graph, V): PC `0x828920` has one caller, wrapper `0x85d620` (connection, state 4,
  `isLoginSuccessPrivate`), called from `0x412d00` and `0x413900` (one site each). PS4
  `cNetGameServer::eventStartNotice 0x35fb40` (connection, CONN_CONNECTED, `mIsLoginSuccess`) is called once
  each from `aStage::move_event` and `aStage::move_event_fsm`. PC `0x828860` -> wrapper `0x85d5e0`, called 3x
  from `0x412d00`, 3x from `0x413900`, 1x from `0x40c620`; PS4 `eventEndNotice 0x35fb80`: 3x `move_event`, 3x
  `move_event_fsm`, 1x `aStage::finishEvent`. Same guard, same 1+1 / 3+3+1 pattern.
- Walk 8/8 + 8/8 (empty; `stream85-…-11/107023_…15_0_16`, 16 B, `c32021d2d44d934c`, end 0x09;
  `…/107198_…15_1_16`, 16 B, `55d2903f5a3825bf`, end 0x09).

## 13. 63.x (Season 3 group; all unresolved -> layout settled by PC code, PS4 rejected)

No PC string names any group-63 packet; PS4 02020005 has no `CHAIN_DUNGEON` symbol or string and no reader with
these sequences (the u32/empty shapes cannot be matched by code). **PS4: rejected for all (no PS4 code to
compare)**; names are `unk_` (raw-file names and Arrowgene names are leads).

| id | PC handler / writer | Body (V order and widths) | Use in the PC handler |
| --- | --- | --- | --- |
| 63.0.16 | `0x7d1ae0` (linear) | u32 | reads u32 and the header u32 (bytes 5-8, from `m_pStart+5`) into a local, then resets the manager at `[0x21af68c]+0x3a0c` (`sub_B60860` zeroes four dwords) |
| 63.1.16 | `0x7d1b80` (linear) | u32 | reads u32 into a local, discards |
| 63.2.16 | `0x7d1be0` (linear) -> `0x806610` | bool, u8, u32, u32, u32, u32, list loc `0x762b40` {u8, u32, MtString} | bool set -> `sub_B5D2F0` on the `+0x3a0c` manager; per element `sub_B85600(i, u32, u8, string, …)`; elements with u8 0x40-0x47 go to the `+0x3a0c` manager by the u32, others to `sub_BF8250(5, u32)`; the head u8 1/2 picks a GUI request (0x26/0x25) |
| 63.3.16 | `0x7d1f50` | **none** | allocates an object tagged (63, 3, 16), stores the header u32 (bytes 5-8) at +0xc and a flag; reads no body |
| 63.5.16 (C2S) | `0x826330`: `WritePacket(63, 5, 16)` | empty | sent by wrapper `0x87dc77` from a quest-process routine (`0x6346bc`) |
| 63.6.16 | `0x7d2150` -> list `0x762c50` | list {u32, u8, u32, u32} | per element: stage lookup by the first u32 (the stage table at +40516, as for layout ids), `(stageNo << 9) + u32 #3` (`sub_5DF7E0`) -> `sSetManager` `sub_BF8250(6, id)` |
| 63.7.16 | `0x7d2000` -> list `0x762c50` | list {u32, u8, u32, u32} | per element: same stage lookup, `sub_A41780(stageNo, u32 #3, u32 #4, 0)` -> `sub_BBF670` |
| 63.10.16 | `0x7d1e60` (linear) -> `0x8066b0` (linear) | u32, MtString, u8 | if the string is empty and u32 < 13: message by index (`getMsgFromIdxInfo`); `sGUIExt::requestAnnounce_w(text, u8 == 2)` |

- Element of 63.6.16/63.7.16: {u32, u8, u32} is `CDataStageLayoutId` (I: same widths and the stage-id lookup
  every layout reader does) + u32 (`unk_u32`; captures 0-7 incrementing within one group, a set index, I).
- 63.3.16: the 16-byte capture holds `0000 0006 0000 01` after the header, byte-identical to a 63.10.16 body
  {6, "", 1}; the PC reads none of it (V). A pattern should model the body as empty plus padding.
- Walk: 63.0.16 1/1 (`stream85-…-11/139432_…63_0_16`, 16 B, `1b344eb91aba8a8c`: `3f00 0010 34 | 0000 1710 |
  0000 0001` end 0x0d); 63.1.16 1/1 (`…/154846`, 16 B, `155f3aaaa5a360a9`, value 1, end 0x0d); 63.2.16 21/21
  (lists of 4; head bool 0/1, u8 0/1, u32 0-6, 15, 0/1, 3; element u8 63-69; `…/144660_…63_2_16`, 192 B,
  `a6ef0bd8f6f63216`, end 0xb3); 63.3.16 1/1 (`…/150195`, 16 B, `8202ca17efd6b14f`, end 0x09); 63.5.16 1/1
  (`…/154379`, 16 B, `3bce358e069055c7`, end 0x09); 63.6.16 1/1 (`…/154409_…63_6_16`, 32 B, `ff53289e385bb375`:
  `3f00 0610 34 | 0000 1ba2 | 0000 0001 | 0000 028f 00 0000 00fa 0000 0000` -> stage 655, layer 0, group 250,
  0, end 0x1a); 63.7.16 8/8 (stage 655, group 109, u32 0-7; `…/140609`, 32 B, `ff748d9304d6142b`, end 0x1a);
  63.10.16 11/11 (u32 1/6/9/10, empty strings, u8 1/2; `…/141554`, 16 B, `ac37596ce57ae66c`, end 0x10).

## 14. 54.0.x GET_CRAFT_RECIPE (Season 3 material)

- 54.0.1 `0x8258f0`: `WritePacket(54, 0, 1)`, u8, u32, s32 (V). PS4 `CPacket_C2S_GET_CRAFT_RECIPE_REQ::WritePacket
  0x1a35ae0` {u8 in_Category, u32 in_Offset, s32 in_Num}: **= PS4 (V)**.
- 54.0.2 `0x7d0eb0` (string "…OnPacket_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES") -> `0x805db0`: header, u8, list loc
  `0x76e000` (CDataMDataCraftRecipe, S3 material), bool. PS4 `0x336480` -> `0x19dfb30` {u8 m_ucCategory,
  m_RecipeList, b8 m_bIsEnd}: **match V; S3 adds a bool per material** (`unk_bool`, 0 in all 354 materials).
  Counter-test: PS4 material fails **3/3**.
- Walk 3/3 + 3/3 (Category 1 or 26, Offset 0, Num 100; up to 79 recipes); 54.0.1 `stream86-…-9/3289_…54_0_1`
  (32 B, `7c42f63c32798756`, end 0x12); 54.0.2 `…/3365_…54_0_2` (6976 B, `fcd2820a3dd1df1c`, end 0x1b40).

## 15. Summary

| id | name | PS4 mark | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 9.1.2 | S2C_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES | V | 8 | 26535 | 47/47 |
| 15.0.16 | C2S_EVENT_START_NTC | V (call graph) | 0 | 107023 | 8/8 |
| 15.1.16 | C2S_EVENT_END_NTC | V (call graph) | 0 | 107198 | 8/8 |
| 18.0.1 | C2S_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_REQ | V | 8 | 12081 | 41/41 |
| 30.0.1 | C2S_CRAFT_GET_CRAFT_PROGRESS_LIST_REQ | V | 0 | 3202 | 10/10 |
| 30.0.2 | S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES | V (S3 element; code-only) | 8+var | 3219 | 10/10 |
| 30.10.1 | C2S_CRAFT_CRAFT_SKILL_UP_REQ | V | 12 | 4543 | 1/1 |
| 30.10.2 | S2C_CRAFT_CRAFT_SKILL_UP_RES | V | 8+20 | 4545 | 1/1 |
| 30.12.1 | C2S_CRAFT_RESET_CRAFTPOINT_REQ | V | 4 | 4628 | 1/1 |
| 30.12.2 | S2C_CRAFT_RESET_CRAFTPOINT_RES | V | 8+12+5n | 4631 | 1/1 |
| 30.13.1 | C2S_CRAFT_GET_CRAFT_SETTING_REQ | V | 0 | 3200 | 2/2 |
| 30.13.2 | S2C_CRAFT_GET_CRAFT_SETTING_RES | V (S3 tail) | 8+var | 3218 | 2/2 |
| 30.15.1 | C2S_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_REQ | V | 0 | 3293 | 2/2 |
| 30.15.2 | S2C_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_RES | V | 8+4+3n | 3295 | 2/2 |
| 34.0.1 | C2S_ENTRY_BOARD_ENTRY_BOARD_LIST_REQ | X (exclusive) | 4+8n | 138924 | 1/1 |
| 34.0.2 | S2C_ENTRY_BOARD_ENTRY_BOARD_LIST_RES | X (exclusive) | 8+4+23n | 138928 | 1/1 |
| 34.1.1 | C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ | V (S3 search) | 16+var | 11735 | 3/3 |
| 34.1.2 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES | V (S3 item) | 8+8+var | 11828 | 3/3 |
| 34.2.1 | C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_REQ | V (S3 recruit) | 8+var | 138931 | 1/1 |
| 34.2.2 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES | V (S3 item) | 8+8+var | 138933 | 1/1 |
| 34.6.1 | C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_REQ | V | 0 | 138967 | 1/1 |
| 34.6.2 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_RES | V | 8 | 138972 | 1/1 |
| 34.6.16 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_NTC | V (behaviour) | 6 | 138947 | 1/1 |
| 34.7.1 | C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_FORCE_START_REQ | V | 0 | 138946 | 1/1 |
| 34.7.2 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_FORCE_START_RES | V | 8 | 138950 | 1/1 |
| 34.14.16 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC | V (unique shape; S3 member) | 1+var | 138932 | 1/1 |
| 34.16.16 | S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_RESERVE_NTC | I (unique shape in group) | 8 | 138971 | 1/1 |
| 41.3.1 | C2S_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_REQ | V (S3 + price) | 2+5+122 | 1748 | 1/1 |
| 41.3.2 | S2C_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_RES | V (S3 - u32 GP) | 8 | 1752 | 1/1 |
| 41.5.1 | C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ | X (exclusive) | 1+5+122+2+n | 1529 | 1/1 |
| 41.5.2 | S2C_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_RES | X (exclusive) | 8 | 1532 | 1/1 |
| 41.8.1 | C2S_CHARACTER_EDIT_GET_SHOP_PRICE_REQ | X (exclusive) | 0 | 1429 | 4/4 |
| 41.8.2 | S2C_CHARACTER_EDIT_GET_SHOP_PRICE_RES | X (exclusive) | 8+var | 1431 | 4/4 |
| 51.0.1 | C2S_DISPEL_GET_DISPEL_ITEM_LIST_REQ | V | 1 | 159324 | 1/1 |
| 51.2.1 | C2S_DISPEL_GET_DISPEL_ITEM_SETTING_REQ | V (S3 + u32) | 4 | 159320 | 1/1 |
| 51.2.2 | S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES | V (S3 u32 + bool) | 8+var+1 | 159322 | 1/1 |
| 52.1.1 | C2S_MY_ROOM_FURNITURE_LIST_GET_REQ | V | 0 | 12968 | 20/20 |
| 54.0.1 | C2S_CRAFT_RECIPE_GET_CRAFT_RECIPE_REQ | V | 9 | 3289 | 3/3 |
| 54.0.2 | S2C_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES | V (S3 material) | 8+1+var+1 | 3365 | 3/3 |
| 57.0.1 | C2S_BOX_GACHA_BOX_GACHA_LIST_REQ | V | 0 | 10018 | 3/3 |
| 63.0.16 | S2C_63_0_16_NTC (raw name) | rejected (no PS4 code) | 4 | 139432 | 1/1 |
| 63.1.16 | S2C_63_1_16_NTC (raw name) | rejected | 4 | 154846 | 1/1 |
| 63.2.16 | S2C_63_2_16_NTC (raw name) | rejected | 22+var | 144660 | 21/21 |
| 63.3.16 | S2C_63_3_16_NTC (raw name) | rejected (no body read) | 0 | 150195 | 1/1 |
| 63.5.16 | C2S_CHAIN_DUNGEON_END_CHAIN_NTC (raw name) | rejected | 0 | 154379 | 1/1 |
| 63.6.16 | S2C_CHAIN_DUNGEON_REWARD_CHEST_APPEAR_NTC (raw name) | rejected | 4+13n | 154409 | 1/1 |
| 63.7.16 | S2C_63_7_16_NTC (raw name) | rejected | 4+13n | 140609 | 8/8 |
| 63.10.16 | S2C_63_10_16_NTC (raw name) | rejected | 7+n | 141554 | 11/11 |

Total 48 ids, 242/242 fit. Triage corrections: 15.0.16, 15.1.16, 34.6.16 unresolved -> matched (V); 34.16.16
unresolved -> matched (I); 63.x unresolved -> layout settled by PC code, PS4 rejected (no PS4 counterpart);
63.5.16 is client-written (C2S, as the triage says); exclusives 34.0.x, 41.5.x, 41.8.x confirmed (V).
Read-seq ratios below 1.0 explained: 30.0.2 (S3 element, `loc_` list), 30.13.2 (S3 tail, handler not a
function), 34.1.x/34.2.x (S3 recruit/member/item/search), 41.3.1 (S3 price), 41.3.2 (dropped u32), 51.2.x
(S3 u32s), 54.0.2 (`loc_` list, S3 material).

## 16. Shared types for pattern authors

Reuse unchanged: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`, `CDataCommonU8`),
`Character.hexpat` (`CDataWalletPoint`, `CDataCharacterListElement` S3, `CDataJobBaseInfo`), `Context.hexpat`
(`CDataEditInfo`), `Pawn.hexpat` (`CDataPawnCraftSkill`), `Instance.hexpat` (`CDataStageLayoutId`). Framing as
T003 § 18 (inline RES header; NTCs and C2S notices without header).

Add (names PS4 DWARF unless marked):

- `include/Craft.hexpat` (new): `CDataCraftPawnInfo` {u32 PawnID, MtString Name}; `CDataCraftProgress` (S3)
  {CDataCraftPawnInfo CraftMainPawnInfo, MtTypedArray<CDataCraftPawnInfo> CraftSupportPawnInfoList,
  MtTypedArray<CDataCommonU32> unk_u32_list, u32 RecipeID, u32 Exp, s32 NpcActionID, u32 ItemID, u32 ToppingID,
  u16 unk_u16, u32 RemainTime, bool ExpBonus, u32 CreateCount} (positions after NpcActionID: I, § 2);
  `CDataCraftPawnList` {u32 PawnID, CraftExp, CraftPoint, CraftRankLimit}; `CDataCraftTimeSaveCost` {u8 ID, u8
  Type, u32 Price, u32 Sec}; `CDataCraftSkillRate` {u8 PawnType, u8 SkillType, u8 Rate};
  `CDataCraftSettingUnkPawn` (struct name I) {u32 unk_u32_0, u8 unk_u8, u32 unk_u32_1, u32 unk_u32_2, MtString
  unk_Name, u32 unk_u32_3, MtTypedArray<CDataPawnCraftSkill> unk_SkillList}; `CDataCraftSettingUnkElement`
  (struct name I) {u32 unk_u32_0..4, bool unk_bool}; `CDataMDataCraftMaterial` (S3) {u32 ItemID, u32 Num, u32
  SortNo, bool unk_bool}; `CDataMDataCraftRecipe` {u32 RecipeID, ItemID, Time, Num, Cost, Exp, NeedRank, s32
  NpcAct, bool IsHide, MtTypedArray<CDataMDataCraftMaterial> CraftMaterialList}.
- `include/EntryBoard.hexpat` (new): `CDataEntryRecruitData` (S3) {u16 ID, u32 unk_u32, MtTypedArray<CDataCommonU8>
  EnableJobList}; `CDataEntryItemParam` {bool PasswordOn, bool PawnOn, s32 BottomEntryJobLevel, s32
  TopEntryJobLevel, u16 RequiredItemRank, u8 ItemRankType, u32 ItemRankCheckRoleType, u16 MinEntryNum, u16
  MaxEntryNum, MtString Comment, MtTypedArray<CDataEntryRecruitData> EntryRecruitList}; `CDataEntryMemberData`
  (S3) {u16 ID, bool IsReady, u32 unk_u32, CDataCharacterListElement CharacterListElement}; `CDataEntryItem` (S3)
  {u32 ID, CDataEntryItemParam Param, MtTypedArray<CDataEntryMemberData> EntryMemberList, u16
  BoardRequiredAvgItemRank, u16 TimeOut, u32 LeaderPartyId, bool unk_bool}; `CDataEntryBoardItemSearchParameter`
  (S3) {MtTypedArray<CDataCommonU8> SearchGroups, MtString FirstName, MtString LastName, bool RankSetting, u32
  RankMin, u32 RankMax, u32 Job, bool IsNoPassword, u32 RequiredItemRankMin, u32 RequiredItemRankMax, u32
  unk_u32_0, u32 unk_u32_1}; `CDataEntryBoardListElement` (exclusive, struct name I) {u64 BoardId (I), u16
  unk_u16_0..2, u16 unk_TimeOut (I), u16 unk_u16_4, bool unk_bool, u32 unk_u32}.
- `include/Character.hexpat` or a new `CharacterEdit.hexpat`: `CDataCharacterEditPriceInfo` (exclusive, struct
  name I) {u8 UpdateType (I), MtTypedArray<CDataWalletPoint> Prices (I)}.
- `include/Dispel.hexpat` (new): `CDataDispelCategoryInfo` (S3) {u32 Category, MtString CategoryName}.
- 63 group (new `ChainDungeon.hexpat` or inline; struct names I): `CData63LayoutSet` {CDataStageLayoutId
  unk_LayoutId (I), u32 unk_u32}; `CData63AnnounceElement` {u8 unk_u8, u32 unk_u32, MtString unk_Text}.

Packet bodies (after the header): 9.1.2 none; 15.0.16/15.1.16 none; 18.0.1 `u64 GroupID`; 30.0.2
`MtTypedArray<CDataCraftProgress> CraftProgressList, MtTypedArray<CDataCraftPawnList> CraftMyPawnList,
MtTypedArray<CDataCommonU32> CreatedReicpeList` (DWARF spelling); 30.10.1 `u32 PawnID, SkillType, SkillLevel`;
30.10.2 `u32 PawnID, SkillType, SkillLevel, UseCraftPoint, RemainCraftPoint`; 30.12.1 `u32 PawnID`; 30.12.2
`u32 PawnID, MtTypedArray<CDataPawnCraftSkill> CraftSkillList, u32 CraftPoint`; 30.13.2 `ColorRegulateItemList
(CDataCommonU32), TimeSaveCostList, u32 ReasonableCraftLv, u32 CraftItemLv, u8 CreateCountMax,
MtTypedArray<CDataCraftSettingUnkPawn> unk_PawnList, u32 unk_u32_0, u32 unk_u32_1,
MtTypedArray<CDataCraftSettingUnkElement> unk_List`; 30.15.2 `MtTypedArray<CDataCraftSkillRate> unk_RateList`
(I); 34.0.1 `MtTypedArray<u64> BoardIdList` (I); 34.0.2 `MtTypedArray<CDataEntryBoardListElement> unk_List`;
34.1.1 `u64 ID, u32 Offset, u32 Num, CDataEntryBoardItemSearchParameter SearchParam`; 34.1.2 `u64 ID,
MtTypedArray<CDataEntryItem> EntryItemList`; 34.2.1 `u64 BoardID, MtString Password, CDataEntryItemParam Param`;
34.2.2 `u64 BoardID, CDataEntryItem EntryItem`; 34.6.16 `u32 MaxMember, u16 TimeOut`; 34.14.16 `bool EntryFlag,
CDataEntryMemberData MemberData`; 34.16.16 `u32 NowMember, u32 MaxMember` (I); 41.3.1 `u8 SlotNo, u8 UpdateType,
CDataWalletPoint unk_Price (I), CDataEditInfo EditInfo`; 41.5.1 `u8 unk_UpdateType (I), CDataWalletPoint
unk_Price (I), CDataEditInfo EditInfo, MtString unk_String`; 41.8.2 `MtTypedArray<CDataCharacterEditPriceInfo>
unk_PriceList`; 51.0.1 `u8 Category`; 51.2.1 `u32 unk_u32`; 51.2.2 `MtTypedArray<CDataDispelCategoryInfo>
DispelCategoryInfo, bool unk_bool`; 54.0.1 `u8 Category, u32 Offset, s32 Num`; 54.0.2 `u8 Category,
MtTypedArray<CDataMDataCraftRecipe> RecipeList, bool IsEnd`; 63.0.16/63.1.16 `u32 unk_u32`; 63.2.16 `bool
unk_bool, u8 unk_u8, u32 unk_u32_0..3, MtTypedArray<CData63AnnounceElement> unk_List`; 63.6.16/63.7.16
`MtTypedArray<CData63LayoutSet> unk_List`; 63.10.16 `u32 unk_MessageIndex (I: < 13 selects a message when the
text is empty), MtString unk_Text, u8 unk_u8 (I: == 2 flags the announce)`. Empty bodies: 9.1.2 (header only),
15.0.16, 15.1.16, 30.0.1, 30.13.1, 30.15.1, 34.6.1, 34.6.2, 34.7.1, 34.7.2, 41.3.2, 41.5.2, 41.8.1, 52.1.1, 57.0.1,
63.3.16, 63.5.16.

## 17. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`:

1. `CDataCraftProgress` writes a third list `CraftMasterLegendPawnInfoList` of `CDataCraftPawnInfo` {u32,
   MtString}; PC reads a list of plain u32 there (`0x75e8e0`). Misplacement (C, by the PC reader; captures
   never hold a progress entry). Its `AdditionalStatusId` u16 position agrees with PC.
2. `CDataEntryMemberData` names its bool `EntryFlag`; DWARF and recompilation name it `m_bIsReady` (EntryFlag
   is the 34.14.16 notice's own bool). Naming only.
3. `CDataEntryItem` names the u32 `PartyLeaderCharacterId`; DWARF `m_unLeaderPartyId`. Naming only.
4. No structure for 18.0.1 (GROUP_CHAT member-list request), 63.1.16, 63.2.16, 63.3.16, 63.5.16, 63.6.16 (only
   `S2C_63_0_16_NTC`, `S2C_63_7_16_NTC`, `S2C_63_10_16_NTC` exist).
5. Agree with PC (shape): `S2CCraftGetCraftSettingRes` (+ `CDataRegisteredLegendPawnInfo`, `Unk1`, `Unk2`,
   `CDataRefiningMaterialInfo`), `CDataMDataCraftMaterial` (+ `IsSp`), `CDataEntryRecruitData` (+ `Unk1`),
   `CDataEntryMemberData` (+ `Unk0`), `CDataEntryItem` (+ `Unk0`), `CDataEntryBoardItemSearchParameter` (+
   `Unk0`, `Unk1`), `CDataEntryBoardListParam`, `C2SEntryBoardEntryBoardListReq`,
   `C2SCharacterEditUpdatePawnEditParamReq` / `…CharacterEditParamExReq` (`EditPrice` = the {u8, u32}),
   `S2CCharacterEditGetShopPriceRes` / `CDataCharacterEditPriceInfo`, `C2SDispelGetDispelItemSettingsReq`
   (`ShopType` u32), `S2CDispelGetDispelItemSettingsRes` (+ `Unk1` bool), `CDataDispelItemCategoryInfo` (u32
   Category), `S2CCharacterEditUpdatePawnEditParamRes` (header only), the 34.6.16/34.14.16/34.16.16 notices,
   `S2C_63_0_16_NTC` (u32), `S2C_63_7_16_NTC` ({CDataStageLayoutId, u32}), `S2C_63_10_16_NTC` (u32, MtString, u8),
   the 30.x and 54.0.x requests.

## 18. Open items and checks not run

- Names without code backing (I or `unk_`): 30.0.2 element u16 position and new list, 30.13.2 tail, 34.x S3
  u32/bool additions, 34.0.x element, 34.16.16 field names, 41.3.1/41.5.1 price struct, 41.5.1 u8/string, 41.8.2
  element, 51.2.1 u32, 51.2.2 bool, 54.0.2 material bool, every 63.x field.
- Consumers not traced: the managers behind `[0x21af68c]+0x3a0c` (63.0/63.2) and `sub_B85600`, `sub_A416C0`
  (63.7), the 30.13.2 S3 tail, the 34 S3 fields.
- Counter-tests that cannot separate PC from PS4 (code decides): 30.0.2 (empty progress lists), 34.1.1 (slack),
  34.16.16 PS4 framing (slack), 41.3.1, 41.3.2, 51.2.1 (slack).
- Code-only (never non-empty in captures): 30.0.2 progress element, 41.5.1 string, 63.10.16 text (always empty).
- 63.3.16 and 63.0.16 read the header u32 at `m_pStart+5`; that `m_pStart` is the header start is inferred
  from the `WritePacket` layout (I).
- ImHex not run (not on `PATH`); no pattern written (outside this package).

## Errata (R3, 2026-11-02)

- § 8, 34.14.16 sample `stream85-…-11/138932_…34_14_16` (64 B, `78cb5da07b8705b2`): the list element
  ends `09 64 00 00 00 00 01`; its trailing byte is 1, not 0 (`xxd` of the raw file, TC1). End 0x32 and
  the fit are unchanged.
- § 16, `CDataEntryRecruitData.EnableJobList` (and § 18's "I: element type"): the name is V, the PS4
  DWARF member `CDataEntryRecruitData::m_EnableJobList` (`binaries/PS4_02020005/DDOORBIS.elf.h:71284`,
  element `CDataEntryRecruitJob`); that it equals Arrowgene's name does not make it a server name. The
  pattern comment and the packets README say so since TC1; no key changed.
