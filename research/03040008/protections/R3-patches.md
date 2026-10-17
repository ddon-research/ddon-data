# R3 Patch inventory: every layer from vanilla to Bunie v7

Research brief `specs/003-client-protections/briefs/R3-patches.md`, including "Added after R2".
Static, read-only, 2026-10-17. No executable was run. Everything was measured on copies in the
session scratchpad: a numpy byte diff over every pair of the 15 dump-sized executables (68,231,680
bytes each), each `patches/*.r2` replayed in memory against its stated parent and hashed, and
`radiff2 -r` (radare2 6.1.0, no `-w`) run on copies to cross-check the three layers that have no
`.r2` (v7 from PerfPatch, v7 from f1c9, Win7 from FIX2). The radiff2 scripts agree with the numpy
runs: radiff2 splits runs at unchanged bytes, nothing else differs. Sites were named in the DUMP_FIX
IDB (`D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.i64`, idalib
through ida-mcp `open_database`, 32-bit, base `0x400000`; read-only, never saved, closed). The
Bunie v7 `dinput8.dll` was loaded into a throwaway headless IDB in the scratchpad, also closed.
Code caves were disassembled with capstone, because `rasm2` printed nothing in this shell.

Reused, not redone: R2 (`R2-static.md`) for the protection inventory; ddon-hook
`specs/011-client-automation/tasks.md` for the purpose of Bunie v7's 20 static patches and its
runtime patches; ddon-hook `specs/009-rng-race-monitor/tasks.md` (T014) for the NtSetContextThread
mask bug.

Conventions: **[fact]** = measured bytes or IDB disassembly; **[inference]** = my reading;
**not run** = no check was done. "IDB" = the f1c9 database, so it shows f1c9's bytes.

Addressing for the dumps (identical section table in all 15 files, verified with `pefile`):

| Section | VA range | File offset of VA start | VA = |
| --- | --- | --- | --- |
| header | `0x400000`–`0x4003FF` | `0x0` | off + `0x400000` |
| `.text` (game, first) | `0x401000`–`0x1AD4FFF` | `0x400` | off + `0x400C00` |
| `.rdata` | `0x1AD5000`– | `0x16D4000` | off + `0x401000` |
| `.data` | `0x2113000`– | `0x1D11A00` | off + `0x401600` |
| `.rsrc` | `0x220F000`– | `0x1D7BE00` | |
| `.reloc` (holds the IAT at `0x2233xxx` and protector code) | `0x2231000`–`0x240EFFF` | `0x1D9DC00` | off + `0x493400` |
| `.text#2` (captured SecureEngine image) | `0x240F000`–`0x45A3FFF` | `0x1F7B200` | off + `0x493E00` |
| `.SCY` (Scylla IAT store) | `0x45A4000`– | `0x410FE00` | |

---

## 1. Lineage

```
01dc41a9 DDO.exe 03040008, Themida-packed (= D:\DDON_03040008\DDO.exe.bak; PE ts 2019-01-25 01:22:59)
 |  Scylla dump at OEP 0xB89168, not byte-diffable (packed vs unpacked)
 v
0a7c5c63 2020_04_26_DDO_DUMP                              plain dump
 |  FIX2: 579 runs / 1,792 B  (patches/2021_05_01_ddo_dump_fix2.r2, replays to ef9d)
 v
ef9d1815 2021_05_01_DDO_DUMP_FIX2 ------------------------------------------------+
 |  FIX_3: 126 runs / 258 B  (r2 replays to e50d)                                 |
 v                                                                               |
e50dd517 2022_01_03_DDO_DUMP_FIX_3                                               |  Win7 re-dump/IAT rebuild:
 |-- MUTEX_E: 1 B   -> 526bd9d2 2022_01_21_DDO_DUMP_FIX_MUTEX_E                  |  1,692 of FIX2's 1,792 B kept,
 |-- MUTEX_F: 1 B   -> c3db6f19 2022_01_21_DDO_DUMP_FIX_MUTEX_F                  |  the other 100 reverted, +8,985 B
 |-- Mutex: 3 runs / 35 B -> 9c9542a7 2022_01_21_DDO_DUMP_Mutex                  |  of its own; no FIX_3, no FIX
 |      | FIX r2 (8 writes, 37 B) undoes Mutex and adds 2 B                       v
 +------+--> f1c974d0 2022_01_29_DDO_DUMP_FIX  (= FIX_3 + 2 B)      1c8cc43a DDO_Windows7Dumped_Mutex
              |-- chat 1 B        -> 31a30332 2025_05_29DDO_ChatEdit             |-- chat 1 B
              |-- cksum+chat 4 B  -> bf5107ef DDO_ChatEdit_4GB_RAM               v
              |-- 6 runs / 14 B   -> b9b9cf86 DDO_Bunie_3-in-1 = DDO_Bunie_100FPSPatch
              |-- 8 runs / 20 B   -> 268536f0 DDO_Bunie_5-in-1        f2a80229 DDO_DUMP_FIX_Patch3_Win7_Mutex_ChatEdit
              |-- 17 runs / 77 B  -> ac836bcd Buns_DDOPerfPatch_v1 = v2 = v3 (exe)       = installed D:\DDON_03040008\DDO.exe
              |                         | 8 runs / 98 B
              |                         v
              +-- (25 runs / 175 B) -> 03062388 Bunie_PerfPatch_v7\DDO.exe
```

