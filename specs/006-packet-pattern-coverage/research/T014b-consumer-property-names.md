# 006 T014b: naming unknown fields from PC consumers and property names (client 03040008)

This report applies basis 1 (consumer and property names) and basis 3 (binary hints) of spec 006 "Naming
unknown fields by inference" to the `unk_*` fields that T014a listed (`T014a-value-correlation.tsv`, 443
unknown rows plus 35 no-data rows = 478). For each field it gives a verdict and, for the T014a strong and
medium rows, whether code confirms or rejects the candidate. Nothing in `research/03040008/packets/` was
changed; renaming is left to the pattern owner.

- Data: `T014b-consumer-property-names.tsv`, one row per T014a row (478). Columns: pattern/include,
  struct, field, packet, key path, T014a tier and best match, proposed name, mark, basis, VAs, T014a
  candidate verdict.
- Builds and databases: PC 03040008 (Season 3 reference), private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t014/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (32-bit, image base 0x400000, checked with `idc.get_idb_path()`). PS4 02020005 (symbol source), private
  copy `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t014/DDOORBIS.elf.i64`
  (64-bit, base 0). The PS4 export `binaries/PS4_02020005/DDOORBIS_{1,2,3}.elf.c` was searched with `rg`
  to find consumers; every hit used here was re-read in IDA. All addresses are VAs. Both databases were
  used read-only; the SHA-256 of the copies was not computed (not run).
- Marks: **V** = data flow read in IDA from the reader to the store or use; **I** = inferred, with the
  basis named (consumer, member order, elimination, reader shape, value). A server name is used only as
  "lead agrees".

## Summary

| Verdict | Rows | Distinct struct.field |
| --- | --- | --- |
| V (consumer read in full) | 13 | 8 |
| I (consumer, member order, elimination, reader shape) | 66 | 16 |
| open (no consumer found, or not traced in the time box) | 399 | 220 |

61 rows get a proposed name that is not `unk_*`. The remaining rows of a settled struct.field keep
`unk_*` because the code shows a role but not a name. 220 struct.field pairs were not traced within the
180-minute time box (`open`, basis "consumer not traced"). The TSV marks them; they are coverage gaps, not
negative evidence.

## Method

