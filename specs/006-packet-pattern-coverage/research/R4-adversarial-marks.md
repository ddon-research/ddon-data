# 006 R4: adversarial review of the T014b provenance marks

Brief: `specs/006-packet-pattern-coverage/briefs/R4-adversarial-marks.md`. Base: `fa812585cf7`.
Risk: a mark that claims more than its evidence (V without a full data flow, a server name dressed as
a code inference, an I basis that does not lead to the name).

Evidence: IDA 9.5 private copies, opened read-only through ida-mcp. Nothing was renamed, retyped,
commented or saved.

- PC 03040008: `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-r4/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (32-bit, image base `0x400000`, confirmed with `idc.get_idb_path()`).
- PS4 02020005: `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-r4/DDOORBIS.elf.i64`
  (64-bit, base `0`, confirmed).

All addresses are VAs. Rows come from `research/T014b-consumer-property-names.tsv` (478 rows) and the
`// T014b` comments in `research/03040008/packets/`. The JSON trees, patterns and `packets/` were
not modified.

## Findings (reproduced)

### F1. EnhanceType and EnhanceId: the marks claim V for names that come from role plus the server lead (lower the name to I)

- **Fields:** `include/Context.hexpat` `CDataContextEquipData_unk_0.EnhanceType` (was `unk_u8_0`, 12 TSV
  rows) and `.EnhanceId` (was `unk_u16_0`, 12 TSV rows). Both are marked `V (consumer; lead agrees)`.
- **What the code shows:**
  - Reader PC `0x765ba0` reads u8 into +8, u8 into +9, u16 into +10 and u16 into +12.
  - `0x4fa120` passes those four values to the setter `0x5f8030`.
  - `0x5f8030` switches on the +8 byte: case 1 writes ctrl +4/+14, case 2 writes +6/+8/+10 indexed by
    the +9 byte (and +16), case 3 writes +12.
  - The ctrl's vtable `0x1b79948` is followed by the DTI string `nEquipEnhanced::cEquipEnhancedCtrl`
    (`0x1b7995c`).
  - `0x4dce10` calls `0x4dde40(this, a2, id)`. `0x4dde40` rejects 0 and ids above `a2->vfunc+80()`,
    and applies entry id-1.
- **Verdict:** the data flow into the ctrl is V. The class name gives "Enhance" from code. "Type"
  comes only from the role (a three-way switch), and no string names either field.
  - The step from `a2` to `rEnhancedParamList` was not reproduced. `a2` comes from the caller of
    `0x4dcda0`, which I did not trace.
  - Spec § "Naming unknown fields by inference", rule 4, says a name the server lead supplies is
    marked `I (<basis>; lead agrees)`. A `V (...; lead agrees)` mark is not a form the spec allows.
- **Fix:** keep both names. Change the marks to `V (consumer); I (name: role + class
  nEquipEnhanced; lead agrees)` in the TSV and the two pattern comments (`Context.hexpat` lines
  183-193).
- **SlotNo:** `EquipElementParam.SlotNo` has the same mark form, but its name is DWARF-backed. PS4
  `CDataEquipElementParam` has `m_ucSlotNo@8, m_unItemID@12`, the same element, and `0x4fa0d0`
  accepts 1..4 as an index. Its V stands; dropping "lead agrees" is cosmetic.

### F2. The GameSetting "Type" key is the current game mode (rename the field)

- **Field:** `include/Server.hexpat` `CDataGameSetting_unk_1.Type` (was `unk_u8`), marked
  `V (role: lookup key); I (name; lead agrees)`.
- **What the code shows:**
  - The default key in PC `0xb5f420` is `a3 ?: *(sGame + 3711*4)`. The function walks the setting
    +296/+308 list for the element whose u8 +4 equals that key, then returns the inner element's +8
    for level `a2+1`.
  - The caller `0x4845d0` sets `ecx = sGamePointer`, so the key is sGame +0x39FC.
  - The same dword is the game mode:
    - `0xb5fd10` returns `sGame[3711] == 1` and `0xb5fea0` returns `== 2`.
    - DECIDE_CHARACTER_ID_RES handler `0x7c7f20` (lines 53-55) stores the trailing u8 there.
    - `0xb5ff70` compares it with `rLandInfo` `mGameMode`, a property registered by `0xa9ef10`.
  - T014b names that storage GameMode itself (rows 224 and 248).
