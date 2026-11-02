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
