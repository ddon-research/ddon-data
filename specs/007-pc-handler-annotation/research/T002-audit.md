# 007 T002: audit of the earlier packet annotations in the accepted PC database

Builds and databases (all addresses are IDA VAs):

- PC **03040008**: private copy `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t002/2022_01_29_DDO_DUMP_FIX.exe.i64`,
  made by `bash research/ida/private-copy.sh pc-accepted t002`. The `.i64` sha256 is
  `382e346e0b48b157e261119cf803c7b10d072b40ba3ae187a79291d640a58c0f`, equal to `accepted_PC.sha256`
  in `CURRENT-RECOVERY.json` (checked with `sha256sum` before opening). Input sha256 is `f1c974d0…fa20`.
  The database is 32-bit with image base `0x400000`.
- PS4 **02020005**: private copy `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t002/DDOORBIS.elf.i64`.
  Input sha256 is `4236f598…63c0`. The database is 64-bit with image base `0`. For DWARF I streamed
  `binaries/PS4_02020005/elf-dumps/local/dwarf-info.llvm-dwarfdump.txt.zst`.
- The work was read-only in substance: no renames, retypes, comments or saves. ddon-data base is `12affeea48`, 2026-11-03.
- Marks: **V** means I verified it here in IDA. **I** means inferred. **C** means contradicted.

Output beside this file: `T002-prior-annotations.tsv` (2,981 rows; columns `pc_va, role, kind, value,
origin, verdict`).

## 0. Answer in brief

- The accepted database holds all **107** earlier packet method views (V). Every contract name is
  present. Every contract prototype is present; 11 differ only in spelling (`unsigned char` versus
  `unsigned __int8`).
- **The 50 earlier handler names hold as PC names (V).** Each one is a table entry's callback. Each
  references exactly one `OnPacket_` string, and the name repeats it byte for byte.
- **The PS4 links of those 50 handlers**:
  - 40 hold (V): there is a unique `cSeedGameSvConnection` symbol, and the read widths agree.
  - 10 are unproved: the widths differ (Season 3 extra fields, header width).
  - None is contradicted.
- **The handler prototypes hold physically (V).** Each handler reads `this` from ecx and ends with
  `ret 4`. It returns 0, 1 or the reader's result.
- **Byte-identical codec pairs**: the PC call sites settle the names; byte identity alone did not.
  - Codec calls line up position by position with the PS4 `nPacket::Read` overloads in 296+2 seed
    pairs (V; the seed pairs are proved by name and widths). The u32, u8, bool, s64 and u64 names
    have zero crossings.
  - The s32 name holds with a caveat: its body is also used for 2 body and 29 header u32
    positions.
  - The 64-bit pair differs in one byte, a rel32 displacement to the same callee. T001 called it
    byte-identical, which is not exact.
  - `Read_f32` `0x8BC520` is a third copy of the s32/u32 body. The writer pairs
    `Write_u8`/`Write_bool` and `Write_s32`/`Write_u32` are also identical; their names are unproved
    (I did not align senders).
- **Wrong or unproved names outside the 50**: 46 other handlers carry names that are not in the 006
  contracts (origin unattributed).
  - 33 hold.
  - 2 use the PS4 form where the PC string differs.
  - 1 is **wrong**: `0x7D36B0` uses class `cNetGameServer`.
  - 10 are unproved: their names have no source in code.
- **Tier-0 is feasible.** Of 1,040 table callbacks:
  - **580** reference exactly one `OnPacket_` string, **0** reference several, and **460** reference none.
  - Of the 580, **412** have a unique PS4 partner by the group-prefix rule. In 298 of those the read
    widths are equal.
- **PS4 readiness**:
  - Prototypes with DWARF parameter names and types are imported (20/20 sampled).
  - The structs are imported with DWARF members (7/7).
  - DWARF **local** names are mostly **not** imported. The DWARF dump has them, for example
    `tmpErr`, `pContext` and `packet` in `OnPacket_S2C_CHARACTER_GOLDEN_REVIVE_RES`, which IDA lacks.

## 1. Identity