- **Fix:** rename `Type` to `GameMode`, marked `V (role: lookup key compared with sGame+0x39FC);
  I (name)`. The server's generic "Type" lead does not contradict this. In the JSON this changes one
  key in `S2C_SERVER_GET_GAME_SETTING_RES` exports.

### F3. DistributionStartDate has a code consumer that T014b did not cite (strengthen the basis)

- **Fields:** `include/Quest.hexpat` `CDataQuestList.DistributionStartDate` (`I (consumer + value;
  lead agrees)`) and `CDataQuestOrderList.DistributionStartDate` (`I (consumer + value)`). The TSV
  still writes the name with "(proposed)"; the patterns use it without that suffix.
- **What the code shows:**
  - `0x64d620` passes packet +80 as the last argument of `0x64d700`, which stores it at
    cQuestTaskParam +376 (`0x64d74c`, `mov [esi+178h], eax`). Packet +88 goes to +296, which PS4
    names `EndDistributionDate`.
  - A scan of `[reg+178h]` in `0x600000-0x700000` and `0x9a0000-0xa40000` finds the getter
    `0x64d260` (single caller `0x9d04c0`). It returns true when (+376 != 0 and +376 > now) or
    (+296 != 0 and +296 < now). "now" is the qword at the global `this + 357*8` (= +2856), the same
    current time T014b cites for the shop (`0x5fa060`).
  - This is a distribution-window test: +376 is the start, +296 the end.
- **Fix:** keep the name. Add `0x64d260` to the basis and raise the mark to `V (consumer); I (name)`.
  `lead agrees` then becomes a side note. Drop "(proposed)" from the TSV.

### F4. Chat fields follow the server's vocabulary beyond what the code shows (low; no mark change)

- **Fields:** `C2S_LOBBY_LOBBY_CHAT_MSG_REQ` `MessageFlavor`, `PhrasesCategory`, `PhrasesIndex`, all
  marked `V (role); I (name; lead agrees)`.
- **What reproduces:**
  - Writer `0x841ad0` writes u8, u32, u8, u32, u32, cstr, matching the pattern order.
  - `0xb29160` calls `0xb291b0(text "%d", 1, category+1, a4)`.
  - In `0xb76030`, case 4 calls `a4 = 0xb79b80(category, index)`.
  - `0x588b80` passes kind 3.
- **What the code does not show:**
  - `0xb79b80` returns the u16 at +4 of entry `index` in per-category table `this+1629*4+cat*4`
    (category < 8). That is a table entry id, not the input index.
  - No code string says "phrase" or "flavor". The PC strings nearby are `rTbl2ChatMacro` and
    `sGUIExt::cChatMacro`, which are not tied to `0xb79b80` here.
- **Verdict:** the I marks are honest, but the lexical names are the server's words ("Flavor",
  "Phrases", "Index").
- **Fix (optional):** keep the I marks and say in the comment that the names come from the lead,
  with code supporting only kind / category+1 / table entry id. A neutral rename (`MessageKind`,
  `MacroCategory`, `MacroEntryId`) would follow the code more closely.

## Checked and reproduced without change (21 field groups)

