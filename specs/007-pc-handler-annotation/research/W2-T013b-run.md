# 007 W2 T013b: extractor v6 run on PC and PS4, matcher rerun

Builds PC 03040008 and PS4 02020005. Base `310ac41bdf6`, 2026-11-03 18:31-18:45 (WEST). All addresses are VAs.

Scripts as committed at HEAD (`git diff --quiet HEAD -- extract_ida.py extract matcher match.py manifest.py`):
`extract_ida.py` `ed7e908b...b43e` (script_version 6), `extract/callargs.py` `395c0cad...34cf`,
`extract/dataflow.py` `9c7fa919...7fd3`, `extract/x86.py` `9da84516...017`.

All IDA work ran as headless `C:/Program Files/IDA Professional 9.5/idat.exe -A` batches. Every script set
`DBFL_KILL` and ended with `qexit`. ida-mcp was not used. The original and accepted databases were not opened.

**Outcome:**
- Both v6 dumps were written. The matcher manifest is **byte-identical** to the committed state on both runs.
- The v6 `args` reproduce T012's destinations at 500 of 502 PC lea sites and 340 of 340 PS4 lea sites. The two
  PC sites with no record are expected (§ 3.2).
- **Contradicted:** the element allocators never fire on PC (0 of 837 `sub_8BC2E0` sites) and never through PS4
  `operator new` (§ 4). Only the PS4 `getAllocator` route produces `from: "result"` records.

## 1. Runs

    T=D:/ddon-data/research/03040008/ida-transfer
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"
    PC=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    PS=D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-w2b/DDOORBIS.elf.i64   # private-copy.sh ps4 w2b
    "$IDAT" -A -L$T/dumps/logs/pc-ida.log     "-S$T/extract_ida.py $T/dumps/pc-ida.jsonl pc"  $PC   # 18:33:26-18:34:00, rc 0
    "$IDAT" -A -L$T/dumps/logs/ps4-ida.v6.log "-S$T/extract_ida.py $T/dumps/ps4-ida.jsonl ps4" $PS  # 18:33:35-18:34:06, rc 0

| | PC 03040008 (work copy) | PS4 02020005 (copy `w2b`) |
| --- | --- | --- |
| `.i64` sha256 before = after | `f7f3a219...3c25` (112,373,500 bytes, mtime 14:00:18 unchanged) | `79d6c2f5...11ea` (= original at copy time) |
| header | `idb_path` the work copy, bitness 32, image base `0x400000`, input `f1c974d0...fa20` | `idb_path` the copy, bitness 64, image base 0, input `4236f598...63c0` |
| dump | `dumps/pc-ida.jsonl` `79827380...6abb`, 16,583,543 bytes, 8,914 lines | `dumps/ps4-ida.jsonl` `8a41931d...4f22`, 10,395,937 bytes, 4,484 lines |
| functions | 7,262 (v5 `pc-ida-applied.jsonl`: 7,262) | 4,146 (v5: 4,146) |
| summary (unchanged against v5) | externs 575, requesters 546, codec functions 20, table ok | externs 336, requesters 471, codec functions 4 |

- The `w2b` copy was deleted after the spot checks; the PS4 folder holds only its original files again.
- Because the PS4 function count did not change, `extract_dwarf.py --ida-dump` was **not run**. `ps4-dwarf.jsonl`
  `352d86c7...8d69` stays.
- The new `pc-ida.jsonl` replaces the wave-1 v4 dump (`4b307aee...61f0`, from before the apply).
  `pc-ida-applied.jsonl` (v5) stays.
- `idat -L` appends: `dumps/logs/pc-ida.log` also holds the earlier runs, and the v6 summary is its last line (142).
  The PS4 log has its own name, `ps4-ida.v6.log`; the old `ps4-ida.log` was kept.

`dumps/MANIFEST.tsv` (`uv run python manifest.py`) changed only in the two dump rows (sha256, size,
script_version 4->6 for PC and 5->6 for PS4). Before that, `match.py` refused the new dumps (rc 1, fail closed on
the sha256) and wrote nothing.

## 2. Counts (verified, `research/w2b/count_args.py`)

