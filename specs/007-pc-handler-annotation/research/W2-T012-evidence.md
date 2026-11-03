# 007 W2 T012: codec destinations, member links, anchored gap pairs

Evidence for wave 2 (`briefs/W2-T012-evidence.md`). Base `89e645b20b`. Read-only; nothing accepted, nothing
written to any database.

## 0. Inputs and identity

| Input | Identity |
| --- | --- |
| PC 03040008 dump | `research/03040008/ida-transfer/dumps/pc-ida.jsonl` (extract_ida v4, sha256 `4b307aee...61f0`, input `f1c974d0...fa20`, taken from `ddon-data-007work`) |
| PS4 02020005 dump | `ps4-ida.jsonl` (v5, `2d00c616...0913`); `ps4-dwarf.jsonl` (`352d86c7...8f69`), ELF `4236f598...63c0` |
| Matcher | `matcher/` at base, run unchanged in-process (`load_facts` checks MANIFEST hashes): 972 pairs, the same 926 PC call sites as `manifest/callsites.tsv` |
| PC listing | private copy of the **accepted** database (`private-copy.sh pc-accepted w2e`, `ddon-data-w2e/2022_01_29_DDO_DUMP_FIX.exe.i64`), `idc.get_idb_path()` confirmed, 32-bit, image base `0x400000` |
| PS4 listing | private copy `PS4_DDON_02020005_2016_12_21/ddon-data-w2e/DDOORBIS.elf.i64`, 64-bit, image base `0` |

All addresses are VAs. Throwaway scripts (scratchpad, not in the repo): `step1.py` (matcher rerun, aligned sites
with their PS4 site and owner), `step2.py`/`step3.py` (destinations, member links, conflicts), `step4.py` (compare
with the MSVC x86 layout of `transfer/layout.py`), `step5.py` (Q3), `step6.py`/`step7.py` (extensions, § 1.5).
Run with `uv run --no-sync python -X utf8 <script>` from `research/03040008/ida-transfer`.

Outputs beside this report:

- `W2-T012-codec-destinations.tsv` (975 rows): one row per aligned (PC site, PS4 site). Columns: owners,
  owner relation, width, overload, destination kind and object/offset on each side, PS4 class/member, outcome.
- `W2-T012-member-links.tsv` (52 classes): links, conflicts, PC minus PS4 offset, link list.
- `W2-T012-gap-proposals.tsv` (5 rows, variant A of Q3).

## 1. Codec destinations (Q1)

### 1.1 How the destination appears (V, listing)

Every PC and PS4 read codec takes `(CPacket*, T* dst)` and returns a status. PC returns the width; PS4 returns
0/1. **The value never comes back in a register.** The destination is always the pointer argument:

- **PC (cdecl):** `lea R,[obj+X]` / `push R` / `push packet` / `call codec` / `add esp,8`.
  - Reader: `obj` is `esi` = `ecx` (`this`).
  - Element reader: `obj` = `[esp+arg_4]` (argument 1).
  - Example: `0x808fba lea eax,[esi+18h]; push eax; push edi; call nPacket__Read_u32`.
- **PS4 (SysV):** `lea rsi,[obj+X]` / `mov rdi,packet` / `call`.
  - `obj` is `this` (`rdi`, kept in `r15`) or argument 1 (`rsi`, kept in a callee-saved register).
  - Seen only in headers: `lea r14,[this+m_usError]; mov rsi,r14`.
  - Seen once: `mov rsi,this; sub rsi,-80h` (`0x19dc407`).

Bulk check of the dump's "single object `lea` between the previous call and this call" rule against the listing:

| Side | lea sites | as stated | exceptions |
| --- | ---: | ---: | --- |
| PC | 502 | 499: the lea register is the second-to-last push and is not redefined before it | 1 **wrong**: `0x757ded lea ecx,[ecx+0]` is MSVC padding (a nop); the real destination is `lea eax,[esi+edi]` (array index). 2 are undefined in the accepted copy (`0x815f2a`, `0x815f4c`); they decode as `8d4618`/`8d4630` = `lea eax,[esi+18h/30h]; push eax; push edi; call` (repaired in `007work`) |
| PS4 | 340 | 340: `lea rsi,[obj+X]` directly | 0 |

The nop row is `owners-unrelated` and makes no link. An implementer must still drop `lea r,[r+0]`.

### 1.2 Counts over all aligned codec call sites

The rule-3 sites come from equal-width contexts only; header positions are excluded by design. They form
975 (PC site, PS4 site) pairs over 926 PC sites. One PC element-reader site aligns with several PS4 inlined copies.

