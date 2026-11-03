# 007 T005g: extractor v4 run on both sides (read-only batch)

Builds: PC 03040008 (work copy; 32-bit, image base 0x400000) and PS4 02020005 (private copy
`ddon-data-t005g`; 64-bit, image base 0). Address basis: VA (decimal in the dumps, hex here).
Base commit a9e9c3eb1d (`extract_ida.py` script version 4 from 778d9264db). Run 2026-11-03
10:59-11:31 (WEST). All IDA work by `C:/Program Files/IDA Professional 9.5/idat.exe` batch with
`MSYS_NO_PATHCONV=1`; no ida-mcp worker was opened; the original and accepted databases were not
opened. No script in the repo was changed.

`DB` = `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`,
`P` = `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t005g/DDOORBIS.elf.i64`,
`T` = `D:/ddon-data/research/03040008/ida-transfer`, `S` = the session scratchpad
`C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/t005g`.

Status marks: V verified (read in this run), I inferred, C contradicted.

## 0. Answer in brief

- PC v4: rc 0, 65 s, `table_ok` true, 1 missing root (0x7D1BE0, as T005d), **7,262 functions**
  (v3 6,261; v3 set fully contained), 48,235 object-access records (1,684 indexed, 4,142 via a pointer
  load), 581 requester sites / 546 requesters / 33 `requester_site` records outside functions, 3,876
  functions with a non-null `codec_distance`. Spot checks all agree with the listing.
- PS4 v4: rc 0, 61 s, 0 missing roots, **4,146 functions** (v3 3,568; contained), but only **722
  object-access records in 102 functions** and **0 slot stores** (`via` 280 = `mpManager`).
