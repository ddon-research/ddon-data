# 007 T004f: repair the PC handler function starts by headless batch, re-extract

Build PC 03040008. Address basis: VA (image base 0x400000, 32-bit; confirmed by the spot-check batch:
`idc.get_idb_path()` = the work copy, `inf_is_64bit` false, image base 0x400000). Base commit
2ffd1fed1c (`repair_functions.py` / `extract_ida.py` as of T004e, 4cd15c65e3). Run 2026-11-03
09:08-09:10 +0100. All IDA work by `idat.exe` batch (`C:/Program Files/IDA Professional 9.5/idat.exe`);
no ida-mcp worker opened the work copy; the original and accepted databases were only read
(hashed and copied by `private-copy.sh`).

Work copy `DB` = `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`;
`T` = `D:/ddon-data/research/03040008/ida-transfer`. Every command ran with `MSYS_NO_PATHCONV=1`.

## 1. Fresh work copy

`bash research/ida/private-copy.sh pc-accepted 007work`. The T004d folder held only the packed `.i64`
(no `.id0/.id1/.nam/.til`), so the script removed it and recopied.

| point | `.i64` sha256 | bytes | mtime (+0100) |
| --- | --- | --- | --- |
| fresh copy | `382e346e0b48b157e261119cf803c7b10d072b40ba3ae187a79291d640a58c0f` (= `accepted_PC.sha256`) | 111,299,352 | 09:08:12 |
| after dry run (2a) | `c7c18fc4c27df0712f76b7af6941f1976daefa9b2cfea53c638d21861c6ce6ed` | 111,299,594 | 09:08:25 |
| after apply (2b) | `7189b4c6f76ff03eb985d1430dfa1a3892d1f8eb2ad7c9e558b5506cfb1b2c65` | 111,609,190 | 09:08:55 |
| after read-back (2c) and both spot-check runs (3) | `7189b4c6...1b2c65` (unchanged) | 111,609,190 | 09:08:55 |

The dry run also rewrites the `.i64`: its batch entry ends in `qexit(0)`, which saves and repacks even
with no repair applied (observed: size +242 B, new hash). Nothing was repaired in it (all results
`would-repair`/`already-ok`/`refused`); the change is IDA's own save. The read-only runs (extract,
spot check) set `DBFL_KILL` and left the `.i64` byte-identical, as designed.

After every run the folder held only the `.i64` (no `.id0`/`.id1`/`.nam`/`.til`), and
`rg -c -i "unpacked|restore" dumps/logs/` found no match (rg exit 1) in any log.

## 2. Batch runs

### a. Dry run

    idat -A -L$T/dumps/logs/repair-dryrun.log "-S$T/repair_functions.py $T/dumps/repair-dryrun.jsonl" $DB

rc 0, 6 s. `dumps/repair-dryrun.jsonl` sha256 `a39be75bf69da3257003e7d13c5f85e27eab760c520470f4973714baeaa22194`,
1,042 lines, script version 2, header `idb_path` = the work copy, `bitness` 32, `image_base` 0x400000,
`input_sha256` `f1c974d0...19fa20`. Log summary line:
`{"apply": false, "by_check": {"indirect_jump": 1}, "by_status": {"already-ok": 909, "refused": 1, "would-repair": 130}, "callbacks": 1040}`.

Of the 131 non-start callbacks: 130 would-repair (118 `add_func`, 2 of them deleting a stray function;
12 `replace_func`), 1 refused. Gate (>= 125 repaired, <= 6 refused): passed.

### b. Apply

    idat -A -L$T/dumps/logs/repair-apply.log "-S$T/repair_functions.py $T/dumps/repair-apply.jsonl --apply" $DB

rc 0, 7 s. `dumps/repair-apply.jsonl` sha256 `7443ba6c34e0ddbb38ef62fed122f3c9f4691d7fd5aee4dedb7a555bb364edc4`,
1,172 lines (1 header, 1,040 results, 130 undo, 1 summary). Summary:
`{"apply": true, "by_check": {"indirect_jump": 1}, "by_status": {"already-ok": 909, "refused": 1, "repaired": 130}}`.
**0 failed.** Every `repaired` record passed the script's own read-back.

