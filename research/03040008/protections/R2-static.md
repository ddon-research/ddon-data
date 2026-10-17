# R2 Static inventory: protections in the PC executables

Research brief `specs/003-client-protections/briefs/R2-static.md` (incl. "Added after R1").
Static-only, read-only, 2026-10-17. No executable was run. The IDA work used a headless idalib
session on the DUMP_FIX database (`D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.i64`,
confirmed 32-bit, image base `0x400000`, input `...DDO_DUMP_FIX.exe`), queried read-only and closed
without saving. PE analysis used `pefile` on scratchpad scripts.

Facts carry an address and the source (IDB = the f1c9 DUMP_FIX database unless noted). Conclusions I
draw are marked **[inference]**. A check I did not run is called out as **not run**. Items reused
from earlier work carry their source; I did not redo them.

Addressing: the dump is based at `0x400000`, so VA = `0x400000` + RVA. "First `.text`" =
`0x401000`–`0x1ad5000` (the recovered game/OEP image, OEP `0xb89168`); "second `.text`" =
`0x240f000`–`0x45a4000` (the captured Themida SecureEngine runtime); `.SCY` = `0x45a4000`–`0x45a7000`
(Scylla rebuilt-IAT store).

---

## 1. Per-executable table

20 distinct SHA-256 among the PC `.exe` files. All 68,231,680-byte files are the **same Scylla dump
of the unpacked client** (timestamp 2019-01-25 01:22:59Z, OEP `0xb89168`, 7 sections incl. `.SCY`,
all section flags RWX, `.text`/`.rdata`/`.data` entropy fallen to 4.7–6.5 = decrypted); they differ
only by small hand-patches. The three `DDO_v*` files are the **Themida-packed originals** (two
`.text`, entry point in the second `.text` loader stub, every section entropy 7.4–8.0 = packed). The
Benchmark installer and `VerifyData.exe` are unrelated tools.

