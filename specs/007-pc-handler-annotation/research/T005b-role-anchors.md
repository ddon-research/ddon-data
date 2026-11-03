# 007 T005b: anatomy of handlers, readers, codecs and senders (evidence for role anchors)

Builds, databases, basis:

- PC **03040008**: private copy `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t005b/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (`private-copy.sh pc-accepted t005b`, the ddon-hook accepted database). I checked `idc.get_idb_path()`:
  32-bit, image base `0x400000`, input sha256 `f1c974d0…fa20`.
- PS4 **02020005**: private copy `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t005b/DDOORBIS.elf.i64`.
  I checked: 64-bit, image base `0`, input sha256 `4236f598…63c0`.
- Seeds: the 467 accepted rows of `research/03040008/ida-transfer/manifest/pairs.tsv` (T005, `499f7c701d`; all 467
  are `cSeedGameSvConnection` **RES** handlers, sub 2). Dumps: `dumps/pc-ida.jsonl` (sha256 `57cb8404…`, taken from the
  `ddon-data-007work` copy *after* the T004 repairs) and `dumps/ps4-ida.jsonl` (`cc4c7c10…`).
- All addresses are IDA VAs. Marks: **V** = verified here by code, **I** = inferred, **C** = contradicted.
- I worked read-only in substance: no renames, retypes, comments or saves.
- **Coverage caveat**: the accepted copy is the database *before* the T004 repairs. 62 of the 467 PC seed handlers
  are not function starts in it (405 are). For those 62, call lists come from the dump. 35 of them are undefined
  code in this copy, so their listener index could not be read (see §1.3). 34 call targets inside readers lie at
  `0x758000`-`0x77C000` and are not functions in this copy (for example `loc_75880E+2` = `0x758810`). These are element
  readers with broken function boundaries, and the dump does not cover them either. They cut 36 reader sequences
  short; I list those pairs as coverage gaps, not as differences.
- Method: in the PC worker and the PS4 worker I flattened each reader's call tree (by call site address, recursive,
  depth ≤ 8) into a width string. Codec calls become width tokens, and each callee that contains codecs becomes a
  bracket. On PS4 I descended only into `nPacket::Read_*` and `CPacket_*::ReadPacket`; on PC into every callee
  except `callOnPacketFunc` `0x878860`, the allocator `0x8BC2E0` and `MtMemoryAllocator::getAllocator`. I moved the
  strings from the PS4 worker to the PC worker by value and compared them there. Nothing was written to disk except
  this report.

## 0. Answer in brief

- **PC handler = one reader call (V)**: 463 of the 467 PC seed handlers have exactly one callee that calls a codec
  read function directly or one level down, and none calls a codec itself. The 4 others (`0x7C44C0`, `0x7E64D0`,
  `0x7EDD70`, `0x7FB860`) call their reader at an address that is not a function in either database (coverage gap).
  The 463 readers are distinct: no reader is shared by two handlers.
- **PS4 inlines the reader (V)**: only 88 of the 467 PS4 handlers call a `CPacket_*::ReadPacket`, and in all 88 the
  class name is `CPacket_<handler NAME>`. 378 call the `nPacket::Read_*` codecs directly, with `ReadPacket`
  inlined. One (`0x7E5F30`'s partner) shows no codec call.
- **Listener slot index (V, new)**: each PC RES handler passes an immediate slot index to `callOnPacketFunc`
  (`0x878860`). The PS4 handler inlines the same logic as `mpManager->mErrorCode[idx]`. The indices **differ**
  between seasons (72 of 427 equal), but the map PS4 idx → PC idx is **strictly order-preserving over all 427 pairs
  (0 inversions)**.
- **Codec width (V)**: each PC codec body states its width three times: the bounds check `lea r,[cur+N]`, the cursor
  advance `add [m_pReader],N`, and the return `mov eax,N`. The byte swap matches the width. The PC `s32`/`u32`/`f32`
  bodies are byte-identical, and so are the PS4 `Read_u32`/`Read_s32` bodies (both use `movbe`). Width therefore
  carries no signedness on either side.
- **Width sequences** (PC header `44` = s32 error + s32 result, PS4 header `24` or `2`; bodies compared):
  - 329 are **equal**, 94 of them with an empty body.
  - 20 PC bodies extend the PS4 body as a prefix.
  - 40 PS4 bodies are a proper subsequence of the PC body.
  - 8 are PC ⊂ PS4.
  - 29 differ otherwise (width changes such as u8→u16 or u32→u64).
  - 36 are coverage gaps, 4 have no PC reader, 1 has no PS4 codec.
- **Is width alone enough?** Only for equal sequences. Where the PC body has insertions, the PS4 body embeds in it
  in more than one way in 38/40 subsequence pairs and in 13/20 prefix pairs.
- **Element readers (V)**: in the 136 equal-width pairs that have brackets, 220 of 222 PS4 `nPacket::Read_CData*`
  calls have a PC callee spanning exactly the same codec positions. Those 220 occurrences pair **117 distinct PS4
  functions with 117 distinct PC functions, a bijection with 0 conflicts**. PC has 44 further brackets where PS4
  inlined.
- **Senders (V)**: all 658 PC `WritePacket` (`0x8BCBB0`) call sites push group, id and sub as immediates, as
  `push -1; push sub; push id; push group; push packet`. The key is never computed.
  - 408 RES seeds have exactly one PC sender with key `(g,id,1)`.
  - 4 have two: one game sender and one sender in the login-connection code at `0x88A6xx`-`0x88A9xx`, which reuses
    group/id numbers.
  - 55 have none.
- **REQ/RES by code (V)**: on both sides a requester function sets `mStatus[idx]`/`mErrorCode[idx]`, calls
  `reserveNetworkErrorDialog(idx)` and calls the sender; the RES handler reports through the same `idx`.
  - On PC, for 327 seeds the requesters of the handler's slot reach only senders with key `(g,id,1)`; 17 are
    ambiguous (shared slots), 1 mismatches (a login-manager slot collision).
  - On PS4, for 321 seeds the slot requester calls exactly `Send_C2S_<NAME>_REQ`; 17 ambiguous, 3 differ (e.g.
    `SET_PAWN_PROFILE_RES` ↔ `Send_C2S_SET_PAWN_PROFILE_COMMENT_REQ`).
  - So "`<NAME>_REQ` of the same g.id" is a **convention, proved per pair only by the slot link**.

## 1. Handler anatomy

### 1.1 Six pairs (call sites in address order)

| # | Pair | PC 03040008 call sites | PS4 02020005 call sites |
| --- | --- | --- | --- |
| 1 | RES, stack packet: `PAWN_GET_PAWN_HISTORY_LIST_RES` 8.28.2, PC `0x7EB1C0` ↔ PS4 `0x2E8620` | `0x7EB22F` reader `sub_812720` (thiscall, ecx = stack packet, `ret 4`); `0x7EB23E` dtor `sub_79E1C0` (failure path); `0x7EB26E` `callOnPacketFunc(mgr=[this+0x13C], 91, "…OnPacket_PAWN_GET_PAWN_HISTORY_LIST_RES", dword_1BC780C, result, 1)`; `0x7EB28C` `sub_883010` (manager set, I); `0x7EB29B` `sub_52FE10` (array clear, I); `0x7EB2A9` dtor `sub_79E1C0`. Inline ctor: vtable `off_1BC3D50`, u8 +4 = 8, u16 +6 = 28, u32 +8 = 2, i.e. **the packet's own g.id.sub** | `0x2E8696` `Read_u16` (m_usError); `0x2E86AD` `Read_s32` (m_nResult); `0x2E86BD` `Read_CDataPawnHistory_`; `0x2E8747` `sNetworkExt::requestNetworkErrorDialog` (inlined listener logic on `mErrorCode[91]`/`mStatus[91]`); `0x2E8778` `cNetGameServer::setPawnHistoryList`; then array destruction (`[rax+8]` virtual dtors, `getAllocator`, `[rcx+70h]` free) |
| 2 | RES, heap packet: `ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_RES`, PC `0x7C3450` ↔ PS4 `0x309890` | `0x7C3462` `[eax]` old packet's virtual dtor (`this+0x454`); `0x7C3472` `sub_8BC2E0(0x30,0x10)` = allocator (vtable `+0x1C` of `src_7`, tag `0x309`); `0x7C3480` ctor `sub_785AC0`; `0x7C349B` reader `sub_7FF7D0`; `0x7C34B2` `[eax]` dtor on failure; `0x7C34E7` `callOnPacketFunc(…, 612, …)` | `0x3098B3` `[rax+8]` old packet dtor; `0x3098CB` `CPacket_S2C_…::operator_new` (ctor inlined); `0x30992C` `Read_u16`; `0x30993F` `Read_s32`; `0x30994F` `Read_CDataAchieveRewardCommon_`; `0x3099BF` `[rax+8]` dtor on failure; `0x3099E5` `requestNetworkErrorDialog` (slot 532) |
| 3 | RES with Season 3 extra field: `SERVER_GET_REAL_TIME_RES` 1.4.2, PC `0x7F95C0` ↔ PS4 `0x2DE130` | `0x7F9619` reader `sub_81A770` (widths `4482`); `0x7F964B` `callOnPacketFunc`; `0x7F9673` `sub_BB3E90` | `0x2DE182` `Read_u16`; `0x2DE195` `Read_u64`; `0x2DE1A5` `Read_u16` (widths `282`: **no** `m_nResult`); `0x2DE1D7` `sNetworkExt::setWorldServerTime`. No `mErrorCode` slot (handler without listener). PC has `s32,s32` header where PS4 has `u16` only. With the header rule the bodies are equal (`82`); the "PC +1 u32" in T002 is the result field |
| 4 | NTC: `GP_COURSE_END_NTC` (PC key 28.27.16), PC `0x7D7770` ↔ PS4 `0x30C2A0`, **not a seed** (no PC string; name from earlier work, I) | `0x7D77B7` reader `sub_809230` (widths `44`); `0x7D77DE` `sGame::isChargeAnnounce`; `0x7D77F0` `sGame::setChargeCourse`. Stdcall (one stack argument, no `this`), no `callOnPacketFunc`. Inline ctor writes u8 28, u16 27, u32 16 | `0x30C2EF` `Read_u16`; `0x30C302` `Read_u32`; `0x30C312` `Read_u32`; `0x30C345` `isChargeAnnounce`; `0x30C362` `setChargeCourse`. PS4 still reads `m_usError`, so PS4[1:] = PC |
| 5 | NTC, heap packet: `QUEST_PROGRESS_NOTICE`, PC `0x7F4790` ↔ PS4 `0x2EC6C0`, **not a seed** | `0x7F4795` `sub_8BC2E0(0x30,0x10)`; `0x7F47A3` ctor `sub_78C1E0`; `0x7F47B4` reader `sub_818410` (head `44`, then an array of `CDataQuestProcessState`); `0x7F47C3` `[eax]` dtor on failure; `0x7F47D0` `sub_646390` (notice object, I); `0x7F47DF` `getQuestSvNoticeMgr`; `0x7F47E6` `pushNotice` | `0x2EC6D7` `operator_new(0x40)`; `0x2EC738` `Read_u16`; `0x2EC748`/`0x2EC758` `Read_u32` ×2; `0x2EC76B` `Read_CDataQuestProcessState_`; `0x2EC790` `cQuestSvNotQuestProgress::MyDTI::newInstance`; `0x2EC7A6` `getQuestSvNoticeMgr`; `0x2EC7B1` `pushNotice`; `0x2EC7CC` dtor |
| 6 | Login: `cSeedLoginSvConnection::OnPacket_L2C_LOGIN_RES` PS4 `0x37C800` | **not reached.** The PC class is registered (`MtDTI` at `0x1A36A00`, size `0x170`). Vtable `0x1BD6AF0`: slot 6 = getDTI `0x88C690`, and slots 21/22 are thunks `mov ecx,[ecx+110h]; jmp sub_88CF90`. Most code at `0x888000`-`0x88E000` is not defined as functions in the accepted copy, and slot 23 runs into junk bytes and `jmp sub_365EB4A`. The PS4 dispatcher `cSeedLoginSvConnection::callOnPacketFunc` `0x1A3E380` indexes a member-pointer table `off_251C500` (`getOnPacketFuncNum` = 21); I did not find the PC counterpart table in the time box | `0x37C855` `Read_u16`; `0x37C86C` `Read_s32`; `0x37C87C` `Read_MtString`; `0x37C9BA` `[rax+70h]` (string free). Listener inlined on `cNetLoginServer::mErrorCode[4]` |

Shapes (V over the sample, I as a general rule):

- **PC stack packet**: reader, dtor (failure), `callOnPacketFunc`, post-processing, dtor. This gives the typical
  "2 PC calls" T005 counted.
- **PC heap packet**: old-dtor (indirect), allocator, ctor, reader, dtor (indirect), `callOnPacketFunc`, which is
  T005's "6 PC calls". 137 seeds call `0x8BC2E0` in their handler.
- **PS4**: the reader and the listener body are inlined. It shows 2-4 codec calls, element readers,
  `requestNetworkErrorDialog`, allocator and dtor calls, and `__stack_chk_fail`. That is why no callee is forced
  in T005.

### 1.2 Counts over the 467 seeds (V)

- **PC**: 463 have exactly one callee that calls codecs directly or one level down, and 0 handlers call a codec
  directly. The 4 others have no reader in either database (coverage gap).
  - The 463 readers are 463 distinct functions.
  - Every reader call has `ecx` loaded, and the reader ends with `ret 4` (thiscall, `(packet object, CPacket*)`).
  - The dump's push count at the call is 1 in 185 cases, 2 in 271, and 0/3/4 in 7, because pushes that are not
    arguments get mixed in. Arity is better taken from `ret 4`.
- **PS4**: 88 call exactly one `CPacket_*::ReadPacket`, and **all 88** name `CPacket_<NAME>` of the handler. 378
  call no `ReadPacket` but call codecs directly. 1 has neither.

### 1.3 Listener slot index (V)

- **The mechanism.** `callOnPacketFunc` `0x878860` (thiscall, `ret 0x14`) writes:
  - `this[743+idx] = result` (mErrorCode).
  - `this[1+idx] = 2` on success or `4` on error (mStatus).
  - It clears `byte[9654+idx]` and calls `sub_BB3980(result)` when `byte[8912+idx]` is 0 (I: the
    `requestNetworkErrorDialog` counterpart).
  - PS4 inlines exactly this logic against `cNetGameServer::mErrorCode[idx]`, `mStatus`, `mIsNgErrorDialog` and
    `mIsOnceNgErrorDialog`.
- **Pairs read**: I read the slot as the immediate pushed last before the call in 432 PC handlers. For the other 35,
  the handler is undefined code in this copy. PS4 had one `mErrorCode[...]` index in 462 handlers: 4 had none
  (`GET_REAL_TIME`, `0x7EF7A0`, `0x7F1F50`, `0x7E5F30` partners) and 1 had two (`0x7EA9D0`: 61, 62). That leaves
  427 pairs with an index on both sides.
- **Result**: the index is equal in 72 pairs and different in 355 (most common PC−PS4 deltas: +70 ×97, +71 ×56,
  +74 ×52). Sorted by PS4 index, the PC index **never decreases (0 inversions in 427)**. Each side has 5 slots shared
  by two handlers.
- **Reading (I)**: Season 3 inserted slots into the same ordered list. The slot is not an identity across builds, but
  it is a monotone order constraint and the code-level REQ↔RES link (§5).

## 2. Codecs

### 2.1 PC read codecs (V, bodies disassembled)

`CPacket` cursor at `+0x0C` (`m_pReader`), limit `+0x10` (`m_pWriter`).

| VA | earlier name | width evidence in the body | swap |
| --- | --- | --- | --- |
| `0x8BC410` | Read_u8 | `lea eax,[ecx+1]`; `inc [m_pReader]`; `mov eax,1`; byte store | none |
| `0x8BC6E0` | Read_bool | byte-identical to `0x8BC410` (T002) | none |
| `0x8BC440` | Read_u16 | `lea [ecx+2]`; `movzx word`; `add [m_pReader],2`; `mov eax,2` | `shr 8 / shl 8 / xor` |
| `0x8BC480` | Read_s32 | `lea [ecx+4]`; `add …,4`; `mov eax,4` | 4-byte swap with `and 0FF00h`/`shl 10h`/`shr 18h` |
| `0x8BC4D0`, `0x8BC520` | Read_u32, Read_f32 | byte-identical to `0x8BC480` (T002) | same |
| `0x8BC570` | Read_f64 | `lea [ecx+8]`; pushes both dwords; `call 0x8BC340` (64-bit swap, `shld`/`shrd`) | 8 |
| `0x8BC660`, `0x8BC6A0` | Read_s64, Read_u64 | `lea [ecx+8]`; stores, then `call 0x8BC340`; `add …,8`; `mov eax,8`. The two differ only in the rel32 of the call (T002) | 8 |
| `0x8BC5B0` | Read_MtString | `lea [eax+2]` and a 2-byte-swapped length; `cmp` with `0x800`; `memset` of a 0x800 buffer; `CPacketBase::ReadBytes` `0x8BC750` (length); `sub_4030A0` (MtString assign, I) | u16 length + bytes |
| `0x8BC710` | Read_bytes | `count` argument: `sub [m_pWriter],[m_pReader]`, `cmp`, `memcpy`, `add [m_pReader],count` | none |

PC writers (`m_pWriter` `+0x10`, end `+0x14`):

- `0x8BC860` (1), `0x8BC890` (2, swapped), `0x8BC920` (4, swapped) were checked. `0x8BC8D0`, `0x8BC970`,
  `0x8BC9D0`, `0x8BCB40`, `0x8BCB80`, `0x8BC790` (MtString) and `0x8BCA30` (cstr) were classed by size and T002
  identity, not disassembled here (I).
- The width rule is `cmp eax,N` on the room left, `add [m_pWriter],N` and `mov eax,N`.

### 2.2 PS4 codecs (V, symbols; bodies checked for u8/u32/s32)

- **Readers**: `nPacket::Read_u8` `0x3B6140` (1), `Read_u16` `0x3B6160` (2), `Read_u32` `0x3B6190` (4, `movbe`),
  `Read_u64` `0x3B61B0` (8), `Read_s8` `0x3B6250`, `Read_s32` `0x3B6280` (4, `movbe`; same instructions as
  `Read_u32`), `Read_s64` `0x3B62A0`, `Read_bool` `0x3B6340`, `Read_f32` `0x3B6360`, `Read_f64` `0x3B6380`,
  `Read_MtString` `0x3B6420` (u16 length, `lea r12,[r14+2]`), `Read_bytes` `0x3B65F0`.
- **Writers**: `Write_u8` `0x3B6640`, `Write_u16` `0x3B6660`, `Write_u32` `0x3B6690`, `Write_u64` `0x3B66C0`,
  `Write_s8` `0x3B6760`, `Write_s32` `0x3B6790`, `Write_s64` `0x3B67C0`, `Write_bool` `0x3B6860`, `Write_f32`
  `0x3B6880`, `Write_bytes` `0x3B68B0`, `Write_f64` `0x3B68F0`, `Write_MT_CSTR` `0x3B69A0`, `Write_MtString`
  `0x3B6A20`.
- There are 355 `nPacket::Read_CData*` and 30 `Write_CData*` symbols in the PS4 dump.

### 2.3 Width sequences over the seeds (V; PC header `44`, PS4 header `24`, or `2` when PS4 has no result)

- **The header is not width-equal.** The PC reader reads `s32` at `+16` (error); if it is non-zero it copies the
  value to `+20` and returns. Otherwise it reads `s32` at `+20` (result).
- Readers also store the header's u32 at `m_pStart+5` (swapped) into `+12`, inline, with no codec. That field is
  invisible to width alignment.
- PS4 reads `u16 m_usError`, then `s32 m_nResult`. The first PS4 token is therefore always `2`, and the first PC
  token pair `44`. `GET_REAL_TIME_RES` has no result field on PS4.

| category | pairs | of which coverage gaps (PC reader reaches a non-function element reader) |
| --- | --- | --- |
| body equal | 329 (94 with an empty body, 84 of 1-2 tokens, 75 of 3-5, 76 of 6+) | 0 |
| PC body = PS4 body + tail (prefix) | 20 | 0 |
| PS4 body ⊂ PC body (insertions), not a prefix | 41 | 1 |
| PC body ⊂ PS4 body | 40 | 32 (8 real, e.g. `0x7C8550` `UPDATE_CHARACTER_EDIT_PARAM_RES`: PS4 reads a u32 PC does not) |
| other (width changes) | 32 | 3 (29 real: `0x7DB090` u32→u64 at position 2; `0x7D1350` last u8→u16; `0x7CEFD0` group mid-body) |
| PC reader missing / PS4 no codec | 4 / 1 | - |

- **Is width alone enough?** Yes for the 329 equal bodies: position-by-position alignment is forced. Of those, 94
  with an empty body and 84 with 1-2 tokens prove little about the pairing.
- For the 20 prefix extensions, alignment is forced if "Season 3 appends" is assumed (a convention). Without that
  assumption, the PS4 body embeds in 1 way in 7 cases, 2-9 ways in 8 and 10+ ways in 5.
- For the 40 insertion pairs without a gap, the embedding is unique in 2, has 2-9 ways in 21 and 10+ in 17. **Width
  alone does not align them**; brackets (§3) or a unique-embedding gate must decide.
- Signedness and float/int never come from the PC side, because the `s32`/`u32`/`f32` bodies are one function body
  copied three times.

## 3. Element readers

- **PS4 (V)**:
  - Arrays are `nPacket::Read_CDataX_(CPacket*, MtTypedArray<CDataX>*)`, which reads `u32` count, allocates and
    calls the element reader `Read_CDataX` (example `0x1A2A2B0` → `0x1A2A530`).
  - Often the element body is inlined into the array reader (for example PS4 `(4444441)` against PC
    `(4(444441))` in `0x7C3280`).
  - On PS4, `ReadPacket` is itself inlined into 378 handlers.
- **PC (V)**:
  - Array readers are cdecl `(CPacket*, array*)`, for example `sub_772020`. The sequence is `Read_u32(count)`,
    `sub_864A60` (grow), then per element `sub_8BC2E0(0x40,0x10)`, ctor `sub_784AF0`, and element reader
    `sub_7720E0`.
  - PC keeps more sub-element calls than PS4. In `0x7EB1C0`, for example, PS4 is `(4(44SSS88114111))` and PC is
    `(4(4(4SSS)88114(111)))`.
- **Alignment check** (equal-width pairs with any bracket: 136):
  - The PS4 `Read_CData*` call occurrences number 222. Of these, 220 have a PC callee with **exactly the same
    codec span** (taking the outermost PC callee when several share a span).
  - Those 220 occurrences give **117 PS4 functions ↔ 117 PC functions**. No PS4 function maps to two PC functions,
    and none the other way.
  - The 2 unmatched are one PS4 function, `0x1A013B0`, in `0x7CCAE0` and `0x7CCBA0`, where PC inlined it (I).
  - PC has 44 further bracket spans with no PS4 call (PS4 inlined). They must stay unnamed.
- **Readers of §1** (pairs 1-3):
  - Pair 1: the PS4 `Read_CDataPawnHistory_` `0x1A2A2B0` and its element `0x1A2A530` span the same codecs as PC
    `sub_772020` and `sub_7720E0`. PC adds `(4SSS)` and `(111)` sub-calls.
  - Pair 2: PS4 `Read_CDataAchieveRewardCommon_` ↔ PC `sub_7584B0` (body `(414)`, equal span).
  - Pair 3: no element readers.

## 4. Senders

- **PC id passing (V)**: `nUserSession::CPacket::WritePacket` `0x8BCBB0` is cdecl `(CPacket*, u8 group, u16 id,
  u8 sub, int a5)`.
  - It writes, inline, `u8 group`, the swapped `u16 id`, `u8 sub` and `u8 0`.
  - It then calls `Write_u32(0)`, and `Write_s32(a5)` when `a5 ≥ 0`.
  - All **658** call sites (643 functions plus 16 sites outside functions) push `group/id/sub` as **immediates**
    (`push 0FFFFFFFFh; push 1; push 1Ch; push 8; push eax` in `0x833670`). The key `(sub<<16)|id` exists only in
    the handler table, never in senders.
  - Sub values: 617 are 1 (REQ), 38 are 16 (NTC), 3 are 2 (`0x821840` 2.1.2, `0x83A9D0` 68.0.2, `0x842050` 68.1.2).
  - Keys: 651 distinct, 7 of them used at more than one site.
- **Two PC sender shapes (V)**:
  - `Send_*`: thiscall. It builds a stack `CPacket` with a 25,000-byte buffer from `src`, calls `WritePacket` and
    the payload writers, calls `cSeedServerConnection::Send` `0x9D6A20`, and ends with `ret N`.
  - `CPacket_C2S_*::WritePacket`: cdecl `(CPacket*, …)`, header plus payload only (e.g. `0x840B20`).
- **PS4 id passing (V)**: `Send_C2S_*` writes `Write_u16(0)`, `Write_u16(<flat id>)`, `Write_u16(0)` and then the
  payload, and patches the length with `movbe`. The flat id is an immediate `esi` in 381 of 393 `Send_C2S_*`. It
  is unrelated to the PC g.id (memory rule: PS4 flat ids never name PC packets).
- **Five REQs whose RES is a seed.** "Slot link" means the slot requester calls this sender (§5); widths are the
  payload after the header.

| RES seed (PC key) | PC sender | PS4 sender | PC / PS4 payload widths | slot link |
| --- | --- | --- | --- | --- |
| `GET_PAWN_HISTORY_LIST` 8.28 (slot PC 91 / PS4 91) | `0x833670` | `Send_C2S_GET_PAWN_HISTORY_LIST_REQ` `0x19B6090` (flat id `0x46`) | `4` / `4` | yes: PC requester `0x86F4B0` (`this[92]`, `reserveNetworkErrorDialog(91)`, `this[834]=33000`); PS4 `cNetGameServer::getPawnHistoryList` `0x34A576` |
| `ADD_BLACK_LIST` 17.1 (PC 521 / PS4 447) | `0x820440` | `Send_C2S_ADD_BLACK_LIST_REQ` `0x19CAA70` | `4SSS` / `4SSS` | yes |
| `START_ATTACH_ELEMENT` 30.6 (PC 326 / PS4 256) | `0x840B20` (cdecl WritePacket shape) | `Send_C2S_START_ATTACH_ELEMENT_REQ` `0x19BDED0` | `C4S1444` / `C4S1444` | no direct requester call (its caller builds the packet, I) |
| `ENTRY_BOARD_ITEM_CREATE` 34.2 (PC 465 / PS4 394) | `0x826AE0` | `Send_C2S_ENTRY_BOARD_ITEM_CREATE_REQ` `0x19C67B0` | `8C114421422S42441` / `8C114421422S4241` (PC +1 u32 inside the element) | yes |
| `GET_SET_CONTEXT` 35.7 (PC 485 / PS4 411) | `0x8249E0` | `Send_C2S_GET_SET_CONTEXT_REQ` `0x19C7910` | `484444` / `44444` (PC inserts u64) | yes |

- **Counts over the 467 seeds (V)**:
  - By key `(g,id,1)`: 408 have exactly one sender, 4 have two (one each in game code and in the
    login-connection code `0x88A600`-`0x88A900`), and 55 have none.
  - Of the seeds with a unique game sender whose PS4 `Send_C2S_<NAME>_REQ` exists (329), payload widths are equal
    in 305. In 9 PC extends, 10 have PC insertions, 2 have PC ⊂ PS4 (`0x8225F0`, `0x823FB0`: PS4 has a trailing u64)
    and 3 are other.

## 5. REQ/RES convention

- **PS4 (V by code)**: the requester `cNetGameServer::<verb>` sets `mStatus[idx]`, calls
  `reserveNetworkErrorDialog(idx)` (`esi` immediate at all 478 call sites), sets `mErrorCode[idx]` to the
  client-request error and calls `Send_C2S_*`. The RES handler writes `mErrorCode[idx]`/`mStatus[idx]`.
  - For the 462 seeds with one PS4 slot: in **321** the slot's requesters call exactly
    `Send_C2S_<NAME without _RES>_REQ`, in 17 among several, and in 3 a different name:
    `GET_CHARACTER_BIN_SAVEDATA_RES` and `MOVE_IN_SERVER_RES` meet `Send_C2L_*` login senders through a slot number
    of the login manager, and `SET_PAWN_PROFILE_RES` meets `Send_C2S_SET_PAWN_PROFILE_COMMENT_REQ`.
  - 65 requesters call no `Send_` and 56 slots have no requester.
- **PC (V by code)**:
  - **The table does not pair g.id.1 with g.id.2.** It holds only S2C keys: sub 2 ×705, 16 ×332, 1 ×3, 255 ×1.
  - The pairing comes from the same slot mechanism. The requester (e.g. `0x86F4B0`) writes `this[1+idx]`,
    `this[743+idx]` and `reserveNetworkErrorDialog(idx)` (581 call sites, 580 immediate, 562 distinct indices) and
    calls the sender; the handler passes `idx` to `callOnPacketFunc`.
  - Over the 432 seeds with a PC slot (requesters and their callees two levels down):
    - **327**: all reached senders have key `(g,id,1)`.
    - 17: `(g,id,1)` among other keys (shared slots, e.g. slot 358 serves three clan RES).
    - 1: different key. `0x7C68E0` `BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES` 9.0.2 is on slot 15, whose only
      requester `0x88AB70` (login code) reaches a 5.2.1 sender: the login manager's slot 15.
    - 33: the requester reaches no sender (requester not a function in this copy, or deeper).
    - 54: no requester.
- **What this proves**:
  - "The request of the same g.id as a named RES is `<NAME>_REQ`" is **a convention**: PS4 breaks it once by name
    (`SET_PAWN_PROFILE_COMMENT`), and both sides have slot collisions with the login manager.
  - It becomes **V per pair** when the slot link holds on PC (requester of the handler's slot reaches only senders
    with key `(g,id,1)`), the slot link holds on PS4 (the requester calls exactly one `Send_C2S_*`), and the payload
    widths agree.
  - Without the slot link, a REQ name from g.id stays **I**.

## 6. Proposal: role anchors

Each anchor pairs a PC callee with a PS4 function inside an already accepted handler or sender pair, by the role
the code gives it. The listed near-misses must be refused.

1. **Reader anchor (handler → ReadPacket)**.
   - **Rule**: in an accepted handler pair, the PC handler's unique callee that reaches codecs (at depth ≤ 2) pairs
     with PS4 `CPacket_<NAME>::ReadPacket` when the PS4 handler calls exactly one such function with that class
     name.
   - **Evidence**: §1.2.
   - **Expected**: 88 named readers.
   - **Refuse**:
     - the 4 handlers whose PC reader is not a function;
     - any PC reader shared by two handlers (0 today, but gate it);
     - the 378 PS4 handlers with an inlined reader. For those, the PC reader can only be named
       `CPacket_<NAME>::ReadPacket` with the DWARF prototype of that symbol where it exists out of line; otherwise
       list it as "inlined on PS4".
2. **Element-reader anchor (codec-span bracket)**.
   - **Rule**: when the PC body widths (after the header rule PC `44` ↔ PS4 `24`/`2`) equal the PS4 widths, a PS4
     `nPacket::Read_CData*` call and a PC callee covering exactly the same codec positions pair (the outermost PC
     callee when nested callees share the span). A pair is accepted only if it is the same pair in every handler
     where it occurs (global uniqueness).
   - **Evidence**: §3.
   - **Expected**: 117 pairs from 220 occurrences in 136 handlers. Applying the same rule inside accepted element
     readers adds more.
   - **Refuse**:
     - the 44 PC-only spans (PS4 inlined);
     - the 2 PS4-only spans (`0x1A013B0`);
     - any span in a non-equal pair unless the embedding is unique (2 of 40 insertion pairs, 7 of 20 prefixes);
     - any reader tree that touches the 34 non-function targets at `0x758000`-`0x77C000` (36 pairs) until they are
       repaired.
3. **Codec-position anchor (naming, not pairing)**.
   - **Rule**: in equal-width sequences, PC codec call sites take the PS4 overload at the same position, as
     T002 did for u8/bool/s32/u32/s64/u64.
   - **Evidence**: §2.
   - **Refuse**: any naming of the PC codec *functions* `0x8BC480`/`0x8BC4D0`/`0x8BC520` by their call sites alone,
     since the bodies are identical (T002's s32 caveat).
4. **Listener-slot anchor (handler ↔ requester ↔ sender)**.
   - **Rule**: a PC function that calls `reserveNetworkErrorDialog(idx)` with the slot of an accepted RES handler,
     and the sender it calls whose `WritePacket` key is `(g,id,1)` of that handler's `(g,id,2)`, pair with the PS4
     requester that calls `reserveNetworkErrorDialog(idx_ps4)` and its single `Send_C2S_*`. This holds when:
     (a) both requesters reach exactly one sender, (b) the payload widths are equal, and (c) PS4 idx → PC idx keeps
     the global order (0 inversions today).
   - **Evidence**: §1.3, §4, §5.
   - **Expected**: about 300 sender pairs: 327 PC slot-to-key links ∩ 321 PS4 slot-to-name links ∩ 305 equal
     payload widths; the exact count is not run as one intersection. The same number of requester pairs.
   - **Refuse**:
     - the 17 shared slots on each side;
     - slots of the login manager (`0x88A600`-`0x88AC00` on PC, `Send_C2L_*` on PS4: `0x7C68E0` 9.0.2,
       `MOVE_IN_SERVER`);
     - the 4 keys with a second sender in login code;
     - `SET_PAWN_PROFILE_RES` and other name-convention breaks (the anchor uses the code link, not the name);
     - payload width mismatch (25 seeds).
5. **Packet-object anchor (handler-local ctor/dtor/allocator)**.
   - **Rule**: the PC inline or called ctor that writes `(u8 g, u16 id, u32 sub)` at `+4/+6/+8` and the vtable of
     the packet object pairs with the PS4 `CPacket_<NAME>` vtable/`operator_new` of the same handler.
   - **Evidence**: §1.1 pairs 1, 2, 4.
   - **Expected**: about 137 heap-packet handlers (PC `sub_8BC2E0` + ctor) and the stack-packet rest; count not run.
   - **Refuse**:
     - the generic allocator `0x8BC2E0`, `callOnPacketFunc` `0x878860` and the shared array dtors
       (`sub_52FE10`, `sub_79E1C0`-like helpers called from several handlers), which are widely shared helpers under
       spec gate (d);
     - the PC-only inline header store (`m_pStart+5` → `+12`).

## Not run / limits

- **Login handler on PC**: not reached. The PC login dispatch table was not found, and `0x888000`-`0x88E000` is
  largely undefined code in the accepted copy.
- **NTC seeds**: T005 has none (all 467 are RES). The two NTC examples are not seeds; their names come from the
  earlier work (I).
- **Exact counts** for anchors 4 and 5 as one intersection: not run.
- **Coverage**: the accepted copy differs from the dumped work copy. 62 handlers are not functions here, 35 are
  undefined, and 34 element readers have broken boundaries. Results for those pairs come from the dump or are
  listed as gaps.
- **PC writer bodies** other than `0x8BC860`/`0x8BC890`/`0x8BC920`: not disassembled.
- **PS4 element-reader brackets** were compared only in equal-width pairs.
- **Tooling**: ida-mcp `execute_python` on both private copies, about 50 calls. No files written besides this report.