How each parent was chosen ([fact], pairwise differing-byte counts, full matrix in scratchpad
`matrix.txt`):

| Child | Parent | Evidence |
| --- | --- | --- |
| 0a7c plain dump | 01dc41a9 packed | Same PE timestamp `2019-01-25 01:22:59Z` and identical section RVAs (`.text` `0x1000`, `.rdata` `0x16D5000`, second `.text` `0x200F000`); the dump only adds `.SCY` and rounds sizes. `DDO_v3.05.exe` (c93f7e4d) is **not** the parent: timestamp 2017-10-13, different section RVAs. |
| ef9d FIX2 | 0a7c | `.r2` replays to the exact hash. |
| e50d FIX_3 | ef9d | `.r2` replays. |
| 526b, c3db, 9c95 | e50d | `.r2` replays; 1 / 1 / 35 bytes. |
| **f1c9 FIX** | **e50d (content); 9c95 (as recorded)** | The `.r2` replays from 9c95, but it writes Mutex's 35 bytes back to the FIX_3 values. Content-wise f1c9 = FIX_3 + 2 bytes (diff e50d→f1c9 = 2 B, against 37 B from 9c95). f1c9 carries **none** of the Mutex layer. |
| 1c8c Win7 | ef9d FIX2 | Fewest diffs (9,085 B to FIX2, 9,343 to FIX_3, 10,677 to the plain dump). At FIX2's 1,792 changed bytes 1c8c holds FIX2's value at 1,692 and the plain dump's at 100 (the 9 constant/filler sites of §2.1); at FIX_3's 258, Mutex's 35 and FIX's 2 bytes it holds the **parent** value at every one. |
| f2a8 installed | 1c8c | `.r2` replays (1 byte). |
| 31a3, bf51, b9b9, 2685, ac83 | f1c9 | `.r2` replays. |
| 0306 v7 | ac83 PerfPatch | v7 = ac83 + 8 runs (98 B); all 17 ac83 runs are present in v7 unchanged. Against f1c9: 25 runs / 175 B. |

The three PerfPatch exes (v1, v2, v3) are byte-identical (ac83); only their `dinput8.dll` differ
(§4). `DDO_Bunie_100FPSPatch.exe` and `DDO_Bunie_3-in-1.exe` are byte-identical (b9b9).

---

## 2. Per-layer sites

### 2.1 FIX2 (nothilvien 2021-05-01), 0a7c → ef9d: 579 runs, 1,792 bytes

| Group | Count | VA range (file offset range) | Function | Old → new | Purpose |
| --- | --- | --- | --- | --- | --- |
| CRC/integrity: hash compare forced equal, `.text#2` | 484 | `0x2410F3A`–`0x4388DFF` (`0x1F7D13A`–`0x3EF4FFF`) | mutated engine code, mostly unnamed (e.g. `sub_D52011` at `0x24136A2`) | `cmp/sub/xor r,[base+idx*4]` (`3B0496` 123×, `3B148E` 113×, `33148E` 70×, `2B148E` 57×, `330496` 43×, `3B0C86` 40×, `2B0496` 37×, `3B0484` 1×) → `39C090` `cmp eax,eax; nop` | Sets ZF so the following `jz`/`jbe`/`cmovz` takes the "match" path. Shape: `mov r,[table+i*4]; cmp r,[computed+j*4]`, i.e. a stored-vs-computed checksum compare **[inference, strong]** |
| same, in the dump's `.reloc` | 44 | `0x223571E`–`0x23CBF09` (`0x1DA231E`–`0x1F38B09`) | protector code that lives in `.reloc` | same patterns → `39C090` | same **[inference]** |
| same, in game `.text` | 8 | `0x5B44D2`, `0x6496C2`, `0x7BAC12`, `0x8C1962`, `0xC5E752`, `0xCEE032`, `0xE9E292`, `0x166C1A2` | mutated code between game functions (IDA: `sub_223676A`, `sub_3785127`, `sub_36CA653`, others none) | same → `39C090`, each followed by `jz`/`jbe` into code | same **[inference]** |
| Anti-debug: `int 1` SEH trap | 12 | `.text` `0x489539`, `0x5F6639`, `0x8870A9`, `0x9658F9`; `.reloc` `0x22CD22D`; `.text#2` 7 sites `0x245069C`–`0x3A48D0D` | none / `sub_383FCEA` | `CD01` `int 1` → `9090` | Each site is `mov fs:[0],esp; push 0; push 0; int 1; jmp engine`: a single-step exception that a debugger swallows **[fact: disassembly; inference: anti-debug]** |
| Anti-debug: flag compare fix-up | 12 | `.text` `0x7408C8`; `.text#2` 11 sites `0x24608CC`–`0x4202ABE` | none | `cmp dword [ebp-2Ch],0` → `,1` (imm `00`→`01`) | Each sits after `pop fs:[0]; popa`: it tests the flag the SEH handler sets. With the `int 1` gone, the flag keeps its other value, so the compare is flipped to match **[inference]** |
| Protector SDK macro skipped | 9 | `0xB2B710` (`sub_811AA6`), `0xC152A0`, `0xC152D0`, `0xC15300`, `0xC15330`, `0xC16DC0`, `0xC16DF0`, `0xC16EB0` (2 B only), `0x145F2A0` (`sub_145EF6C`) | function entries | `E9 rel32` (to a `push offset ret; …` engine stub) → `EB1E 909090` `jmp +0x20` | Skips the first jump of the entry, which enters a SecureEngine macro, and lands on the real body at +0x20 **[inference: macro type unknown, could be CHECK_CODE_INTEGRITY or CHECK_DEBUGGER]** |
| Process enumeration | 1 | `0x13B4FAC` (`0xFB43AC`) | IAT thunk `jmp [Process32Next]` (IAT `0x22334D8`) | `FF25D8342302` → `C20800 909090` `ret 8` | Process32Next returns at once, so the process walk started at `0x7BAD02` (`CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS)`) stops. Likely a debugger/tool blacklist scan **[inference]** |
| CRC compensation / unknown | 8 | `0x5FD2B6`, `0x778156`, `0x86F13A`, `0xA6D376`, `0xC1189A`, `0xCA294A` (3 B), `0xCD8198`, `0xDCF28A` | inter-function padding (IDA: data) | 4 random bytes → 4 other random bytes | Unreferenced filler between functions. Changing 4 free bytes per region is how a patcher restores a region's CRC32 **[inference]** |
| Unknown | 1 | `0x188FC0F` (`0x148F00F`), 69 B | inside SIMD float code after `addss xmm5,xmm0` (no function in IDB) | real `movaps/mulss/addss` code → `C4` × 69 | Would fault if executed, so the path must be dead in f1c9. Purpose unknown; the Win7 lineage restores the original **[fact: bytes; inference: dead]** |

