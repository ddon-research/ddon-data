# 007 T004b: IDA and DWARF fact extractor run

Date 2026-11-03. Repo base `8c1c409e620`. Address basis: VA (PC 32-bit, image base `0x400000`;
PS4 64-bit, image base `0`). Status words: **verified** (checked in IDA in the same session),
**inferred**, **not run**.

## Inputs

| Item | Identity |
| --- | --- |
| PC database (private copy) | `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t004b/2022_01_29_DDO_DUMP_FIX.exe.i64` (copied by `bash research/ida/private-copy.sh pc-accepted t004b`), IDA 9.5, 32-bit, base `0x400000`; input SHA-256 `f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20` (PC 03040008) |
| PS4 database (private copy) | `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t004b/DDOORBIS.elf.i64` (`private-copy.sh ps4 t004b`), IDA 9.5, 64-bit, base `0`; input SHA-256 `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0` (PS4 02020005) |
| `extract_ida.py` | sha256 `7d9bb14d641242e9fcc04fc4645aea48d36da84a5ac9a92d5452d7797cd93eb2`, script_version 1 |
| `extract_dwarf.py` | sha256 `532a84cacda823ba8c6b01f0e67f31a98cd2125ce33a9a2893d7e67138af6cb6`, script_version 1 (pyelftools 0.33, capstone 5.0.9, Python 3.15.0 per header) |
| `manifest.py` | sha256 `4e233c079644a88f33e7704db8d7f71ff668c09246f0ffaffa19ebb22db51b3d` |

Both databases confirmed before analysis with `idc.get_idb_path()`, `ida_ida.inf_is_64bit()` and
`ida_nalt.get_imagebase()` (PC: False / `0x400000`; PS4: True / `0x0`). Stored input paths name
`IDA9.3` (import metadata). Nothing was renamed, typed, commented, patched or saved.

## Commands and times

1. PC, ida-mcp `execute_python` (instance `139bcb81906c`):
   `exec(open(".../extract_ida.py").read(), {"OUT": ".../dumps/pc-ida.jsonl", "SIDE": "pc"})`:
   6.1 s, one call, no batching needed.
2. PS4, ida-mcp `execute_python` (instance `ac1af0fa0a5c`), same with `ps4`: 8.5 s.
3. `cd research/03040008/ida-transfer && uv run python extract_dwarf.py --ida-dump dumps/ps4-ida.jsonl`
   (default `--out dumps/ps4-dwarf.jsonl`): 08:37:16 to 08:44:43, wall 7 m 26 s (script reports
   `seconds` 362.3, `scope_seconds` 5.1), exit 0. Its stdout went to the session scratchpad, so
   `dumps/run.log` is still the log of the **earlier** T004 run (08:33), not this one.
4. `uv run python manifest.py` rewrote `dumps/MANIFEST.tsv`.

## Outputs (`research/03040008/ida-transfer/dumps/`)

| File | bytes | lines | sha256 | source sha256 |
| --- | --- | --- | --- | --- |
| `pc-ida.jsonl` | 6,832,064 | 6,674 | `6b6bf0a3704f0174fb57a5ff0654a1a11e95222d8926f904920e0cb552b816af` | `f1c974d0...19fa20` |
| `ps4-ida.jsonl` | 3,895,852 | 3,570 | `cc4c7c10d8ca3f6bcc9a4e8ffef73c30d0f1fe8f1087b87857a531b343a22346` | `4236f598...c63c0` |
| `ps4-dwarf.jsonl` | 19,393,414 | 12,188 | `ed2182bc2cd8a752f74a892d3d4ce87ce50ace920b04c60113ada9fe3a2bb5bf` | `4236f598...c63c0` |

The previous `ps4-dwarf.jsonl` (`415a4b05...`, 19,399,288 bytes, own scope 3,574) is replaced; its
header now says `scope_source: ida-dump dumps/ps4-ida.jsonl`.

## Summary records