| Field (pattern) | Mark | Reproduced at |
| --- | --- | --- |
| Context `CDataContextPlayerInfo.RoomNo`, `.PlayerStatusFlag` | V (property name) | createProperty `0x471a50`: `this+14992` "mRoomNo", `+14996` "mPlayerStatusFlag" (type 6); reader `0x75f930` +324/+328; copy `0x84b174`/`0x84b18f` (`[edi+144h]`/`[edi+148h]`) -> `0x84c049` `sub_47BAD0` (`+14992 = v`) and `0x84c081` `sub_478E20` (`+14996 \|= v`); h+0xE4 bit 0x20 at `0x84c072` |
| Context `EquipElementParam.SlotNo` | V | `0x4fa0d0` (1..4, `cCrestParam[u8-1]`); PS4 DWARF `m_ucSlotNo` |
| Context `CDataContextPawnInfo_unk_0.SpSkillId/Lv` | I (binary hint; lead agrees) | element reader `0x772950` shared with `0x813510`, whose caller `0x7eca50` carries `OnPacket_PAWN_SP_SKILL_GET_ACTIVE_SKILL_RES` |
| Context/Pawn `TrainingStatus` | I (binary hint; lead agrees) | `CDataPawnInfo` reader `0x772180` calls `0x772aa0(+432)`; the same reader is used by `0x813860` and `0x813970`, read by handler `0x7ed6d0` (`OnPacket_PAWN_TRAINING_GET_TRAINING_STATUS_RES`, `qmemcpy(+1964, buf, 64)`); the context copy reads the 64 bytes inline (`0x75f8d0`), consistent with the basis wording |
| Item `CDataItemList.EquipCharacterId`, `.EquipPawnId` | V | PC `0xb941e0` lines 65-82 (+28 -> owner type 1, else +32 -> type 2); PS4 `0x7cee20` `m_unEquipCharacterID` / `m_unEquipPawnID` (`2*(id != 0)`) |
| Item `CDataItemList.EquipPoint` | I (consumer; lead agrees) | `0xb941e0` +24 -> `*((_WORD*)x+38)` (lines 167, 195); PS4 `EquipPoint = m_unEquipPoint` |
| Server `CDataGameSetting_unk_0.WalletType`, `.MaxValue` | V; I (name) | `0x7f9070` -> `0xb61880(sGame, u32_0 in 1..16, u32_1)` -> `sGame[3692+type]`; `0x67cd40` tests `0xb997b0(type)+add > 0xb5f590(type)` |
| Server `CDataGameSetting_unk_2.Exp` | V (role); I (name) | `0xb5f420` returns inner element +8 for level `a2+1` |
| Character `CHARACTER_PENALTY_REVIVE_REQ.NoBadHpMax` | V (source); I (PS4 member order) | `0x879940` disasm: `0x872760` reads `+0x172C` (fistp -> ebx), `0x65ab10` reads `+0x1730` (fistp -> ebp), `push ebp; push ebx; call 0x820e00` (writes u32, u32); context +8896 (`0x474e60`); PS4 `reqCharacterPenaltyRevive` `0x3682a0` sends `mWeakHpMax_pri`@5776; DWARF next member `mNoBadHpMax_pri`@5780 |
| Quest `CDataLightQuestDetail` AreaId, BaseAreaPoint, GetCP, OrderLimit, ClearNum, BoardType | V / I (member order) | PC `0x9d2af0`: +4 -> b367, +12 -> d312, +24 -> w354, +20 -> w356, +16 -> d360, +28 -> b364; PS4 `setLightQuestDetail` `0x54ed20` with `cQuestTaskParam` `mClearNum@474, mOrderLimit@476, mGetCP@480, mBoardType@484, mAreaId@487` and `CLightQuestDetail` order AreaId, BaseAreaPoint, GetCP, OrderLimit, ClearNum, BoardType; PC +8 -> b368 is the Season 3 addition |
| Quest `CDataSetQuestDetail.LeaderCompleteNum` | I (elimination) | reader `0x778040` reads u16 +60/+62; `0x64dd10` never reads +60 and stores +62 at +204; PS4 `CSetQuestDetail` `m_usLeaderCompleteNum@30`, `m_usRepeatRewardType@32` |
| Quest `CDataQuestTalkInfo.QuestId` | V; name V (`nQuest::QUEST_ID`) | `0x9d2ce0` line 155 `nQuest::QUEST_ID::QUEST_ID_0(v83, elem+4)` -> `0x9ce880` arg 5 -> `cTalkData +24` |
| Shop `CDataGoodsParam.HideIfReqsUnmet` | V; I (name; lead agrees) | `0xfccd30` line 79: listed when `+17 == 0 \|\| 0xfcc020(e)`; `0xfcc020` returns 0 for `0x5fa060` state 1/4, else 1 only when every requirement +12 != 0 |
| Shop `CDataGoodsParam.SalesPeriodStart` | V; I | `0x5fa060`: start > now -> 1, end passed -> 4 |
| Shop `CDataGoodsParam.ItemId` | V | `0xfccd30` line 80 `0xb98c80(sItemManager, +8)` |
| QUEST_REWARD_BOX_LIST_NUM_NTC `RewardItemSlotNum/Max` | V; I (UI text) | `0x7f4e10` lines 107-137: Num >= Max -> msg 0x12C, Num >= 80% Max -> 0x12D; `system_log.gmd.json` Index 300 `syslog_reward_box_limit_over_item`, 301 `..._notion_item` |
| PAWN_EXPEDITION_GET_SALLY_REWARD_RES `IsHotSign` | V (role); name I | `0x5ef5ab` getter `0x86f4a0`, `cmp [eax+3Dh], 1`; Index 296 `syslog_pawn_expedition_hotsign`, 256 `..._sp_delivery` |
| DECIDE_CHARACTER_ID_RES / Character list `GameMode` | V (store/compare); I (name) | `0x7c7f20` lines 53-55; `0xb5ff70` vs `rLandInfo` `mGameMode` (`0xa9ef10`); `0xef0c00` compares a2 with `sGame[3711]` |
| Gacha `CDataGachaSettlementInfo.ChargeId` | V (flow); I (name) | reader `0x768830` (+36 is the ninth u32); `0xd9fef0` GACHA branch (getter `0x86c250`) line 274 `v76 = v44[9]` -> `0xda2f00` arg 5; `0xd9df40(..., chargeId)` -> `sGame::isChargeEffect`; PS4 `0x7854a0` parameter `nGpCourse::E_GP_COURSE_EFFECT chargeId`. The box-gacha branch (`0x869100`) reads +40 of its own element |
| Craft `CDataCraftSettingUnkPawn.CraftRank` | V (role); I (name) | `0xb39c40` case 3 returns element +24 keyed by +16; cases 1/2 return pawn entry +52; PS4 `sCraftManager::getPawnRank(pawnId)` `0x761ac0` |
| LOBBY_CHAT_MSG_REQ field order | - | writer `0x841ad0` (see F4) |