| repair kind | count | callbacks |
| --- | --- | --- |
| `add_func`, no function before | 116 | |
| `add_func` after deleting a stray in the body | 2 | 0x7E1330 (`nullsub_3712` at 0x7E13F4), 0x7F4040 (`nullsub_3369` at 0x7F4120) |
| `replace_func` (delete enclosing, add at callback) | 12 | the 9 T004d `gap_not_padding` (0x7C5C90, 0x7C68E0, 0x7C6A90, 0x7D7150, 0x7E0950, 0x7E0F10, 0x7E1530, 0x7F0480, 0x7FE5E0; `gap_junk` true) + the 3 T004d failures (0x7C3840, 0x7D8590, 0x7F1790; `gap_junk` false) |

Refusal (1): **0x7D1BE0, `indirect_jump` at 0x7D1CAE** (no function). Stated check, verified in the
spot-check batch: the bytes at 0x7D1CAE are `ff 24 85 4c 1e 7d 00` (`jmp [eax*4+7D1E4Ch]`), but the
listing there is undefined (`db 0FFh`, `is_code` false at the callback and at the jump) and
`ida_nalt.get_switch_info(0x7D1CAE)` is None, so the T004e switch exception cannot apply. Inferred: it
needs IDA switch info first (create the code and let IDA or a hand-set switch recover the table at
0x7D1E4C); not done (outside the authorized writes).

Names are not moved (README, by design). Three deleted enclosing starts carried user names, which now
sit on non-function bytes while the callback is `sub_<va>` (verified for two in the spot check;
from the undo records for the third):

| callback | old enclosing start | name left there |
| --- | --- | --- |
| 0x7C5C90 | 0x7C5C8D | `cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_PHASE_ENTRY_READY_RES` |
| 0x7D7150 | 0x7D714C | `cSeedGameSvConnection::OnPacket_GP_GET_CAP_TO_GP_CHANGE_LIST_RES` |
| 0x7D8590 | 0x7D858F | `cSeedGameSvConnection::OnPacket_GP_GP_SHOP_DISPLAY_BUY_RES` |