| Owner relation (PC owner of the call vs PS4 owner) | Outcome | Rows |
| --- | --- | ---: |
| accepted pair | **link** | 126 |
| context root (PC reader <-> PS4 `ReadPacket` of a seed handler; reader pair not accepted) | **link** | 41 |
| accepted pair | no object lea on either side (array readers: element pointer or stack local, § 1.4) | 302 |
| accepted pair | variable width (MtString/bytes) | 14 |
| accepted pair | PC lea, PS4 `add rsi,imm` / `mov rsi,reg` | 6 |
| context root, PS4 `ReadPacket` inlined into the handler | PC lea, PS4 stack object (§ 1.4) | 136 |
| unrelated (neither paired nor context roots: nested element functions one side inlined) | not linked | 350 |

Every link has `obj` = the owner's object argument:
- PC: `ecx:0` in readers, `stack:1` in element readers.
- PS4: `rdi:0` or `rsi:1`, typed by the owner's DWARF parameter.
- No link goes through a member pointer (`via`): 0 such rows on either side.

**Member links:**
- 167 distinct links (PC offset, PS4 member, equal width) in **52 classes**: 46 `CPacket_S2C_*`, 6 `CData*`.
- Conflicts: **0** PC offsets linked to two members, **0** members linked to two offsets.

Against the MSVC x86 layout computed from DWARF (`transfer/layout.py`):
- All 45 links of the 6 `CData*` classes agree (shift 0).
- All 122 packet-class links differ by a constant per class:
  - +0xc in 41 classes;
  - +0x8 in 3 (`GAME_TIME_GET_BASEINFO_RES`, `NG_WORD_GET_LIST_RES`, `SYSTEM_MAIL_GET_ALL_ITEM_RES`);
  - {+0xc, +0x10} in 2 (`GET_GP_RES`, `PARTY_JOIN_RES`): the extra 4 is the 8-byte alignment of a u64.
- This is the wave-1 "`CHANGE_JOB_RES` shifted 0xc", now measured per member.
- **Inferred cause:** the PC `CPacket` header area is 0xc bytes larger. The readers write the error s32 to
  `+0x10` and the result to `+0x14`, and store a header u32 at `+0xc` without a codec. DWARF predicts `m_usError`
  at 4 and `m_nResult` at 8.
- **Header (excluded from rule 3):** PC `+0x14` s32 <-> `m_nResult` (s32, width equal). PC `+0x10` is a **s32**
  where PS4 `m_usError` is a u16: width differs (V, `0x80cf89` and `0x19dc3b0`).

### 1.3 Hand checks (V, listing in both copies)

1. `nUserSession::CPacket_S2C_CHANGE_JOB_RES`, PC reader `0x80cf80`, PS4 `ReadPacket` `0x19dc3a0`.
   - Its body has no rule-3 sites: the context is not width-equal. PC calls 8 element readers; PS4 calls 10 plus
     `u8` and `u32`.
   - Header:
     - PC `0x80cf89 lea ebx,[esi+10h]` -> `Read_s32` vs PS4 `m_usError` (u16, +8): **width differs**.
     - PC `0x80cfbc lea eax,[esi+14h]` -> `Read_s32` vs PS4 `0x19dc3cb lea rsi,[this+m_nResult]` (+0xc, s32):
       **agree**.
   - Body (element-reader calls, § 1.5): the only forced alignment is the unique pair `Read_CDataEquipJobItem_`
     (PC `0x766120` <-> PS4 `0x19f2800`, accepted).
     - PC `0x80d02c lea eax,[esi+0B0h]` <-> PS4 `0x19dc49c lea rsi,[this+m_EquipJobItemList]` (+0x160).
     - The DWARF-predicted PC offset is 0xf4. PC is 0x44 lower: Season 3 dropped three `ItemList`s and
       `DifferentEquipList` before it (PS4 `0x19dc407`..`0x19dc456`). The next PC member starts at `+0xc4`
       = 0xb0 + 0x14 (`MtTypedArray` size on PC).
     - The other PC members (`+0x18`, `+0x60`, `+0x74`, `+0x88`, `+0x9c`, `+0xc4`, `+0xd0`) stay unlinked: their
       callees are unpaired or repeated without a forced alignment.
     - This class must stay partial. A shift rule would be wrong here.
2. `nUserSession::CPacket_S2C_GET_GP_RES`, PC `0x808f70`, PS4 `0x19d7af0`. All four agree in offset, width and member:

   | PC | codec | PS4 | member | width |
   | --- | --- | --- | --- | ---: |
   | `+0x18` | u32 | `0x19d7b27` | `m_unGP` | 4 |
   | `+0x20` | s64 | `0x19d7b37` | `m_llUseLimit` | 8 |
   | `+0x28` | u64 | `0x19d7b47` | `m_ullRealTime` | 8 |
   | `+0x30` | u16 | `0x19d7b57` | `m_usMilliseconds` | 2 |

   The PS4 header here is `u16` + `u32 m_unResult`.