1. Start from the PC reader that the earlier batch reports name (T002-T013, the includes' comments). Read
   it in IDA for the member offsets of the receiving object.
2. Follow the object to its consumer:
   - the packet handler (the T00x handler VA, or the `cSeedGameSvConnection::OnPacket_*` string xref);
   - the copy into a client object (e.g. `0x880cf0`);
   - the function that reads the member (a setter, a lookup, a UI store).
   Where the handler only keeps the packet (`conn+1008`), the getter (`0x86d400`) and its callers were
   followed.
3. Match the PC consumer to its PS4 counterpart by code shape: the same branch logic, constants (`% 0xC
   + 1`, `2 * (id != 0)`, `* 1000`), argument lists and callees. Then read the PS4 DWARF member or
   argument name at the same step. Where the PC member has no PS4 member, PS4 member order inside the
   same class (`cQuestTaskParam`) and the PC offsets of members already settled by another PC setter fix
   the remaining ones (marked I, member order).
4. To find consumers, all PC functions were indexed by displacement and immediate operands (one pass,
   about 60 s), and the index was queried by offset sets, for example cCharacterData +0x34C4 and the
   cQuestTaskParam offsets.
5. Property names: the PC string table and the PS4 `createProperty` functions of the receiving classes
   were checked (below).

## Property tables

- **PC 03040008**: the 26,631 IDA strings hold `MtProperty` names only for resource and unit classes (e.g.
  `mSpotId`, `mAreaId`, `mQuestId`). None of the classes that receive packet data has a property name in
  the PC binary: the searches `EquipPoint`, `mEquipChar`, `GetCP`, `BoardType`, `OrderLimit`,
  `Distribution` and `CheckPawn` return no member name (only class names such as
  `cQuestSvReqCheckQuestDistribution`). DTI class names do exist (`dti_cQuestPoint`, `cQuestTask::MyDTI`)
  and are cited where they identify an object.
- **PS4 02020005**:
  - `cQuestTaskParam::createProperty` (`0x1c6ff0`) and `cCharacterData::createProperty` (`0x48070`) are
    empty.
  - `cItemParam::createProperty` (`0xdff90`) registers five Japanese UI labels: アイテムID (item ID),
    アイテム名 (item name), 個数 (count), 強化度 (enhancement level) and クラフト (craft), plus
    `mWstrUID`. None of them names an unknown field.
  - The `cContext*::createProperty` functions exist (`0x51e80`..`0x5a320`); they were not read in this
    batch.

  No property table names a field in this batch.

## T014a candidates: verdicts

| T014a row (tier) | Candidate | Verdict | Basis (VAs) |
| --- | --- | --- | --- |
| CDataItemList.unk_u32_1 (strong) | CharacterID | **confirmed, V**: EquipCharacterId | PC addItemNotice `0xb941e0`: `item+28 != 0` -> owner, type 1; else `item+32` -> owner, type `2*(x!=0)`. Same code as PS4 `sItemManager::cItemBag::addItemNotice` `0x7cee20` with `m_unEquipCharacterID` / `m_unEquipPawnID`. Path: handlers `0x7dd540`/`0x7dd270` -> setItemList `0x880cf0` (copies +24/+28/+32 1:1) |
| CDataItemList.unk_u32_2 (strong) | PawnID | **confirmed, V**: EquipPawnId | same |
| AREA_GET_LEADER_AREA_RELEASE_LIST unk_list_0.unk_u32_0 (strong) | ReleaseList value | **confirmed**: SpotId (V role, I name) | PC `0xd40fd0` finds the element by `+4 == CDataSpotInfo.SpotID`. `0xbfe8e0` builds `+4*1000 + +8` (`0x5df870`) -> sSetManager `0xbf8250` type 1 |
| unk_list_0.unk_s64, unk_list_1.unk_s64 (3 strong rows) | timestamp | not confirmed by code: no consumer found reads element +16. The timestamp reading (basis 2) stands | consumers `0xbfe8e0`, `0x9784f0`, `0xd40fd0` read +4/+8 only |
| CharacterBinSaveData unk_u32_13508 (2 strong rows) | PawnID | not confirmed: no PC consumer exists in the scan. cCharacterData +0x34C4 / +0x3504 are touched only by init `0x467df0`, copy `0x465700`, deserialize `0x466560` and serialize `0x467790`. The PawnID match stays basis 2 only | displacement/immediate scan of all PC functions |
| TUTORIAL_QUEST_LIST Param.unk_u64 (medium) | timestamp | **confirmed as a date**. Start-date reading I | PC `0x64d620` (below) |
| the other 9 medium rows (StageNo, Param01, GroupId matches of CDataContextEquipData_unk_0, CycleContentsRank, GoodsRequirement, AreaChangeUnk0, JoinLobbyUnkOrderList, REWARD_BOX_LIST_NUM unk_u16_0) | various | not traced (time box); unconfirmed | - |

## Settled fields (beyond the T014a candidates)

### CDataItemList (include `Item.hexpat`)

- `unk_u32_0` = **EquipPoint**, I (consumer; lead agrees). PC `0xb941e0` reads `item+24` at the step
  where PS4 reads `m_unEquipPoint`, between the owner and the colour, and stores it as a u16 (sub-object
  +76). The other two u32 are V, so the third is EquipPoint by elimination. The server lead EquipPoint
  agrees.
- `unk_u8`: open. setItemList copies it to item +16, and addItemNotice does not read it.

### Area Season 3 lists (include `Area.hexpat`, packets 23.8.2 and 23.11.2)

- Handlers: PC `0x7c4600` keeps the 23.8.2 packet at `conn+1008` (getter `0x86d400`); `0x7c46b0` keeps
  23.11.2 at `conn+1020` (getter `0x871b30`).
- `CDataAreaUnkU32BoolS64.unk_u32` = **SpotId**, V role, I name.
  - PC `0xd40fd0` compares it with the spot id.
  - `0x9784f0` compares it with a set unit's id (+0x1b8) and returns the bool.
- `CDataAreaUnkU32BoolS64.unk_bool`: I (consumer), a per-spot flag. `0x9784f0` returns it and the callers
  `0x98e990`, `0x9927e0` and `0xf185f0` branch on it. No name.
- `CDataAreaUnkU32U32S64.unk_u32_1`: I (consumer), a per-spot value.
  - `0xd40fd0` stores it into the spot UI object (+60).
  - `0xbfe8e0` uses it as the low part of the sSetManager key `SpotId*1000 + x`.
  - No name.

### Quest dates and lists (include `Quest.hexpat`)

- PC `setDistributionParams` for CDataQuestList is `0x64d620`.
  - It passes `+88` where PS4 `cQuestTaskParam::setDistributionParams` passes `m_ullEndDistributionDate`
    (stored at cQuestTaskParam +296). This confirms the pattern's `EndDistributionDate` (V).
  - It passes `+80` (`unk_u64`) as a new trailing argument, stored at cQuestTaskParam +376, which has no
    PS4 member.
  - It also confirms `OrderNpcId` at +64 (V).
- The CDataQuestOrderList variant is `0x64d690`.
  - The reader `0x774a70` reads u64 at +80, +88 and +96.
  - `0x64d690` passes +96 as EndDistributionDate (V), +80 as the same new argument, and +16 as AreaId
    (V). +88 is not passed, so it is OrderDate by elimination (PS4 does not pass `m_ullOrderDate`
    either).
- The CDataSetQuestInfoList consumer is PC `0xbd6b40`, the counterpart of PS4
  `sQuestManagerExt::callbackGetSetQuestInfoList` (same ImageId fallback `% 0xC + 1`, QUEST_ID and
  SCHEDULE_ID).
  - It stores `+24` with the MtTime update check (PS4 `mEndDistributionDate`, V).
  - It stores `+16` (`unk_u64`) to a new nQuest member (+112).
- The proposed name for `unk_u64` in the three structs is **DistributionStartDate**, I (consumer + value;
  lead agrees for CDataQuestList).
  - The values in 146 TUTORIAL_QUEST_LIST files are 0 or past epoch dates, always below
    EndDistributionDate 2145884400.
  - The server lead for CDataSetQuestInfoList says OrderDate. The code puts this u64 in the same new slot
    as CDataQuestList's, not in an order-date slot.
- `unk_u32_list` of CDataQuestList (+136) and CDataQuestOrderList (+144): I (consumer). `0x64d700` wraps
  each u32 as `mIdx` of a `cQuestPoint` (PC DTI name) in a new cQuestTaskParam array (+384). There is no
  PS4 counterpart and no name.
- `CDataLightQuestDetail` (7 u32, PC reader `0x76d1c0`).
  - PC setLightQuestDetail is `0x9d2af0` (cQuestTask, taskParam at +0x68); PS4
    `cQuestTask::setLightQuestDetail` is `0x54ed20`.
  - The PC setter's targets are anchored by other PC setters: `0x64dd10` (setSetQuestDetail) writes +312
    and +354, and `0x64d690` writes +367.
  - Results:
    - u32_0 = **AreaId** (V)
    - u32_1 = new byte +368 (I, no PS4 member; lead BoardId)
    - u32_2 = **BaseAreaPoint** (V)
    - u32_3 = **GetCP** (I, member order)
    - u32_4 = **OrderLimit** (I, member order)
    - u32_5 = **ClearNum** (V)
    - u32_6 = **BoardType** (I, member order)
  - The server order (AreaId, BoardId, GetAp, GetCp, OrderLimit, ClearNum, BoardType) agrees with all
    seven positions.
- `CDataSetQuestDetail`: PC setSetQuestDetail `0x64dd10` = PS4 `cQuestTaskParam::setSetQuestDetail`
  `0x1c5c10`.
  - `unk_u16_1` (+62) = **RepeatRewardType** (V). It goes to +204, beside +208 = RepeatRewardValue and
    +212 = the CompleteNum formula, as PS4 `mRepeatBonus.mType`.
  - `unk_u16_0` (+60) is unread. **LeaderCompleteNum** is proposed by elimination (I).
  - Side result (named lists, outside the unk rows): `unk_wallet_point_list` and `unk_quest_exp_list`
    are the Season 3 undiscovery-ratio lists. Wallet type 1 -> mUndiscoveryGold, type 2 ->
    mUndiscoveryRim, exp type 1 -> mUndiscoveryExp, the same formula as PS4's three u16 ratios (V).
- `CDataQuestEnemyInfo.unk_u32`: the role from T001c (Quest.hexpat: a new cEnemyGroupInfo dedupe-key
  member, PC `0x9d2590`) is carried into the TSV; it was not re-read here.

### EquipElementParam (include `Context.hexpat`)

- The PC element reader `0x765a90` reads u8 -> +4, then u32 -> +12 and u16 -> +16 inside a nested
  object with its own vtable at +8.
- It is used for the first list of CDataItemList and of CDataEquipItemInfo, in the place of PS4
  `m_EquipElementParamList` (CDataEquipElementParam {u8 m_ucSlotNo, u32 m_unItemID}).
- Results:
  - `unk_u8` = **SlotNo**, I (reader shape, basis 3; lead agrees).
  - `unk_u32` = **ItemId**, proposed, I (reader shape). It sits in a Season 3 nested object; the lead
    says CrestId.
  - `unk_u16`: open.
- PC consumer not found: `0x880180`, `0xb3f9b0` and `0x88d320` only copy the element.

## Open and not traced

- 220 struct.field pairs are `open`, including the largest groups:
  - CDataContextEquipData_unk_0 (48 rows), CDataEquipItemInfo (36), CDataContextBase_unk_0 (14),
    GoodsRequirement (12), CDataPawnInfo_unk_0 (10), CDataCharacterListElement.unk_u8 (10),
    CDataQuestDeliveryItem (10), CDataQuestExp.unk_u8 (9), the mandragora, craft, dispel, entry-board
    and GP structs, and CDataTimeGainQuestList's five bools (Quest.hexpat's open item).
  - The PS4 consumers of the PS4 members that would anchor them were searched in the export without a
    name hit: `m_bIsJoinPawn`, `m_bIsNoTimeup` and `m_ucJoinPawnNum` appear only in the reader;
    `m_ucEquipSlot` and `m_ucEquipType` only in craft packets.
  - The next step for them is a pointer-level trace in IDA.
- Not run: SHA-256 of the private database copies; the `cContext*::createProperty` tables of PS4; the
  PC consumers of `stOptionData` +9/+37/+96..98 and of cCharacterData +13637 (`0x14f50f0`).

## Next field