Similarly the stray names `nullsub_3712`/`nullsub_3369` stay on the `retn 4` inside the repaired bodies
(the address now belongs to the callback's function).

### c. Read-back

    idat -A -L$T/dumps/logs/pc-ida.log "-S$T/extract_ida.py $T/dumps/pc-ida.jsonl pc" $DB

rc 0, 18 s. `dumps/pc-ida.jsonl` sha256 `57cb84040e79964433a2dd248a84f0b602b8bd5cb7a90efd37e0a70fef588118`,
7,112 lines, `extract_ida` version 2.

- `table_ok` true: 1,041 records, 1,040 callbacks, 74 initializers, `unproved_records` [].
- `missing_roots` 1 (no-function 1, inside-function 0) = refusals (1) + failures (0) of b. The single
  `missing_root` record is VA 0x7D1BE0 (`root` table), the refused callback: sets identical.
- `depth0_expected` 1,681 = `depth0_functions` 1,681; `roots` 1,682; `onpacket_functions` 675
  (T004d 671); `senders` 642; `functions` 6,068 (T004d 6,000).
- `onpacket_orphan_ref_count` 6 (T004d 9, T004b 38). The 6 strings and their referencing addresses
  (`from`): `OnPacket_QUEST_GET_PACKAGE_QUEST_LIST_RES` (0x45668B8),
  `OnPacket_SKILL_SET_ABILITY_RES` (0x2BDF3C0), `OnPacket_SKILL_SET_OFF_PAWN_SKILL_RES` (0x2BDF468),
  `OnPacket_SKILL_GET_ABILITY_COST_RES` (0x2BDF560), `OnPacket_POTION_ORB_ELEMENT_CHECK_RES`
  (0x2BDF5C8), `OnPacket_POTION_JOB_ELEMENT_RELEASE_RES` (0x2BDF5D8). Inferred, not checked: the
  `from` addresses lie far above the handler code (0x7Cxxxx-0x7Fxxxx), so these are data references,
  not callbacks the repair could fix.

## 3. Spot checks (read-only batch)

Script `spot_check.py` in the session scratchpad (not in the repo); run as
`idat -A -L<scratch>/t004f-spot2.log "-S<scratch>/spot_check.py $T/dumps/repair-apply.jsonl <scratch>/t004f-spot.json" $DB`,
rc 0; the log is copied to `dumps/logs/spot-check.log`. It sets `DBFL_KILL` before `qexit` (`.i64`
unchanged, table 1). A first run (log not kept) decompiled the same functions but failed to strip tags
(`ida_hexrays.tag_remove` does not exist; fixed to `ida_lines.tag_remove`). Function count in the
copy after the repairs: 151,549 (`get_func_qty`; the count before was not measured in this run).

All 9: start = callback, end = the end recorded by the repair, one chunk (0 tails),
`ida_hexrays.decompile` succeeded.

| kind | callback | start / end | first / last insn | Hex-Rays (lines, declaration) |
| --- | --- | --- | --- | --- |
| add_func | 0x7C3280 | 0x7C3280 / 0x7C336E | `push esi` / `retn 4` | 61, `int __thiscall sub_7C3280(int this, CPacket *packet)` |
| add_func | 0x7F7BB0 | 0x7F7BB0 / 0x7F7C56 | `push esi` / `retn 4` | 44, `int __thiscall sub_7F7BB0(int this, CPacket *a2)` |
| stray deleted | 0x7E1330 | 0x7E1330 / 0x7E13F7 | `sub esp,30h` / `retn 4` | 51, `int __thiscall sub_7E1330(MtObject **this, CPacket *a2)` |
| stray deleted | 0x7F4040 | 0x7F4040 / 0x7F4123 | `push esi` / `retn 4` | 42, `int __stdcall sub_7F4040(int a1)` |
| replace, gap junk | 0x7C5C90 | 0x7C5C90 / 0x7C5D62 | `push esi` / `retn 4` | 54, `int __thiscall sub_7C5C90(int this, CPacket *a2)` |
| replace, gap junk | 0x7E0F10 | 0x7E0F10 / 0x7E10DB | `sub esp,68h` / `retn 4` | 56, `int __thiscall sub_7E0F10(int this, CPacket *a2)` |
| T004d failure | 0x7C3840 | 0x7C3840 / 0x7C38C0 | `sub esp,1Ch` / `retn 4` | 18, `int __thiscall sub_7C3840(MtObject **this, CPacket *a2)` |
| T004d failure | 0x7D8590 | 0x7D8590 / 0x7D8647 | `push esi` / `retn 4` | 46, `int __thiscall sub_7D8590(int this, CPacket *a2)` |
| T004d failure | 0x7F1790 | 0x7F1790 / 0x7F1836 | `push esi` / `retn 4` | 44, `int __thiscall sub_7F1790(int this, CPacket *a2)` |

- The 3 T004d failures are now **repaired** (verified above); no function remains at their old
  enclosing starts 0x7C383F, 0x7D858F, 0x7F178E.
- Strays: 0x7E13F4 and 0x7F4120 now belong to the functions at 0x7E1330 and 0x7F4040.
- Old enclosing 0x7C5C8D: no function, not code (junk undefined). Old enclosing 0x7E0F0C: no function,
  but still a code item (`is_code` true) - observed, not explained; it lies outside every function.
- 0x7F4040 decompiles as `__stdcall (int a1)` while its body ends `retn 4` like the others; Hex-Rays
  did not infer `__thiscall` (no prototype set). Inferred: a typing matter for T006, not a bounds error.

## 4. Manifest

`uv run python manifest.py` (from `$T`) rewrote `dumps/MANIFEST.tsv`: rows pc-ida (57cb8404..., 7,112
lines, extract_ida 2), repair-apply (7443ba6c..., 1,172, repair_functions 2), repair-dryrun (a39be75b...,
1,042, repair_functions 2); ps4-dwarf and ps4-ida rows unchanged.

Logs (`dumps/logs/`): `repair-dryrun.log` 1702494b..., `repair-apply.log` e8c52de1...,
`pc-ida.log` c1eda52d..., `spot-check.log` 69d562fe....

Not run: the repo gates (`tools/check.sh`, pytest); no script was changed.