3. `CDataGameTimeBaseInfo`, PC element reader `0x769030` (argument `esi = [esp+arg_4]`), PS4
   `nPacket::Read_CDataGameTimeBaseInfo_` `0x19f3bd0` (`d`):
   - Nine `lea eax,[esi+X]; push eax; push edi; call` with X = 4, 8, 0xc, 0x10, 0x14, 0x18, 0x20, 0x28, 0x30.
     Codecs: u32 x6, s64 x2, u32.
   - PS4 reads the same widths into `m_unGameTimeOneDayMin` ... `m_unOriginalWeek` (+8 .. +0x30).
   - Width and member agree for all nine; PC offsets equal the predicted 32-bit layout.

### 1.4 What does not link, and why (V, listing classification)

Each destination below was classified from the listing (PS4: the last write to `rsi`; PC: the definition of the
pushed register):

| Shape | PC rows | PS4 rows | Meaning |
| --- | ---: | ---: | --- |
| `lea [R+X]`, R not an argument (accepted pairs) | 213 | 205 | array readers: R = the element just allocated (`MtTypedArray<T>` element) |
| `lea` of a stack slot (accepted pairs) | 88 | 88 | count or temporary `value` read into a local, then copied |
| PS4 stack packet in an inlined handler (context roots) | - | 107 + 28 | `lea rsi,[rbp+var_38]` / `[rbp+packet+10h]`: IDA split the stack `packet`; or `lea rsi,[packet+Class.m_x]` through a register holding `&packet` |
| PS4 `add rsi,imm` / `mov rsi,reg` | - | 8 + 8 | arithmetic on the object pointer |

### 1.5 Extensions measured (inferred; the brief asked only for codec sites)

- **Array element destinations.** These are accepted array-reader pairs where both sides use `lea [elem+X]`; the
  element class is the `T` of the PS4 parameter `MtTypedArray<T>&`.
  - 174 candidate links in 69 `CData*` classes, 0 conflicts.
  - **174/174 PC offsets equal the predicted 32-bit layout.**
  - The base register is the element pointer only by reading. The dump does not prove it (§ 2).
- **Element-reader call sites as anchors** (`step7.py`). In reader and element-reader contexts, calls were aligned
  with `matcher.propagate.align` on paired callees plus aligned codec sites. Of 150 aligned paired-callee sites,
  47 have a single object lea on both sides.
  - Result: 47 links (member = an `MtTypedArray<...>`/struct member start) in 29 classes, 0 conflicts.
  - PC minus predicted offset: +0xc in 25 classes, +0x8 in 2.
  - -0x44 in 2: `CHANGE_JOB_RES` and `CHANGE_PAWN_JOB_RES` `m_EquipJobItemList`, the Season 3 removal above.

## 2. What the extractor lacks (Q2)

The rules above use the v4/v5 `object_accesses` plus call order. That is a positional guess, true for 841 of 842
lea sites here but not proved by the dump. The extractor needs the following.

1. **Per-call argument provenance.** For each call site, record each argument's value as
   `{arg: k, kind: addr|value, base: {arg: i, via: d?} | {stack: off} | {result_of: site} | unknown, disp: X,
   def_ea}`:
   - PC: the operand of each push in the argument window (`pushes`/`pushed_bytes` exist, values do not). For a
     register push, follow its last definition in the block (`lea R,[base+disp]`, `mov R,reg`) back to the base.
   - PS4: the same for `rdi/rsi/rdx/rcx/r8/r9` at the call. `arg_regs` lists names only; `const_regs` keeps only
     immediates.
   - Without this the codec destination is inferred by order. With it, it is proved (`def_ea` -> `call`).
2. **Drop MSVC padding nops** `lea r,[r+0]` / `lea r,[r+0x0]` (e.g. `0x757ded`). Today they are recorded as an
   object `lea` at displacement 0.
3. **Arithmetic pointer forms.** `mov rsi,obj; add/sub rsi,imm` (PS4 `0x19dc407`: `sub rsi,-80h` = +0x80) are not
   recorded. Treat `sub r,-imm` as `+imm`.
4. **Non-argument bases with known type.** In array readers the base is the return of the grow/allocate call:
   - PC: `sub_8BC2E0(0x40,0x10)`, then the ctor with `ecx` = element.
   - PS4: the inlined allocation.
   - Record `base: {result_of: <site>}`. The type then comes from DWARF (`MtTypedArray<T>&` parameter -> `T`).
     That unlocks the 174 element links of § 1.5.
5. **Stack objects.** On PS4 the inlined handlers keep `packet` on the frame.
   - Record `base: {stack: rbp/rsp offset}` (normalised to the frame).
   - Join it with the DWARF `packet` local's location at that PC (`DW_OP_fbreg`/`DW_OP_breg6`). The dump has
     location lists, but for this local in these handlers they are often registers (`DW_OP_reg14` holds
     `&packet`), so the register case (`lea rsi,[r14+X]` with r14 = `&packet`) needs the same location-list join.
   - That covers 136 rows (§ 1.2).