| | PC | PS4 |
| --- | ---: | ---: |
| call-site records | 33,476 | 28,094 |
| sites with `args` | 17,810 | 16,454 |
| `obj` | 19,126 (13,257 the argument itself, 5,869 formed) | 23,963 (21,276 / 2,687) |
| `const` | 9,377 | 8,864 |
| `stack` | 2,092 | 4,855 |
| `element` | 6 (all `from: "index"`) | 1,367 (1,356 `from: "result"` via `getAllocator` `0xd5c780`, 11 `index`) |

**Padding nops (verified).** The dump has no counter for skipped nops; I compared the v5 dump `pc-ida-applied.jsonl`
with v6 (same 7,262 functions):
- `object_accesses` went from 48,246 to 48,387: 47 records removed (one each in 47 functions, all `disp` 0) and 188
  added in 19 functions.
- The T012 nop `0x757ded lea ecx,[ecx+0]` is gone from `object_accesses`.
- Inferred: the 47 removals are the skipped nops. The additions are argument registers that a nop no longer kills;
  9 of the 19 functions are among the 47, and the other 10 were not checked.

**Pass-through `obj` values (inferred, consumer caveat).** `args` records every ABI slot whose value is held,
not only the slots the callee takes:
- PS4 records `rdx..r9` = the caller's untouched arguments at `nPacket::Read_u32` (`0x1a0a434`, `arg_regs`
  `['rsi']`). `obj` in `r8` (3,478) and `r9` (3,505) come mostly from this.
- PC records `ecx` before cdecl codecs (`0x75832f`).
- Consumers should intersect with the callee's prototype or `arg_regs`.

PC `element` records name the index register in 64-bit form (`"index": "rsi"`, `"rbx"`). That is cosmetic
(`x86.canon_reg`), not checked further.

## 3. Against T012

### 3.1 Lea destination sites

| T012 lea sites | v6 `obj` with the same offset, object and def | other |
| --- | ---: | --- |
| PC 502 (slot 1) | **500** | 2 with no slot 1 |
| PS4 340 (`rsi`) | **340** | 0 |

### 3.2 The two PC sites without a slot-1 record (verified against the listing)

- `0x757df5`: T012's wrong row, the padding nop. The real `lea eax,[esi+edi]` is not argument-relative, so no
  record is correct.
- `0x768b6b`: the T012 lea `0x768b66` lies in the previous basic block; the site's block starts at `0x768b69`.
  v6 proves derived values within the block only, so this is a coverage gap, not an error.

### 3.3 The 975 aligned codec site pairs

| PC slot 1 / PS4 `rsi` | pairs |
| --- | ---: |
| `obj` / `obj` | 350 |
| none / none | 287 |
| none / `stack` | 131 |
| `obj` / `stack` | 124 |
| `obj` / none | 75 |
| none / `obj` | 8 |

The 136 inlined-context rows of T012 § 1.4 now carry a PS4 `stack` frame offset. The array-reader rows carry
nothing on either side (§ 4).

## 4. Element allocators (contradicted against the README's v6 claim)

### PC `sub_8BC2E0`: 837 call sites in the dump, 0 `from: "result"` records

Listings `w2b/spot-pc-alloc.txt` (`0x758154..0x758187`, `0x403df2..0x403e3c`). MSVC null-checks every allocation:

    call sub_8BC2E0; mov esi,eax; add esp,8; test esi,esi; jz L0
    ...                                      ; construct
    L0: xor esi,esi
    L1: lea eax,[esi+4]; push eax; push ebx; call nPacket__Read_u8   ; L1 = join block

At the join, `esi` is the result or 0. Neither the block-local proof nor the must-analysis keeps it.

The size and alignment pushes are lost too. 606 of the 837 sites have `arg_bytes` 0: the callee ends in a plain
`retn`, and the caller's `add esp,8` follows a `mov`, not the call directly. So `push 10h; push 8; call sub_8BC2E0`
(`0x403df2`) has no `args`. Over all PC sites, 5,453 have pushes but `arg_bytes` 0, and 5,653 have `arg_bytes`
null; none of these get stack slots.

### PS4 `operator new`: 0 records

The regex `^operator new(?:\[\])?$` never matches:
- The database names the global allocator `operator_new` (`0xd61f30`), with an underscore. It is not mangled, so
  `demangled()` returns the name as it is.