### 2.2 FIX_3 (nothilvien 2022-01-03), ef9d → e50d: 126 runs, 258 bytes

| Group | Count | VA range (file offset range) | Function | Old → new | Purpose |
| --- | --- | --- | --- | --- | --- |
| **CRC read stubbed** (the "~120" of 011/R2) | 121 | `.text#2` 113 sites `0x24115A0`–`0x4261986` (`0x1F7D7A0`–`0x3DCDB86`); `.reloc` 7 sites `0x22CE8E9`–`0x23C9DFB`; `.text` 1 site `0x1993575` (`sub_2F6AE97`) | mutated engine code | `8B02` `mov eax,[edx]` → `31C0` `xor eax,eax` | The checksum word reads as 0, then is stored to a global (e.g. `0x1993575: xor eax,eax; mov ds:[0x947026],eax`) **[fact: bytes; inference: CRC read]** |
| same, other register | 1 | `0x2F500BE` | engine | `8B08` `mov ecx,[eax]` → `31C0` | same **[inference]** |
| CRC compare branch forced | 1 | `0x32D83D7` (`sub_32D83C5`) | engine | `0F84` `jz` → `90E9` `nop; jmp` after `sub ecx,[esi+eax*4]` | Always takes the "match" path **[inference]** |
| CRC compare continuation redirected | 1 | `0x40E593B` | engine | the `push offset` after `sub ecx,[esi+eax*4]` at `0x40E5937`: `36762204` → `33C2BB00` (continuation becomes `sub_BBC233`) | Forces the "match" continuation **[inference]** |
| Unknown | 2 | `0xC11B40`, `0xCD3E29` | padding after a `ret` (IDA: data) | `B7F80000` / `B1F20000` → `FFFFFFFF` | Possibly descriptor fields read by the engine, like FIX's 2 bytes below **[inference, weak]** |

### 2.3 MUTEX_E / MUTEX_F (2022-01-21), e50d → 526b / c3db: 1 byte each

| VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- |
| `0x1CA3A59` (`0x18A2A59`) | `.rdata` string `"sDDOMain"`, the MtDTI class name passed by `sub_1A716C0` | `44` 'D' → `45` 'E' / `46` 'F' | Renames the main class. The single-instance check keys on that name (README: mutex string), so each rename is a separate instance slot. The check itself is not located: the only `CreateMutexA` (`sub_1497880`) is the savedata storage mutex. `FindWindowA` is read once in mutated code at `0xDBB363` **[inference]** |

### 2.4 Mutex (2022-01-21), e50d → 9c95: 3 runs, 35 bytes

| VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- |
| `0x3A87F85` (`0x35F4185`) | engine | `0F44C1` `cmovz eax,ecx` → `89C890` `mov eax,ecx; nop` | Forces the continuation `sub_10C9E63`. The ZF it consumes comes from the **CRC compare at `0x3A87F64`** (`sub ecx,[esi+eax*4]`), which FIX2 missed. So this neutralises the checksum over the instance-check code **[fact: bytes; inference: purpose]** |
| `0x3D174FA` (`0x38836FA`) | `sub_3D1749C` | `8B15A9559000` → `E99CC58800 90` jmp to the cave | Hooks into the cave below |
| `0x45A3A9B` (`0x410FC9B`), 29 B | end of `.text#2` (zero area) | cave: `mov byte[0x15BFFEF],6A; [..+1],00; [..+2],90` (writes `push 0; nop`), replays the stolen `mov edx,[0x9055A9]`, jumps back | Patches `0x15BFFEF` (undefined bytes next to the window/class setup `sub_15BF030`/`sub_15BF6A0`) **at runtime**, so no static CRC sees it: the actual instance-limit removal **[inference]** |

