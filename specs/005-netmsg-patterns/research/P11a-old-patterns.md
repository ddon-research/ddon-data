# P11a: evidence for the old packet patterns, batch A (18 packets)

Brief: `specs/005-netmsg-patterns/briefs/P11-old-patterns-evidence.md` (committed at 007e296a9d), batch A.
Base c748cd3a53. This report edits nothing; it lists what P12 must fix.

## What ran

- PC 03040008 (Season 3 truth): private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-p11a/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (`bash research/ida/private-copy.sh pc p11a`), ida-mcp instance `661d2ba72f83`; `idc.get_idb_path()`
  returned that path, 32-bit, image base `0x400000`.
- PS4 02020005 (seed, symbols): private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-p11a/DDOORBIS.elf.i64`
  (`... ps4 p11a`), instance `1666a225af03`; 64-bit, image base `0`. PS4 DWARF types and enums read
  through `ida_typeinf` in this database (no `*.elf.c/.h`).
- Read-only: Hex-Rays, `ida_ua` decode of undefined bytes, xrefs, byte search. No rename, retype,
  comment, function creation or save.
- Address basis: IDA VA in each database. PC `sub_`/`loc_` names are IDA defaults. Some PC functions
  carry earlier user names (`nUserSession::CPacket_S2C_GET_STAGE_LIST_RES::ReadPacket`,
  `nPacket::Read_CDataMyMandragora*`, `nPacket::Read_CDataQuestEnemyInfo_`, ...) of unknown provenance:
  cited as names only, never as evidence.
- Marks: **V** = read in IDA (PC unless "PS4"); **I** = inferred; **C** = contradicts the pattern or a
  source named in the row; **PC-cap** = from 03040008 captures only; **unresolved**.
- Method (PC). S2C: the packet's RES handler is found from its PC name string
  `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>` (pushed to `callOnPacketFunc`); NTCs and the one
  RES whose string xref IDA missed come from the static handler tables (entry = handler, 8 zero bytes,
  key `(sub<<16)|id` at +0x10, as P4): group 11 initializer `0x1a32060` (146 entries), group 23
  initializer `0x1a27840` (16 entries). Every packet's group/id/sub is **V** from the immediates its
  handler or packet constructor stores (`+4` group, `+6` id, `+8` sub). The reader is the function the
  handler calls with `(packetObj, CPacket*)`; its wire order is the order of `nPacket::Read_*` calls,
  traced recursively. C2S: the writers come from the 658 `nUserSession::CPacket::WritePacket`
  (`0x8bcbb0`) call sites by the pushed `(packet, group, id, sub, -1)`.
- PS4 counterparts are matched **by code** (reader body: same sequence of reads and the same nested
  list shapes; handler behaviour), never by packet number. Their names then come from PS4 symbols and
  DWARF types.
- Captures: every `packets/decrypted_raw/*/*.<g>_<id>_<sub>` file of the 18 suffixes (1,053 files),
  walked in the ida-mcp Python session (no repo tooling) with the PC reader layouts. Framing as P4
  section 1: body from file offset 9; "ok" = no read past the end and slack (file size - end) in
  0..15. Also walked: the pattern's own layout where it differs from the PC reader.
- Server (`D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline`, Arrowgene.Ddon.Shared/Entity) opened only
  for the disputed structures; lead, never evidence.

## Common findings (all 18 patterns)

| # | Finding | Evidence | Mark |
| --- | --- | --- | --- |
| G1 | **RES header**: all 16 S2C RES patterns declare `u32 Error; s32 Result;` unconditionally. The PC readers read `s32 Error`, and read `s32 Result` and the body **only if Error == 0**; otherwise they copy Error into Result and stop (e.g. `0x815ba0`, `0x80f730`, `0x81cc40`). Fix: use `ResHeader` from `include/Packet.hexpat` and guard the body with `Error == 0`. | PC readers | V |
| G2 | No capture of the batch has Error != 0 (0 of 1,053), so G1 is never exercised by the captures. | walk | PC-cap |
| G3 | **NTCs have no error field on PC**: 11.89.16 (`0x817340`) starts with its first list, 11.120.16 (`0x817940`) with a u32. PS4 has `u16 m_usError` in every packet class (DWARF) and its RES `u16 m_usError, s32 m_nResult`: that is PS4 framing, not the PC wire. | PC readers; PS4 DWARF | V |
| G4 | None of the 18 patterns imports `include/Packet.hexpat`: each redefines `CPacket`, `MtTypedArray`, and (where used) `MtString` locally (as `strLen`/`string`). | pattern text | V |
| G5 | List counts are u32 everywhere (every list reader starts with `nPacket::Read_u32` into the count); `MtString` is u16 BE length + bytes (`nPacket::Read_MtString` `0x8bc5b0`, P4). The patterns' `MtTypedArray<T>{u32 ...}` and string layouts are right. | PC readers | V |
| G6 | Enums not from DWARF (see per pattern): `WalletType` (server names; PS4 DWARF is `nCharacter::E_WALLET_POINT_TYPE`, values 1-8 named `WALLET_POINT_TYPE_GOLD, _RIM, _ORB, _TICKET, _GP, _SUPPORT, _JP_RESET, _CP_RESET`; the pattern's 9-0x10 have no DWARF source); `ExpType` and `QUEST_ANNOUNCE_TYPE` (no PS4 DWARF enum of these names or members found); `CYCLE_CONTENTS_SUB_CATEGORY` values 1005-1009 and 3007 are absent from PS4 DWARF `nQuest::CYCLE_CONTENTS_SUB_CATEGORY`. Enums that do match DWARF: `COMMAND_CHECK_LIST` (`nQuestScript::COMMAND_CHECK_LIST`, all 210 values equal; the pattern omits only the sentinels `COMMAND_CHECK` 0, `_END`, `_NUM`), `ORDER_CONDITION_TYPE`, `CYCLE_CONTENTS_TYPE`, `CYCLE_CONTENTS_CATEGORY` (`nQuest::`). | PS4 `ida_typeinf` | V |

## Per pattern

Each section: (1) status; (2) PC reader/writer and how found; (3) wire table and PS4 counterpart;
(4) errors and gaps; (5) shared structures; (6) capture walk; (7) raw name. "R." = `nPacket::Read_`.

### 1. S2C_JOIN_LOBBY_QUEST_INFO_NOTICE (11.89.16)

1. Status: **partial** (finished in shape; S3 fields still `Unk*`; three layout errors in structures
   the captures never fill). V
2. Handler `0x7f2a20` (bytes not a function; group-11 table key 16/89), packet ctor `0x78bda0`
   (11, 89, 16), reader **`0x817340`**. The handler pushes a notice whose DTI `dti__1502` is
   initialised with the PC string **"cQuestSvNotJoinLobbyQuestInfo"** (`0x1a13bad`), the same class PS4
   `OnPacket_S2C_JOIN_LOBBY_QUEST_INFO_NOTICE` `0x2eb770` creates. V
3. Wire (PC `0x817340`), each a u32-count list unless noted. V

   | # | PC reader | Element | PS4 (`CPacket_S2C_JOIN_LOBBY_QUEST_INFO_NOTICE::ReadPacket` `0x19d62c0`) |
   | --- | --- | --- | --- |
   | 1 | `0x76d350` | QuestOrderList + **7 x u32** (`0x76d1c0`) | m_LightQuestOrderList; CDataLightQuestDetail has **6** u32 |
   | 2 | `0x7785f0` | u32, QuestOrderList, SetQuestDetail (`0x778040`) | m_SetQuestOrderList |
   | 3 | `0x76eb40` | QuestOrderList | m_MainQuestOrderList |
   | 4 | `0x77b790` | QuestOrderList, u8 | m_TutorialQuestOrderList |
   | 5 | `0x76dc20` | QuestOrderList, u8 | m_LotQuestOrderList |
   | 6 | `0x7709a0` | u32, list(`0x770b90`) of {u32, s32, s32, list u32 (`0x75e8e0`), bool, list QuestOrderList (`0x770ab0`)} | none (S3) |
   | 7 | `0x76efd0` | QuestOrderList, u32, u8 | none (S3) |
   | 8 | `0x77b2a0` | QuestOrderList | m_TimeLimitedQuestOrderList |
   | 9 | `0x77ce60` | QuestOrderList, u8 | m_WorldManageQuestOrderList |
   | 10 | `0x766a00` | u32, u32 | m_ExpiredQuestList |
   | 11, 12 | `0x773f80` | u32 | m_MainQuestIdList, m_TutorialQuestIdList |
   | 13 | `0x7735b0` | u32, u32, list u32 (`0x773820`), list ProgressWork (`0x7754a0`) | m_PriorityQuestList |
   | 14 | `0x7592d0` | u32, u32 | m_AreaRankList |
   | 15 | `0x773d30` (struct) | u8, u8, u8, u16 | m_QuestDefine |

   PS4 match by code: same list types in the same order, minus PC rows 6-7; same QuestDefine. V (PS4)
   CDataQuestOrderList, PC `0x774a70` (V): u32 KeyId, u32 QuestScheduleId, u32 QuestId, u32 AreaId,
   u32 BaseLevel, u16 ContentJoinItemRank, list WalletPoint {u8, u32} (`0x77c5a0`), list QuestExp
   {u8, u8, u32} (`0x76c780`), **3 x u32, 3 x u64**, list RewardItem {u32, u16} (`0x7771b0`) x 2,
   list u32 (`0x75eec0`), QuestLog (`0x774850`: list u32 `0x773820`, list {u32, u32, u16, bool}
   `0x7757e0`), list u32 (`0x773eb0`), list u32 (`0x774350`), list QuestProcessState (`0x775310`),
   list {u32, s32, s32} (`0x774890`), list QuestEnemyInfo {u32, u32, u16, bool} (`0x773d90`),
   list {u32, list {u32, u32}} (`0x774420`), list {u32, s64} (`0x775900`), list {u32, u16, u16, u16}
   (`0x762fb0`), bool, bool, bool. QuestProcessState element `0x775420`: u16, u16, u16, list
   {u32, s32 x 4} (`0x7754a0`), list of lists (`0x757f20` → `0x7738f0`) {u16, s32 x 4}, list
   {u16, s32 x 4} (`0x7738f0`). PS4 `CDataQuestOrderList` (DWARF) has u32 BaseGold/BaseExp/BaseRim
   instead of the two lists, 3 u32 (OrderNpcId, NameMsgId, DetailMsgId) + 2 u64 (OrderDate,
   EndDistributionDate), EnemyInfo/TalkInfo without the leading u32, and no u32 list, {u32,s64} list
   or delivered-item list. V (PS4)
4. Errors / gaps:
   - **CDataLightQuestDetail: 6 x u32, PC reads 7** (`0x76d1c0`). Which of the 7 is new: unresolved
     (PS4 DWARF has 6; server order AreaId, BoardId, GetAp, GetCp, ... is a lead). V
   - **CDataSetQuestDetail uses the PS4 layout** (u32 x4, u16 x5, u8 x5, bool). PC `0x778040`: u32 x4,
     **list WalletPoint, list QuestExp**, u16, u16, u8 x5, bool. V (C)
   - **CDataQuestOrderList `u32 Unknown1; u32 Unknown2;` before OrderDate is one u64 on PC**: the reader
     reads 3 u32 then 3 u64 (`0x774b0c`-`0x774b75`). Same size, wrong type. Which of the three u64 is
     the Season 3 one is unresolved (the pattern's naming of the last two as OrderDate /
     EndDistributionDate is I). V
   - Signedness: `CDataUnknown.unknown2` u64, PC `R.s64` (`0x775900`). V
   - Dead code: `CDataQuestList`, `CDataSetQuestList`, `CDataDeliveryItem` are defined but unused. V
   - Enums `WalletType`, `ExpType`, `QUEST_ANNOUNCE_TYPE` not from DWARF (G6). V
   - Rows 6-7 and many S3 fields are `Unk*`: names unresolved (no PS4 counterpart, no PC string).
5. Shared: QuestOrderList `0x774a70` (also 11.71.2, 11.120.16), QuestProcessState `0x775310`,
   WalletPoint `0x77c5a0`, QuestExp `0x76c780`, RewardItem `0x7771b0`, QuestEnemyInfo `0x773d90`,
   CommonU32 `0x75e8e0`, ProgressWork `0x7754a0`.
6. Walk: 41/41 ok with the PC layout; **41/41 also ok with the pattern's layout** because lists 1, 2,
   3, 5, 6 and 8 are empty in every capture (non-empty: 4 in 21 files, 7 in 20, 9 in 1; 10-14 always).
   The LightQuestDetail and SetQuestDetail errors are therefore not exercised. One walk (PC-cap):
   `stream1-marked.pcapng_tcp-stream-35/12006_S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC_...11_89_16`
   (22,224 B, SHA-256 prefix `7bb6d7d3148f516b`): lists 1-8 empty at 0x9-0x29; list 9 n=33
   0x29→0x55bf; 10 n=0; 11 n=5 →0x55db; 12 n=9 →0x5603; 13 n=0; 14 n=24 →0x56cb; QuestDefine
   0x0a, 0x0a, 0x64, u16 0x1e; end 0x56d0, slack 0.
7. Raw name: `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC` (pattern file name differs).

### 2. S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES (64.0.2)

1. Status: **partial** (layout right; almost every name `Unk*`/`Maybe`). V
2. Handler `0x7e4dc0` (name string `0x1bd39d8` "…OnPacket_MANDRAGORA_GET_MY_MANDRAGORA_RES"),
   ctor `0x78a2d0` (64, id 0, 2), reader `0x80f730`. V
3. Wire (V): RES; list {u32, u32} (`0x75bcd0`); list (`0x75bb10`) of {u32, u8, u32, MtString, u32,
   s64, u32, {u32, u32, list {u32, u16} (`0x75b360`), s64} (`0x75bc70`)}; list {u8, MtString}
   (`0x75b690`); list {u8, u32} (`0x75b270`); list {u32, u32} (`0x75b870`); u32; list {u32, MtString,
   u32} (`0x75b160`); list {u32, MtString} (`0x75b450`); list u8 (`0x75e9b0`); u32.
   PS4 counterpart: **none** (no Mandragora handler, reader or type in PS4 02020005). V (PS4)
4. Errors / gaps: G1 only; layout matches field for field. Names unresolved (no DWARF; PC
   function names `Read_CDataMyMandragora*` are earlier user names, not evidence). V
5. Shared: CommonU8-style list `0x75e9b0` (also element shape of other u8 lists).
6. Walk: 20/20 ok. `stream21-failedlogin-marked.pcapng_tcp-stream-48/12991_S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES_...64_0_2`
   (624 B, `540c7b791878e152`): Error 0, Result 0, lists n=3 →0x2d, 3 →0xd5, 2 →0x100, 1 →0x109,
   1 →0x115, u32 0x14, n=12 →0x210, 5 →0x25b, 3 →0x262, u32 0x1e; end 0x266, slack 10.
7. Raw name: `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES`.

### 3. S2C_PARTY_QUEST_PROGRESS_NOTICE (11.120.16)

1. Status: **partial**. V
2. Handler `0x7f30f0` (group-11 table key 16/120; inline ctor 0x0B, 0x78, 0x10), reader **`0x817940`**.
   The handler pushes a notice of DTI `dti__1507` = PC string **"cQuestSvNotPartyQuestProgress"**
   (`0x1a13d6d`), as PS4 `OnPacket_S2C_PARTY_QUEST_PROGRESS_NOTICE` `0x313510` does. V
3. Wire (V): **u32** (PS4 `m_unProgressCharacterId`), CDataPartyQuestProgressInfo (`0x771aa0`):
   list QuestOrderList (`0x7749a0`), list {u32, u32} (`0x774050`; PS4 CDataQuestIdScheduleId),
   list {u32, u32, u16, list {u32, u16, u16}} (`0x762e80`/`0x762d80`; PS4 CDataDeliveredItemRecord),
   list {u32, u16, list {u8, u16}} (`0x774230`/`0x774140`; PS4 CDataQuestKeyItemPointRecord).
   PS4 match by code: same u32 + four lists (`CPartyQuestProgressInfo`, DWARF). V
4. Errors / gaps:
   - **Extra `u32 Error` before ProgressCharacterId**: the PC reader has no error field (G3). V (C)
   - Inherits the QuestOrderList errors of section 1 (u32+u32 vs u64; `CDataUnknown` signedness). V
   - The file also defines the RES struct (copy of section 4); one shared include would do. V
5. Shared: CDataPartyQuestProgressInfo `0x771aa0` with 11.71.2.
6. Walk: **not run: no capture** of suffix `11_120_16` (0 files).
7. Raw name: `S2C_QUEST_PARTY_QUEST_PROGRESS_NTC` (from `packets/all_packets_v03040008.txt`; no file).

### 4. S2C_GET_PARTY_QUEST_PROGRESS_INFO_RES (11.71.2)

1. Status: **partial** (same structures as section 3). V
2. Handler `0x7f1c60` (string `0x1bc9470` "…OnPacket_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES"),
   inline ctor (11, 71, 2), reader `0x8168c0`. V
3. Wire: RES, CDataPartyQuestProgressInfo (`0x771aa0`, section 3). PS4
   `OnPacket_S2C_GET_PARTY_QUEST_PROGRESS_INFO_RES` `0x313220`, same body. V
4. Errors: G1; QuestOrderList errors of section 1. V
5. Shared: as section 3.
6. Walk: 43/43 ok (pattern layout is the PC layout up to the same-size u64). `stream1-marked.pcapng_tcp-stream-35/12215_S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES_...11_71_2`
   (14,784 B, `55e8d78545b18bab`): Error 0, Result 0, QuestOrderList n=30 0x11→0x39b0, three empty
   lists, end 0x39bc, slack 4. DeliveredItemRecord and KeyItemPointRecord are empty in all 43 files
   (not exercised); SoloQuestOrderList non-empty in 23.
7. Raw name: `S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES` (pattern file name lacks `QUEST_`).

### 5. S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES (11.15.2)

1. Status: **partial** (S3 fields unnamed). V
2. Handler `0x7f0b70` (string `0x1bc8458`), ctor `0x78b350` (11, 15, 2), reader `0x815cb0`. V
3. Wire (V): RES; list (`0x7615e0`) of {u32, u64, u64, u8, u32, list RewardItem (`0x7771b0`), list
   {u32, u32, u16, u8} (`0x761850`), list {u8, u32, u32, u64, **u32, u8**} (`0x761d90`/`0x761e80`),
   u32, u32, bool, **list QuestEnemyInfo (`0x773d90`), list {u32, s64, s64} (`0x774e80`), u64 x 6**}.
   PS4 `OnPacket_S2C_GET_CYCLE_CONTENTS_NEWS_LIST_RES` `0x2ebf90`: CDataCycleContentsNews ends after
   m_bIsCreateRanking; CDataCycleContentsRank = {u8, u32, u32, u64} (DWARF). Bold = S3 additions. V
4. Errors: G1; signedness `CDataCycleContentsUnk.Unk1/Unk2` u64, PC `R.s64`. Layout otherwise right.
   Names of the S3 fields unresolved. V
5. Shared: RewardItem `0x7771b0`, QuestEnemyInfo `0x773d90` (with QuestOrderList).
6. Walk: 6/6 ok. `stream76-marked.pcapng_tcp-stream-11/11557_..._11_15_2` (1,632 B,
   `41509874cbd7af33`): Error 0, Result 0, list n=4 0x11→0x65c, slack 4.
7. Raw name: `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES`.

### 6. S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES (51.0.2)

1. Status: **partial**. V
2. Handler code at `0x7d23ec`-`0x7d2471` (not defined as a function; the string `0x1bd1ff0` is pushed
   at `0x7d248c`), inline ctor `0x7d2402` (0x33, 0, 2), reader `0x806830`. V
3. Wire (V): RES; list (`0x7630d0`) of CDataDispelBaseItem (`0x763190`): u32 Id, **u32**, s64 Begin,
   s64 End, list {u32, **u32**} (`0x7632a0`), list WalletPoint {u8, u32} (`0x77c5a0`), bool IsHide,
   list LotData (`0x763c20`), u32 SortId, MtString Label, **u32, u16, u16**. LotData: u32 Id,
   ItemLot (`0x763d40`) {u32, u8, u8, **u16, bool, u8**}, CrestLot (`0x7639e0`) {u32, u8, **u8, u8,
   list {u16, u8}** (`0x763b30`)}, ColorLot {u8, u8} (`0x7638f0`), PlusLot {u8, u8} (`0x763dc0`).
   PS4 `OnPacket_S2C_GET_DISPEL_ITEM_LIST_RES` `0x333820` (DWARF): BaseItem {u32 Id, s64, s64,
   list {u32 ItemID, **u8** Num}, list Cost, b8 IsHide, list LotItemList, u32 SortId, MtString Label,
   **u8 m_ucCategory**}; LotItem {u32, u8, u8, **u32** ItemNum}; LotCrest {u32, u8}. V (PS4)
4. Errors / gaps:
   - **CDataDispelLotCrest** {u32, u8, u16 Unknown}: PC reads {u32, u8, u8, u8, list {u16, u8}}.
     Wrong from the third byte on; any non-empty CrestLot breaks the pattern. V (C)
   - **CDataDispelLotItem** `u16 ItemNum; u16 Unknown`: PC u16, bool, u8 (same size). V
   - **CDataDispelBaseItem tail** `u32 Category; u32 Unknown2`: PC u32, u16, u16 (same size). V
   - Enum `WalletType` not from DWARF (G6). G1. V
5. Shared: WalletPoint `0x77c5a0` (with QuestOrderList, SetQuestDetail).
6. Walk: 1/1 ok with the PC layout; the pattern layout also fits this capture, so its CrestLot lists
   are evidently empty (I). Byte walk of
   `stream85-marked.pcapng_tcp-stream-11/159334_S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES_...51_0_2`
   (9,424 B, `1a1eb218a481568c`) with `xxd`, first element: 0x09 Error 0; 0x0d Result 0; 0x11 count
   0x61; 0x15 Id 0x0001c314; 0x19 u32 0x0b51; 0x1d/0x25 s64 0, 0; 0x2d list n=1 {0x3e43, 1}; 0x39
   Cost n=0; 0x3d IsHide 0; 0x3e LotItemList n=1: 0x42 Id 0, ItemLot 0x46 0x2e2d (11821), 0x64, 0x00,
   u16 1, bool 0, u8 0xff; 0x50/0x54/0x58 three empty lists; 0x5c SortId 1; 0x60 MtString len 0x0c
   "<ITEM 11821>"; 0x6e u32 0x98; 0x72 u16 0; 0x74 u16 0; next element 0x76 Id 0x0001c315. End of
   all 97 elements 0x24cc, slack 4.
7. Raw name: `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES`.

### 7. S2C_STAGE_GET_STAGE_LIST_RES (12.0.2)

1. Status: **finished** (two S3 bools named `Unknown1/2`). V
2. Handler `0x7fd9e0` (string `0x1bc9a94`; on-stack packet 12, 0, 2), reader `0x81cc40`. V
3. Wire (V): RES; list (`0x77a020`) of {u32 ID, u32 StageNo, u32 RandomStageGroupID, u32 Type,
   CStageAttribute (`0x779f40`: **11 bools**), bool IsAutoSetBloodEnemy}. PS4
   `OnPacket_S2C_GET_STAGE_LIST_RES` `0x2f33c0`: CDataStageAttribute has **9** b8 (DWARF). V
4. Errors: G1 only. The two S3 bools are the last two of the attribute (PC reads 11 in `0x779f40`),
   where the pattern has them. V
6. Walk: 42/42 ok. `stream1-marked.pcapng_tcp-stream-34/11917_..._12_0_2` (15,744 B,
   `9fbcc6459f1f6dc9`): list n=561 0x11→0x3d71, slack 15.
7. Raw name: `S2C_STAGE_GET_STAGE_LIST_RES`.

### 8. S2C_BOX_GACHA_BOX_GACHA_LIST_RES (57.0.2)

1. Status: **finished** (two `Unknown1` fields). V
2. Handler `0x7c6f40` (string `0x1bd2d68`; inline 57, 0, 2), reader `0x8018e0`. V
3. Wire (V): RES; list (`0x75a970`) of {u32, s64, s64, **bool**, MtString x3, u8, MtString x3, list
   Settlement {u32 x4, u8, u8, u32 x4, **u32**} (`0x75acd0`), list Item {u32 x5, f64, u16}
   (`0x75ab40`)}. PS4 `OnPacket_S2C_BOX_GACHA_LIST_RES` `0x337c40` (DWARF CDataBoxGachaInfo /
   SettlementInfo / ItemInfo) lacks the two bold fields. V
4. Errors: G1 only. V
6. Walk: 3/3 ok. `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/10023_..._57_0_2` (1,104 B,
   `c2aeb4a3ffb4475b`): list n=1 0x11→0x44d, slack 3.
7. Raw name: `S2C_BOX_GACHA_BOX_GACHA_LIST_RES`.

### 9. S2C_QUEST_GET_AREA_BONUS_LIST_RES (11.19.2)

1. Status: **finished** (one `UnknownRatio`). V
2. Handler `0x7f0960` (string `0x1bc6adc`), ctor `0x78b230` (11, 19, 2), reader `0x815b20`. V
3. Wire (V): RES; list (`0x758f30`) of {u32, u16 x **5**} (`0x759010`). PS4
   `OnPacket_S2C_GET_AREA_BONUS_LIST_RES` `0x2ec110`: CDataAreaBonus has 4 u16. V
4. Errors: G1 only. V
6. Walk: 182/182 ok (first file `stream10-musicplayer-marked.pcapng_tcp-stream-9/10537_..._11_19_2`).
7. Raw name: `S2C_QUEST_GET_AREA_BONUS_LIST_RES`.

### 10. S2C_MY_ROOM_FURNITURE_LIST_GET_RES (52.1.2)

1. Status: **finished** (one `Unk0`). V
2. Handler `0x7e5a90` (string `0x1bd2478`), ctor `0x78a3d0` (52, 1, 2), reader `0x80fa00`. V
3. Wire (V): RES; list {u32, u32, u8} (`0x766f90`); CDataMyRoomOption (`0x76f300`): list u32
   (`0x75e8e0`), u32, **u32**. PS4 `OnPacket_S2C_FURNITURE_LIST_GET_RES` `0x334ba0` /
   `ReadPacket` `0x19df920`: CDataMyRoomOption = {list, u32} (DWARF). V
4. Errors: G1 only. V
5. Shared: CommonU32 list `0x75e8e0`.
6. Walk: 20/20 ok. `stream21-failedlogin-marked.pcapng_tcp-stream-48/12970_..._52_1_2` (384 B,
   `c6afc38e985feaee`): list n=38 0x11→0x16b, list n=0, u32 0x53e4, u32 0, end 0x177, slack 9.
7. Raw name: `S2C_MY_ROOM_FURNITURE_LIST_GET_RES`.

### 11. S2C_QUEST_GET_AREA_INFO_LIST_RES (11.56.2)

1. Status: **finished**. V
2. Handler `0x7f0a10` (string `0x1bc6a78`), ctor `0x78b290` (11, 56, 2), reader `0x815ba0`. V
3. Wire (V): RES; list (`0x759090`) of {u32, u8, u8, u8, bool}. PS4
   `OnPacket_S2C_GET_AREA_INFO_LIST_RES` `0x2f27d0`, CDataAreaInfoList, identical. V
4. Errors: G1 only. V
6. Walk: 1/1 ok. `stream76-marked.pcapng_tcp-stream-11/11565_..._11_56_2` (224 B,
   `3ff04f69adefea7b`): list n=24 0x11→0xd5, slack 11.
7. Raw name: `S2C_QUEST_GET_AREA_INFO_LIST_RES`.

### 12. S2C_GET_CYCLE_CONTENTS_STATE_LIST_RES (11.37.2)

1. Status: **finished** in layout; enum issue. V
2. Handler `0x7f1080` (string `0x1bc94e0`; on-stack 11, 37, 2), reader `0x816010`. V
3. Wire (V): RES; list (`0x762100`) of {u32, u8, u32, u8}. PS4
   `OnPacket_S2C_GET_CYCLE_CONTENTS_STATE_LIST_RES` `0x2ee2f0`, CDataCycleContentsStateList, identical. V
4. Errors: G1; `CYCLE_CONTENTS_SUB_CATEGORY` has values 1005-1009 and 3007 not in PS4 DWARF (G6);
   whether S3 added them is unresolved. The enum `: s32` views over a u8/u32 are display only. V
6. Walk: 41/41 ok. `stream1-marked.pcapng_tcp-stream-35/12008_..._11_37_2` (64 B,
   `3e814da8e934b1d0`): list n=4 0x11→0x3d, slack 3.
7. Raw name: `S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES` (pattern file name lacks `QUEST_`).

### 13. S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES (23.9.2)

1. Status: **finished**. V
2. Handler `0x7c4330` (string `0x1bcda68`; group-23 table key 2/9), ctor `0x785d10` (23, 9, 2),
   reader `0x7ffe90`. V
3. Wire (V): RES; list (`0x7591c0`) of {u32, u32, bool}. PS4 `OnPacket_S2C_GET_AREA_QUEST_HINT_LIST_RES`
   `0x303220`, CDataAreaQuestHint, identical. V
4. Errors: G1 only (and the unused `CDataCommonU32` define). V
6. Walk: 183/183 ok. `stream1-marked.pcapng_tcp-stream-35/12188_..._23_9_2` (160 B,
   `04e93ff7e7750d78`): list n=14 0x11→0x93, slack 13.
7. Raw name: `S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES`.

### 14. C2S_AREA_GET_AREA_QUEST_HINT_LIST_REQ (23.9.1)

1. Status: **finished**. V
2. Writer `0x81e5a0`: `WritePacket(0x17, 9, 1, -1)` + `Write_u32`, found at call site `0x81e613`. Name:
   pairs with the 23.9.2 handler named by its PC string (I, pairing). V
3. Wire: u32 (PS4 `CPacket_C2S_GET_AREA_QUEST_HINT_LIST_REQ.m_unAreaID`; PS4
   `Send_C2S_GET_AREA_QUEST_HINT_LIST_REQ` `0x19c1f60` writes one u32 after its u16 header). The PS4
   body alone cannot tell this sender from `0x19c1a60` (same body); the match rests on the PC pairing. V / I
4. Errors: none (no RES header). V
6. Walk: 183/183 ok. `stream1-marked.pcapng_tcp-stream-35/12187_..._23_9_1` (16 B,
   `ec4a180e0fedc388`): u32 1, end 0xd, slack 3.
7. Raw name: `C2S_AREA_GET_AREA_QUEST_HINT_LIST_REQ`.

### 15. S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES (23.8.2)

1. Status: **stub / wrong** (stops after the first of three lists). V
2. Handler `0x7c4600` (string `0x1bcda00`), ctor `0x785dd0` (23, 8, 2), reader `0x8000b0`. V
3. Wire (V): RES; list (`0x776890`) of {u32, list u32 (`0x75e8e0`)}; **list (`0x7696e0`) of
   {u32, u32, s64}**; **list (`0x76d440`) of {u32, bool, s64}**. PS4
   `OnPacket_S2C_GET_LEADER_AREA_RELEASE_LIST_RES` `0x3030a0` reads only the first list
   (CDataReleaseAreaInfoSet). V
4. Errors: **two trailing lists missing** (S3). Names unresolved (server lead: MonsterGatheringSpots,
   PeriodicallyReleasedSpots). G1. V (C)
5. Shared: CommonU32 list `0x75e8e0`.
6. Walk: PC layout 131/131 ok; **pattern layout 0/131** (ends at 0x41 in a 96-byte file, slack > 15).
   `stream1-marked.pcapng_tcp-stream-35/12143_..._23_8_2` (96 B, `1146bf9659b7ea65`): list n=3
   0x11→0x41, list n=0 0x41→0x45, list n=1 0x45→0x56, slack 10. List 2 is non-empty in 98 files.
7. Raw name: `S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES`.

### 16. S2C_AREA_GET_AREA_BASE_INFO_LIST_RES (23.12.2)

1. Status: **finished**. V
2. Handler `0x7c3f70` (string `0x1bcdb88`; on-stack 23, 12, 2), reader `0x7ffc40`. V
3. Wire (V): RES; list (`0x758d80`) of {u32 x5, bool, u32, u32, bool} (`0x758e80`). PS4
   `OnPacket_S2C_GET_AREA_BASE_INFO_LIST_RES` `0x3036c0`, CDataAreaBaseInfo, identical. V
4. Errors: G1 only. V
6. Walk: 72/72 ok. `stream1-marked.pcapng_tcp-stream-35/12059_..._23_12_2` (656 B,
   `d5094ae36b44c9fe`): list n=21 0x11→0x28b, slack 5.
7. Raw name: `S2C_AREA_GET_AREA_BASE_INFO_LIST_RES`.

### 17. S2C_AREA_GET_AREA_MASTER_INFO_RES (23.0.2)

1. Status: **finished**. V
2. Handler at `0x7c4180` (group-23 table key 2/0; bytes not a function, so IDA has no xref from it to
   the string): it pushes `0x1bcd7d4` "…OnPacket_AREA_GET_AREA_MASTER_INFO_RES" to `callOnPacketFunc`
   at `0x7c4208`; ctor `0x785c90` (0x17, 0, 2); reader `0x7ffcc0`. V
3. Wire (V): RES; u32 x6; list u32 (`0x75e8e0`); bool; bool; list (`0x75a860`) of {u32, list {u32,
   u16} (`0x77a9f0`)}; list {u32, u32} (`0x7593c0`). PS4 `CPacket_S2C_GET_AREA_MASTER_INFO_RES::ReadPacket`
   `0x19da7a0`, identical field for field (DWARF names = pattern names). V
4. Errors: G1 only (and the unused `CDataCommonU32` define). V
5. Shared: CommonU32 list `0x75e8e0`.
6. Walk: 42/42 ok. `stream21-failedlogin-marked.pcapng_tcp-stream-48/13716_..._23_0_2` (272 B,
   `1074a159ad6d04f6`): AreaId 0x11, Rank 0xf, Point 0x6338, WeekPoint 0x5dc, LastWeekPoint 0x1770,
   ToNextPoint 0x6338, ReleaseList n=14 0x29→0x65, bools 1, 0, list n=4 0x67→0xd9, list n=5
   0xd9→0x105, slack 11.
7. Raw name: `S2C_AREA_GET_AREA_MASTER_INFO_RES`.

### 18. C2S_AREA_GET_AREA_MASTER_INFO_REQ (23.0.1)

1. Status: **finished**. V
2. Writer `0x81e4c0`: `WritePacket(0x17, 0, 1, -1)` + `Write_u32` (call site `0x81e533`). Name by
   pairing with 23.0.2 (I). V
3. Wire: u32 (PS4 `CPacket_C2S_GET_AREA_MASTER_INFO_REQ.m_unAreaID`, sender `0x19c1a60`; same caveat
   as section 14). V / I
4. Errors: none. V
6. Walk: 42/42 ok. `stream21-failedlogin-marked.pcapng_tcp-stream-48/13715_..._23_0_1` (16 B,
   `249566824b73b05e`): u32 0x11, slack 3 (the RES above answers AreaId 0x11).
7. Raw name: `C2S_AREA_GET_AREA_MASTER_INFO_REQ`.

## Shared structures (include candidates, PC 03040008)

| Structure | PC reader (element / list) | Wire | Used by | PS4 type | Mark |
| --- | --- | --- | --- | --- | --- |
| CDataQuestOrderList | element `0x774a70`; list `0x7749a0`, `0x76eb40`, `0x77b2a0`, `0x770ab0` | section 1 | 11.89.16 (9 lists), 11.71.2, 11.120.16 | CDataQuestOrderList (S2 layout) | V |
| CDataQuestProcessState | list `0x775310`, element `0x775420` | u16 x3, list ProgressWork, list of list QuestCommand, list QuestCommand | QuestOrderList | same name | V |
| CDataQuestCommand | list `0x7738f0`; list of lists `0x757f20` | u16, s32 x4 | ProcessState | CDataQuestCommand | V |
| CDataQuestProgressWork | list `0x7754a0` | u32, s32 x4 | ProcessState, PriorityQuest | same | V |
| CDataQuestLog | `0x774850` (`0x773820` u32 list, `0x7757e0` {u32, u32, u16, bool}) | | QuestOrderList | CDataQuestLog (TalkInfo without leading u32) | V |
| CDataQuestEnemyInfo | list `0x773d90` | u32, u32, u16, bool | QuestOrderList, 11.15.2 | {u32, u16, b8} | V |
| CDataRewardItem | list `0x7771b0` | u32, u16 | QuestOrderList, 11.15.2 | same | V |
| CDataWalletPoint | list `0x77c5a0` | u8, u32 | QuestOrderList, SetQuestDetail, 51.0.2 | same | V |
| CDataQuestExp (name from patterns, no DWARF) | list `0x76c780` | u8, u8, u32 | QuestOrderList, SetQuestDetail | none | V |
| CDataPartyQuestProgressInfo | `0x771aa0` | 4 lists (section 3) | 11.71.2, 11.120.16 | same | V |
| CDataCommonU32 list | `0x75e8e0` | u32 | 23.0.2, 23.8.2, 52.1.2, 11.89.16 row 6 | CDataCommonU32 | V |
| u32-only lists with separate PC readers | `0x75eec0`, `0x773eb0`, `0x774350`, `0x773f80`, `0x773820` | u32 | QuestOrderList, QuestLog, 11.89.16 | CDataQuestFlag / LayoutFlag / QuestId / QuestAnnounce | V |
| CDataSetQuestDetail | `0x778040` | section 1 | 11.89.16 | S2 layout | V |
| CDataLightQuestDetail | `0x76d1c0` | u32 x7 | 11.89.16 | u32 x6 | V |
| MtString | `nPacket::Read_MtString` `0x8bc5b0` | u16 + bytes | 64.0.2, 57.0.2, 51.0.2 | MtString | V |

## Server disagreements met (lead only)

- The server agrees with the PC client, and the patterns do not, on: CDataLightQuestDetail (7 u32),
  CDataSetQuestDetail (two lists), CDataQuestOrderList (3 u32 + 3 time values), the three lists of
  23.8.2, CDataDispelLotCrest and CDataDispelLotItem, CDataDispelBaseItem tail (u32, u16, u16), and the
  11.120.16 body (u32 ProgressCharacterId first, no error).
- Disagreements with the client: CDataQuestOrderList times are `ReadInt64` (PC `R.u64`);
  CDataDispelBaseItem Begin/End are `ReadUInt64` (PC `R.s64`). Signedness only.
- Not checked: the other server structures of the batch.

## Summary

| Pattern | Status | Errors found (beyond G1 RES header, G4 no include) | Walk ok (PC layout) |
| --- | --- | --- | --- |
| S2C_JOIN_LOBBY_QUEST_INFO_NOTICE (11.89.16) | partial | LightQuestDetail 6→7 u32; SetQuestDetail S2 layout; OrderList 2 x u32 → u64; signedness; dead structs; 3 enums not DWARF | 41/41 (pattern also fits: errors unexercised) |
| S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES (64.0.2) | partial | none in layout; names unknown, no PS4 | 20/20 |
| S2C_PARTY_QUEST_PROGRESS_NOTICE (11.120.16) | partial | extra `u32 Error`; OrderList errors | not run (0 captures) |
| S2C_GET_PARTY_QUEST_PROGRESS_INFO_RES (11.71.2) | partial | OrderList errors | 43/43 |
| S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES (11.15.2) | partial | signedness of 2 s64 | 6/6 |
| S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES (51.0.2) | partial | LotCrest wrong; LotItem and BaseItem tail types; WalletType enum | 1/1 (crest lists empty) |
| S2C_STAGE_GET_STAGE_LIST_RES (12.0.2) | finished | none | 42/42 |
| S2C_BOX_GACHA_BOX_GACHA_LIST_RES (57.0.2) | finished | none | 3/3 |
| S2C_QUEST_GET_AREA_BONUS_LIST_RES (11.19.2) | finished | none | 182/182 |
| S2C_MY_ROOM_FURNITURE_LIST_GET_RES (52.1.2) | finished | none | 20/20 |
| S2C_QUEST_GET_AREA_INFO_LIST_RES (11.56.2) | finished | none | 1/1 |
| S2C_GET_CYCLE_CONTENTS_STATE_LIST_RES (11.37.2) | finished | SUB_CATEGORY values not in DWARF | 41/41 |
| S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES (23.9.2) | finished | none | 183/183 |
| C2S_AREA_GET_AREA_QUEST_HINT_LIST_REQ (23.9.1) | finished | none | 183/183 |
| S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES (23.8.2) | stub/wrong | two lists missing | 131/131 (pattern 0/131) |
| S2C_AREA_GET_AREA_BASE_INFO_LIST_RES (23.12.2) | finished | none | 72/72 |
| S2C_AREA_GET_AREA_MASTER_INFO_RES (23.0.2) | finished | none | 42/42 |
| C2S_AREA_GET_AREA_MASTER_INFO_REQ (23.0.1) | finished | none | 42/42 |

Totals: 1,053 capture files over 17 suffixes, all walk with the PC layouts (0 failures); 11.120.16 has
no capture. Raw-name mismatches with the pattern file names: 11.89.16, 11.120.16, 11.71.2, 11.37.2.

## Left open

- Names of the Season 3 fields (`Unk*`), the position of the new u32 in CDataLightQuestDetail and of
  the new u64 in CDataQuestOrderList: need the PC consumers (not read).
- The SetQuestDetail, LightQuestDetail, DeliveredItemRecord, KeyItemPointRecord and DispelLotCrest
  paths have no non-empty capture: their PC layouts are V from code only.
- The PS4 match of the two C2S REQs rests on PC REQ/RES pairing; their PC callers were not compared
  with the PS4 callers.