- The array readers use per-class allocators such as `CDataAbilityLevelParam::operator_new` (`0x1a0a5ca` in
  `0x1a0a4c0`), followed by `mov rbx,rax; lea rsi,[rbx+8]; call nPacket__Read_u8` (`0x1a0a5f6`, no `args`).
- `0x830822 operator_new(0x38)` -> `mov r15,rax` -> `mov rdi,r15` -> `nNetwork::Decoder::Decoder` (`0x830831`):
  `rdi` is not recorded.

### PS4 `getAllocator` -> indirect allocate: 1,356 records (verified)

Example `0x4a72d`/`0x4a749`/`0x4a759`. Inferred: these are mostly the `MtArray` storage buffer handed to `memset`
and similar, not element objects. The T012 § 1.5 element links (174) therefore get no proof from v6 yet.

## 5. Spot checks against the listing

Read-only batch `w2b/spot_listing.py` on the work copy and `w2b`. Both report the idb path, 32-bit/`0x400000` and
64-bit/0, and the input sha256 above.

| Side | Site | Listing | Dump `args` | Status |
| --- | --- | --- | --- | --- |
| PC | `0x75832f` Read_u32 | `mov esi,[esp+0Ch]`=arg1, `mov edi,[esp+0Ch]`(after 2 pushes)=arg0, `lea eax,[esi+4]`, push eax, push edi | slot0 obj stack:0; slot1 obj stack:1 disp 4 def `0x75832a`; ecx obj ecx:0 | verified |
| PC | `0x758187` Read_u8 | join block, `lea eax,[esi+4]` with `esi` = result or 0; `push ebx` = packet | slot0 obj stack:0; slot1 none | verified (fail closed) |
| PC | `0x757df5` Read_u8 | `lea eax,[esi+edi]` | slot0 only; nop gone | verified |
| PC | `0x403df2` sub_8BC2E0 | `push 10h; push 8` | none (`arg_bytes` 0) | gap (§ 4) |
| PS4 | `0x1a0a434` Read_u32 | `mov rbx,rsi; lea rsi,[rbx+8]` | rsi obj rsi:1 disp 8 def `0x1a0a430`; rdi obj rdi:0 | verified |
| PS4 | `0x4a759` memset | `rdi=rax` (indirect `[rcx+40h]` on getAllocator), `xor esi,esi`, `rdx=[rbp-58h]` | rdi element result site `0x4a749` getter `0xd5c780`; rsi const 0; rdx none | verified |
| PS4 | `0x830831` Decoder ctor | `lea rsi,[rbp+var_58]` (= entry-0x60), `rdi=r15=operator_new result` | rsi stack frame -96 def `0x83082a`; rdi none | verified, rdi gap (§ 4) |
| PS4 | `0x830822` operator_new | `mov edi,38h` | rdi const 56 | verified |

## 6. Matcher (`uv run python match.py`, twice)

- rc 0 both times, 5 s each. The two runs' `manifest/*.tsv` sha256 are identical (`w2b/match-run1.sha256`) and
  the two logs are identical (`1cb12abc...f1c9`).
- `git diff --quiet HEAD -- manifest` holds: **0 pairs added or removed in any rule**.
- `callsites.tsv`: 926 rows, all with `ps4_site`/`ps4_owner`, 975 site pairs. These were already filled at HEAD
  (T013a).
- `matcher/` reads no `args` yet, so v6 cannot change the manifest until T013c consumes them.

## 7. Files

- Dumps and logs:
  - `research/03040008/ida-transfer/dumps/{pc-ida,ps4-ida}.jsonl`, both gitignored.
  - `dumps/logs/pc-ida.log` (appended) and `dumps/logs/ps4-ida.v6.log`.
- `dumps/MANIFEST.tsv`, modified.
- `manifest/*.tsv`: rewritten, identical to HEAD.
- `specs/007-pc-handler-annotation/research/w2b/`:
  - scripts: `spot_listing.py` (`e70a0a79...ceff`), `count_args.py`, `alloc_next.py`;
  - spot-check output: `spot-{pc,ps4,pc-alloc}.{txt,log}`;
  - matcher output: `match-run{1,2}.log`, `match-run1.sha256`.