### 2.5 FIX / DUMP_FIX (2022-01-29), f1c9: 2 bytes on top of FIX_3

The `.r2` (from 9c95) has 8 writes: 6 restore the three Mutex runs to the FIX_3 bytes, 2 are new.

| VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- |
| `0x738B76` (`0x337F76`) | padding after the DTI getter `0x738B70` (`mov eax,offset dti; ret`) | `13` → `00` | The neighbouring words `0x738B66` (pointer) and `0x738B7A` (`dword 1`) are read by engine code (`sub_249A126` `sub edx,[0x738B66]`; `sub_496CB2`/`sub_350E411` `mov r,[0x738B7A]; sub r,1`), so this is a protector descriptor in game padding. Zeroing the `0x13` field (a length or count) disables one check block **[inference]**. README: "a few CRC checks removed around RNG" |
| `0xD5C79A` (`0x95BB9A`) | padding after `sub_D5C790` (`mov eax,offset dti__4056; ret`) | `13` → `00` | Same layout (`… c3 07 00 00 00 [13] 00 00 00 cc`) **[inference]** |

Net effect: f1c9 = FIX2 + FIX_3 + 2 descriptor zeroings. It has **no instance-limit removal**: the
Mutex layer is reverted.

### 2.6 Win7 dump (filmmachine_, 2025-08-25), ef9d → 1c8c: 75 runs, 9,085 bytes

| Group | Count | VA (off) | Old → new | Purpose |
| --- | --- | --- | --- | --- |
| IAT re-resolved | ~30 runs, 1,456 B | IAT `0x2233228`–`0x2233833` (in `.reloc`) | FIX2 holds absolute DLL addresses bound on the dumping machine (e.g. `0x60A64460`); 1c8c holds hint/name RVAs (`0x01E3xxxx`) and ordinal entries (`0x8000000n`) | Unbound IAT that any Windows can resolve: the Win7 compatibility fix **[fact: bytes; inference: purpose]** |
| `.SCY` rebuilt | 33 runs, 7,485 B | `0x45A4000`–`0x45A630F` | new Scylla import table | Paired with the import directory change in the header **[fact]** |
| Header | 2 | `0x4001E0` DataDirectory[1] (import) `0x41A461C/0x21C` → `0x41A4610/0x1E0`; `0x4001F9` DataDirectory[4] (security) zeroed | new import directory; certificate pointer dropped | **[fact]** |
| Instance limit | 1 | `0x1CA3A58` (`0x18A2A58`) `"sDDOMain"` → 8 × `00` | Empty class name, presumably no instance collision (name "…_Mutex") **[inference]** |
| CRC compares FIX2 missed | 5 | `0x24CD5DE`, `0x32D83D4`, `0x3A87F64`, `0x430DF3B` (`2B0C86`/`2B148E` `sub` → `39C990`/`39D290` `cmp r,r; nop`); `0x40E5937` (`2B0C86` → `29C990` `sub ecx,ecx; nop`) | Force "match". Three of these are **still live in f1c9 and every Bunie build** (§6) **[fact: bytes]** |
| Macro skip completed | 1 | `0xC16EB2` `1EDCFF` → `909090` | Makes FIX2's 2-byte `EB1E` at `0xC16EB0` look like the other 8 | cosmetic **[fact]** |
| CRT `_IsNonwritableInCurrentImage` | 1 | `0x19BD8A5` (`sub_19BD840` → `sub_19BD7F0`), 11 B | dump's `…; xor eax,eax; inc eax` → `mov eax,0; nop; not eax; and eax,1` | Both return 1 (equivalent). This check would fail on the all-RWX dump sections **[fact: disassembly; inference: why]** |
| FIX2 sites reverted | 9 (100 B) | the 8 "CRC compensation" words and the 69-byte `C4` fill of §2.1 | back to the plain-dump bytes | Consistent with those sites being CRC fix-ups rather than code changes **[inference]** |

### 2.7 Chat and 4GB layers

| Layer | VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- | --- |
| ChatEdit (rootofallthings 2025-05-29, 31a3), Win7 ChatEdit (techwomanwow, f2a8), and every Bunie build | `0xB298C5` (`0x728CC5`) | `sub_B298C0` (chat input setup) | `push 20h` → `push 7Fh` | Chat limit 32 → 127 characters **[fact]** |
| "4GB RAM" (mr.september 2025-11-26, bf51) and every Bunie build | `0x4001B8` (`0x1B8`) | `OptionalHeader.CheckSum` (`e_lfanew` `0x160` + `0x58`) | `0x041A920D` → `0x0411D321` | **Only the PE checksum.** `IMAGE_FILE_LARGE_ADDRESS_AWARE` (Characteristics `0x123`) is already set in the plain dump and every descendant. The new value equals the computed checksum of bf51 only. Functionally a no-op: a 4GB tool re-set an already-set flag and rewrote the checksum **[fact]** |

### 2.8 Bunie 3-in-1 (= 100FPSPatch) and 5-in-1, from f1c9

