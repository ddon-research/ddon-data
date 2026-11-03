# 007 T005d: repair undefined call targets (v3), re-extract PC and PS4 by headless batch

Builds: PC 03040008 (work copy; 32-bit, image base 0x400000) and PS4 02020005 (private copy
`ddon-data-t005d`; 64-bit, image base 0). Address basis: VA. Base commit 78eeab0adc
(`repair_functions.py` / `extract_ida.py` script version 3, T005c 581571a37e). Run 2026-11-03
10:01-10:08 (+0000 WEST). All IDA work by `C:/Program Files/IDA Professional 9.5/idat.exe` batch;
no ida-mcp worker was opened; the original and accepted databases were not touched (the PS4
original was only hashed and copied by `private-copy.sh`). Every command ran with
`MSYS_NO_PATHCONV=1`.

`DB` = `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`,
`P` = `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t005d/DDOORBIS.elf.i64`,
`T` = `D:/ddon-data/research/03040008/ida-transfer`.

Status marks: V verified (read in this run), I inferred.

## 0. Answer in brief

- Dry run: 125 call-target roots (124 level 1, 1 level 2, 0 level 3, 0 pending): 118 would-repair,
  7 refused (5.9 % of would-repair; stop gate 25 % not reached). Table callbacks unchanged since T004f:
  1,039 already-ok, 1 refused (0x7D1BE0, `indirect_jump`).
- Apply: **118 repaired, 7 refused, 0 failed** (no `readback_neighbours` failure, so the T005c warning
  did not occur; the 3 listing checks it asked for have no subject). Apply results equal the dry run
  per VA (status mapped would-repair -> repaired; `diff` empty).
- Range 0x758000-0x77C000: 55 repaired, 2 refused. Range 0x888000-0x88E000: **no roots at all** (176
  functions already exist there). Other: 63 repaired, 5 refused.
- PC re-extract v3: `table_ok`, 1 missing root (0x7D1BE0), 6 orphan refs, 6,261 functions (6,068
  before), 28,472 call sites, 4,837 with a constant argument; 20 codec functions, every T005b § 2.1
  VA with its T005b width.