### JSON keys (one exported file per sampled pattern, `rg -c "\"<name>\""`)

Present: LOBBY_CHAT_MSG_REQ (3 names); SHOP_GET_SHOP_GOODS_LIST_RES (9);
SERVER_GET_GAME_SETTING_RES (`WalletType`, `MaxValue`, `Exp`, `Type`, `Level`);
CHARACTER_PENALTY_REVIVE_REQ (`HpMax`, `NoBadHpMax`); DECIDE_CHARACTER_ID_RES `GameMode`;
QUEST_REWARD_BOX_LIST_NUM_NTC (2); SALLY_REWARD_RES `IsHotSign`; MAIL_GET_ALL_ITEM_REQ `StorageType`;
CRAFT_GET_CRAFT_SETTING_RES (5); CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC (`RoomNo`, `PlayerStatusFlag`,
`SlotNo`, `Add`; and `EnhanceType`/`EnhanceId` in stream26 stream-44 12579);
PARTY_MYPAWN_CONTEXT_NTC (`SpSkillId`, `SpSkillLv`, `TrainingStatus`); ITEM_GET_POST_ITEM_LIST_RES
(`Equip*`); L2C_GET_CHARACTER_LIST_RES (`GameMode`, `EquipType`, `EquipSlot`);
QUEST_GET_LIGHT_QUEST_LIST_RES (6); TUTORIAL_QUEST_LIST_RES (`DistributionStartDate`, `QuestId`);
GACHA_LIST_RES `ChargeId`; `LeaderCompleteNum` in stream20 stream-47 12456 SET_QUEST_LIST_RES.

No mismatch between pattern name and JSON key was found.

## Not checked

- `rEnhancedParamList` as the `0x4dde40` table: not traced (F1).
- PS4 `addItemNotice` storing EquipPoint at +76: PC side only.
- `0xb5f370`: only `0xb5f420` was read.
- Shop requirement texts (`0xf50470` cases): not checked for PeriodStart, Condition, Progress or
  Param1-3. Stock (`0xfcd5a0`, `0xf52d20`) not checked.
- Mail StorageType dialog (`0x54cbd0`).
- Login EquipType: only `0xb959c0` lines 81-90 were read (storage 14/15 -> 1, 16/17 -> 2).
- Craft WalletType, Price, PawnName; Area and Stage SpotId, StageNo, GroupId; Dispel; Stamp;
  JoinLobby quest info; TimeGain UI-text rows; IsRecoverOcd; Quest Rank/RankPoint, EndTime/TimerIdx;
  QUEST_PLAY_END Error; GP and nNetMsg rows.
- Arrowgene was not opened: only the lead names recorded in the TSV and the comments were compared.