| Check | Result |
| --- | --- |
| `idc.get_idb_path()` | the `ddon-data-t002` copy path above (V); input path metadata still says `IDA9.3\PC_DDON_03040008\…exe` |
| `.i64` sha256 = `accepted_PC.sha256` | equal, `382e346e…a58c0f` (V, `sha256sum` on the copy) |
| bitness / base | 32-bit, `0x400000` (V); PS4 64-bit, `0x0` (V) |
| 107 method views | 105 contract methods (22 codec/framework, 13+2+9+12+12 handlers, 1 server list, 30 peer, 2 string writers, Send, history sender) plus 2 destructors `0x7B6B20`/`0x7B6B60` are all present with the contract name (V). Types: 94 equal after whitespace normalisation; 11 differ only `unsigned char`/`unsigned __int8` spelling (V) |
| contract source | `C:/Users/morph/CLionProjects/ddon-hook/specs/006-recover-pc-packets/contracts/*.json` (read-only) |

## 2. Inventory (packet area)

**Scope (V).**

- **Table**: `0x1BC0110`, `{table,count}` × 74, entries with stride 0x18 and the key `(sub<<16)|id`
  at +0x10. It holds **1,041** entries.
- **Callbacks**: I took each callback from its record's `movq [record], xmmN` back to
  `movq xmmN, [esp]` and then to `mov [esp], imm`. That gives **1,040** distinct callbacks, plus
  the null key `15:65535:255`, whose initializer `0x1A2C6D0` stores 0. Each record is written once.
- **Cross-check**: the result is identical, record for record, to ddon-hook
  `packet-catalog.json` `pc_registration` (`diff` empty, 1,041 lines).
- **Initializers**: **74** of them, `0x1A27560`-`0x1A36540`. The brief's range `0x1A27560`-`0x1A343B0`
  misses 13 of them, `0x1A34430`-`0x1A36540`, which write 163 records.
- **Senders**: the 642 functions that hold the 658 call sites of `nUserSession::CPacket::WritePacket`
  `0x8BCBB0`.
- **Helpers**: 1,999 direct callees of handlers and senders, one level.
- **Other**: 36 further earlier-work functions outside that set (peer methods, `0x8BC660`, …).

**What carries non-default metadata.** "Prototype" counts only types that are user-set or that
carry a named type. Each prototype column has the form `user-set / with a named type`.

| Role (functions) | user names | prototypes (user-set / with a named type) | function comments | saved local settings (rows) |
| --- | --- | --- | --- | --- |
| handlers (1,040) | 96 (50 earlier packet work, 46 unattributed) | 52 / 844 | 12 | 24 functions (120) |
| senders (642) | 39 | 2 / 641 | 2 | 10 (25) |
| helpers (1,999) | 87 | 24 / 944 | 10 | 19 (56) |
| other earlier work (36) | 36 | 36 / 36 | 3 | 2 (7) |

- **Propagated types (I).** Named types in prototypes:
  - `CPacket` appears in 1,786 prototypes and `cSeedServerConnection` in 551. That matches T001's
    propagation from the codec and `Send` retypes (I: IDA propagation; the database keeps no
    provenance).
  - `cSeedGameSvConnection` appears in 50 prototypes, `nNetwork::*` in 28.
  - 20 named types are referenced in all: 16 structs and 4 typedefs. **No enums.**
- **Origin rules used in the TSV:**
  - **Earlier packet work**: the address is in a 006 contract.
  - **Unattributed**: a user name or type outside the contracts.
  - **IDA propagation**: a guessed type that carries a named type.

## 3. Checks

### 3.1 The 50 earlier handler names (V unless marked)

**Gate (a): the entry is the table's callback.** All 50 pass.

**Gate (b): it references the `OnPacket_` string its name repeats, and only that one.** All 50 pass.
References are xrefs plus a raw `imm`/`mem` operand scan over every function. The scan found no
reference the xrefs had missed.

**Gate (c): one PS4 symbol with the same `<NAME>`.**

- The rule: a PS4 `cSeedGameSvConnection::OnPacket_S2C_<NAME>`, where `<NAME>` is the PC string
  with the group prefix removed.
- The group prefix is any token prefix of the common token prefix of the group's table strings.
- `cNetGameServer` has 42 same-named PS4 `OnPacket_` functions with no reads (another class). I
  excluded them.