6. **Loads through a lea register** (`0x80cf89 lea ebx,[esi+10h]` ... `0x80cfa2 mov eax,[ebx]`) are not recorded
   as accesses at `+0x10`. This matters for the layout access check, not for the links.
7. **`callsites.tsv` lacks `ps4_site` and `ps4_owner`.** `step1.py` recomputes them from `roles.compare`;
   `callsite_rows` already computes `lb.site`. Export them, plus the owner relation of § 1.2.
8. **Rule 3 covers equal contexts only.** CHANGE_JOB_RES-like classes (Season 3 insertions or removals) get links
   only through forced anchors (§ 1.5). The 58 ambiguous-embedding, 11 embedded and 39 other contexts give 0 codec
   sites today.

## 3. Anchored gap pairs (Q3, offline, measured only)

Method:
- `matcher.propagate.align` and the T005 gap rule over every accepted pair (972 parents; all present in both dumps).
- Call tokens:
  - an accepted pair (by PC VA);
  - a PC codec call site aligned by rule 3 = the PS4 call to that overload (`ov`), on the PS4 side only at the
    aligned PS4 site;
  - identical PC import names (15 imports; no PS4 call matched one).
- Unaligned codec calls are anchors that never align, so they block their gap.
- Variant B adds width equality for every codec call. Variant C removes every codec/reader/writer call on both
  sides.

| | A | B | C |
| --- | ---: | ---: | ---: |
| anchors aligned | 621 | 748 | 0 |
| gaps blocked by an unaligned anchor | 696 | 696 | 106 |
| uneven gaps | 401 | 512 | 817 |
| even gaps with 2+ calls each side | 29 | 29 | 41 |
| **1:1 gaps** | **108** (requester 104, handler seed 2, reader 1, element reader 1) | 109 (reader 2) | 2 |
| distinct proposed pairs | 5 | 6 | 1 (**wrong**: `callOnPacketFunc` <-> `__stack_chk_fail`, no anchors at all) |
| unique both ways / contradict an accepted pair | 5 / 0 | 6 / 0 | - |
| with 2+ independent parents | 1 | 1 | - |

Blocking tokens in A: PS4 codec calls not aligned 1,955, PS4 overload 264, PS4 pair 130; PC codec unaligned 351,
PC overload 64, PC pair 12. Inlined `ReadPacket` codec runs in PS4 handlers dominate.

All proposals (A; the brief asked for 20, only 5 exist):

| PC callee | PS4 partner | parents |
| --- | --- | --- |
| `0xbb21a0` | `sNetworkExt::cancelReserveNetworkErrorDialog` `0x7edfc0` | 104 requesters |
| `0x7594b0` | `nPacket::Read_CDataAreaSpotSet_` `0x19e23e0` | 1 reader |
| `0x773820` | `nPacket::Read_CDataQuestAnnounce_` `0x1a1c3d0` | 1 element reader |
| `0x782210` | `CDataAllContextPlayer::CDataAllContextPlayer` `0x19fb240` | 1 handler |
| `0x7848b0` | `CDataPartyContextPlayer::CDataPartyContextPlayer` `0x19fb940` | 1 handler |

B adds `0x76e000` <-> `nPacket::Read_CDataMDataCraftRecipe_` `0x19e7640` (1 reader).

**`sContextManager::getContextMyPlayer` is not proposed.**
- PS4 calls it out of line in 17 parent gaps. 9 are blocked; the 8 open ones are uneven (6 with 10+ calls on each
  side; the others (6,7), (5,3), (5,4)).
- Example, handler `0x7de910` <-> `0x31f2c0` (CHANGE_JOB_RES): after the reader anchor, PC makes 44 calls and
  PS4 31.
  - PC calls out-of-line helpers (`sub_402760`..`sub_4056D0`, 14 calls) that PS4 inlines.
  - PS4 calls `__stack_chk_fail`, `abort` and `scePthreadMutex*`, which PC lacks.
- **Inferred:** the gap rule cannot reach the context getters. They need another anchor: a fingerprint (string or
  constant), the call's argument shape, or vtable or DTI evidence.

## 4. Not run, and cleanup

- Not run: `tools/check.sh` (no code changed); ImHex (not relevant); the Q3 gates (b)-(d) on the proposals
  (measuring only).
- Q1 listing checks ran on the **accepted** copy, not on `ddon-data-007work`. 2 PC sites are undefined there and
  were decoded byte-wise.
- Cleanup: the private copies are deleted except the unpacked `.id0/.id1/.nam` that the two ida-mcp workers still
  hold (close is withheld). Delete these folders once the workers exit:
  - `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-w2e/`
  - `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-w2e/`