3-in-1: checksum + chat + 4 FPS bytes. 5-in-1 = 3-in-1 + 2 chat-cooldown runs.

| VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- |
| `0x609CC0` (`0x2090C0`) | `sub_609C90` | third byte of the float imm at `0x609CBE`: `42700000` (60.0) → `42C80000` (100.0), stored to `[n4+3Ch]` | FPS cap 60 → 100 (one of the two frame targets `sub_609C90` picks; 011) **[fact]** |
| `0x1556FA4`, `0x1556FAE`, `0x1556FC2` | `sub_1556BF0` | float `3C888889` (1/60) → `3C23D70A` (0.01 = 1/100) | Model simulation step **[fact]** |
| `0xB2924A` (`0x72864A`) (5-in-1) | `sub_B291B0` (chat send) | `jbe` → `jmp` after `comiss` on `[ebx+1BF34h]` | Hidden-chat cooldown removed **[fact; purpose from r2 comment]** |
| `0xB29564` (`0x728964`) (5-in-1) | `sub_B291B0` | `mov eax,[ebx+1BF60h]` → `mov eax,5` | Shout cooldown 10 s → 5 s **[fact; purpose from r2 comment]** |

### 2.9 Buns_DDOPerfPatch v1/v2/v3 exe (ac83), from f1c9: 17 runs, 77 bytes

5-in-1's 8 runs, plus:

| VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- |
| `0x7BAD02` (`0x3BA102`), 14 B | process-walk call site (`push 0; push 2; push ret; jmp CreateToolhelp32Snapshot`) | → `mov eax,-1; jmp 0x59E9F6` + NOPs | Snapshot "fails" (INVALID_HANDLE_VALUE) and goes straight to the `cmp esi,-1` continuation: no process enumeration at all. Same target as FIX2's Process32Next stub **[fact]** |
| `0x22334E0` (`0x1DA00E0`) | IAT slot `CreateToolhelp32Snapshot` (in `.reloc`) | bound `0x77B45910` → `0x015BF901` | Every other caller lands in the cave `mov eax,-1; ret 8` **[fact]** |
| `0xBEEA2D` (`0x7EDE2D`) | `sub_BEEA00` | `jz 0xBEEB0E` → `jmp 0xBEEB0E` right after `call IsDebuggerPresent; cmp eax,1` | Always takes the "debugger present" branch, which skips the free-disk-space check (011). Launcher/boot check; also the one game-side IsDebuggerPresent made constant **[fact: bytes; purpose: 011]** |
| `0x147EEF1` | `sub_147EEF0` | `push 32h` → `push 1` | `Sleep(50)` → `Sleep(1)` (perf) |
| `0x14882A0` | `sub_14882A0` | `push [ecx+4]` → `push 1; nop` | `Sleep(var)` → `Sleep(1)` (perf) |
| `0x15BF83A` + cave `0x15BF8F2` (23 B) | `sub_15BF6A0` (message loop) | `jz loc_15BF708` retargeted to the cave `push 1; call Sleep; jmp 0x15BF708`; the cave also holds the `mov eax,-1; ret 8` thunk at `0x15BF901` | Idle message loop yields with Sleep(1) (perf) **[fact]** |
| `0x1805870` | `sub_1805870` (callback forwarder; called from `sub_1804090`, `sub_18055C0`) | → `xor eax,eax; ret 14h` | Callback stubbed to return 0 (011). Purpose unknown **[unknown]** |
| `0x180DB03` | `sub_180DA20` | `ja` → `jmp` in an rdtsc delta loop | Ends the rdtsc busy-wait (perf; R2 §4) |

### 2.10 Bunie PerfPatch v7 exe (0306), from ac83: 8 runs, 98 bytes

| VA (off) | Function | Old → new | Purpose |
| --- | --- | --- | --- |
| `0x5C1D66` | `sub_5C1D60` (called from `sub_5C4140`) | `jnz` → `nop nop`: the function now always returns 0 | unknown (011 lists it without a purpose) **[unknown]** |
| `0xC764F8` | float in mutated code | `1.0f` → `0.1f` | Periodic send interval 1.0 → 0.1 (`PeriodicSendInterval` default, 011) |
| `0x104A6DC`, `0x104A71C`, `0x104A73C` | `sub_104A6D0`, `sub_104A710`, `sub_104A730` | `jz` → `jmp`: never call `sub_16DEB60` | unknown. Perhaps tied to FastActionUpdates or the shadow features **[unknown]** |
| `0x3D159C5` (`0x3881BC5`), 45 B | zero area in `.text#2` | cave re-implementing `sub_16DEB60`'s tail: `call sub_16EBC40`; increment a counter at `0x3D159C1`; call vfunc `+0x74` only when `((esi>>4)+counter)&7==0` | A throttled version of `sub_16DEB60`. No static reference in the exe, and none among the 103 game addresses the v7 DLL references: possibly dead **[inference]** |
| `0x1CA3A88`, `0x1CA3A94` (`.rdata`) | quit-dialog strings | Shift-JIS "終了" / "Dragon's Dogma Online を終了しますか？" → "Exit DDO" / "Close Dragon's Dogma Online (DDO) now?" | English quit dialog (UI) |