- Result: all 50 have exactly one partner, and it equals the earlier work's recorded PS4 name.
- Two need the group rule:
  - `0x7EC0F0` `PAWN_LOST_PAWN_POINT_REVIVE_RES`: `LOST_PAWN_POINT_REVIVE_RES` and
    `PAWN_POINT_REVIVE_RES` both exist on PS4 and **have the same widths**. Only the group prefix
    `PAWN` decides between them.
  - `0x7EC030`: the widths separate the two candidates.

**Body shape.**

- **Method**: flatten each side's calls (depth 5) to the scalar codecs.
  - PC codecs are classed by address.
  - PS4 codecs are named `nPacket::Read_*`. The PS4 symbol table confirms the mapping, e.g.
    `0x3B6160` is `nPacket::Read(CPacket&, unsigned short&)`.
  - Then compare the width strings.
- **What PS4 reads first**: every PS4 handler first reads `m_usError` as **u16** (PS4 DWARF: packet
  classes have `m_usError u16`@8, `m_nResult s32`@12).
  - PC response handlers read that field with a 4-byte codec.
  - PC notice handlers do not read it.
  - So "equal" means PS4[1:] equals PC[1:] for RES, or PS4[1:] equals PC for NTC.
- **Verdicts**:
  - **40 hold**.
  - **10 are unproved**, because the PS4 link stays unproved:

| PC VA | key | PS4 symbol | PS4 / PC widths (head) | reading (I) |
| --- | --- | --- | --- | --- |
| `0x7FD9E0` | 12.0.2 | `OnPacket_S2C_GET_STAGE_LIST_RES` | `2144444…` / `4444444…` | PS4 `m_ucResult` u8, PC 4 B; PC 2 more bools |
| `0x7F95C0` | 1.4.2 | `GET_REAL_TIME_RES` | `282` / `4482` | PC has one more u32 |
| `0x7E2CE0` | 3.0.2 | `LOBBY_JOIN_RES` | `24444SSS41111` / `444` | PC body reads not reached by the flattener (indirect calls?) |
| `0x7E96C0` | 6.14.2 | `PARTY_SEARCH_RES` | differ mid-sequence | element layout changed |
| `0x7E9A70` | 8.1.2 | `DELETE_MYPAWN_RES` | `24` / `4414` | PC extra fields |
| `0x7EA9D0`, `0x7EAED0`, `0x7EB6E0`, `0x7EB9F0` | 8.3/8.11/8.6/8.9.2 | pawn data RES | equal for the first ~190 reads, then PC differs and adds a tail `144444411` | Season 3 pawn-data growth |
| `0x7EAB80` | 8.2.2 | `GET_MYPAWN_LIST_RES` | PC +3 u32 | Season 3 growth |

**Prototypes of the 50.** The earlier prototype is `int __thiscall(cSeedGameSvConnection *self,
CPacket *packet)`. It **holds**.

- **this**: ecx is read before any write in 50/50 handlers.
- **Arguments**: the return is `ret 4` in 50/50, so there is one stack argument. The callers are the
  indirect dispatch; there are no direct callers.