| Exe (representative) | SHA-256[:12] | Size | Timestamp | Kind | EP sec | Sections (flags, entropy) | DllChar | LAA | TLS | Imp | Notable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DDO_v1.1.0.exe | ef6ca484d217 | 34.4 MB | 2015-09-28 | Themida packed | .text#2 | .text(RX,7.96) .rdata(R,8.0) .data(RW,7.99) .rsrc(R,7.94) .idata(RW,5.58) .text(RX,7.88) | DEP,TSAware | yes | none | 337 | IsDebuggerPresent; no VEH imports |
| DDO_v2.3.0.exe | b36a542d314e | 64.5 MB | 2017-03-07 | Themida packed | .text#2 | .text(RX,7.95) .rdata(R,7.78) .data(RW,7.82) .rsrc(R,7.94) .reloc(R,7.39) .text(RX,7.62) | DEP,TSAware | yes | none | 368 | +VEH, Get/SetThreadContext, Toolhelp |
| DDO_v3.05.exe (vanilla S3) | c93f7e4d6dad | 66.8 MB | 2017-10-13 | Themida packed | .text#2 | .text(RX,7.95) .rdata(R,7.76) .data(RW,7.58) .rsrc(R,7.94) .reloc(R,7.41) .text(RX,7.58) | DEP,TSAware | yes | none | 365 | Themida IAT (real imports wrapped) |
| 2020_04_26_DDO_DUMP.exe | 0a7c5c637aee | 68.2 MB | 2019-01-25 | Scylla dump | .text#1 | .text(RWX,6.48) .rdata(RWX,6.24) .data(RWX,4.74) .rsrc(RWX,7.93) .reloc(RWX,5.06) .text(RWX,5.59) .SCY(RWX,5.65) | DEP,TSAware | yes | none | 365 | earliest dump |
| 2021_05_01_DDO_DUMP_FIX2.exe | ef9d18154004 | 68.2 MB | " | Scylla dump | .text#1 | (identical layout) | " | yes | none | 365 | |
| 2022_01_03_DDO_DUMP_FIX_3.exe | e50dd5177212 | 68.2 MB | " | Scylla dump | .text#1 | (identical) | " | yes | none | 365 | |
| 2022_01_21_DDO_DUMP_Mutex.exe | 9c9542a78fd5 | 68.2 MB | " | Scylla dump | .text#1 | (identical) | " | yes | none | 365 | mutex rename |
| 2022_01_21_..._MUTEX_E.exe | 526bd9d23cf8 | 68.2 MB | " | Scylla dump | .text#1 | (identical) | " | yes | none | 365 | |
| 2022_01_21_..._MUTEX_F.exe | c3db6f1952a8 | 68.2 MB | " | Scylla dump | .text#1 | (identical) | " | yes | none | 365 | |
| **2022_01_29_DDO_DUMP_FIX.exe (target, f1c9)** | f1c974d0e529 | 68.2 MB | " | Scylla dump, "CRC disabled" | .text#1 | (identical) | DEP,TSAware | yes | none | 365 | nothilvien final; base of all Bunie builds |
| DDO_DUMP_FIX_Patch3_..._ChatEdit.exe (**installed `DDO.exe`, f2a8**) | f2a802295407 | 68.2 MB | " | Scylla dump + patches | .text#1 | (identical; .SCY e=5.6) | DEP,TSAware | yes | none | 365 | on filmmachine Win7 dump, not on f1c9 (patches/README) |
| DDO_Windows7Dumped_Mutex.exe | 1c8cc43a50cd | 68.2 MB | " | Scylla dump (Win7) | .text#1 | (identical; .SCY e=5.6) | " | yes | none | 365 | filmmachine base of f2a8 |
| 2025_05_29DDO_ChatEdit.exe | 31a30332010e | 68.2 MB | " | Scylla dump + patch | .text#1 | (identical) | " | yes | none | 365 | |
| DDO_ChatEdit_4GB_RAM.exe | bf5107ef7ddf | 68.2 MB | " | Scylla dump + patch | .text#1 | (identical) | " | yes | none | 365 | LAA already set in all dumps |
| DDO_Bunie_100FPSPatch.exe (= 3-in-1) | b9b9cf865012 | 68.2 MB | " | Scylla dump + Bunie | .text#1 | (identical) | " | yes | none | 365 | |
| DDO_Bunie_5-in-1.exe | 268536f0e898 | 68.2 MB | " | Scylla dump + Bunie | .text#1 | (identical) | " | yes | none | 365 | |
| Bunie_PerfPatch_v7/DDO.exe | 030623885f5a | 68.2 MB | " | Scylla dump + Bunie v7 | .text#1 | (identical) | " | yes | none | 365 | MinHook + 20 static patches (011) |
| Buns_DDOPerfPatch_v1/2/3 | ac836bcdfb67 | 68.2 MB | " | Scylla dump + Buns | .text#1 | (identical) | " | yes | none | 365 | three files identical |
| Benchmark/DDON_Benchmark_4Gamer_Installer.exe | 63b2e8fa40c1 | 1.33 GB | 2010-10-05 | Installer (not game) | .text | .text(RX,6.59) .rdata(R,4.94) .data(RW,4.58) .rsrc(R,7.14) | TSAware | no | none | 332 | has LoadConfig; WriteProcessMemory, SetTimer |
| Translation.Pack/VerifyData.exe | 52ab7e70745d | 8.88 MB | 2019-04-05 | Tool (not game) | .text | .text(RX,5.18) .rsrc(R,4.28) .reloc(R,0.1) | ASLR,DEP,NO_SEH,TSAware | no | none | 1 | modern stub, 1 import |

Per-exe PE traits worth calling out (all game files unless noted):

- **DllCharacteristics**: every game exe has only `NX_COMPAT(DEP)` + `TERMINAL_SERVER_AWARE`. **No
  ASLR (`DYNAMIC_BASE`), no CFG (`GUARD_CF`), no `FORCE_INTEGRITY`** on any game build. Only
  `VerifyData.exe` (a separate tool) sets ASLR/DEP/`NO_SEH`.
- **SafeSEH**: none of the game exes have a load-config directory (`has_loadconfig=False`), so there
  is **no SafeSEH handler table** — hand-rolled SEH is not rejected. (Only the Benchmark installer
  and modern tools carry a load config.)
- **LARGEADDRESSAWARE**: set in every game exe, including the plain dumps — the `_4GB_RAM` variant's
  edit is therefore elsewhere, not the LAA flag (f1c9 and bf51 both already LAA). This confirms
  009's "both exes large-address-aware" and rules out address-space exhaustion for the crash.