- PC: `table_ok: true`; `table_records` 1,041, `table_callbacks` 1,040, `initializers` 74
  (all equal to `expected`); `unproved_records` []; conflicts 0; `onpacket_functions` 589,
  `onpacket_orphan_refs` 38, `senders` 642, `roots` 1,691, `functions` 5,631.
  One record (group 15, id 0xFFFF, sub 0xFF, record VA `0x212C748`, assignment `0x1A2C5F7`) has the
  proved literal `0`: callback null, so 1,041 records give 1,040 non-null distinct callbacks.
- PS4: `roots` 1,455, `functions` 3,568.
- DWARF: `scope` 3,568 (= the PS4 IDA dump), `functions` 3,534, `scope_without_dwarf` 34,
  `scope_without_cu` 34, params 7,598, locals 6,629 (all named; 4,133 with location), inlined
  37,787, blocks 23,031, types 8,652 (class 6,946, structure 640, typedef 669, enumeration 246,
  union 151), CUs parsed 660. Earlier run (own scope 3,574): also 34 without DWARF.

## Sanity counts (stdlib Python over the dumps)

| Count | PC 03040008 | PS4 02020005 |
| --- | --- | --- |
| function records (distinct VAs) | 5,631 | 3,568 |
| roots by kind (function records) | table 909, write_entry_caller 642, onpacket_string 9, none (callee) 4,071 | symbol 1,455 (OnPacket_ 802, Send_ 404, CPacket Read/WritePacket 249), none 2,113 |
| depth 0/1/2/3 | 1,560 / 1,999 / 1,156 / 916 | 1,455 / 980 / 766 / 367 |
| call sites per function: median / mean / max / total | 4 / 4.49 / 265 / 25,300 | 6 / 7.1 / 183 / 25,327 |
| indirect call sites | 4,523 | 4,734 |
| `default_name` true | 5,320 | 15 |
| functions with a string containing `OnPacket_` | 589 | 0 (verified: IDA's string list has no `OnPacket_` string in the PS4 database) |
| PC table callbacks with a function record | 909 of 1,040 | n/a |
| PC table callbacks that are also OnPacket_-string functions | 580 | n/a |
| PC `ecx_read_before_write` true | 4,748 | n/a |
| PC annotations: lvars / insn comments / func comment / Hex-Rays comments / hexrays_error | 82 / 3,580 / 26 / 598 / 0 | n/a |

## Finding: 131 PC table callbacks have no function record (coverage gap, reported not fixed)

131 of the 1,040 proved callbacks (all in `.text`, `0x7C3280`..`0x7FE880`) are not IDA function
starts in the PC database, so `_ida_function` returns `None` and they are absent from the dump.
The summary does not list them: `roots` 1,691 counts them, depth-0 records are 1,560 (1,691 - 131).
**Verified** in IDA (`ida_funcs.get_func`, `idc.get_item_head`, `ida_bytes.get_flags`):

| State at the callback VA | count |
| --- | --- |
| no function, item head, not code (data/unknown) | 50 |
| no function, inside a misaligned code item | 38 |
| no function, inside a data item | 30 |
| no function, code head | 1 |
| inside a function that starts 1-4 bytes earlier (code head 7, mid-item 5) | 12 |

Examples: `0x7C3280` lies inside the misdecoded item `0x7C327D` (`add eax, 5756035Dh`) although its
bytes `56 57 8B F9` are `push esi; push edi; mov edi, ecx`; `0x7E62C0` lies inside `dd` data at
`0x7E62BE` although its bytes `B8 01 00 00 00 C2 04 00` are `mov eax, 1; retn 4`. For the 12, the
enclosing functions start just before the callback (e.g. `0x7C5C90` in
`cSeedGameSvConnection::OnPacket_BATTLE_CONTENT_PHASE_ENTRY_READY_RES` at `0x7C5C8D`, `0x7D7150` in
`OnPacket_GP_GET_CAP_TO_GP_CHANGE_LIST_RES` at `0x7D714C`); 9 of those enclosing functions are in
the dump (as `onpacket_string` roots or callees), 3 are not (`0x7E152F`, `0x7F047F`, `0x7FE5DE`).

Consequences for the matcher (**inferred**, from the code at `extract_ida.py` lines 438-442 and
666-684): (a) the dump silently lacks 131 handler roots and their callee subtrees, so 909 (or 918
counting the 9 shifted starts) of 1,040 handlers are matchable; (b) `_ida_callees(va)` uses
`get_func(va)`, which returns the enclosing function, so for the 12 shifted callbacks the
enclosing function's callees enter scope at depth 1 under the wrong root VA. Neither is a wrong
table count; it is an IDA database coverage gap the script does not report (no field for dropped
roots). The 38 `onpacket_orphan_refs` (OnPacket_ strings referenced from outside any function) are
likely the same gap (**inferred**, not cross-checked VA by VA). Not fixed, per the brief.

## Spot checks (verified, same session)

Method: for each function, an independent walk of `idautils.Chunks`/`Heads` collecting `call`
sites (`idc.get_operand_value` for near/far operands, else `indirect`), near `jmp` tail calls to
another function start, and string-literal data refs; compared as sets of (site, target) and
(ea, text) with the dump record.

| Side | VA | Function | calls dump/IDA | equal | strings equal |
| --- | --- | --- | --- | --- | --- |
| PC | `0x7C31D0` | `sub_7C31D0` (table root) | 6/6 | yes (targets: indirect, `sub_8BC2E0`, `sub_785A60`, `sub_7FF650`, indirect, `cSeedGameSvConnection::callOnPacketFunc`) | yes (`...OnPacket_ACHIEVEMENT_ACHIEVEMENT_GET_...`) |
| PC | `0x81DC90` | `cSeedGameSvConnection::Send_C2S_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_REQ` (write_entry_caller) | 5/5 | yes (`WritePacket`, `nPacket::Write_u8`, `cSeedServerConnection::Send`, 2 indirect) | yes (none) |
| PC | `0x4A94F0` | `sub_4A94F0` (depth 3) | 4/4 | yes | yes (2 `obj\pl\pl000000\edit\preset\body\...` paths) |
| PC | `0x7C5C8D` | `OnPacket_BATTLE_CONTENT_PHASE_ENTRY_READY_RES` (shifted start, see above) | 5/5 | yes | yes |
| PS4 | `0x303B00` | `cSeedGameSvConnection::OnPacket_S2C_AREA_POINT_UP_NTC` | 10/10 | yes (`CPacket_S2C_AREA_POINT_UP_NTC::ReadPacket`, `snprintf` x2, `sGUIExt::getMsgFromIdxInfo`, `sChat::addMessage`, ...) | yes (`%d`) |
| PS4 | `0x19AFDF0` | `cSeedGameSvConnection::Send_C2S_LOGOUT_REQ` | 7/7 | yes (`nPacket::Write_u16` x3, `cSeedServerConnection::Send`, `__stack_chk_fail`, 2 indirect) | yes (none) |
| PS4 | `0x19D4760` | `nUserSession::CPacket_S2C_DECIDE_CHARACTER_ID_RES::ReadPacket` | 6/6 | yes (`Read_u16`, `Read_s32`, `Read_u32`, `Read_CDataCharacterInfo_`, `Read_bool`, `Read_u8`) | yes (none) |

Call arguments (`arg_regs`, PC stack/ecx arguments), constants, `ecx_read_before_write` and the
DWARF records were not spot-checked: **not run**.

## Housekeeping

- Only the three dumps and `dumps/MANIFEST.tsv` were written, plus this report. Scripts untouched.
- The ida-mcp workers for both private copies (`139bcb81906c`, `ac1af0fa0a5c`) could not be closed:
  `close_database` is withheld from this role. They hold the `ddon-data-t004b` copies only; the
  coordinator should close them (and may delete the `ddon-data-t004b` folders).