- **C / defect (V): the PS4 object-access pass is defeated by IDA register-variable names.** The PS4
  database names argument registers (`this`, `src`, `pBase`, ...), so `print_operand` prints
  `[this+cArcLoaderBase.mNum]` and `parse_mem_text` finds no base register; every such operand is
  silently dropped. A scratch what-if that maps regvar names back to their canonical registers
  (`ida_frame.find_regvar`) before the same parse gives **30,587 records in 2,839 functions** (1,772
  indexed, 7,345 via, **2,685 `mpManager` slot stores**). The same what-if on PC changes nothing
  (0 regvar operands, 48,235 = 48,235). The PS4 v4 `object_accesses` are therefore not fit for T006;
  `extract_ida.py` needs a fix (owner: the script's task, not this one) and a PS4 re-run.
- `extract_dwarf.py --ida-dump` re-run (PS4 scope grew 3,568 -> 4,146): 4,106 functions with DWARF,
  40 without; `manifest.py` rewrote `dumps/MANIFEST.tsv`.
- Work copy sha256 `65120b34...8b9111` before and after every run (V).

## 1. Database identity and state

| point | `.i64` | sha256 |
| --- | --- | --- |
| PC work copy before | `DB` | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` (= brief) |
| PC work copy after extract, what-if, spot (11:30) | `DB` | same; folder holds only the `.i64` |
| PS4 private copy after `private-copy.sh ps4 t005g` | `P` | `79d6c2f574f8f241429f6e2e842ed13e7f4be93335d06f4055187438c68c11ea` (= T005d's copy) |
| PS4 after extract | `P` | same |

Identity from the dump headers and the spot script (V): PC `idb_path` = `DB`, bitness 32,
`image_base` 4194304 (0x400000), `input_sha256` `f1c974d0...19fa20`; PS4 `idb_path` = `P`,
bitness 64, `image_base` 0, `input_sha256` `4236f598...2c63c0`.

One scratch what-if attempt on `P` failed at import (`ida_regvar` does not exist in IDA 9.5; the
function lives in `ida_frame`): rc 1, and it left the unpacked `.id0/.id1/.nam/.til` beside the
private copy (the `.i64` hash stayed `79d6c2f5...`). The private copy folder was deleted at the end
(11:30), so nothing of it survives. The PC work copy was never touched by that failure.

## 2. Runs

    idat -A -L$T/dumps/logs/pc-ida.log  "-S$T/extract_ida.py $T/dumps/pc-ida.jsonl pc"  $DB   # rc 0, 65 s
    idat -A -L$T/dumps/logs/ps4-ida.log "-S$T/extract_ida.py $T/dumps/ps4-ida.jsonl ps4" $P    # rc 0, 61 s

`-L` appends: both logs hold the earlier runs plus this one (summary line last).

| dump | sha256 | bytes | lines | version |
| --- | --- | --- | --- | --- |
| `dumps/pc-ida.jsonl` | `4b307aee49d00d5018861e4c4395555f6997a3fa914f6d62a4ab0243114361f0` | 14,277,655 | 8,914 | 4 |
| `dumps/ps4-ida.jsonl` | `e1d96a484424c0c3edc980007e005c172230cb616e240c7ed43987a90b537325` | 4,991,561 | 4,484 | 4 |
| `dumps/ps4-dwarf.jsonl` | `352d86c700f8d7dc0f6262e78816d818f77feab749b9d070b8f2a1d8834d8f69` | 21,841,300 | 12,916 | extract_dwarf 1 |

Logs: `pc-ida.log` `33520412...cb99bb5`, `ps4-ida.log` `d6c8e8fa...4cabe3cad`, new `ps4-dwarf.log`
`988c97f1...af514f` (stdout+stderr of the DWARF run).

## 3. Counts (V, `jq` over the dumps)

| count | PC v4 | PS4 v4 |
| --- | --- | --- |
| functions (v3) | 7,262 (6,261) | 4,146 (3,568) |
| v3 functions missing from v4 / new in v4 | 0 / 1,001 | 0 / 578 |
| by scope: depth / `codec_path` | 7,054 / 208 | 4,132 / 14 |
| by root: table / write-entry caller / requester / symbol / none | 1,039 / 642 / 546 / - / 5,035 | - / - / 468 / 1,455 / 2,223 |
| roots = depth-0 functions (expected) | 2,228 roots, 2,227 = 2,227 | 1,923 = 1,923 |
| `table_ok` | true (1,041 records, 1,040 callbacks, 74 initializers, unproved []) | n/a |
| missing roots | 1 (no-function 0x7D1BE0, `root` table) | 0 |
| externs (by reason) | 575 (import 15, inside_function 12, not_function 20, out_of_scope 528) | 336 (import 31, out_of_scope 305) |
| codec functions | 20 | 4 (T005d gap unchanged) |
| object-access records | 48,235 in 5,884 functions | **722 in 102 functions** |
| of which indexed | 1,684 | 39 |
| of which via a pointer load (`via`) | 4,142 | 90 |
| stores / loads / lea; immediate-value stores | 22,805 / 18,534 / 6,896; 13,104 | 363 / 321 / 38; 92 |
| by `arg_loc` | ecx 35,851, stack 12,384 | rdi 519, rsi 173, rdx 24, rcx 6 |
| PS4 slot stores (`via` 280 = `mpManager`, offset from `ps4-dwarf.jsonl`) | - | **0** |
| reserve dialog VA / name | 0xBB39D0 `sNetworkExt::reserveNetworkErrorDialog` | 0x7EDF80 same |
| `requester_sites` / `requesters` / sites outside functions (`requester_site` records) | 581 / 546 / 33 | 478 / 471 / 0 |
| functions with non-null `codec_distance` | 3,876 (0: 24, 1: 2,048, 2: 1,507, 3: 279, 4: 10, 5: 5, 6-8: 1 each) | 2,324 (0: 411, 1: 1,262, 2: 626, 3: 16, 4: 3, 5: 2, 6: 1, 7: 3) |
| run time | 65 s | 61 s |

Notes:
- PC `requester_sites` 581 = T005b § 5 (V). The 24 PC `codec_distance` 0 functions are more than the 20
  `codec` functions: the four variable-length codecs count as codecs for the distance (README v4).
- PS4 `codec_distance` 0 = 411: every `nPacket::Read_*`/`Write_*` symbol in scope counts (README), not
  only the 4 shape-classified codecs.

## 4. The PS4 register-variable defect (V, with a scratch what-if)

Observation: `cArcLoaderBase::clear` 0x241E0 (PS4) has 0 records. Its listing (spot batch, § 5):
`mov r15, this` at 0x241EA (where `this` is IDA's register-variable name for `rdi`), then
`movzx r14d, [this+cArcLoaderBase.mNum]` 0x24204 and `mov [this+cArcLoaderBase.mNum], 0` 0x24236. The
dataflow trace shows `r15` holding argument 0 at both, but the operands carry no `base`
(`parse_mem_text` sees only `this` and the member name in the brackets, neither a register), so the
access is dropped. In `nJobParam::cJobInfo::operator_` 0x62470 the `[rdi+...]` stores are recorded but
the `[this+...]` and `[src+...]` operands from 0x624E1 on are not. The README states the
operand-text SIB parse as the design (IDAPython 9.5 has no `ida_intel` SIB helpers); it did not
account for register-variable names.

What-if (`S/whatif.py`, read-only batch, `DBFL_KILL`): the extractor module imported unchanged, run
over every function of each v4 dump with one shim: before `parse_mem_text`, each bracketed identifier
that is not a register and is a register variable at that EA (`ida_frame.find_regvar(pfn, ea, ea+1,
None, name)`) is replaced by `regvar.canon`.

| side | dump records | what-if records | functions with records | indexed | via | via 280 stores | regvar operands rewritten | time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PS4 | 722 | 30,587 | 2,839 | 1,772 | 7,345 | 2,685 | 31,522 | 18.8 s |
| PC | 48,235 | 48,235 | 5,884 | 1,684 | 4,142 | 1 | 0 | 22.8 s |

Examples (what-if, V against the listing): `cNetGameServer::logout` 0x33F230
`mov [this+(cNetGameServer.mStatus+0Ch)], 4` at 0x33F273 -> rdi arg 0, disp 20, width 4, store, value
4; `cNetGameServer::finalPartyFlow` 0x33F9E0 `mov [this+(cNetGameServer.mStatus+0A0h)], 4` at
0x33FA2E -> disp 168, value 4. The v4 dump has 0 records for both functions.

I: a fix in `extract_ida.py` along the shim's line (or taking the base from `op.phrase` when the
operand has no SIB) restores PS4 coverage; PC is unaffected. Until then the PS4 v4
`object_accesses` (and anything derived from slot stores) are a coverage gap, not negative evidence.
The what-if output (`S/whatif-ps4.json`, `S/whatif-pc.json`) is scratch, not a deliverable.

## 5. Spot checks (V; `S/spot.py`, read-only batch, `DBFL_KILL`)

`spot.py` imports the extractor, re-runs `_ida_object_accesses` on the function with a traced
`_step` (register state before each instruction) and prints `GetDisasm` per item; for call sites,
the 8 heads before the site. Identity printed: PC `DB`, not 64-bit, base 0x400000; PS4 `P`, 64-bit,
base 0. Re-run records equal the dump records for all four functions.

PC `sub_4169B0` 0x4169B0 (`push ebx; mov ebx,[esp+4+arg_0]; ... mov edi,ecx`):

| VA | listing | record | ok |
| --- | --- | --- | --- |
| 0x4169BA | `mov edx,[ebx+4]` (ebx = stack arg 0) | stack 0, disp 4, w 4, load | V |
| 0x4169C7 | `mov [edi+8E0h],edx` (edi = ecx) | ecx, disp 0x8E0, w 4, store | V |
| 0x4169D2 | `mov ecx,[ebx+10h]` | stack 0, disp 16, w 4, load | V |
| 0x4169D5 | `mov esi,[ecx+eax*4]` (ecx = [arg0+10h]) | stack 0, via 16, indexed eax*4, w 4, load | V |
| 0x4169E6 | `lea edx,[edi+ecx*4]` | ecx, lea, indexed ecx*4 | V |
| 0x416A07 | `cmp eax,[edi+8E0h]` | ecx, disp 0x8E0, w 4, load | V |

PC `sub_403DC0` 0x403DC0 (`mov eax,[esp+arg_0]; ... mov esi,ecx`):

| VA | listing | record | ok |
| --- | --- | --- | --- |
| 0x403DCD | `mov byte ptr [esi+0Ch],1` | ecx, disp 12, w 1, store, value 1 | V |
| 0x403DD1 | `cmp [eax+4],ebp` (eax = stack arg 0) | stack 0, disp 4, w 4, load | V |
| 0x403E1E | `mov ecx,[esi+4]` | ecx, disp 4, w 4, load | V |
| 0x403E2B | `mov [eax+ecx*4],ebx` (eax = [esi+10h]) | ecx, via 16, indexed ecx*4, w 4, store | V |
| 0x403E30 | `lea edi,[eax+10h]` (eax = [esi+8] on the `jnb` path) | ecx, via 8, disp 16, lea | V |

Not recorded (correct by the must-rule): 0x403DE0 `mov eax,[eax+10h]` is a loop head whose back edge
arrives with `eax` overwritten.

PS4 `nJobParam::cJobInfo::operator_` 0x62470 (rdi = this): 0x6247B `mov [rdi+_vptr],rax` disp 0 w 8
store; 0x6247E `mov [rdi+mItemSealResist_pri],0` disp 108 w 1 value 0; 0x62482
`mov dword ptr [rdi+mDefDownResist_pri],0` disp 104 w 4; 0x62489 `mov qword ptr [rdi+mStoneResist_pri],0`
disp 96 w 8; 0x62491 `[rdi+mSlowResist_pri]` disp 88 w 8: all V (op `addr` = record disp). DWARF:
`mItemSealResist_pri` offset 108, `mDefDownResist_pri` offset 104 size 1 (the dword store covers 104-107:
a merged store; width is the operand's, as designed).

PS4 `sub_194E9F0` 0x194E9F0 (`mov rbx, rdi`; rbx is callee-saved across the indirect calls):
0x194EA17 `mov [rbx],rax` disp 0 w 8 store; 0x194EA1A `mov rax,[rbx+28h]` disp 40 w 8 load; 0x194EA28
`lock xadd [rax],ecx` via 40 w 4 store rmw; 0x194EA4B `mov qword ptr [rbx+28h],0` disp 40 value 0;
0x194EA5E `mov [rbx+10h],rax` disp 16 store: all V.

Requester slot values (the reserve-dialog argument):

| side | function | site | listing | dump | ok |
| --- | --- | --- | --- | --- | --- |
| PC | `sub_42BBF0` 0x42BBF0 (2 chunks) | 0x8792F8 | `push 2D4h` | `const_stack` [[0, 724]] | V |
| PC | `sub_844430` 0x844430 | 0x844448 | `push 1B4h` | [[0, 436]] | V |
| PS4 | `cNetGameServer::logout` 0x33F230 | 0x33F282 | `mov esi, 3; comId` | `const_regs` rsi 3 | V |
| PS4 | `cNetGameServer::finalPartyFlow` 0x33F9E0 | 0x33FA48 | `mov esi, 28h; comId` | rsi 40 | V |

Side note (I): the site 0x8792F8 of `sub_42BBF0` lies in its second chunk, which starts
`push esi; mov esi, ecx; push 2D4h; mov dword ptr [esi+0B54h], 4` right after a `jmp` (a prologue
shape); its `[esi+0B54h]` store is not in the function's records. Likely a separate function IDA
attached as a tail; not investigated.

## 6. DWARF re-run and manifest

PS4 scope grew (3,568 -> 4,146), so (from `T`):

    uv run python extract_dwarf.py --ida-dump dumps/ps4-ida.jsonl     # rc 0, 1,131 s wall (script: 611.7 s, scope 9.6 s)

Summary (V): scope 4,146, `functions` 4,106 (before 3,534), `scope_without_dwarf` 40, params 8,767,
locals 7,813 (4,310 with location), inlined 45,051, blocks 26,998, types 8,808, CUs parsed 665. The
`missing_sample` begins with 0x194E9F0 (`CDataCommunityCharacterBaseInfo` D1) and lists PLT stubs
(`/PLstrlen`, `/PLmemcpy`, ...). Header: ELF `elf-dumps/.staging/input/DDOORBIS.elf`, sha256
`4236f598...2c63c0`, inline chains with the same ELF hash.

`uv run python manifest.py` rewrote `dumps/MANIFEST.tsv` (7 rows): `pc-ida` v4 (4b307aee...), `ps4-ida`
v4 (e1d96a48...), `ps4-dwarf` (352d86c7...); the four repair rows unchanged.

## 7. Not run, cleanup

- Not run: the repo gates (`tools/check.sh`, pytest), since no script changed; the matcher (`match.py`).
- The v3 dumps were kept as scratch copies (`S/pc-ida.v3.jsonl`, `S/ps4-ida.v3.jsonl`) for the
  containment check only.
- PS4 private copy folder `ddon-data-t005g` deleted at 11:30 after every batch had exited.