- **TLS callbacks**: **none** in any game exe (no TLS directory in the dumps). The classic Themida
  TLS-callback anti-debug entry does not survive in the dump, consistent with R1 §2's inference that
  TLS is not the hook-crash vector.
- **Entry point**: packed `DDO_v*` have EP in the *second* `.text` (the Themida loader stub, e.g.
  v3.05 EP `0x1490a01`); every dump has EP at the recovered **OEP `0xb89168`** in the first `.text`.
- **Section flags**: packed originals have correct R/RX/RW flags; **every dump marks all sections
  RWX** (the dumper over-permissioned), so DEP gives the whole image execute rights — any page is a
  legal jump/trampoline target in the dumps.

---

## 2. Protector identity and what survives the dump

- **Packer = Oreans Themida/WinLicense** (R1 §1; corroborated here): the `DDO_v*` originals show the
  Themida signature — two `.text` sections, EP in the second (loader) `.text`, and uniform
  entropy 7.4–8.0 across all sections (encrypted/compressed body). **[fact: PE entropy, f1c9 sibling
  files]**
- **The dump preserves two things that matter.** (1) A **second `.text` at `0x240f000`–`0x45a4000`
  (~34 MB)** that is the captured **SecureEngine runtime image** (Themida's VM + anti-debug + the
  protector-mutated copies of stolen game code). (2) **`.SCY` at `0x45a4000`** (3 pages), the
  Scylla rebuilt-IAT store. **[fact: IDB segments]**
- **`.SCY` is data, not code flow**: 0 relative calls/jmps from the first `.text` land in `.SCY`
  (scan of E8/E9 targets, f1c9 IDB). It holds IAT thunks only. **[fact]**
- **The engine image is reachable from game code.** A scan of relative `E8`/`E9` edges in the first
  `.text` whose targets fall inside the second `.text` finds **~1,493 calls and ~14,765 jumps**
  (validated samples decode as real `jmp loc_3D142F7`, `jmp loc_3D9B9B4`, …). So normal game control
  flow tail-jumps into the SecureEngine blob throughout the run; the protector runtime is intertwined
  with execution, **not orphaned**, in the dump. **[fact: byte/edge scan + spot disassembly, f1c9
  IDB]** This is the structural basis for a live integrity/VM job (R1 H1/H2). **[inference]**
- **Real anti-debug instructions live in the second `.text`.** Of 24 raw `64 A1 30 00 00 00`
  matches, **23 decode as real `mov eax, large fs:30h`** (PEB access) — all at `0x240f000+`
  (e.g. `0x246a13b`, `0x24a1000`, `0x24bf352`, `0x24c9d83`, `0x24ceb5c`). The first `.text` has **no
  real `fs:[30h]`, rdtsc, `int 2d`, `ud2` or `cpuid`** at the byte matches tested — every first-`.text`
  match was incidental (bytes inside other instructions/data; `is_code`=False). **[fact: validated
  disassembly, f1c9 IDB]** Caveat: most of the second `.text` is **not disassembled** in the IDB
  (undefined bytes), so rdtsc/int2d/cpuid counts there are **not run** reliably — only the analyzed
  islands (where the 23 PEB reads sit) are countable.

---

## 3. Debugger checks

