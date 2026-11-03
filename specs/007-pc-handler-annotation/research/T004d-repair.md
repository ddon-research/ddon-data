# 007 T004d: repair the PC handler function starts and re-extract

Build PC 03040008. Address basis: VA (image base 0x400000). Base commit 43ed48dafc. Run 2026-11-03
08:56-08:58 +0100, one ida-mcp worker (instance `20da69c39583`, backend idat).

## 1. Work copy

- `bash research/ida/private-copy.sh pc-accepted 007work` (the folder did not exist before) printed
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`.
- Source: `accepted_PC` of `CURRENT-RECOVERY.json`
  (`feature008-field-map-property-working-20261029T161123Z/2022_01_29_DDO_DUMP_FIX.exe.i64`).
- sha256 of the copy before any write: `382e346e0b48b157e261119cf803c7b10d072b40ba3ae187a79291d640a58c0f`
  (equals `accepted_PC.sha256`), 111,299,352 bytes.
- Confirmed in IDA: `idc.get_idb_path()` = the copy's path, 32-bit (`inf_is_64bit` false), image base
  0x400000, min ea 0x401000, 151,408 functions before repair.

## 2. Dry run

`exec(open("D:/ddon-data/research/03040008/ida-transfer/repair_functions.py").read(), {"OUT": ".../dumps/repair-dryrun.jsonl", "APPLY": False})`

Output `dumps/repair-dryrun.jsonl`, sha256 `a7f4bad3afd1cc05c14b239eca6982fdbb7c424e4473cb72ccdedf91f43cfdcc`, 1,042 lines.

| status | count |
| --- | --- |
| already-ok | 909 |
| would-repair | 119 (116 `add_func`, 3 `set_func_start`) |
| refused | 12 (`gap_not_padding` 9, `runs_into_function` 2, `indirect_jump` 1) |

Gate (>= 100 would-repair, <= 30 refused): passed, so APPLY ran.

### Refusals (verified from the listing; all 12 callbacks begin with a clean prologue)

Every refused callback starts a plausible MSVC `__thiscall` handler body (`sub esp,N` / `push esi` /
`push [esp+..+packet]`), 16-byte aligned. The refusals are the script's conservative rules, not bad
callbacks; whether each counts as a "script defect" is the coordinator's call. Listings below are from
the work copy before APPLY (these 12 were not touched).

**`gap_not_padding` (9)**: IDA's function starts 1-4 bytes before the callback, on unreferenced
non-padding bytes (no xrefs to any of the 9 enclosing starts). Gap bytes and the enclosing listing:

| callback | enclosing start | gap bytes | enclosing listing (enclosing name) |
| --- | --- | --- | --- |
| 0x7C5C90 | 0x7C5C8D | `43 0d b3` | `inc ebx` / `or eax,8B5756B3h` (crosses cb) (`cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_PHASE_ENTRY_READY_RES`) |
| 0x7C68E0 | 0x7C68DE | `56 57` | `push esi; push edi`, then `sub esp,450h` at cb (`sub_7C68DE`) |
| 0x7C6A90 | 0x7C6A8E | `31 c6` | `xor esi,eax` (`sub_7C6A8E`) |
| 0x7D7150 | 0x7D714C | `83 ec 24 a1` | `sub esp,24h` / `mov eax,ds:0F98B5756h` (crosses cb) (`cSeedGameSvConnection::OnPacket_GP_GET_CAP_TO_GP_CHANGE_LIST_RES`) |
| 0x7E0950 | 0x7E094D | `8b 14 24` | `mov edx,[esp]` (`sub_7E094D`) |
| 0x7E0F10 | 0x7E0F0C | `40 00 cc 37` | `inc eax; add ah,cl; aaa` (`sub_7E0F0C`) |
| 0x7E1530 | 0x7E152F | `56` | `push esi` (`sub_7E152F`) |
| 0x7F0480 | 0x7F047F | `53` | `push ebx` (`sub_7F047F`) |
| 0x7FE5E0 | 0x7FE5DE | `31 e0` | `xor eax,esp` (`sub_7FE5DE`) |

Inferred: the gap bytes are junk left between functions (preceded by `int3`/`align` padding, never
referenced), so moving the start to the callback would be correct; the script refuses because its
padding whitelist (and its "tail of a crossing instruction" rule, which only frees bytes from the
crossing item on) does not cover them. Two enclosing starts carry user names that the script would
leave at the old start.

**`runs_into_function` (2)**: the decoded body reaches a 3-byte IDA `nullsub` sitting on the body's own
final `retn 4`:

- 0x7E1330 (no function): body runs to 0x7E13F4, where `nullsub_3712` = [0x7E13F4, 0x7E13F7) `retn 4`.
- 0x7F4040 (no function): body runs to 0x7F4120, where `nullsub_3369` = [0x7F4120, 0x7F4123) `retn 4`.

Inferred: the nullsubs are spurious functions on the callbacks' epilogues (no xrefs to either), so the
refusal comes from IDA's stray function, not from the body.

**`indirect_jump` (1)**: 0x7D1BE0 (no function, body undefined in the listing) has a switch dispatch
`ff 24 85 4c 1e 7d 00` = `jmp [eax*4+7D1E4Ch]` at 0x7D1CAE; the jump table follows at 0x7D1E4C. A clean
handler with a switch; the linear walker does not follow switch tables by design.

## 3. Apply

`exec(open(".../repair_functions.py").read(), {"OUT": ".../dumps/repair-apply.jsonl", "APPLY": True})`

Output `dumps/repair-apply.jsonl`, sha256 `a0c949879162546cf780f60946e806f610b6e4fd305853e601ea4c78ba14d4c9`,
1,161 lines (header, 1,040 results, 119 undo records, summary).

| status | count |
| --- | --- |
| already-ok | 909 |
| repaired | 116 (all `add_func`) |
| failed | 3 (all `set_func_start`, rc 3) |
| refused | 12 (as in the dry run) |

### Script defect: all 3 `set_func_start` repairs failed and left the listing without a function

rc 3 is `ida_funcs.MOVE_FUNC_NOFUNC` (verified: the constant reads 3). Before calling
`set_func_start(enc, cb)`, `_apply` undefines the conflicting items, and these include the enclosing
function's entry instruction (at `enc`). Undefining a function's entry deletes the function in IDA, so
`set_func_start` then finds no function. The read-back state now (verified):

| callback | old enclosing start | body end | now |
| --- | --- | --- | --- |
| 0x7C3840 | 0x7C383F (unnamed) | 0x7C38C0 | no function at cb or at 0x7C383F; 0x7C383F is `db 83h`; cb decodes `sub esp,1Ch` |
| 0x7D8590 | 0x7D858F `cSeedGameSvConnection::OnPacket_GP_GP_SHOP_DISPLAY_BUY_RES` | 0x7D8647 | no function; the name stays on the undefined byte `db 0Fh` at 0x7D858F; cb decodes `push esi` |
| 0x7F1790 | 0x7F178E (unnamed) | 0x7F1836 | no function; 0x7F178E is `db 3Dh`; cb decodes `push esi` |

The undo records for these three are in `repair-apply.jsonl` (written before the change). I did not
fix them by hand (outside the authorized writes). The fix belongs in `repair_functions.py`: for
`set_func_start`, move the start (or `del_func` + `add_func(cb)`) before undefining the item at `enc`,
or skip undefining `enc` until after the move. Until then, `add_func(cb)` on each would likely
complete the repair (inferred, not run).

### Spot checks (5 repaired, sampled every 23rd repaired record)

| callback | start | end (= decoded end) | first / last | Hex-Rays |
| --- | --- | --- | --- | --- |
| 0x7C3280 | 0x7C3280 | 0x7C336E | `push esi` / `retn 4` | ok, 61 lines, `int __thiscall sub_7C3280(int this, CPacket *packet)` |
| 0x7D23D0 | 0x7D23D0 | 0x7D24A5 | `push esi` / `retn 4` | ok, 59 lines, `int __thiscall sub_7D23D0(int this, CPacket *a2)` |
| 0x7E11D0 | 0x7E11D0 | 0x7E1276 | `push esi` / `retn 4` | ok, 44 lines |
| 0x7F0D10 | 0x7F0D10 | 0x7F0DF1 | `push esi` / `retn 4` | ok, 56 lines |
| 0x7FE880 | 0x7FE880 | 0x7FE931 | `sub esp,20h` / `retn 4` | ok, 36 lines, `int __thiscall sub_7FE880(MtObject **this, CPacket *packet)` |

All 116 `repaired` records passed the script's own read-back (start, end, no neighbour bound change).

## 4. Re-extract

`exec(open("D:/ddon-data/research/03040008/ida-transfer/extract_ida.py").read(), {"OUT": ".../dumps/pc-ida.jsonl", "SIDE": "pc"})`

Output `dumps/pc-ida.jsonl`, sha256 `4e0f8e8b70b7cce633b9579eb505626a866a22c4bb19241e6415449104206730`,
7,058 lines, `extract_ida` version 2, input sha256 `f1c974d0...19fa20`.

- `table_ok` true: 1,041 records, 1,040 callbacks, 74 initializers (as expected), no unproved records.
- `missing_roots` 15 (no-function 6, inside-function 9): exactly the 12 refusals plus the 3 failures
  (VA sets compared, identical). Expected "only the refusals": off by the 3 failures above.
- `onpacket_orphan_ref_count` 9 (T004b: 38).
- `onpacket_functions` 671, `senders` 642, `roots` 1,688, `depth0_functions` 1,673, `functions` 6,000.

`uv run python manifest.py` rewrote `dumps/MANIFEST.tsv` (5 rows: pc-ida, ps4-dwarf, ps4-ida,
repair-apply, repair-dryrun; ps4 rows unchanged).

## 5. Persistence (2026-11-03 08:58 +0100, worker still open)

- `.i64`: 111,299,352 bytes, mtime 08:56:21, sha256 still `382e346e...a58c0f` (not repacked).
- Unpacked beside it: `.id0` (246,702,080 B, 08:57:52), `.id1` (272,932,864 B, 08:57:52), `.id2`
  (183,552 B), `.nam` (417,792 B, 08:57:52), `.til` (106,417 B). The repairs live only in these
  unpacked files until the worker closes and repacks; the worker remains open (instance `20da69c39583`).