The first open field by capture frequency is `include/Context.hexpat`
`CDataContextEquipData_unk_0.unk_u16_0` (T014a medium rows; PC reader `0x765ba0`). To trace it, start from
the copy loop in `0x880210` (setItemList's second list) to its consumer.

## Part 2 (2026-11-02): Context.hexpat and CharacterData.hexpat

Scope: the 141 TSV rows of `include/Context.hexpat` and `include/CharacterData.hexpat`. They cover 25
distinct struct.field pairs, counting each CharacterBinSaveData bit-stream member separately.

Builds and databases:
- PC 03040008: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t014b2/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (32-bit, image base 0x400000, checked with `idc.get_idb_path()`).
- PS4 02020005: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t014b2/DDOORBIS.elf.i64`
  (64-bit, base 0).

Both copies were used read-only. The SHA-256 of the copies was not computed (not run). All addresses are VAs.

| Verdict | Rows | Distinct struct.field |
| --- | --- | --- |
| V (data flow read in full) | 77 | 8 |
| I (consumer, binary hint, enum range) | 44 | 8 (5 named, 3 role only) |
| open, with the reason in the TSV | 20 | 9 |

### Property tables: correction to part 1

Part 1 searched the PC strings and found no property table that names packet data. That search missed the
tables. The PC binary has 1,227 functions that call `MtPropertyList::insert` (`0x4236b0`). Their
registrations were extracted from the decompiler output: 7,237 name/offset pairs.

- The context class has four tables:
  - `0x471180`: HumanType, PawnType, CharId (+8676), PawnId (+8680), ...
  - `0x4708e0`
  - `0x471b20`: mUniqueId, Stage, mMasterIndex, ...
  - `0x471a50`: **mRoomNo** at +14992 and **mPlayerStatusFlag** at +14996 (type 6, u32).
- The equip classes below have no table: `cItemEquipParam`, `cCraftParam`, `cCrestParam` and
  `nEquipEnhanced::cEquipEnhancedCtrl` all use the shared empty createProperty `0x402470` in their vtables.
- No table covers cCharacterData +8968 (stOptionData) or +13508..13637.

### T014a candidates

| Row (tier) | Candidate | Verdict |
| --- | --- | --- |
| CDataContextEquipData_unk_0.unk_u16_0 (3 medium) | StageNo, Param01 | **rejected** by code: the field is an rEnhancedParamList index (EnhanceId, below) |
| CDataContextEquipData_unk_0.unk_u16_1 (1 medium) | StageNo | **rejected** (I): the field is stored beside the enhance ids in the enhance ctrl |
| CharacterBinSaveData unk_u32_13508 (2 strong) | PawnID | unchanged from part 1: no PC consumer, value match only |

### Equip enhancement list: CDataContextEquipData_unk_0 (V)

Data flow, PC:
- Reader `0x765ba0` fills a 16-byte element: u8 at +8, u8 at +9, u16 at +10 and u16 at +12.
- Item lists (reader `0x76aca0`, list at +56):
  - addItemNotice `0xb941e0` passes `[esi+38h]` to `0x4fad50`, which calls `0x4fa120`.
  - `0x4fa120` resets the ctrl, then calls the setter `0x5f8030(ctrl, +8, +9, +10, +12)` for each element.
  - The ctrl sits at cItemEquipParam +92. cItemEquipParam (DTI `dti__123`, 120 B) hangs at cItemParam +40.
- Context:
  - copyContextParam (`0x84aca0`) passes equip element +32 to `0x4fad50` at `0x84afda`. IDA cuts this
    function short at `0x84aeaf`, so the code after it was read as disassembly.
  - The equip-list path `0xb959c0` copies the item list +56 to +36, and `0xb9e3d0` passes it on (`0xb9e4a5`).
- The ctrl class has ctor `0x5f7e30` and vtable `0x1b79948`. The vtable is followed by the string
  `nEquipEnhanced::cEquipEnhancedCtrl`. Related Season 3 strings: `OnPacket_EQUIP_ENHANCED_*`,
  `uGUIEquipEnhance`.
- Setter `0x5f8030`:
  - type 1: the id goes to +4, `unk_u16_1` to +14;
  - type 2 with slot 1..3: the id goes to +6/+8/+10; slot 1 also writes `unk_u16_1` to +16;
  - type 3: the id goes to +12.
- Consumer: status calc `0x4dd630`.
  - `0x4dcda0` loops types 1..3 and calls `0x4dce10` (count `0x5f7f80`, getter `0x5f7f40`), which calls
    `0x4dde40(id)`.
  - `0x4dde40` ignores id 0 and ids above the rEnhancedParamList count. Otherwise it applies entry id-1
    through the stat table `0x1b0fcb8`.
  - `client/03040008/enhanced_param/param/enhancedParamList.epl.json` has 947 entries; the captured
    `unk_u16_0` values reach 944.

Names:
- `unk_u8_0` = **EnhanceType** (V; lead agrees).
- `unk_u8_1` = **EnhanceSlotNo** (V; the name comes from the role).
- `unk_u16_0` = **EnhanceId** (V; lead agrees).
- `unk_u16_1`: I (consumer), kept unnamed. No reader of ctrl +14/+16 was found by the word-access scan, and
  the ctrl copy `0x5f7ed0` copies +14 only.

### Equip parameter list: CDataContextBase_unk_0 (V value, I kind)

- The same {u8, u16} struct serves two lists: the item's third list (reader `0x766210`, item +76) and the
  CDataContextBase trailing list (`0x7605e0`, base +216).
- Item path: addItemNotice `[esi+4Ch]` -> `0x4fae60` -> `0x4fa310` -> `0x5fc610`. The setter writes u8 to +4
  and u16 to +6 of an element of the cItemEquipParam +80 list.
- Context path: `0x84afc0` passes base +216 to `0x4fae30`. `0x4fae30` applies the list through `0x4fa190`,
  and only to the equip item whose rItemParam category is 10 and subcategory 5 (`0x4f9620`).
- Consumer: status calc `0x4dd630` loops the +80 list and calls `table_0x1b0fcb8[u8](this, arg, u16)` for
  u8 < 0x4B.
  - The same table applies rEnhancedParamList `ParamId`/`ParamValue` (`0x4dde40`).
  - The first loop of `0x4dd630` sorts the rItemList equip params by the kind ranges of the PS4 DWARF enum
    `rItemList::KIND_TYPE`; the PC ranges are shifted by one.
- Names:
  - `unk_u8` = **EquipParamKind** (I: consumer + enum range).
  - `unk_u16` = **EquipParamValue** (V).
  - The leads EffectID / EffectValue (EmblemStatList) agree in role.

### Crest element: EquipElementParam (V, one I)

- Reader `0x765a90`: u8 -> +4, u32 -> +12, u16 -> +16.
- Item path `0x4fa0d0`:
  - u8 must be 1..4 and selects cCrestParam[u8-1].
  - u32 goes to crest +4; the item lookup `0xb98c80(u32)` writes crest +8. addItemNotice uses the same
    lookup for the CDataItemList ItemId.
  - u16 goes to crest +12.
- Context path `0x84af60..0x84afa6` -> `0x4fa090` does the same, taking the slot from the list position.
- Classes by DTI name: four `cCrestParam` (`dti__796`, 16 B) inside `cCraftParam` (`dti__795`), which sits
  at cItemEquipParam +4. PS4 counterpart: `cCraftParam.mCraftElementItemNo[4]` / `mpElementParam[4]`.
- Consumer of the u16: status calc `0x4dd630` -> `0x4f9be0`, which passes crest +12 to the callback
  `0x4ddaf0`. Its handlers (e.g. `0x4ddb80`) add the u16 to each crest param value.
- Names:
  - `unk_u8` = **SlotNo** (V; part 1 had I).
  - `unk_u32` = **ItemId** (V; part 1 had a proposed I).
  - `unk_u16` = **Add** (I, consumer; lead agrees).

### Pawn info: CDataContextPawnInfo (I, binary hints)

PC copyContextParam_0 (`0x84ab50`) is the counterpart of PS4 `cNetGameServer::copyContextParam_0`
(`0x35bf70`): it calls copyContextParam, then loops the reactions into the auto-motion setter.

- `unk_u8[64]` = **TrainingStatus**, I (binary hint; lead agrees).
  - The 64 bytes are copied as one block (`rep movsd` into the `0x5fd640` object), then pass through
    `0xb14d10` to `0x47b6a0`.
  - Reader `0x772aa0` fills the same object for PAWN_TRAINING_GET_TRAINING_STATUS_RES (handler `0x7ed6d0`,
    named by its `OnPacket_` string), which stores it at pawn data +1964.
  - All 576 captured bytes are 0.
- `unk_List` {u8, u8} = **SpSkillId** / **SpSkillLv**, I (binary hint; lead agrees).
  - copyContextParam_0 takes up to three elements, writes +4 to a[i] and +5 to b[i], then calls
    `0x6042c0` -> `0x473be0` (cContext +8860).
  - The same reader `0x772950` serves PAWN_SP_SKILL_GET_ACTIVE_SKILL_RES (69.0.2, `0x813510`). The group-69
    NTC handler `0x7ec870` builds the same record for `0x6042c0`.
  - Values 2..9 fit the ten `ui/00_common/pspskill/pspskill_000..009` icons. The id/level order rests on the
    lead and the value ranges, not on a reader of +8860.

### Player info: CDataContextPlayerInfo (V, property names)

- Reader `0x75f930` puts the two u32 at +324/+328. copyContextParam copies them (`0x84b174`, `0x84b18f`).
- They are applied at two calls:
  - `0x84c049` (`sub_47bad0`): cContext +14992 = v. A nonzero value on the own player sets bit 0x20 of h+0xE4.
  - `0x84c079` (`sub_478e20`): cContext +14996 |= v.
- createProperty `0x471a50` names both members:
  - `unk_u32_0` = **RoomNo** (`mRoomNo`). Its readers `0xbb12b0`/`0xbb1300` compare it with the own CharId
    (`0x4770b0`, property CharId +8676).
  - `unk_u32_1` = **PlayerStatusFlag** (`mPlayerStatusFlag`).
- Captured values: 0.

### Open with reasons

- `CDataContextSetBase.unk_u32`:
  - Received values go to the context +84 (`0x850010` -> `0x47bc80`). No getter of that member was found,
    and no createProperty table names it.
  - The C2S builder `0x851700` never writes the field, and ctor `0x783220` zeroes it. The client therefore
    always sends 0, which matches all 2,264 captured values.
- `CDataContextSetAdditional.unk_u32[4]` and `CDataContextEnemyStatus.unk_u32[4]`: role I, no name.
  - Both write the enemy-context array cContext +3144 (setter `0x479fd0`, getter `0x475520`).
  - `0xcd5c80` uses element 1 as a bitfield: bit 0 is a state flag, bits 1..4 and 5..8 are two 4-bit timers.
- CharacterBinSaveData `unk_bit_09`, `unk_u8_37`, `unk_bit_96..98` (stOptionData +9/+37/+96..98): no reader
  outside the serializer. The displacement scan of all 151,366 PC functions finds cCharacterData
  +8977/+9005/+9064..9066 only in other classes, and no function returns the option base +8968.
- `unk_bit_13637`: only copy `0x465700`, deserialize `0x466560` and serialize `0x467790` touch it;
  `0x14f50f0` is another class.
- `unk_u32_13572` and `unk_u32_13508`: only init, copy, deserialize and serialize touch them. The part 1
  result was re-checked for +13572: `0xe78e60` stores a vtable at that offset of another class.

### Method notes

- The displacement/immediate index of all PC functions was rebuilt: 151,366 functions in 42 s.
- Word-access scans looked for reads of the enhance ctrl +14/+16.
- IDA does not make some consumers into functions: copyContextParam is cut at `0x84aeaf`, and `0x4ddaf0`
  starts with data. Those parts were read as disassembly. Missing decompiler output there is a coverage gap,
  not negative evidence.

### Next field

None remains in this scope. Two leads for a later pass:
- a reader of the enhance ctrl +14/+16 (`unk_u16_1`), likely in the uGUIEquipEnhance code;
- a reader of cContext +8860, to fix the SpSkill id/level order.

## Part 4 (2026-11-02, T014b4): Quest, Login, Server, GP, Stamp, nNetMsg, QUEST/LOBBY/STAMP/GP patterns

Builds and databases: PC 03040008 private copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t014b4/2022_01_29_DDO_DUMP_FIX.exe.i64`
(32-bit, image base 0x400000, checked with `idc.get_idb_path()`); PS4 02020005 private copy
`D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t014b4/DDOORBIS.elf.i64` (64-bit,
base 0). Both read-only; SHA-256 of the copies not computed (not run). All addresses are VAs. Row updates
are applied by `T014b4-upd.py` from `T014b4-updates.json` (only rows still `open` change). A
displacement/immediate index of all PC functions was rebuilt (45 s) for consumer searches.

### Server.hexpat: CDataGameSetting tail (packet kept at conn+392, getter `0x86c6b0`)

- Handler `0x7f9070` (OnPacket_SERVER_GET_GAME_SETTING_RES) copies most members into sGame.
- `CDataGameSetting_unk_0` {u32, u32} = **WalletType** / **MaxValue** (V flow, names I, lead agrees):
  `0xb61880` stores the value per type 1..16 at sGame +14768; the getter `0xb5f590(type)` is compared with
  the owned amount `sItemManager 0xb997b0(type)` (`0x67cd40`, `0x6556a0`, `0xf18d20`).
- `CDataGameSetting_unk_1.unk_u8` = **Type** (V role) and `CDataGameSetting_unk_2` {u8, u32} = **Level** (V) /
  **Exp** (V role, I name): `0xb5f420(level, type)` picks the type element, then returns the u32 of the inner
  element whose u8 == level+1.
- `unk_u16` (150): I role only, stored at sGame +14566 and used by uGUIEntryBoardSearch (`0xe34b90`,
  `0xdf7fd0`) as the upper bound of a range slider beside JobLevelMax.
- `unk_u32_1` (10000): I role only, denominator of a three-step gauge in `0x62e4c0` (0.33 / 0.66).
- `unk_bool`: copied to conn-owner +41814, no reader (open). `unk_u32_0`, `unk_u32_2`: no reader in the
  handler or the getter's callers (open).

### Quest.hexpat

- `CDataQuestTalkInfo.unk_u32` = **QuestId** (V): the PC setTaskParam variants (`0x9d2ce0`, `0x9d32f0`,
  `0x9d41d0`; PS4 `0x54d850`, `0x54e0e0`, `0x54e4d0`) wrap element +4 in `nQuest::QUEST_ID` and pass it to
  addTalkData `0x9ce880` (PS4 `cQuestPersonalData::addTalkData` `0x54f100`), which stores it in a new
  `nQuest::cTalkData` member (+24). The weak T014a candidate QuestId agrees.
- `CDataQuestDeliveryItem.unk_u16_0` / `unk_u16_1` = **MsgTagKey0** / **MsgTagKey1** (V role, I name). setTaskParam
  `0x9d2ce0` copies the element into `cQuestTask::cDeliveryItemInfo` (DTI `dti__55`; PS4 has only mItemId and
  mItemNum) at +12/+16. `0x9cf870` / `0x9cf8b0` find the entry whose pair equals the two numbers of the message
  tag `<QDEL NAME a b>` / `<QDEL NUM a b>` (`sGUIExt::analyzeTagExtend` `0xb688e0`; e.g. quest q22018013
  `<QDEL NUM 0 3>`) and return ItemId / Num. The server lead NeedNum is contradicted.
- `CDataTimeGainQuestList` and `CDataTimeGainQuestList_unk_0` (packet END_CONTENTS_GROUP kept at conn+484,
  getter `0x86b090`, consumer `0xed89f0`, texts from `ui/.../Quest_res.gmd.json`):
  - `unk_bool_1` = **IsEquipRestriction** (V; Quest_res 0x90 "Equipment restrictions"). The PS4-position name
    IsJoinCharacter is contradicted.
  - `unk_bool_2` / `unk_bool_3`: I role only, bits 1/2 of a party-join mode read beside JoinPawnNum.
  - `unk_bool_0`, `unk_bool_4`: open (no reader among the getter's 17 callers).
  - `unk_0.unk_bool_0` = **IsNoEquipArmor** (0x92 "Armor cannot be equipped."), `unk_0.unk_bool_1` =
    **IsNoEquipJewelry** (0x93), `unk_0.unk_u32_list` = **NoEquipAbilityList** (0x94, names via `0xb772b0`), all V.
  - `CDataQuestUnkU32U16` = **ItemId** / **Num** (I): a list with its layout at quest object +112 is printed
    with 0xB1 "%s x%d (Have: %d)"; the copy into that object was not traced.
- `CDataQuestExp.unk_u8`: open; no setTaskParam variant reads the BaseExp list.
- `CDataQuestUnkU32U32` (FORT_DEFENSE): open; the packet becomes a `cQuestSvNotCycle01Phase` notice and no
  reader was reached.

### Login.hexpat: CDataEquipItemInfo (`0xb959c0`, called by addItemNotice `0xb941e0`)

- `unk_u8_1` = **EquipType** (V): 1 for item StorageType 14/15, 2 for 16/17; it selects the performance or
  visual list.
- `unk_u16` = **EquipSlot** (V copy of the item SlotNo, CDataItemList +18; I name).
- `unk_u8_0`: V copy of CDataItemList.unk_u8 (item +16), itself unnamed.

### QUEST, LOBBY, STAMP, GP pattern files

- REWARD_BOX_LIST_NUM_NTC `unk_u16_0` / `unk_u16_1` = **RewardItemSlotNum** / **RewardItemSlotMax** (V; handler
  `0x7f4e10` announces system_log 300 "item slots ... full" at >= and 301 "running low" at 80 %). The T014a
  medium candidate StageNo is rejected.
- LOBBY_CHAT_MSG REQ `unk_u8` / `unk_u32_0` / `unk_u32_1` = **MessageFlavor** / **PhrasesCategory** /
  **PhrasesIndex** (V role, lead agrees): `0xb291b0` sends (0,0,0) for typed chat, (1, category+1, index) from
  the preset-phrase path `0xb29160` / `0xb76030`, kind 3 from `0x588b80`. NTC: I, same triple.
- AREA_BONUS `unk_u16`: the consumer `0xbd4e40` reads only the first four u16, so the Season 3 u16 is the
  fifth (V position); name open.
- CYCLE_CONTENTS_NEWS: `CDataCycleContentsRank.unk_u32` / `unk_u8` are dropped by the consumer `0xbd53e0`
  (open; the T014a medium StageNo candidate is not confirmed). `CDataCycleContentsUnk` s64 pair: V copy into
  an nQuest object (+16/+24), name open.
- JOIN_LOBBY `CDataQuestJoinLobbyUnkOrderList` (element +384/+388): open; the medium StageNo candidate is
  unconfirmed.
- GP lineup: the packet getter `0x86be20` has no code xref (callers sit in undefined code). The BUY_REQ
  writer `0x829f00` has no caller. STAMP handlers are not functions. All stay open with that reason.
- nNetMsg `CtrlAction` and `GameNormal`, `CDataContentsPlay*`, `CDataQuestContents`, `CDataQuestUnkU32S64`,
  `CDataCycleContentsNoticeData.unk_u64` and the JoinLobby Season 3 lists were not traced. Their values are
  constant or absent in the captures.

### Counts (174 TSV rows in scope, including the rows settled in part 1)

| Verdict | Rows | Distinct struct.field |
| --- | --- | --- |
| V | 72 | 27 |
| I | 39 | 20 |
| open, with the reason in the TSV | 63 | 53 |

Not run: SHA-256 of the private copies; a raw byte scan for calls into the undefined handlers (GP, STAMP,
PLAY_END, LOBBY NTC).

### Next field

`CDataQuestJoinLobbyUnkOrderList.unk_u32` (JOIN_LOBBY row 7, element +384, T014a medium). Find the consumer of
the `cQuestSvNotJoinLobbyQuestInfo` notice (dti__1502) and follow packet +136.

## Part 5 (2026-11-02, T014b5): remaining includes and patterns, and the rows left "not traced"

Builds and databases: PC 03040008 private copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t014b5/2022_01_29_DDO_DUMP_FIX.exe.i64`
(32-bit, image base 0x400000, checked with `idc.get_idb_path()`); PS4 02020005 private copy
`D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t014b5/DDOORBIS.elf.i64` (64-bit,
base 0). Both read-only; SHA-256 of the copies not computed (not run). All addresses are VAs. Rows are
updated by `T014b4-upd.py` from `T014b5-*.json` (one file per include; only rows still `open` change). A
displacement/immediate index of all PC functions was rebuilt (39 s).

### Shop.hexpat and 20.0.2 SHOP_GET_SHOP_GOODS_LIST_RES

- Path: handler `0x7fa010` keeps the packet at conn+972; the getter `0x86c800` has one caller, the cShop
  receive callback `0xb9f0f0`, which moves the goods element pointers into the cShop at sItemManager +88
  (array +108, data +124) and stores packet +33 at +104. `unk_u8_0` (packet +32) is not copied (open, not read).
- Goods element (V flow; names I, the server leads agree): `unk_u32` = **ItemId** (item-param lookup
  `0xb98c80` in the list builder `0xfccd30`); `unk_u8` = **Stock** (signed char, 255 = -1 = unlimited; buy
  dialog `0xfd05a0` via `0xfcd5a0`, message 0xE in `0xf52d20`); `unk_bool` = **HideIfReqsUnmet** (`0xfccd30`
  lists the entry when it is 0 or `0xfcc020` says all requirements are met); `unk_s64_0` / `unk_s64_1` =
  **SalesPeriodStart** / **SalesPeriodEnd** (`0x5fa060` states 1 not yet, 2 no end, 3 on sale, 4 ended;
  dates printed by `0xf51ac0`).
- Requirement element (reader `0xf50470`, loop `0xf502f0`): `unk_u32_1` = **Condition** (switch 2, 3/6, 4,
  5), `unk_bool_0` = **IsCleared** (met flag: `0xfcc020`, text greyed when 0; lead IgnoreRequirements
  contradicted), `unk_bool_1` = **IsDisplayed** (line shown when != 0; lead HideRequirementDetails has the
  opposite polarity), `unk_u32_2` = **Progress**, `unk_u32_3` = **Param1** (target count), `unk_u32_4` =
  Param2 (id among 15 fixed ids 1001, 1002, 3002.. resolved by `0xbdbaf0`), `unk_u32_5` = Param3 (id resolved
  to a message by `0xb783f0`; the medium GroupId candidate is not confirmed), `unk_s64_0` / `unk_s64_1` =
  **PeriodStart** / **PeriodEnd** (messages 0x11..0x15). `unk_u32_0`, `unk_u32_6`, `unk_u32_7`: open (no reader).
- `S2C_SHOP_GET_SHOP_GOODS_LIST_RES.unk_u8_1` = **WalletType** (V: cShop +104 -> `0x547580` -> uGUIShop
  factory `0x52eba0` -> uGUIShop +2032 -> owned amount `0xb997b0`).

### JOIN_LOBBY_QUEST_INFO_NTC Season 3 lists (rows 6 and 7)

- The notice callback is not a function in the database: the raw byte search for `dti__1502` finds the
  registration at `0xbcefa3` inside the undefined sQuestManagerExt constructor code (`addCallbackFunc` +
  `setCallbackFunc(0xbd73c0)`). `0xbd73c0` (read instruction by instruction, also undefined) hands each
  packet list to the registTask of a quest manager kind: row 6 (+116) to `0x5983a0` (kind 11), row 7 (+136)
  to `0x597160` (kind 12).
- Row 6 = package quests (`dti cPackageQuestManager::cPackageSequence`, ctor `0x597310`):
  `CDataQuestJoinLobbyUnk.unk_u32` = **PackageId** (sequence +4; name I from the class and the resource
  property `rPackageQuestInfo.mPackageId`, PC `0xabe130`); element `unk_u32` = sequence key (+8);
  `unk_s32_0` / `unk_s32_1` = **Progress** / **ProgressMax** (+16 clamped to +12); `unk_u32_list` =
  **ClientNpcList** (one `cClientNpc` per u32). `unk_bool` is not read (open).
- Row 7: per element `0x9d2b00` -> `0x64dc20` stores `unk_u8` / `unk_u32` at task param +404 / +408. No
  reader of those members was found; both stay open and the medium StageNo candidate is not confirmed.

### Stage.hexpat: 12.1.2 AREA_CHANGE_RES Season 3 lists

- Handler `0x7fd690` -> `0x7fd490` copies both lists into the sArea stage object: list 0 by `0x416a20`
  (max 64), list 1 by `0x4169b0`.
- `CDataAreaChangeUnk0`: `unk_u32_0` = **StageNo** (same table lookup `0x84a200` as the RES StageNo; the
  medium candidate is not the basis), `unk_u32_1` = **GroupId** (key `stage | group << 16`; sSetManager
  type 2 add/remove in `0xbfec20`), `unk_u32_2` = second key (role), `unk_u8_1` = state (role: 1 removes;
  63..76 kept by `0x5bd670`), `unk_u8_0` not read (open).
- `CDataAreaChangeUnk1`: `unk_u32` = object id key (`0x40c530` from `0x752f50`), `unk_bool_0` = suppress flag
  (role), `unk_bool_1` not read (open).

### Pawn.hexpat

- `CDataPawnInfo.unk_u8` (u8[64]) = **TrainingStatus**, I: same reader `0x772aa0` as
  PAWN_TRAINING_GET_TRAINING_STATUS_RES (as in part 2 for CDataContextPawnInfo).
- `CDataPawnInfo_unk_0` u32 x5: open. The reader `0x772e80` sits only behind CDataPawnInfo; the packet is
  kept at the pawn entry +88 (`0x881d10`) and no reader of info +504..+520 was found.
- `CDataPawnList.unk_u32_0`: role I, a PawnId -> value table in sGame_0 (`0xbcdac0`, getter `0xbccbd0`,
  threshold >= 2 in `0x9a1940`); `unk_u32_1` / `unk_u32_2` are copied to the pawn entry +100/+104 by
  `0x881da0` with no reader found (open).

### Instance.hexpat: CDataGatheringItemElement (DROP_ITEM_LIST)

- Handler `0x7db2a0` hands the list to sSetManager `0xbfe6e0`, which finds the layout object and calls
  cpOmDropItem `0x995ff0`: it drops ItemId 0x1e73..0x1e75, Num 0 and unknown items, then `0x994560` fills a
  24-byte slot (12 slots) through protected setters (memcpy via obfuscated stubs): +4, +8 ItemId, +12 Num,
  +16 `unk_u32` (`0x995e60`), +20 `unk_bool` (`0x996160`). No reader of slot +16/+20 was found: both open
  (V store).

### 64.0.2 MANDRAGORA_GET_MY_MANDRAGORA_RES (no PS4 counterpart)

- Handler `0x7e4dc0` consumes the packet itself. Each CDataMyMandragora goes to `0x10dbff0`, slot =
  MandragoraId (< 4). It derives a slot state 2..6 from `unk_u32_1`, `unk_u32_2`, `unk_s64` (a time
  compared with now) and UnkState `unk_u32_1` / `unk_s64` (roles V, names open). `unk_u32_0`, `unk_u8`,
  UnkState `unk_u32_0` and the UnkItem pair are copied with no reader found.
- `CDataMyMandragoraUnkU8U32`: kind 5 stores the u32 at manager +1880. Packet `unk_u32` (+188) is stored at
  manager +1904. No reader was found for either.

### Character.hexpat: CDataLobbyMemberInfo.unk_u8

- Element +34 (reader `0x76d7f0`). LOBBY_JOIN handler `0x7e2ce0` -> `0x8814e0` copies each element whole into
  the conn +17880 list. None of the 16 functions using that list reads +34: open (V copy, no reader).

### Method notes (part 5)

- Notice callbacks and handlers that IDA did not make functions were read as raw instructions decoded
  with `ida_ua.decode_insn` (no item created, database unchanged). The `dti__1502` registration was found
  by a raw byte search for the DTI address.
- The cpOmDropItem slot setters are protected stubs (memcpy through obfuscated thunks); their getters were
  not identified.

### Counts (part 5: 60 struct.field pairs updated, 71 TSV rows)

| Verdict | Rows | Distinct struct.field |
| --- | --- | --- |
| V (data flow read; most names I, see the mark) | 33 | 33 |
| I | 2 | 1 |
| open, with the reason in the TSV (no reader found, not read, or V store only) | 36 | 26 |

- T014a candidates decided in part 5: the goods and requirement timestamps (weak) are confirmed; the
  requirement Price and equip-item-id candidates (weak) are rejected; GoodsRequirement.unk_u32_5 GroupId
  (medium), JoinLobbyUnkOrderList.unk_u32 StageNo (medium) and AreaChangeUnk0.unk_u32_0 (medium) are not
  confirmed. AreaChangeUnk0.unk_u32_0 is named StageNo from the code instead.
- **Cut short.** 109 rows (92 struct.field) still carry "consumer not traced" in the TSV: Craft, Dispel,
  EntryBoard, Gacha/BoxGacha, Character list `unk_u8`, the Instance REPOP/gathering lists, the small
  single-pattern rows, the T014b4 leftovers (GP lineup, STAMP, nNetMsg, ContentsPlay*, QuestContents,
  CDataQuestUnkU32*), and the remaining Season 3 rows. Part 5 rows are listed in `T014b5-*.json`.
- Not run: SHA-256 of the private copies; a reader search for the PC pawn-entry members +100/+104; getters of
  the protected cpOmDropItem slots.

### Next field

`CDataCharacterListElement.unk_u8` (L2C_GET_CHARACTER_LIST_RES): the last u8 of reader `0x75ccf0` (element
+52). Find the login character-list handler, then the reader of the copied +52.

## Part 6 (2026-11-02, T014b6): Character list, Craft, Dispel, EntryBoard (cut short)

Builds and databases: PC 03040008 private copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t014b6/2022_01_29_DDO_DUMP_FIX.exe.i64`
(32-bit, image base 0x400000, checked with `idc.get_idb_path()`); PS4 02020005 private copy
`D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t014b6/DDOORBIS.elf.i64` (64-bit,
base 0). Both read-only; SHA-256 of the copies not computed (not run). All addresses are VAs. Rows are
updated by `T014b4-upd.py` from `T014b6-{character,craft,dispel,entryboard}.json` (only rows still `open`
change; two dispel rows re-worded with `force`). A displacement index of all PC functions was rebuilt (29 s).

### Character list: CDataCharacterListElement.unk_u8 = GameMode (10 rows; DECIDE_CHARACTER_ID_RES.unk_u8 too)

- `0xef0ec0` passes element +52 to `0xef0c00`, which colours the row differently when the value is not 0
  and differs from sGame +0x39FC. sGame +0x39FC is the current game mode: `0xb5ff70` accepts a land when
  `rLandInfo::cLandInfo.mGameMode` (+9, PC property table `0xa9ef10`; land looked up by `mLandId` +4 in
  `0xb5f050`) is 0 or equal to it, and `0xb5fd10` / `0xb5fea0` test it for 1 and 2.
- DECIDE_CHARACTER_ID_RES (`0x7c7f20`): when IsReturnPrepare != 0 the trailing u8 is stored in sGame
  +0x39F8 and +0x39FC (copied +0x39F8 -> +0x39FC again in `0x4044b0`). Mark V (compare / store), I (name,
  from the property name). The server's `unk2` "Party type?" does not agree; its GameMode enum (1 Normal,
  2 BitterblackMaze) agrees with the compares. PS4 sGame has no such member (Season 3).

### Craft.hexpat and 30.13.2 CRAFT_GET_CRAFT_SETTING_RES

- Handler `0x7d0bf0` (not a function) keeps the packet at conn sub-object +0x32C (getter `0x86a2c0`, 22
  callers + undefined `0x53243f`) and gives the pawn list to `0x87f610`, which builds pawn entries (the 112-byte
  class that `0x881310` fills from CDataPawnList).
- CDataCraftSettingUnkPawn: `unk_u32_2` = **PawnId** (V: entry +4, lookup key in `0xb37d10`, `0xb397e0`,
  `0xb39c40`), `unk_Name` = **PawnName** (V: entry +12), `unk_u32_3` = **CraftRank** (V role: `0xb39c40` kind 3
  returns it where kinds 1/2 return pawn entry +52, the member PS4 `sCraftManager::getPawnRank` `0x761ac0`
  returns; I name), `unk_u8` = **WalletType** and `unk_u32_1` = **Price** (V role: `0xb397e0` sums +12 *
  create count when +8 == 5; `0xe02a20` compares count * +12 with the owned amount of wallet 5, `0xb997b0`;
  I names). `unk_u32_0`: open, no reader.
- CDataCraftSettingUnkElement (packet +108): `unk_u32_0` = **ItemId** (V: `0xb3d310`, `0xb3aca0`,
  `0xb3ad60`). The other u32 pairs are rate/cap pairs (V role: `+8 * itemParam vfunc+80` capped at +12;
  `+16 * ...` capped at +20); `unk_bool` lets a listed item past its level cap (`0xb3d310`). Names open.
- Packet `unk_u32_0` / `unk_u32_1` (+100/+104): open, no reader among the getter callers.
- CDataCraftProgress (progress list, packet conn +0x320, getter `0x86c670`, 27 callers): `unk_u32_list` =
  pawn ids printed by name after the support pawns in `0xe03c80` (`0xb79e30`, pawn id -> name); proposed
  **LegendPawnIdList** (V role, I name). `unk_u16` (+76) is passed to `0xdfe5c0`, which does not use it: open.
- CDataMDataCraftMaterial.unk_bool: open, not read (`0xb3ff00` sorts by SortNo `0xb414c0` and copies
  ItemId/Num only).

### Dispel (51.0.2, 51.2.1, 51.2.2)

- ITEM_LIST_RES packet at conn +0x4A8 (getter `0x86ab90`, one caller, the sorter `0xe8e420`).
  `CDataDispelBaseItem.unk_u16_0` = **ExchangeLimit**, `unk_u16_1` = **ExchangeCount** (V role: `0xe94d40`
  prints limit - count; `0xe93760` disables the entry at the limit; `0xe8e2e0` sets the count from
  DISPEL_EXCHANGE_DISPEL_ITEM_RES, conn +0x4AC, reader `0x8067b0`; I names). `unk_u32` is a second key with
  Id in that match (V role). `CDataDispelLotItem.unk_u8` and `CDataDispelLotCrest.unk_u8_0` are the first
  (descending) sort keys of the lot and crest sorters `0xe957d0` / `0xe95760` (V role).
- Open with reason: LotItem `unk_bool`, LotCrest `unk_u8_1`, the CrestUnk list (not read on the dispel list
  path; a full reader scan was not run), SETTING_RES `unk_bool` (its two consumers read the list only).
  SETTING_REQ `unk_u32` is the dispel UI byte +2012 (`0xe905b0` -> `0x86ac30` -> `0x826750`); meaning open.

### EntryBoard.hexpat

- `CDataEntryRecruitData.unk_u32` (3 rows): copied by `0xa2a050` / `0x585600`; `0x4e5890` (uGUIEntryBoard)
  sums it over the recruit slots and shows the sum via `0xe18db0`; V role (per-slot amount), name open.
- `CDataEntryMemberData.unk_u32`: copied to the member copy +8 (`0xa2aa80`), no reader identified: open.
- `CDataEntryItem.unk_bool`: not read by the copy `0xa2a050` nor by the ITEM_LIST_RES getter callers: open.
- `CDataEntryBoardItemSearchParameter.unk_u32_0/1`: the search object at conn +0x4748 is never written at
  +60/+64 (no displacement or raw-byte hit for +0x4784/+0x4788): open, constant.

### T014a candidates in these rows

All are weak; none is confirmed. The craft-pawn candidates (party-quest progress values, GP course
params) are not confirmed: the code gives the roles above; the character-list row had no candidate.

### Counts (part 6: 35 struct.field pairs, 49 TSV rows)

| Verdict | Rows | Distinct struct.field |
| --- | --- | --- |
| V (flow or role read; names I where marked) | 32 | 21 |
| I only | 0 | 0 |
| open, with a concrete reason (no reader, not read, never written, passed and unused) | 17 | 14 |

- **Cut short** (tool-call budget): 60 TSV rows (57 struct.field) still carry "not traced": Gacha/BoxGacha,
  Instance (REPOP enemy-info bool at element +34 of `0x77a1b0`; gathering lists), Stage attributes, STAMP,
  nNetMsg, ContentsPlay*, QuestContents, CDataQuestUnkU32*, CDataCycleContentsNoticeData, GP course, and the
  single-pattern rows (C2S INSTANCE/SKILL/MAIL/ITEM_SORT/PENALTY, GROUP_CHAT, MY_ROOM, PAWN_EXPEDITION,
  PLAY_END, AREA spot list).
- Partial leads: GACHA_LIST_RES packet conn +0x460 (getter `0x86c250`), BOX_GACHA_LIST_RES conn +0x468
  (getter `0x869100`); their 12 UI callers (`0xd9df40`..`0xda6410`) read the settlement elements, e.g.
  `0xd9fef0` reads box settlement +4..+40. For the enemy-info bool, the byte-offset scan +0x1d..+0x22 gives 9
  functions; `0xbf11e0`, `0xbef510`, `0x9fec20` are not the consumer.
- Not run: SHA-256 of the private copies; a full reader scan for the CrestUnk list.

### Next field

`CDataGachaSettlementInfo.unk_u32` (element `0x768830`, +36): map the settlement element offsets in
`0xd9fef0` / `0xda2620` (box: element reader `0x75ade0`) and find the reader of +36.

## Part 7 (2026-11-02, T014b7): the last rows left "not traced"

Builds and databases: PC 03040008 private copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t014b7/2022_01_29_DDO_DUMP_FIX.exe.i64`
(32-bit, image base 0x400000, checked with `idc.get_idb_path()`); PS4 02020005 private copy
`D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t014b7/DDOORBIS.elf.i64` (64-bit,
base 0). Both read-only; SHA-256 of the copies not computed (not run). All addresses are VAs. Rows are
updated by `T014b4-upd.py` from `T014b7-<include>.json` (only rows still `open` change).

### Gacha and BoxGacha (39.x, 40.x LIST_RES)

- `CDataGachaSettlementInfo.unk_u32` (+36) and `CDataBoxGachaSettlementInfo.unk_u32` (+40) = **ChargeId** (V flow,
  I name). `0xd9fef0` copies each settlement into a price slot (`0xda2f00`, slot +128/+140); `0xda5f90` passes
  the slot value to `0xd9df40` as `chargeId` of `sGame::isChargeEffect` (bit 0x100: GP course effect not
  active), and `0xda55f0` labels the price "Service Benefit (GG) x%d" / "Service Benefit (Free)" (gacha_res
  0x64 / 0x60) when it is non-zero. PS4 `sGame::isChargeEffect` `0x7854a0` names the argument
  `chargeId` (`nGpCourse::E_GP_COURSE_EFFECT`).
- `CDataBoxGachaInfo.unk_bool` (+24): open, not read (no byte read of +0x18 in the 19 getter call sites of
  `0x869100` or elsewhere in the gacha UI range 0xd9c000-0xdab000).

### Instance (13.x): enemy info, gathering, C2S requests (`T014b7-instance.json`, drop row in `T014b7-stage.json`)

- `CDataStageLayoutEnemyPresetEnemyInfoClient.unk_bool` (element +34, 2 rows): **V (role)**. Both ENEMY_SET_LIST
  (`0x7db4c0` -> `0xbfe8a0` -> `0xaa7330`) and REPOP (`0xaa6cb0`) copy the info into the 80-byte set object
  (dti__5393, `0xaa3050`) at +8; `0x752540` copies set +41 (IsBloodEnemy) to enemy record +489 and +42 (this) to
  +490. `0xc405c0` reads +490; `0xf11f20` returns enemy gauge kind 2 for it (1 for IsBloodEnemy), and `0x4d11a0`
  runs a separate effect for it. A second special-enemy kind beside IsBloodEnemy; the server lead IsHighOrbEnemy
  fits but no client string names it, so the name stays `unk_bool`.
- GATHERING_ITEM_LIST_RES: `unk_bool` is stored at conn +0x9E74 (`0x880b30`) and never read (raw displacement
  search: writers `0x880b91`, `0x846e72` only). The restriction list (+0x34, `GatheringItemListRes_unk_0/1`) is
  passed only as an unused argument of `0xbfe9d0`: not read (3 rows open).
- C2S GET_GATHERING_ITEM_REQ: the request record (`0xb91260`: +16 PosId, +20, +24) is registered by the undefined
  `0xb627d0` and sent by the callback `0xb93fb0`. `unk_u32` (+20) is the element +4 of the first entry of the
  cpOmGather list +528 (`0xf00d90`, V source, name open). `unk_bool` (+24) has no writer found (open); after the
  send it selects request +66 = 75 or 1. GET_DROP_ITEM_REQ `unk_bool` has the same shape (`0xb93ead`, 0x4C or 1;
  open).
- ENEMY_KILL_REQ `unk_bool`: `0xbfd900` sends 1 unless a living member slot passes `0x478d40` / `0x475c50`;
  the decompiled `0x475c50` returns 0, so the value is 1 (I).
- BAD_STATUS START/END: `unk_zero` is the constant 0 (V source); `unk_u32` is +0x30 of the record at enemy +0x1B50
  (`0x4d9e70`, protected copy thunk), not the enemy set object: open.

### Stage attributes (`T014b7-stage.json`)

- `CDataStageAttribute.unk_bool_0` / `unk_bool_1`: copied by `0x883d30` / `0x7a6030` into the stage table at conn
  +0x9E44 (entry +33 / +34). The 27 functions that address the table read +8, +26 (`0x875ca0`) and +28
  (`0x875c50`) only: open (stored, no reader).

### Stamp (`T014b7-stamp.json`)

- GET_LIST handler `0x7fe140` (read by instruction) keeps the packet at conn sub +0x478 (getter `0x871bd0`,
  caller `0xebcaf0`). `CDataStampBonus.unk_u32` (and the StampBonusTotal row) is the bonus kind: when it is 1,
  bonus +8 is mapped by `0xebb610` (1..5 -> 7789, 7792, 7795, 10682, 10664), else shown as is; +12 is the
  amount (V role). The pattern's PS4-position names BonusType (+8) / BonusValue (+12) do not fit this code (I).
- `CDataStampBonusDailyGroup.unk_u32_0` is the group key matched with UI +0x25A8; CHECK_RES (`0x65cbd0`, getter
  `0x871bc0`) stores element +4 / +8 (`CDataStampBonusCheckRes_unk_0.unk_u32_0` / `unk_u32_1`) at UI +0x25A8 /
  +0x25AC, which `0x8785c0` (request 561) sends (V role / V flow). `DailyGroup.unk_u32_1` is not read (open).

### nNetMsg (`T014b7-nnetmsg.json`)

- `CtrlAction.unk_0x3C` (and the PARTY_SEND_BINARY_MSG_NTC Data row) / `unk_0x3D`: the cContext +0xC48 4-slot
  work array (setter `0x479fd0`, getter `0x475520` used by enemy code `0xccddc0`, `0xcd5c80` and others); V flow,
  role I, name open.
- `GameNormal` 0x0F `unk_u32` / `unk_uid_0` / `unk_uid_1`: receive `0x894bf0` adds {u32, uid, uid} to the
  sEnemyManager +0xDB0 block (`0x4d3060`); `0x5a12b0` queries it by a pair of character UIDs (`0x4d2fd0`) to start
  action 3. V flow, role I, names open.

### Single-pattern rows (`T014b7-single.json`)

- GROUP_CHAT GET_MEMBER_LIST `unk_serverResult` / `unk_serverListCount`: open, never read (the reader `0x809d80`
  stops after a non-zero Error).
- AREA_GET_SPOT_INFO_LIST `unk_list_2`: `0xd40fd0` sets UI spot entry +85 when the spot id is in the list (V flow);
  no reader of +85 found.
- `CDataMyRoomOption.unk_u32` (+0x1C): not read by the copy `0x10db890` (open; a wider reader search not run).

### T014a candidates in these rows

All are weak; none is confirmed. GROUP_CHAT `unk_serverResult` (ErrorID) is never read by the client; the stamp
check `unk_u32_1` (GP EffectUID) is the value paired with the daily group key; BAD_STATUS `unk_u32` (mCommonWork)
stays unresolved.

### Counts (part 7: 34 struct.field pairs, 35 TSV rows)

| Verdict | Rows | Distinct struct.field |
| --- | --- | --- |
| V (flow, source or role read; names I where marked) | 20 | 19 |
| I only | 0 | 0 |
| open, with a concrete reason (not read, stored without reader, never read, source or record not found) | 15 | 15 |

- **Cut short** (tool-call budget): 25 TSV rows (23 struct.field) still carry "not traced": PENALTY_REVIVE,
  MAIL GET_ALL_ITEM, SKILL ACQUIRABLE x2, ITEM_SORT, PAWN_EXPEDITION `unk_bool`, PLAY_END `unk_s32`,
  `CDataContentsPlayEnd` x3, `CDataContentsPlayStartData` x4, `CDataQuestContents` x2 (4 rows),
  `CDataQuestUnkU32Bool` x2, `CDataQuestUnkU32S64` x2, `CDataQuestUnkU32U32.unk_u32_0` (and its `unk_u32_1` row),
  `CDataCycleContentsNoticeData.unk_u64`, `CDataGPCourseValid.unk_MtString`.
- Leads: the PAWN_EXPEDITION packet is kept at conn +1216 (`0x7ea150`); the C2S writers are reached through
  `cSeedGameSvConnection::Send_*` callers as in the instance rows.
- Not run: SHA-256 of the private copies; a reader scan for UI spot entry +85 outside 0xd30000-0xd50000; a reader
  search for MyRoomOption +0x1C beyond `0x10db890`.

### Next field

`CDataContentsPlayStartData.unk_bool_0` (TIME_GAIN_QUEST_PLAY_START_NTC, reader `0x75f030`, caller `0x7f5830`):
follow the notice object from `0x7f5830` to its consumer.