| Check | Where | Evidence | State |
| --- | --- | --- | --- |
| `IsDebuggerPresent` | IAT `0x2233318`; 4 callers: `sub_BEEA00` (`0xbeea24`), `sub_19A7F4B` (`0x19a7f4e`), `sub_19AE207` (`0x19ae2f1`), `sub_19C1338` (`0x19c1429`) | import xrefs, f1c9 IDB | live, but 3 of 4 are in the `0x19Axxxx` statically-linked MSVC CRT cluster (CRT error/`_CrtDbgReport` path). `sub_BEEA00` is a game function whose area Bunie also patches (free-disk check at `0xBEEA2D`, 011). **[inference: CRT, low value as a hook trap]** |
| `CheckRemoteDebuggerPresent` | — | not in IAT | **absent** (would be resolved dynamically by the live Themida engine, stripped from the dump's IAT) |
| `NtQueryInformationProcess` / `NtSetInformationThread` / `NtQuerySystemInformation` / `NtClose` | — | not in IAT | **absent from IAT** of the dump. Bunie v7's runtime adds its own `NtQueryInformationProcess`/`NtSetContextThread` "Themida compatibility" hooks + a PEB.BeingDebugged-clearing watchdog (011 tasks) — i.e. the live protector *does* call these; they are reached through the engine, not the game IAT. **[reused: ddon-hook 011]** |
| `OutputDebugString` A/W | IAT `0x22332cc`/`0x2233344`; callers `sub_10F7990`, `sub_19C1338`, a `.SCY` thunk `0x45a46a4` | import xrefs | live; ordinary logging + CRT |
| `GetThreadContext` (27) / `SetThreadContext` (18) | IAT `0x2233308`/`0x2233548`; callers cluster in `sub_145Cxxx`/`sub_145Dxxx` | import xrefs | live — this is the **game's own crash reporter / exception dumper** (§6), which walks thread contexts, not a debug-register anti-debug probe. **[inference]** |
| PEB `fs:[30h]` reads | 23 real `mov eax, large fs:30h` at `0x240f000+` (e.g. `0x246a13b`) | validated disassembly | present in the **SecureEngine image** (second `.text`); **none decoded in game first `.text`** |
| rdtsc / `int 2d` / `int3` scan / `ud2` / icebp / debug registers | no real instances in first `.text`; one real rdtsc **timing busy-wait at `0x180DB03`** (first `.text`), which Bunie v7 patches out ("rdtsc busy-wait ended", 011) | byte scan validated by `is_code`; 011 | the only confirmed live rdtsc in game code is a **timing wait**, not a debugger trap (§4). Engine-side timing checks: **not run** (second `.text` undisassembled). |

**Summary**: in the *game* (first `.text`) the only debugger-facing imports are CRT's
`IsDebuggerPresent` and the game's own context-walking crash reporter. The genuine Themida anti-debug
(PEB reads, and the Nt* probes Bunie neutralises) lives in the second `.text` engine image and is
reached through the ~16 k cross-segment edges. **[inference]**

---

## 4. Timing checks

| Mechanism | Where | State |
| --- | --- | --- |
| rdtsc busy-wait | `0x180DB03` (first `.text`) | **live**; a timing spin, ended by Bunie v7's patch (011). Not a debugger check. |
| `QueryPerformanceCounter` | IAT `0x223349c`; callers `sub_143F000`/`_120`/`_230` (timer subsystem) + `sub_19B924B` (CRT) | live; ordinary high-res timing |
| `GetTickCount` | IAT `0x22334cc`; `sub_124F160` | live; ordinary |
| `timeGetTime` | IAT `0x2233738`; **~21 real callers** across the engine/timer code | live; heavily used game timing |
| `CreateTimerQueueTimer` / `timeSetEvent` / `SetTimer` | — | **absent from IAT** — no API-timer drives a periodic check in the game image; a periodic job would run on a worker thread or inside the engine. **[inference]** |

No evidence of a rdtsc/QPC *delta* anti-debug in the game image; the timing APIs are the game's frame
and network clocks. **[inference]**

---

## 5. Integrity / anti-tamper / CRC

- **The "CRC routines DUMP_FIX neutralises" are in the second `.text` (`0x240F000+`).** ddon-hook's
  byte compare of the installed exe (f2a8), the fixed dump (f1c9) and Bunie v7 over Bunie's **155
  `.text` diff sites** found **135 sites equal in f1c9 and Bunie but different in the installed
  f2a8**, of which **~120 are `mov eax,[edx]` → `xor eax,eax` in the protector-mutated section
  `0x240F000+`** — i.e. the CRC *reads* were stubbed to read zero. **[reused: ddon-hook
  `specs/011-client-automation/tasks.md` ll. 228–236]** This is exactly the second `.text` my IDA
  pass identifies as the SecureEngine image, and it is the "disable CRC checks" edit that names
  nothilvien's f1c9. **State: neutralised in f1c9 (and Bunie); live in the installed f2a8.**
- **Consequence for the lineage**: installed `DDO.exe` f2a8 = "Patch3 … ChatEdit" built on
  filmmachine's Win7 dump `1c8cc43a`, **not** on f1c9 — so it still runs those ~120 code-integrity
  reads (patches/README; 011). This matches the T026 matrix where f2a8 dies faster/more reliably than
  f1c9 (§7). **[reused + corroborated]**
- **A residual check survives even in f1c9.** f1c9 still AV-crashes ~20 s after an `nrand` inline
  hook (T026) despite the ~120 neutralised reads, so the neutralisation is **incomplete**: a further
  integrity/VM job in the un-stubbed engine still reacts to the live `.text` patch. **[inference,
  aligns with R1 H1]**
- **SHA-256 helper `sub_A0F280`** (`CryptAcquireContextA(PROV_RSA_AES, CRYPT_VERIFYCONTEXT)` +
  `CryptCreateHash(CALG_SHA_256=0x800C)`; `CryptHashData` in `sub_A0F3A0`). **State: live, purpose
  unconfirmed** — this is a generic SHA-256 helper (could be save/data verification like
  `VerifyData.exe`, not code integrity). I did **not** trace what buffer it hashes (**not run**). It
  is *not* on the `nrand` path.
- **No routine hashes the `nrand` bytes directly**: there are **0 data xrefs** to `nrand`'s entry
  (`0x13B5E10`) or `init`'s entry (`0x13B5D70`), and the 6,459 data refs into page `0x13B5000` are
  vtable/pointer-table entries from `.rdata`/`.data` to *other* functions, not reads of the code
  bytes. **[fact, f1c9 IDB]** This confirms 009's "the `nrand` page is free of [protector checks]".
  **Caveat**: a *bulk* CRC that loops over a whole `.text` range references only its start pointer,
  so the absence of per-byte xrefs does **not** exclude a section-wide CRC — that possibility stays
  **unknown** from static xrefs alone.

---

## 6. Exception handling and crash-dump suppression

- **The game ships its own crash reporter** in the `sub_145Cxxx`/`sub_145Dxxx` cluster: it installs
  `AddVectoredExceptionHandler` (IAT `0x2233314`; e.g. `sub_145D41F`, `sub_145D4DF`, `sub_145D59F`)
  and walks thread state via `GetThreadContext`/`SetThreadContext` (27/18 callers in the same
  cluster). `RemoveVectoredExceptionHandler` (IAT `0x2233310`) is paired from the same subsystem.
  **State: live.** This is a VEH-based in-process fault handler. **[fact: import xrefs, f1c9 IDB]**
- **Top-level filter is the CRT's.** `SetUnhandledExceptionFilter` (IAT `0x22333f8`) is called only
  from the `0x19ABxxxx` MSVC CRT path (`sub_19AB8EB`, wrapper `SetUnhandledExceptionFilter_w`), which
  also calls `UnhandledExceptionFilter` (`0x19ab8f9`) and, next door, `TerminateProcess`
  (`sub_19AB8D6`, IAT `0x2233440`) — the classic `__crt` / `_invoke_watson` fast-fail. `ExitProcess`
  (IAT `0x2233488`) from `sub_1848950`, `sub_19A943C`. **[fact: import xrefs]**
- **WER suppression [inference, R1 H5]**: a process that installs its **own** VEH crash reporter and
  a CRT unhandled filter that ends in `TerminateProcess`/`_invoke_watson` will, on a fatal fault,
  either handle-and-exit or fast-fail **before** WER runs — matching T026's "silent exit, no dump, no
  WER". The game crash reporter plus the CRT watson path are both present and live; which one wins a
  given exit is runtime-dependent and **not determinable statically**. The E4 run that *did* produce
  `DDO.exe.44936.dmp` shows a dump is possible when the fault reaches a handler that writes one.
- **SafeSEH**: absent (no load config, §1), so a hand-rolled SEH frame is not rejected — relevant to
  any handler the engine installs. **[fact]**

---

## 7. Memory-protection changes, threads, watchdog

- **Make-executable helper `sub_13EE875`** = the *only* `VirtualProtect` user (IAT `0x2233554`):
  `VirtualQuery` → set `PAGE_EXECUTE_READWRITE (0x40)` unless already `PAGE_GUARD (0x80)`. It is a
  page-RWX helper for the dump's dynamic code, **not** an integrity or PAGE_GUARD trap. `VirtualQuery`
  (IAT `0x2233354`) also used by `sub_19BE570`. **State: live, benign.** **[fact: decompile, f1c9]**
- **`VirtualAlloc`** (IAT `0x223351c`): allocators `sub_13B6120`, `sub_13C2930`, `sub_13C37E0`,
  `sub_13C39B0`, `sub_13C3B80` — the game heap/pool next to MtRandom. No `PAGE_NOACCESS`/`PAGE_GUARD`
  tripwire found on the `nrand` path. **[fact]**
- **Thread creation**: `CreateThread` (IAT `0x22332dc`, ~21 sites) / `ResumeThread` (~19). Sampled
  `lpStartAddress` values all resolve **inside the first `.text`** (`0x10fb3f0`, `0x143e650`,
  `0x145e960`, `0x14a2d90`, `0x14e9e80`) — ordinary game worker bodies. `_beginthreadex` is not
  imported (static CRT inlines it). **No game-visible CreateThread targets the second `.text`**, so a
  protector watchdog thread, if any, is spawned by the engine via its own wrapped `CreateThread`
  (not visible as a clean `push imm32` in the game image). **[fact + inference]**
- **`CreateToolhelp32Snapshot`** (IAT `0x22334e0`): 1 caller at `0x13b4fa0`, an *undefined* stub on
  page `0x13b4000` (adjacent to the MtRandom page). Not resolved to a function; likely CRT/thread
  enumeration. **State: unknown, low value.** **[fact: xref; not further traced — not run]**

---

## 8. `nrand` specifics

- **Address / shape**: `MtRandom::nrand` = `sub_13B5E10`, VA `0x13B5E10` (RVA `0xFB5E10`),
  `__thiscall`, returns `u32`; function body `0x13B5E10`–`0x13B5E3E` (46 bytes). First 16 bytes:
  `56 8B F1 8B 16 8B 46 04 8B 4E 0C C1 E2 0F 33 16`. **[fact: f1c9 IDB; "bytes identical in the fixed
  dump and installed DDO.exe" per ddon-hook 17-rng-monitor.md]**
- **Prologue instruction boundaries**:
  `0x13B5E10 push esi` (1) · `0x13B5E11 mov esi,ecx` (2) · `0x13B5E13 mov edx,[esi]` (2) ·
  `0x13B5E15 mov eax,[esi+4]` (3) · `0x13B5E18 mov ecx,[esi+0Ch]` (3) …
- **What a 5-byte `E9` hook overwrites**: bytes `0x13B5E10`–`0x13B5E14` = `56 8B F1 8B 16` = exactly
  the **three whole instructions** `push esi; mov esi,ecx; mov edx,[esi]`. The patch boundary lands
  **cleanly** on `0x13B5E15`; **no instruction is split**, and **none of the relocated instructions
  is a branch or has a jump target inside the patched range** (it is pushes/moves on `esi`/`ecx`).
  So the inline patch and trampoline are instruction-aligned and branch-free — the hook mechanics are
  sound; the crash is not a mis-sized or boundary-crossing patch. **[fact: disassembly, f1c9 IDB;
  supports ruling out R1 H5]**
- **Callers / threads**: 328 direct `call` xref sites in the IDB (type `fl_CN`); ddon-hook counts
  ~420 call sites incl. inlined copies, on several threads, no lock (17-rng-monitor.md). Key
  generators that burst 48×`alphabet[nrand()&63]`: `sub_88ADD0` (returns to RVA `0x48AE7A`),
  `sub_849C00` (RVA `0x449CBA`). `MtRandom::init` = `sub_13B5D70` (`ret 4`), first bytes
  `8B 44 24 04 53 55 56 …`. **[reused + corroborated]**
- **Same page as `init`**: both `nrand` (`0x13B5E10`) and `init` (`0x13B5D70`) sit on page
  **`0x13B5000`** — so SafetyHook's thread-trap (which drops the page's protection during install)
  and both detours touch one page; 009 T023 orders the two installs around this. **[fact]**
- **Who reads its bytes**: no data xref reads the `nrand`/`init` bytes (§5); no routine statically
  demonstrated to hash the page. A section-wide CRC is not excluded (§5 caveat). **[fact + unknown]**
- **The E4 fault site**: `sub_18C6490` (`0x18C6490`–`0x18C8719`, first `.text`) — the AV in E4's
  `DDO.exe.44936.dmp`. Decompiled, it is a large **SIMD/float gameplay-math routine** (hundreds of
  `__m128`/`float` temporaries), an ordinary RNG *consumer*, **not** a protector check. A fatal AV
  surfacing in unrelated float code is the signature of a **delayed, decoupled corruption** (a bad
  pointer/state written elsewhere), not a check with a visible trap. **[fact: decompile, f1c9 IDB;
  supports R1 H1 over a point-of-use trap]**

---

## 9. T026 candidates (ranked by static evidence)

**T1 — Themida in-memory code-integrity / VM job in the second `.text` reacting to the live `nrand`
patch with a delayed corruption (R1 H1).** Strongest. Evidence: (a) ~120 CRC *reads* in `0x240F000+`
are stubbed in f1c9/Bunie but **live in the installed f2a8** (§5), explaining why f2a8 dies faster and
more reliably; (b) f1c9 still crashes ~20 s after the `nrand` patch despite those stubs, so a residual
job survives; (c) the engine image is reachable through ~16 k cross-segment edges (§2); (d) the fault
lands in an unrelated float consumer `sub_18C6490` (§8), the delayed-corruption signature; (e) no
check reads the `nrand` bytes directly, matching a decoupled check→reaction. **Next (dynamic, not this
brief)**: early-unhook survival test; TTD/VEH log of the corrupting write; diff the stubbed vs live
CRC sites between f1c9 and f2a8.

**T2 — Engine re-protect / re-encrypt of the region reached via the cross-segment jumps (R1 H2).**
Medium. The first `.text` tail-jumps into the SecureEngine blob ~14.8 k times; if the engine revisits
or re-encrypts a region near the trampoline the copied prologue goes stale. Static only shows the
edges exist, not their timing. **Next**: compare live `nrand` prologue vs the trampoline's saved bytes
after the crash.

**T3 — SafetyHook's persistent priority-1 trap VEH vs the game/engine exception flow (R1 H3).**
Medium-low. The game runs its own VEH crash reporter (§6) and the engine uses exceptions; SafetyHook
keeps a process-wide first-in-line VEH for the session (R1 §3). Static shows both exception systems
are live and co-resident. **Next**: reproduce with MinHook (SuspendThread, no persistent VEH) — Bunie
v7 uses MinHook and runs stably, a hint this matters. **[reused: 011 Bunie=MinHook]**

**T4 — WER/crash suppression masking the real fault (R1 H5).** Explains "silent exit, no dump" but is
a *symptom amplifier*, not the cause: the CRT watson path + game VEH reporter end the process before
WER (§6). **Next**: the exit tracer + forced minidump that 011 proposes.

**T5 — hook mechanics (prologue/relocation, R1 H5-mech).** Lowest. The `nrand` patch is
instruction-aligned, branch-free, 3 whole instructions (§8); `init` shares the page but 009 T023
already orders the installs; registers and address space were ruled out (009). Static evidence argues
**against** a pure hook-mechanics fault.

---

## 10. Checks not run / caveats

- Second `.text` (`0x240F000+`) is **largely undisassembled** in the IDB; rdtsc/`int2d`/`cpuid`/`ud2`
  counts there are **not run** (only the 23 real `fs:[30h]` PEB reads in analyzed islands are
  defensible).
- I did **not** independently re-locate each of the ~120 CRC-read sites in IDA or re-run the
  f1c9/f2a8/Bunie byte diff — reused from ddon-hook 011 and corroborated by the segment identity.
- `sub_A0F280` SHA-256 helper: the hashed buffer was **not traced** (purpose unconfirmed).
- `0x13b4fa0` (`CreateToolhelp32Snapshot`) was **not resolved to a function**.
- A section-wide `.text` CRC cannot be excluded by data-xref absence alone (§5).
- Nothing was executed; all crash timings/outcomes are reused from ddon-hook 009/011.

## 11. External references

No new external document or clone was introduced; this report relies only on the in-repo R1 survey,
the ddon-hook specs (009 `tasks.md`/`T009-live-run.md`/`17-rng-monitor.md`, 011 `tasks.md`), and the
f1c9 IDA database. `research/external-references.jsonl` needs no new row.