- **Return**: the decompiled returns are `return 1` (45), `return 0` (15), and
  `return result`/`v3`/`v5` (35, which is the reader's return or a 0/1 flag).
- PS4 declares `BOOL`. A 32-bit `int` is the right physical width.

### 3.2 Sender `0x833670` `Send_PAWN_GET_PAWN_HISTORY_LIST_REQ`

- **Body (V)**: it builds a stack `CPacket` and calls `WritePacket(&p, 8, 0x1C, 1, -1)`, so the
  key is 8.28.1. It then calls `Write_u32(arg)` and `cSeedServerConnection::Send(this, …)`, and
  ends with `ret 4`.
- **Caller (V)**: its only caller is `0x86F4B0`, which pushes one value with `ecx = [esi+0x29CC]`.
  It returns 0 or 1.
- **Prototype**: `int __thiscall(void *self, unsigned int)` **holds** (V).
- **Name: unproved.**
  - Requests have no PC string. The name repeats the 8.28.2 response string
    `OnPacket_PAWN_GET_PAWN_HISTORY_LIST_RES` (handler `0x7EB1C0`, a tier-0 seed whose widths
    equal PS4's).
  - It reaches the request only through the PC's own g.id pairing (I).
  - PS4 `cSeedGameSvConnection::Send_C2S_GET_PAWN_HISTORY_LIST_REQ` `0x19B6090` exists once and also
    writes one u32 after its header. That agrees, but a one-u32 payload is not distinctive.

### 3.3 Structures

| Type | Verdict | Evidence (V) |
| --- | --- | --- |
| `cSeedGameSvConnection` (1,344 B: `vft`@0, `mpManager`@316, opaque) | **size holds; `vft` holds; `mpManager` unproved** | PC DTI registration `0x1A2B1B0`: `MtDTI("cSeedGameSvConnection", parent cSeedServerConnection DTI, 0x540)`. Allocation `0x877840` `alloc(0x540)` → ctor `0x78F060`, which writes vtable `0x1BC5C38` (slot 4 = `getDTI` → `dti_cSeedGameSvConnection`) and a second vptr at **+0x110**. The highest `this` offset any of the 1,040 handlers touches is 0x538+4 ≤ 0x540. +316 is a 4-byte field read in 46 handlers. PC base `cSeedServerConnection` DTI size is **0x110** (`0x1A45DB0`), and PS4 has `mpManager` as the first own member (`cNetGameServer*`@280 after a 280-B base). The extra PC vptr at +0x110 shows the PC layout differs from PS4, so the name at 316 is not proved (I: plausible). T001's "no located evidence" for 1,344 B is now closed. |
| `nUserSession::CPacket_S2C_GET_STAGE_LIST_RES` (48 B) | **holds** for size and accessed members; names partly neutral | The handler `0x7FD9E0` reserves `sub esp, 30h` and fills `vft`@0, u8@4 = 0x0C, u16@6, dword@8 = 2, @12, @16, @20, the `MtTypedArray`@24..43 and u8@44. `ReadPacket` `0x81CC40` reads `Read_s32` into @16 and @20, the array into @24, and stores @12 and @44. Every access lands on a member start with that member's width. PS4 DWARF for the same class has `m_usError` u16@8 and `m_ucResult` u8@10, which is a different 64-bit layout and different widths. The PC names `mError`/`mResult` are role names (I). |
| 6 peer structs (`MtMemoryStream` 28, `nNetwork::Coder` 44, `Decoder` 40, `PacketBase` 36, `PacketReader` 96, `PacketWriter` 1,644) | **accesses hold; sizes unproved** | I decompiled the 30 peer methods: 0 off-member casts or pointer arithmetic on these types; every access is a named member. Sizes not checked against allocations (not run). |
| 3 `_vtbl` types (`PacketBase`, `PacketReader`, `PacketWriter`) | not checked beyond slot 0 | each declares one slot, `scalarDeletingDestructor` |

There are also types I did not audit, which the earlier work or another source left:

- `CPacketBase` (28 B, PS4-style member names such as `_vptr$CPacketBase` and `m_pReader`@12; the
  codecs' accesses at +12 and +16 agree).
- `CDataStageInfo`, with size **37**, which is suspicious with 4-byte members and no tail padding.
- `CDataStageAttribute` (16).

### 3.4 Codec pairs: PC call-site alignment

| Pair | Identity (V) | Callers: sites / functions (V) | PS4 overload at aligned positions (V) | Verdict |
| --- | --- | --- | --- | --- |
| `0x8BC480` `Read_s32` / `0x8BC4D0` `Read_u32` (74 B) | byte-identical; **`0x8BC520` `Read_f32` too** | 1,425/731 · 2,023/1,021 · f32 20 | body: 480↔s32 **23**, 480↔u32 2, 4D0↔u32 **551**, 4D0↔s32 **0**; header Result: 480↔s32 267, 480↔u32 29 | `Read_u32` holds; `Read_s32` holds with a caveat: the compiler did not fold them, but the PC source routes some PS4-u32 fields (all header `Result`s of groups 11/13/28/29) through it |
| `0x8BC410` `Read_u8` / `0x8BC6E0` `Read_bool` (35 B) | byte-identical | 705/408 · 263/176 | 410↔u8 **216**, 6E0↔bool **43**, crossings **0** | both hold |
| `0x8BC660` `Read_s64` / `0x8BC6A0` `Read_u64` (60 B) | **not byte-identical**: one byte differs at +0x20, the rel32 of `call sub_8BC340` (same target); otherwise identical | 67/48 · 117/82 | 660↔s64 **11**, 6A0↔u64 **38**, crossings 0 | names hold; `Read_s64`'s `unsigned __int64 *` pointee contradicts its name (**C**, minor) |

- **Basis**: 296 response seeds and 2 notice seeds. Each is a tier-0 handler with a unique PS4
  partner and equal width strings, so signedness was not used to pair them.
- **PS4 order**: the PS4 address order of the overloads (u8, u16, u32, u64, s8, s32, s64, bool, f32,
  f64, bytes) differs from the PC order. Address order gives no evidence.
- **Writer pairs**: `0x8BC860`/`0x8BCB80` (`Write_u8`/`Write_bool`) and `0x8BC8D0`/`0x8BC920`
  (`Write_s32`/`Write_u32`) are also code-identical. I did not run a sender alignment, so their names
  are **unproved**.
- **ReadBytes**: `CPacketBase::ReadBytes` `0x8BC750` has a single call site, so the codecs read
  inline. I did not check the name.

### 3.5 The 46 other user-named handlers (outside the 006 contracts, origin unattributed)

| Count | Verdict |
| --- | --- |
| 32 | **Holds**: equals the PC string it references. |
| 1 | **Holds**: equals its unique tier-0 PS4 partner. |
| 2 | **Wrong form**: `0x7C6510`, `0x7C61F0` are named `OnPacket_S2C_BAZAAR_…`, but the PC string is `OnPacket_BAZAAR_…`. The PS4 symbol exists and the widths are equal. |
| 5 | **Unproved**: `0x7F4790`, `0x7D7770`, `0x7D80C0`, `0x7D7810`, `0x7D3960` are notices with no PC string. A PS4 symbol of that name exists, and the widths are equal after the PS4 u16. The name source is not code (I: a packet list). |
| 5 | **Unproved**: `0x7F5A20` `QUEST_11_106_16_NTC`, `0x7F04F0`, `0x7F4AB0`, `0x7E1E70`, `0x7C50D0`. No PC string, and either no PS4 symbol or different widths. |
| 1 | **Wrong**: `0x7D36B0` is named `cNetGameServer::OnPacket_S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LEAVE_NTC`. It is a `cSeedGameSvConnection` table entry, and no PS4 symbol has that name. |

## 4. Tier-0 feasibility (counts)

| Count | Value (V) |
| --- | --- |
| `OnPacket_` strings in PC (all `cSeedGameSvConnection::`) | 675 |
| table callbacks referencing exactly 1 / several / no `OnPacket_` string | **580 / 0 / 460** |
| strings referenced by no code | 54 |
| strings referenced by exactly one function | 615 (575 table callbacks, 40 elsewhere) |
| strings referenced from two places | 6 |

The six strings with two referrers:

- `QUEST_GET_PACKAGE_QUEST_LIST_RES` (`0x7F1BB0` plus data at `0x45668B8`).
- `SKILL_SET_ABILITY_RES`, `SKILL_SET_OFF_PAWN_SKILL_RES`, `POTION_ORB_ELEMENT_CHECK_RES` and
  `POTION_JOB_ELEMENT_RELEASE_RES`: each has its table callback plus a data reference at
  `0x2BDF3C0`-`0x2BDF5D8`.
- `SKILL_GET_ABILITY_COST_RES`: code at `0x7FA970` outside any function, plus data.

None of these makes a function reference several strings.

Strings referenced only from code outside a table callback (40):

- Code that IDA did not make a function, e.g. `0x7FE8FD`, `0x7F148F`, `0x7DA07D`.
- Functions that start inside a handler, e.g. `0x7C68DE`, `0x7F178E`.

These are boundary gaps (I) to repair or list before Tier-0. They likely cover some of the 460
string-less callbacks.

The 580 single-string callbacks against PS4 (group-prefix rule):

| Count | Result |
| --- | --- |
| 412 | Unique PS4 partner. No PS4 symbol is used twice, and every partner has one body. 296 are equal (RES), 2 are equal (NTC) and 114 differ. All 114 are responses. |
| 166 | No PS4 partner. |
| 2 | Several PS4 partners. |

## 5. PS4 readiness (10 handlers + 10 readers)

Sampled:

- **Handlers**: `CHARACTER_GOLDEN_REVIVE_RES`, `GET_PAWN_HISTORY_LIST_RES`, `GET_SERVER_LIST_RES`,
  `GET_STAGE_LIST_RES`, `PARTY_SEARCH_RES`, `QUEST_PROGRESS_NOTICE`, `GP_COURSE_END_NTC`,
  `BAZAAR_GET_ITEM_PRICE_LIMIT_RES`, `LOBBY_JOIN_RES` and `GET_MYPAWN_DATA_RES`.
- **Readers**: 5 of 150 `CPacket_S2C_*::ReadPacket` (every 30th) and 5 of 363 `nPacket::Read_CData*`
  (every 73rd). Reader VAs: `0x19D4760`, `0x19D6F10`, `0x19D8B80`, `0x19DAAF0`, `0x19DDE00`, `0x19E11D0`, `0x19EFAE0`, `0x19FF950`, `0x1A103E0`, `0x1A1F480`.

| Item | IDA PS4 database (V) | DWARF dump only (V for one function) |
| --- | --- | --- |
| Prototype | 20/20 user-set (`is_userti`), with DWARF parameter names and types: `BOOL __fastcall(cSeedGameSvConnection *this, CPacket *pPacket)`, `s32 (… *this, CPacket *pPacket)`, `int (CPacket *packet, MtTypedArray<CDataX> *ar)` / `(CPacket *packet, CDataX *d)` | same names; the DWARF also gives location lists |
| Local names | 0/20 functions have saved Hex-Rays local settings. 12/20 show a few user-flagged locals that look like DWARF names (`v`, `ar`, `packet`, `d`, `nRet`; `packeta` is a collision rename). The rest are `vN` or Hex-Rays automatic names taken from expressions (`mpManager`, `Allocator`, `p_m_usError`), which are not DWARF. | Example: `OnPacket_S2C_CHARACTER_GOLDEN_REVIVE_RES`, DIE `0x09e9cb3b`. Locals `tmpErr` (`s32`, location list), `pContext` (`cContextInstHm*`, location list), `packet` (`nUserSession::CPacket_S2C_CHARACTER_GOLDEN_REVIVE_RES`, no location), plus 3 lexical blocks and inlined subroutines. IDA shows none of those three names. |
| Struct types | 7/7 present with DWARF members, in the **64-bit** layout. The 7 types: `CPacket_S2C_GET_STAGE_LIST_RES` 56 B, `…PAWN_HISTORY_LIST_RES` 56, `CDataPawnHistory` 104, `CDataStageInfo` 56, `CDataEquipBindNotice` 32, `…DECIDE_CHARACTER_ID_RES` 1,768, `cNetGameServer` 36,248. `cSeedGameSvConnection` is 1,600 B with 1 base and members such as `mpManager`@280. | DIE ids and members, same source |

**Reading (I).** IDA's DWARF import brought in prototypes, parameter names and types, but almost no
locals. The likely reason is that it skips variables that live in location lists or have no
location. The local-transfer rule in `spec.md` therefore needs locals from the DWARF dump, keyed by
the defining operation. The PS4 database's local names are not a usable source. I streamed only one
function's DIE subtree; the import gap for the other 19 is inferred.

## Not run / limits

- I did not check the writer-codec name pairs against senders.
- I did not check the peer struct sizes against allocations.
- I did not audit the 629/551 propagated caller prototypes individually; the TSV lists them with
  verdict "not checked".
- I did not check helper names and comments (87 helper and 39 sender user names) beyond the
  inventory.
- I did not audit `CDataStageInfo` (37 B) or `CPacketBase`.
- The DWARF local comparison covers 1 of the 20 sampled functions.
- I did not trace the 460 string-less callbacks against the 40 strings referenced from orphan code.
- Tooling: ida-mcp `execute_python` on both private copies. Offline Python 3.15 over JSON dumps in
  the session scratchpad (`pc_table.json`, `pc_flat.json`, `ps4_flat.json`, `t002_seeds.json`,
  `check50.json`, `v50.json`). None of these is committed.