- PS4 extract v3: 3,568 functions, 0 missing roots, 25,327 call sites, 5,554 with constant registers;
  only **4 codec functions** (all widths agree with T005b § 2.2; 18 fixed-width PS4 codecs are not
  classified: the classifier's shape rule does not fit the PS4 bodies, § 3).
- 6 spot checks (3 in range A, 3 "other", since range B has none): bounds = recorded, 0 tails,
  Hex-Rays decompiles all 6.

## 1. Work copy state

| point | `.i64` sha256 | bytes | mtime |
| --- | --- | --- | --- |
| before (T004f state, checked) | `7189b4c6f76ff03eb985d1430dfa1a3892d1f8eb2ad7c9e558b5506cfb1b2c65` | 111,609,190 | 09:08 (+0100) |
| after dry run | `514350e4e57126ffc3499238ccdc5440d1ea926dba837d00123db4fef0fbf9c5` | 111,709,184 | 10:02 |
| after apply | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 | 10:03 |
| after PC extract and spot check | `65120b34...8b9111` (unchanged) | 111,886,983 | 10:03 |

- The before hash matched the brief (`7189b4c6...1b2c65`), so the write runs went ahead.
- The dry run rewrote the `.i64` again (batch entry ends in `qexit(0)`, T004f note), this time by
  +99,994 B, not +242 B as in T004f. No repair was applied in it (all results would-repair /
  already-ok / refused). The cause of the larger repack is not explained (I: IDA's own save after
  `auto_wait`; the function-count arithmetic in § 4 shows no function was added or removed in net).
- After every run the folder held only the `.i64` (no `.id0/.id1/.nam/.til`), and
  `rg -c -i "unpacked|restore"` over the four logs found nothing (rg exit 1).

## 2. PC repair v3

### a. Dry run

    idat -A -L$T/dumps/logs/repair3-dryrun.log "-S$T/repair_functions.py $T/dumps/repair3-dryrun.jsonl" $DB

rc 0, 35 s. `dumps/repair3-dryrun.jsonl` sha256 `3f1e9acc45b8bc1c970adfd9312358609f6fd2a7fa49334284e9e5c1cc0ecfee`,
1,167 lines, `repair_functions` 3 / `extract_ida` 3; header `idb_path` = the work copy, `bitness` 32,
`image_base` 4194304 (0x400000), `input_sha256` `f1c974d0...19fa20`. Log summary:

    {"apply": false, "by_check": {"indirect_jump": 1}, "by_status": {"already-ok": 1039, "refused": 1},
     "call_targets": {"by_check": {"branch_out_of_body": 1, "gap_referenced": 2, "overlaps_function": 1,
     "runs_into_function": 3}, "by_level": {"1": 124, "2": 1, "3": 0}, "by_status": {"refused": 7,
     "would-repair": 118}, "pending_beyond_depth": 0, "roots": 125, "scope_functions": 6068}, "callbacks": 1040}

Would-repair by plan: 89 `add_func` level 1, 1 `add_func` level 1 deleting a stray (0x80D540),
1 `add_func` level 2 (0x775FB0), 14 `replace_func` without junk gap, 13 `replace_func` with
`gap_junk` true. Gate: refused 7 / would-repair 118 = 5.9 %, failed 0 -> apply.

### b. Apply

    idat -A -L$T/dumps/logs/repair3-apply.log "-S$T/repair_functions.py $T/dumps/repair3-apply.jsonl --apply" $DB

rc 0, 29 s. `dumps/repair3-apply.jsonl` sha256 `ce5e61da1db4941fb8b2b1d24c1b1f3f1f0045757a9d123ef70587873f5c25d4`,
1,285 lines (1 header, 1,165 results, 118 undo, 1 summary). Summary as the dry run with
`"by_status": {"refused": 7, "repaired": 118}`. **0 failed** (no `readback_neighbours`).

| root kind | repaired | refused | failed |
| --- | --- | --- | --- |
| table callback | 0 (1,039 already-ok) | 1 (0x7D1BE0 `indirect_jump`, as T004f) | 0 |
| call target | 118 | 7 | 0 |

| range (call targets) | repaired | of which add_func / replace_func | refused |
| --- | --- | --- | --- |
| 0x758000-0x77C000 | 55 | 32 / 23 | 2 |
| 0x888000-0x88E000 | 0 | - | 0 (no roots in the range) |
| other | 63 | 59 / 4 | 5 |

The "other" repairs spread from 0x416100 to 0xBF4xxx, most in 0x784000-0x790000 (35) and
0x754000-0x758000 (2); the full list is in the dump.

Refusals (V, the script's own check; all level 1, one call site each):

| VA | range | check | at / enclosing |
| --- | --- | --- | --- |
| 0x7688E0 | A | `gap_referenced` | enclosing 0x7688DE, referenced 0x7688DE |
| 0x770EE0 | A | `runs_into_function` | 0x770F39 |
| 0x7884F0 | other | `runs_into_function` | 0x7884F4 |
| 0x78B540 | other | `runs_into_function` | 0x78B544 |
| 0x78D4A0 | other | `gap_referenced` | enclosing 0x78D496, referenced 0x78D496 |
| 0x7FFF90 | other | `overlaps_function` | function at 0x80000A (name at target `loc_7FFF90`) |
| 0xB6C750 | other | `branch_out_of_body` | 0xB6C758 |

Not investigated beyond the recorded check (out of the authorized writes).

## 3. Re-extracts (read-only batch, `DBFL_KILL`)

### PC

    idat -A -L$T/dumps/logs/pc-ida.log "-S$T/extract_ida.py $T/dumps/pc-ida.jsonl pc" $DB

rc 0, 63 s. `dumps/pc-ida.jsonl` sha256 `7e323747fd5995867448396135f1f5d6076a9f4acab4eee7dc3d422791190ece`,
7,948 lines, `extract_ida` 3. Note: `-L` appends, so `dumps/logs/pc-ida.log` holds the T004f run
(summary line 31) and this run (line 68).

- `table_ok` true: 1,041 records, 1,040 callbacks, 74 initializers, `unproved_records` [].
- `missing_roots` 1 (no-function 1): 0x7D1BE0 (`root` table) = the one table refusal.
- `roots` 1,682, `depth0_expected` = `depth0_functions` = 1,681, `onpacket_functions` 675, `senders`
  642, `onpacket_orphan_ref_count` 6 (same 6 as T004f), `functions` 6,261 (T004f 6,068; the depth-3
  scope grows through the bodies now defined).
- Externs 643: import 6, out_of_scope 629, not_function 6, inside_function 2. The 8 non-import,
  in-scope externs are the 7 refusals of § 2b (0x7688E0 and 0x78D4A0 `inside_function`, the other five
  `not_function`) plus 0x3468A01 (`.text`, `not_function`, 1 site; not a repair root; not
  investigated - I: an odd address, likely not a `call rel32` target the repair scope reaches).
- Call sites (non-tail calls in function records): 28,472; `arg_bytes` known 23,259; with
  `const_stack` 3,271; with `const_ecx` 1,944; **with either 4,837**.
- Codec functions 20 (V, from the dump):

| VA | name | dump codec | T005b § 2.1 |
| --- | --- | --- | --- |
| 0x8BC410 | Read_u8 | read/1 | 1 |
| 0x8BC6E0 | Read_bool | read/1 | 1 |
| 0x8BC440 | Read_u16 | read/2 | 2 |
| 0x8BC480 | Read_s32 | read/4 | 4 |
| 0x8BC4D0 | Read_u32 | read/4 | 4 |
| 0x8BC520 | Read_f32 | read/4 | 4 |
| 0x8BC570 | Read_f64 | read/8 | 8 |
| 0x8BC660 | Read_s64 | read/8 | 8 |
| 0x8BC6A0 | Read_u64 | read/8 | 8 |
| 0x8BC860 | Write_u8 | write/1 | 1 (checked) |
| 0x8BC890 | Write_u16 | write/2 | 2 (checked) |
| 0x8BC920 | Write_u32 | write/4 | 4 (checked) |
| 0x8BC8D0 | Write_s32 | write/4 | 4 (I in T005b) |
| 0x8BC970 | Write_f32 | write/4 | 4 (I) |
| 0x8BC9D0 | Write_f64 | write/8 | 8 (I) |
| 0x8BCB40 | Write_u64 | write/8 | 8 (I) |
| 0x8BCB80 | Write_bool | write/1 | 1 (I) |
| 0x8BC3E0 | sub_8BC3E0 | read/1 | not listed |
| 0x8BC830 | sub_8BC830 | write/1 | not listed |
| 0x8BCB00 | sub_8BCB00 | write/8 | not listed |

  Every T005b § 2.1 fixed-width VA has the T005b width; the variable-length ones are null as designed
  (`Read_MtString` 0x8BC5B0, `Read_bytes` 0x8BC710, `Write_MtString` 0x8BC790, `Write_cstr` 0x8BCA30),
  and so is the 64-bit swap helper 0x8BC340. Three unnamed functions classify as codecs too (not in
  T005b; not checked here).

### PS4

`bash research/ida/private-copy.sh ps4 t005d` -> `P`, sha256
`79d6c2f574f8f241429f6e2e842ed13e7f4be93335d06f4055187438c68c11ea` (unchanged after both batch runs).

    idat -A -L$T/dumps/logs/ps4-ida.log "-S$T/extract_ida.py $T/dumps/ps4-ida.jsonl ps4" $P

rc 0, 33 s. `dumps/ps4-ida.jsonl` sha256 `f6101fea37475e8854057715e00686c8e0edd4312b9341d9ab33e24f399fd8d4`,
3,902 lines, `extract_ida` 3, header `bitness` 64, `image_base` 0, `input_sha256` `4236f598...2c63c0`
(= the DWARF dump's ELF). Summary: `functions` 3,568, `roots` 1,455 = `depth0_functions`,
`missing_roots` 0, externs 332 (import 25, out_of_scope 307), `codec_functions` 4. No table and no
orphan-ref count on PS4 (PC-only fields). Call sites 25,327; with `const_regs` 5,554.

Codec check against T005b § 2.2 (V): the four classified agree (`Read_u8` 0x3B6140 read/1, `Read_s8`
0x3B6250 read/1, `Write_f32` 0x3B6880 write/4, `Write_f64` 0x3B68F0 write/8). The other 18 fixed-width
`nPacket::Read_*`/`Write_*` (e.g. `Read_u16` 0x3B6160, `Read_u32` 0x3B6190, `Write_u8` 0x3B6640) have
`codec` null. Reason, from their disassembly (read-only batch, § 4):

- `Read_u16` / `Read_u32`: `lea rcx,[rdx+2|4]`, `cmp rcx,[packet+20h]`, then the cursor is advanced by
  **storing** the precomputed pointer (`mov [packet+18h], rcx`), not by `add [..], N`, so the
  classifier finds no cursor advance. `Read_u8` uses `inc qword ptr [packet+18h]` and passes.
- `Write_u8`: the bounds check is `cmp [packet+10h], rcx` / `jz` (pointer equality), no `cmp r, N`,
  so no direction; it advances with `inc [packet+20h]`.

This is a coverage gap of `classify_codec` on PS4 (script owned by T005c; not edited), not
negative evidence. I: a PS4 rule accepting `mov [base+d], r` where `r = lea [cursor+N]` would cover the
reads.

## 4. Spot checks (read-only batch)

Script `spot.py` in the session scratchpad (not in the repo:
`C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/t005d/spot.py`),
`idat -A -L<scratch>/spot-pc.log "-S<scratch>/spot.py pc $T/dumps/repair3-apply.jsonl <scratch>/spot-pc.json" $DB`
and `... spot.py ps4 - <scratch>/spot-ps4.json $P`; both rc 0, `DBFL_KILL` before `qexit`, both
`.i64` hashes unchanged. Database identity from the script: PC `get_idb_path` = the work copy,
`inf_is_64bit` false, image base 0x400000; PS4 = the private copy, 64-bit, image base 0x0.

Range 0x888000-0x88E000 had no repair, so the 6 checks are 3 in 0x758000-0x77C000 and 3 "other".
All 6: function start = target, end = recorded end, 0 tails, `ida_hexrays.decompile` succeeded, the
recorded call site's instruction is `call sub_<target>`.

| case | VA | start / end | first / last insn | caller | Hex-Rays |
| --- | --- | --- | --- | --- | --- |
| A add_func | 0x75D430 | 0x75D430 / 0x75D57A | `push ecx` / `retn` | 0x803350 | 72 lines, `int __cdecl sub_75D430(CPacket *packet, unsigned int value)` |
| A replace, gap junk | 0x7626E0 | 0x7626E0 / 0x7627E9 | `push ecx` / `retn` | 0x806440 | 63, `int __cdecl sub_7626E0(CPacket *packet, unsigned int value)` |
| A add_func level 2 | 0x775FB0 | 0x775FB0 / 0x77605D | `push esi` / `retn` | 0x775E90 | 12, `BOOL __cdecl sub_775FB0(CPacket *packet, int a2)` |
| other add_func | 0x785D70 | 0x785D70 / 0x785DCA | `mov byte ptr [ecx+4],17h` / `retn` | 0x7C44C0 | 18, `_BYTE *__thiscall sub_785D70(_BYTE *this)` |
| other add_func, stray deleted | 0x80D540 | 0x80D540 / 0x80D5B3 | `push ebx` / `retn 4` | 0x7DFEC0 | 22, `int __thiscall sub_80D540(int this, CPacket *packet)` |
| other replace, gap junk | 0x579640 | 0x579640 / 0x579755 | `mov eax,[esp+arg_0]` / `retn 4` | 0x57EFE0 | 81, `int __thiscall sub_579640(int this, int a2)` |

- Old enclosing starts 0x7626DD and 0x57963E: no function, no name, still a code item (`is_code`
  true), as T004f saw at 0x7E0F0C; observed, not explained.
- Function count (`get_func_qty`): 151,639 after the apply; T004f measured 151,549. Net +90 = 89 + 1
  `add_func` into undefined code (the stray case and the 27 `replace_func` are net 0). I: so no extra
  functions were created by auto-analysis at callees, and the dry run changed no functions.

## 5. Manifest, logs, cleanup

`uv run python manifest.py` (from `$T`) rewrote `dumps/MANIFEST.tsv` (7 rows): new rows `repair3-dryrun`
(3f1e9acc..., 1,167 lines, v3), `repair3-apply` (ce5e61da..., 1,285, v3); updated `pc-ida` (7e323747...,
7,948, v3) and `ps4-ida` (f6101fea..., 3,902, v3); `ps4-dwarf`, `repair-apply`, `repair-dryrun` unchanged.

Logs (`dumps/logs/`): `repair3-dryrun.log` fca087b3..., `repair3-apply.log` f77163467..., `pc-ida.log`
67de5945... (appended to T004f's), `ps4-ida.log` 6e57178c....

The PS4 private copy folder `ddon-data-t005d` was deleted after the runs (only batch processes, all
exited, had opened it; no ida-mcp worker).

Not run: the repo gates (`tools/check.sh`, pytest); no script was changed. The 3 listing checks for
`readback_neighbours` failures: not applicable (0 such failures).