Summary of v7 against f1c9 (175 B, 25 runs): 1 header, 20 `.text`, 2 `.rdata`, 1 IAT (`.reloc`), 1
`.text#2` cave. This matches 011's "20 own static exe patches".

---

## 3. Which layers carry the CRC stubs ("Added after R2")

| Build | FIX2: 536 compares + 12 `int 1` + 9 macro skips | FIX_3: 122 reads `→ xor eax,eax` + 2 forced compares | FIX: 2 descriptor zeroings | Win7: 5 extra compares | Mutex runtime cave |
| --- | --- | --- | --- | --- | --- |
| 0a7c plain dump | no | no | no | no | no |
| ef9d FIX2 | yes | no | no | no | no |
| e50d FIX_3, 526b, c3db | yes | yes | no | no | no |
| 9c95 Mutex | yes | yes | no | no | yes |
| **f1c9 DUMP_FIX** and all its descendants (31a3, bf51, b9b9, 2685, ac83, 0306) | yes | yes | yes | **no** (3 of 5 live: `0x24CD5DE`, `0x3A87F64`, `0x430DF3B`; the other 2 are covered by FIX_3's branch forcing) | no |
| **1c8c Win7, f2a8 installed** | yes, except the 9 compensation/fill sites (reverted) | **no**: all 258 FIX_3 bytes are the FIX2 originals | **no** | yes | no |

So R2 and 011 are right that f2a8 lacks the ~120 CRC-read stubs. Exactly: 122 sites, all from FIX_3
(2022-01-03), not from FIX (f1c9). f2a8 does carry FIX2's 536 compare stubs and the `int 1` removal.
Neither lineage neutralises every check: f1c9 keeps 3 compares that Win7 removed, and f2a8 keeps the
122 reads (whose compares FIX2 may already force **[inference]**) and both FIX descriptor blocks. The name
"…_Patch3_…" on f2a8 does not mean nothilvien's FIX_3.

---

## 4. Bunie's injected DLLs: hook libraries and the Nt* "Themida compatibility" hooks

| Build | `dinput8.dll` (SHA-256[:12], size) | Hook library | Anti-debug pieces |
| --- | --- | --- | --- |
| PerfPatch v1 | 669647e269ff, 13,824 (`BunDDOInject.pdb`) + `dinput8_real.dll` e3c170b06b87 (Microsoft dinput8, forwarded) | **own 5-byte `E9` inline hook** with a `VirtualAlloc` trampoline (no MinHook strings or code) **[inference from v3's source, same helper strings]** | NtQIP + NtSetContextThread hooks, one-shot PEB.BeingDebugged clear |
| PerfPatch v2 | a29b6e975c22, 14,848 | same own hook | same; loads the real dinput8 from the system directory (`LoadLibraryA`) |
| PerfPatch v3 | 7d11ffbd45ad, 22,528 (IDA `.c`/`.i64` beside it) | same own hook, `sub_10001B90` **[fact: v3 `dinput8.dll.c`]**: copies 5 bytes to a 0x20-byte RWX trampoline (or rebuilds an existing `E9`), writes `E9 rel32` | + `NtQueryInformationThread` for thread identity, a **PEB watchdog thread**, the "SB patch" at `0xF09655` (5 × `90` over the game→engine `jmp loc_378C552` in `sub_F09652`, runtime only), crash logger (`AddVectoredExceptionHandler`) |
| PerfPatch v7 | 8b60d64259d8, 262,144 (not packed: `.text` entropy 6.68, clean IAT, `.fptable`) | **MinHook** (`MH_CreateHook`/`MH_EnableHook` strings and error paths; `THIRD_PARTY_NOTICES.txt`; `InstallHook` `sub_1000E790` follows up to 8 chained `E9`s before hooking) **[fact: IDB of the DLL]** | same two Nt hooks, always on ("baseline"); the SB patch and the watchdog only with `Debugging=1` |

The Nt* hooks in v7 (`sub_10001000`, `sub_10001150`, installed by `sub_100014B0`; v3's
`sub_10001C40`/`sub_10001D70` are the same) **[fact: Hex-Rays on the DLL]**:

| Hook | Filter | Effect |
| --- | --- | --- |
| `NtQueryInformationProcess` → `sub_10001000` | Only classes 7, 30, 31, and only for the own process (`GetCurrentProcess()`, or a handle whose `ProcessBasicInformation` PID is ours); all else passes through | 7 `ProcessDebugPort` → 0, STATUS_SUCCESS. 30 `ProcessDebugObjectHandle` → 0 and `STATUS_PORT_NOT_SET` (`0xC0000353`), what Windows returns with no debugger. 31 `ProcessDebugFlags` → 1 (NoDebugInherit, i.e. not debugged). `ReturnLength` = 4. With a null trampoline it returns `STATUS_INTERNAL_ERROR` without calling the original |
| `NtSetContextThread` → `sub_10001150` | Only the own thread (`GetCurrentThread()`, or `NtQueryInformationThread`/`GetThreadId` TID match) | `ContextFlags &= 0xFFFEFFEF` and Dr0–Dr3, Dr6, Dr7 zeroed, then the original. The mask clears `0x10` (debug registers) **and `0x10000` (`CONTEXT_i386`)**, the bug 009 T014 found (it should clear only `0x10`) |
| PEB watchdog `sub_100012D0` (v7: `Debugging=1`; v3: always) | — | Every 100 ms: `if (PEB.BeingDebugged) PEB.BeingDebugged = 0`, rate-limited logging |

Reading **[inference]**: these hooks answer the debugger probes that the live SecureEngine image
makes through ntdll (the dump's IAT has no Nt* imports, R2 §3). They keep a debugger or ScyllaHide-style
tooling from tripping Themida, and they also protect Bunie's own `SetThreadContext` users. Bunie
calls them "Themida compatibility" and keeps them on in normal play, which suggests the engine's
debug-port and debug-register checks can fire without a debugger, for example from leftover
Dr7 state.

Other v7 runtime patches (from 011, corroborated by the 103 game addresses the DLL references):
MinHook on `GetForegroundWindow`, IAT writes on `GetActiveWindow` (`0x223365C`), `IsIconic`
(`0x223367C`) and XInput (`0x22337AC`–`0x22337B8`), NOPs at `0x14EAD29`/`0x14EAD33`
(`sub_14EACE0`), hooks at `sChat::addMessage` (`0xB27D70`), `sub_B291B0`, the logo/title callbacks
(`0xDAA536`, `0xFED460`, `0xFEE190`), the shadow allocator `sub_17AC910`, and runtime float writes at
`0x609CBE` and `0x1556FA4/FAE/FC2` (an FPS watchdog re-applies them).

---

## 5. What cannot be diffed

- **Packed originals** (01dc41a9 `DDO.exe.bak`, c93f7e4d `DDO_v3.05`, b36a…, ef6c…): Themida
  encrypts every section (entropy 7.4–8.0, R2), so no byte diff against the dumps means anything.
  Lineage plain dump ← 01dc41a9 rests on the PE timestamp and section RVAs only.
- **Bunie v7's exe is not Themida-packed.** It is the same Scylla dump as f1c9 plus 175 bytes, and its
  DLL is a plain MSVC build. What is Themida-protected is the game: the live SecureEngine code in
  `.text#2` is captured, mutated and mostly undisassembled in the IDB (R2 §10). So these cannot be
  read statically: what each CRC compare covers, whether more compares or reads exist in the
  undisassembled islands, and which code each FIX/FIX_3 descriptor describes.
- **Runtime-only patches**: the Mutex cave's write to `0x15BFFEF`, v3/v7's SB patch at `0xF09655`,
  and every MinHook/IAT/float write by the DLLs. None of them is in an exe diff. Listed from code
  (§4) and from 011, never observed at runtime (**not run**).

---

## 6. Protections no layer touches: crash-trap candidates

From R2's inventory, checked against every diff run of every layer (for the PEB reads: no diff
within `0x80` bytes; the nearest is a FIX2 compare stub at `0x3B166F7`, `0x7B` from the read at
`0x3B1667C`).

| Protection (R2 §) | Location | Touched by | Note |
| --- | --- | --- | --- |
| **3 live CRC compares** (new here) | `0x24CD5DE` (`sub ecx,[esi+eax*4]; jz`), `0x3A87F64` (feeds `cmovz` at `0x3A87F85`), `0x430DF3B` (`sub edx,[esi+ecx*4]; jmp`) | Win7 lineage only; **live in f1c9 and all Bunie builds** | Prime candidates for f1c9's residual integrity reaction (R2 T1) **[inference]** |
| FIX/FIX_3-style padding descriptors | other `… c3 [len] 00 00 00 …` blocks next to DTI getters, read by engine code (pattern of `0x738B66`/`0x738B7A`) | only two zeroed (FIX), two set to -1 (FIX_3, unconfirmed) | **not run**: a scan for more such blocks |
| 23 PEB `fs:[30h]` reads | `.text#2`: `0x246A13B`, `0x24A1000`, `0x24BF352`, `0x24C9D83`, `0x24CEB5C`, `0x24D0150`, `0x2527530`, `0x2F487A4`, `0x33CF678`, `0x33D9701`, `0x350E390`, `0x35125C5`, `0x3645E41`, `0x3A8644F`, `0x3B1667C`, `0x3C06CA0`, `0x3C0714F`, `0x3D2C8AA`, `0x40861F3`, `0x4092D1E`, `0x412C3EF`, `0x41B6891`, `0x4225011` | no exe layer; Bunie's watchdog clears `BeingDebugged` at runtime | Live in every dump |
| Nt* debug probes via ntdll | engine, dynamic | no exe layer; Bunie DLL hooks (all PerfPatch builds) | Live in every build without the DLL, including f1c9 and f2a8 as ddon-hook runs them |
| IsDebuggerPresent in the CRT | `sub_19A7F4B`, `sub_19AE207`, `sub_19C1338` | none | CRT paths, low value |
| Game VEH crash reporter, Get/SetThreadContext | `sub_145Cxxx`/`sub_145Dxxx` | none (FIX2's macro skip at `0x145F2A0` sits in neighbour `sub_145EF6C`) | |
| CRT `SetUnhandledExceptionFilter` → `TerminateProcess` fast-fail | `sub_19AB8EB`, `sub_19AB8D6` | none | the silent-exit amplifier (R2 T4) |
| SHA-256 helper | `sub_A0F280`/`sub_A0F3A0` | none | purpose still unknown |
| Page-RWX helper | `sub_13EE875` | none | benign |
| Mutation dispatch / cross-segment edges | ~32.6k `lea esp,[esp+4]; jmp [esp-4]`; ~16k E8/E9 into `.text#2` | only the 9 macro-entry skips (FIX2) and the SB patch (runtime, v3/v7 `Debugging=1`) | the engine stays reachable everywhere |

---

## 7. Discrepancies

With `patches/README.md`:

1. **DUMP_FIX's parent.** The README gives 9c95 (Mutex) and says f1c9 has "all previous patches
   (mutex removed etc)". The `.r2` does replay from 9c95, but it reverts all 35 Mutex bytes. f1c9 =
   FIX_3 (e50d) + 2 bytes and has **no** instance-limit removal.
2. **The 4GB patch is only a checksum.** LAA (`0x20` in Characteristics `0x123`) is already set in
   the plain dump. The `wx 21d311 @ 0x1b8` the README and the r2 comments call "4GB RAM patch" rewrites
   `OptionalHeader.CheckSum`; the 3-in-1/5-in-1/PerfPatch r2 files repeat it with the same label.
3. **Vanilla 03040008.** The README hash 01dc41a9 is not in `D:\research\DDON-binaries\PC`. It is
   `D:\DDON_03040008\DDO.exe.bak`. `PC\DDO_v3.05.exe` (c93f7e4d, ts 2017-10-13) is not in the
   README, and it is not the dump's source. R2's table calls it "vanilla S3": it is an older build.
4. **Win7 dump parent.** The README leaves it blank. It is FIX2 (ef9d) plus an IAT rebuild, minus
   FIX2's 9 compensation sites, plus 5 compare stubs and an empty "sDDOMain". It is not built on FIX_3
   or FIX, so "DDO_DUMP_FIX_Patch3_Win7_Mutex_ChatEdit" (f2a8) contains no FIX_3.
5. **Missing rows**: Bunie PerfPatch v7 (DDO.exe 03062388…, dinput8 8b60d642…, derived from
   PerfPatch v1, 8 runs / 98 B; no `.r2`), and `DDO_Bunie_100FPSPatch.exe` (= 3-in-1, b9b9). PerfPatch
   v1/v2/v3 share one exe hash: the README is right on that, but their DLLs differ (§4) and the README
   does not record them.
6. **MUTEX_E/F notes.** "Modding the mutex code will trigger a CRC error" fits the CRC compare at
   `0x3A87F64` that guards the `cmovz` the Mutex layer forces. The renamed string is the MtDTI class
   name `sDDOMain`, not a literal mutex name (the only CreateMutexA names the savedata mutex)
   **[inference]**.
7. **Encoding.** 10 of the 12 `.r2` files are UTF-16LE with a BOM. Only `rootofallthings_chat_edit.r2`
   and `bunie_5_in_1.r2` are UTF-8. radare2 copes, but `rg`/`sd` over them see NULs. Every `.r2`
   replays to its stated target hash ([fact], 12/12).

With ddon-hook 011 and R2:

- 011's "155 `.text` diff sites" and "135 equal in DUMP_FIX and Bunie" do not reproduce as stated.
  My counts: v7 vs f1c9 = 175 bytes / 25 runs, v7 vs 5-in-1 = 155 bytes, f1c9 vs f2a8 = 9,346 bytes.
  The substance holds: f2a8 lacks FIX_3's 122 `mov →xor eax,eax` sites, 120 of them at `0x22CE8E9+`
  (113 in `.text#2`, 7 in the `.reloc` code).
- R2 places the IAT (`0x2233xxx`) and some protector code in `.text`/IAT terms. In the dump's
  section table that range is `.reloc` (`0x2231000`–`0x240EFFF`). 52 of FIX2's and FIX_3's stubs sit
  there (44 compares and 1 `int 1` from FIX2, 7 reads from FIX_3).

---

## 8. Checks not run / caveats

- Purposes are inferred from instruction shape unless marked otherwise. No site's runtime behaviour
  was observed (nothing executed).
- I did not scan for further live CRC compares or reads beyond the five Win7 sites; the
  undisassembled engine islands make a byte-pattern count unreliable (pattern `8B ?? ?? 2B/3B ?? 86/8E`
  is a cheap next scan).
- The single-instance check and the target of the Mutex cave at `0x15BFFEF` were not resolved
  (undefined bytes in the IDB).
- The purposes of `0xC11B40`/`0xCD3E29` (FIX_3), `0x188FC0F` (FIX2), v7's `0x5C1D66` and
  `0x104A6DC/71C/73C`, and who reaches the v7 cave `0x3D159C5` stay unknown.
- PerfPatch v1/v2's own-hook claim rests on their strings and imports plus v3's decompiled source,
  not on a disassembly of v1/v2.

## 9. External references

No new external document or clone. MinHook (`D:/GitHub/TsudaKageyu/minhook`) is already in
`research/external-references.jsonl` (R1), so no row was added.

Scratchpad artefacts (session-local): `matrix.txt` (pairwise counts), `edges.json`/`edges.txt`
(per-edge runs, r2 replay results), `win7.txt`, `dlls.txt`, `radiff_*.r2`, and scripts in `py/`.
