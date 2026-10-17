# R1 Online: DDO PC client protections and how hookers cope

Research brief `specs/003-client-protections/briefs/R1-online.md`. Web + repository-clone research,
read-only, 2026-10-17. Every claim carries its source URL; conclusions I draw rather than cite are
marked **[inference]**. Clones used are listed in `research/external-references.jsonl`.

The target is DDO.exe build 03040008 (2019, 32-bit, Win7), protected with Oreans Themida/WinLicense
(vanilla `DDO_v3.05.exe`), plus unpacked/"dump fix" variants. The motivating symptom (009 T026): a
SafetyHook inline hook on `nrand` crashes both the installed exe (~50 s) and the DUMP_FIX dump
(~20 s) with 0xC0000005 and no crash report; unhooked runs survive; IDA ruled out the CRC checks,
register clobbering, and address space.

Clone paths and commits (shallow `--depth 1`, read-only, never built or run):

| Repo | Path | Commit |
| --- | --- | --- |
| cursey/safetyhook | `D:/GitHub/cursey/safetyhook` | `f44cc070a8340f2f26649553c49533475417304d` |
| TsudaKageyu/minhook | `D:/GitHub/TsudaKageyu/minhook` | `8af6b4acae5a9388fd742b56fa79ece89d96f823` |
| microsoft/Detours | `D:/GitHub/microsoft/Detours` | `1dbd4ea281d73d478aa8d09a8b83fbd265f715f7` |
| stevemk14ebr/PolyHook_2_0 | `D:/GitHub/stevemk14ebr/PolyHook_2_0` | `49a95d4566d47342b122303cf73585cf22653b0a` |
| x64dbg/ScyllaHide | `D:/GitHub/x64dbg/ScyllaHide` | `baa5c8e853ace2bee752631f27fdfe5b271d92f6` |
| mrexodia/TitanHide | `D:/GitHub/mrexodia/TitanHide` | `14aee055b1fc0afef3e710b7ed8c1912b6cb3347` |
| Air14/HyperHide | `D:/GitHub/Air14/HyperHide` | `cbbf364c8358ce479011139ef2ae1f72d5bceeec` |

---

## 1. Themida / WinLicense protections

Oreans ships Themida and WinLicense from the same SecureEngine core; the macro and option set below
applies to both. Build 03040008 predates the 2024-era 3.1.9 releases, so it is Themida 2.x or early
3.x **[inference]**, but the protection model has been stable across those versions.

### Protection options (packer-level, no SDK source required)

From the Themida "Protection Options" help page
(https://oreans.com/help/tm/hm_protection-options.htm) and the Themida product page
(https://www.oreans.com/Themida.php), all enabled by default:

- **Anti-Debugger Detection** — detects kernel and user-mode debuggers attached to the process.
- **Advanced API-Wrapping** — hides which APIs the app imports; wrapped APIs are reached through a
  Themida stub rather than the raw import, so a naive IAT hook never fires. Oreans notes a speed
  cost for APIs called very often.
- **Anti-File Patching** — detects on-disk modification of the protected file and shows
  `MSG_ID_FILE_CORRUPTED` (on-disk only, not in-memory).
- **Entry Point Obfuscation / Virtualization** — the first instructions run virtualized.
- **Detect File/Registry Monitors** and **Anti-Sandbox** — detect ProcMon/RegMon-style tools and
  sandbox virtualization.
- **Compress and Encrypt** — the body, resources, and boot loader are encrypted/compressed at rest
  and unpacked at runtime (typically via `VirtualProtect`/`VirtualAlloc`).
- **Perform Protection checks on VM macros** — extra pre-execution checks on each VM macro.
- **Allow execution under VMware/Virtual PC** — if disabled, blocks VM execution.
- The feature list explicitly advertises "anti-memory patching and CRC techniques in target
  application" (https://www.oreans.com/Themida.php), though these are not exposed as named checkboxes
  on the options page.

### Anti-debug techniques Themida is known to exercise

Themida 3.x writeups and the Checkpoint anti-debug encyclopedia document the standard battery that a
protector of this class uses (not all confirmed present in 03040008 — verify in IDA):

- PEB `BeingDebugged`, `NtGlobalFlag`, and heap flags (ScyllaHide calls heap flags "very important"
  because "Themida checks for heap artifacts and heap flags", `ScyllaHideDocumentation.tex` l.125).
- `NtQueryInformationProcess` classes `ProcessDebugPort`/`ProcessDebugFlags`/`ProcessDebugObjectHandle`
  (https://anti-debug.checkpoint.com/techniques/interactive.html).
- `NtSetInformationThread(ThreadHideFromDebugger=0x11)` to detach threads from the debugger
  (https://anti-debug.checkpoint.com/techniques/interactive.html).
- Hardware debug registers (DR0-DR7), `int 2d` / `int3` scanning, and RDTSC timing checks; the
  Themida 3.x guidance in the search corpus recommends hardware breakpoints precisely because
  software breakpoints modify code and trip Themida's integrity checks.
- Parent-process and `NtClose`/invalid-handle checks.

### Integrity / anti-tamper — the part that matters for T026

Oreans exposes two SDK macros that embody Themida's in-memory tamper response:

- **CHECK_CODE_INTEGRITY** (https://oreans.com/help/tm/hm_checkcodeintegrity-macro.htm): "checks if
  the code section of your protected application has been patched in runtime." SecureEngine sets a
  caller-supplied variable only when the `.text` section is unmodified. Oreans' own recommended usage
  is decisive for our crash: call it "from inside VM macros, at specific points or **from a thread
  that runs about every 30-60 seconds**", and react with a **"late crash"** — "set a flag when
  tampering is detected, then at a later point crash the app or initialize data incorrectly so it
  fails in a way that is hard to trace", deliberately *not* an immediate message or crash, so the
  attacker cannot locate the check.
- **CHECK_PROTECTION** (https://oreans.com/help/tm/hm_checkprotection-macro.htm): detects partial
  unpacking or an attacked protection engine; same set-variable-or-not pattern, same "late crash"
  advice, recommended ~5 calls across different routines, placed inside VM/CodeReplace macros.

These are developer-opt-in SDK macros, so their presence in DDO.exe is not guaranteed from packer
options alone. However, the behaviour they prescribe — a periodic integrity thread plus a delayed,
untraceable crash — exactly matches the T026 signature. **[inference]** Even if Capcom did not insert
the macros by hand, a protector that advertises "CRC techniques in target application" plus
"Perform Protection checks on VM macros" produces the same effect automatically.

### What survives in an unpacked / "dump fix" dump

- A dump captures the decrypted `.text` and a rebuilt IAT, but **virtualized (VM'd) functions remain
  bytecode** interpreted by the SecureEngine VM; if the VM context or a referenced Themida section is
  not in the dump, calls into it fault. The TERA case study below is the canonical demonstration.
- Checks that call back into stubs removed by the dumper become dangling calls.
- unlicense (https://github.com/ergrelet/unlicense) recovers OEP and the obfuscated IAT for
  Themida/WinLicense 2.x/3.x, 32/64-bit, but its README warns it "doesn't produce runnable dumps in
  most cases" — i.e. a dump that launches at all (like DUMP_FIX) has already had manual repair, and
  residual integrity/VM logic may still be live. That the DUMP_FIX dump still crashes on hook
  (faster, 20 s vs 50 s) says the integrity machinery survived dumping. **[inference]**

---

## 2. Windows specifics, Win7 vs Win10/11

- **Exception dispatch order** (relevant because both Themida and SafetyHook use VEH): debugger →
  vectored exception handlers (VEH) → frame-based SEH → `UnhandledExceptionFilter`
  (https://reviews.llvm.org/D29462). `RaiseFailFastException` bypasses all handlers
  (https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-setunhandledexceptionfilter).
- **SetUnhandledExceptionFilter as an anti-debug signal**: if a process is debugged, its unhandled
  filter is not called and the exception goes to the debugger, so reaching (or not reaching) the
  filter is itself a debugger check (https://anti-debug.checkpoint.com/techniques/exceptions.html). A
  game that installs its own unhandled filter and then triggers a controlled fault can both detect a
  debugger and suppress the OS crash dialog — consistent with "no crash report". **[inference]**
- **VEH ordering contention**: SafetyHook registers its trap VEH at priority 1 (first), see §3. A
  protector that relies on first-chance exceptions for its own flow can be perturbed by any
  first-in-line VEH. **[inference]**
- **32-bit / WOW64**: DDO.exe is x86 on WOW64. Thread contexts are WOW64 contexts; a hooker that
  reads/writes `Eip` via the WOW64 `CONTEXT` must use the 32-bit context (SafetyHook and MinHook do,
  being compiled x86 for an x86 target). DEP is on for the process; any trampoline page must be
  executable (all four libraries allocate RX/RWX). `/LARGEADDRESSAWARE` would extend the user address
  space past 2 GB on WOW64, affecting near-memory trampoline search ranges (§3).
- **CFG/ASLR/SafeSEH**: a 2019 build may lack CFG; ASLR is likely on. These affect where trampolines
  land but not integrity detection. SafeSEH would reject a hand-rolled SEH but not VEH.
- **TLS callbacks** run before the entry point and are a classic Themida anti-debug hook point; a
  `dinput8.dll` proxy loaded as an import dependency runs its `DllMain` before the exe's OEP, i.e.
  before Entry Point Obfuscation unpacks — hooking `nrand` that early would hit still-packed bytes,
  but ddon-hook installs later, so this is likely not the issue. **[inference]**

---

## 3. Hooking libraries

### SafetyHook — `D:/GitHub/cursey/safetyhook` @ `f44cc07`

- **What it does**: C++23 inline and mid-function hook library for Windows x86/x86_64, Zydis-based
  disassembly (https://github.com/cursey/safetyhook). This is ddon-hook's library.
- **Install mechanics** (read from the clone): `InlineHook::enable()` (`src/inline_hook.cpp` l.418)
  calls `trap_threads(m_target, m_trampoline, len, ...)` which writes the `E9` jump while other
  threads are trapped. On x86 it uses an `E9` relative jump; `FF` absolute is x64-only.
- **Trampoline allocation**: `Allocator::allocate_near` / `allocate_nearby_memory`
  (`src/allocator.cpp`) searches for free memory within `max_distance` of the target and
  `VirtualAlloc`s it RWX, so the `E9` displacement fits in ±2 GB; if no near block is found it returns
  `ip_relative_instruction_out_of_range`.
- **Thread handling is VEH-based, not SuspendThread**: `trap_threads` (`src/os.windows.cpp` l.271)
  does **not** enumerate/suspend threads. Instead it registers a process-wide
  `AddVectoredExceptionHandler(1, trap_handler)` (l.176), temporarily drops the target and trampoline
  pages to a non-executable protection (`PAGE_READWRITE`, or `PAGE_EXECUTE_READWRITE` when the region
  shares an allocation with the library or overlaps the first 0x20 bytes of `VirtualProtect`, l.284-298),
  edits the bytes, then restores protection. Any thread executing in the trapped page faults with
  `EXCEPTION_ACCESS_VIOLATION`; `trap_handler` (l.233) rewrites that thread's `Eip`/`Rip` from the old
  site to the trampoline (`fix_ip`, l.327) and continues. This is the "process-wide VEH when it traps
  threads during install" the brief mentions.
- **Caveat found in the clone — the trap VEH is never torn down mid-session**: `TrapManager::instance`
  is created on first hook and only destroyed via its destructor (which calls
  `RemoveVectoredExceptionHandler`), and nothing in the shown code resets `instance` before process
  exit. So after the first hook, SafetyHook leaves a **permanent priority-1 VEH** that inspects every
  first-chance access violation in the process; for a fault outside any trapped page it returns
  `EXCEPTION_CONTINUE_SEARCH` (l.248) so the fault still propagates, but it is first in line ahead of
  the game's own handlers. **[inference]** This is a genuine interaction surface with Themida's
  exception-based checks and worth logging.
- **Known issues (GitHub)**: #22 "Thread IP/register corruption due to late SuspendThread?"; #52
  "ResumeThread causes crash when unfreezing"; #48 "MidHook x86: ESP is offset by -8" (an x86-specific
  mid-hook stack bug — relevant if ddon-hook uses a mid-hook on `nrand`); #11 "Program crashes when
  unhooking"; #79/#70 launch/LoadLibrary crashes
  (https://github.com/cursey/safetyhook/issues). No issue names Themida directly.
- The library has no release tags on `main`; it is consumed at a pinned commit via CMake FetchContent.

### MinHook — `D:/GitHub/TsudaKageyu/minhook` @ `8af6b4a`

- Classic x86/x64 inline hook library. **Freezes threads the traditional way**: `Freeze`
  (`src/hook.c` l.327) enumerates threads with `CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD)`,
  `SuspendThread`s each, and calls `ProcessThreadIPs` → `FindOldIP`/`GetThreadContext`/
  `SetThreadContext` (l.163-257) to relocate any suspended thread's IP that sits inside the patched
  region.
- Trampoline search is bounded by `MAX_MEMORY_RANGE 0x40000000` around the target (`src/buffer.c`
  l.36), `VirtualAlloc`ing blocks within ±1 GB.
- **Themida interaction**: suspending every thread and walking the TID list is itself observable;
  Themida's thread-count / `NtSetInformationThread` checks can react. The TERA writeup (§6) shows a
  protected target where any `.text` edit (regardless of hook library) trips a delayed check.

### Microsoft Detours — `D:/GitHub/microsoft/Detours` @ `1dbd4ea` (version 0x4c0c1 ≈ 4.0.1)

- Transaction model (`DetourTransactionBegin`/`DetourUpdateThread`/`DetourAttach`/`Commit`). The
  caller must enlist each thread with `DetourUpdateThread`; threads not enlisted are **not** IP-fixed,
  so a thread mid-prologue at commit is a known crash source.
- Trampolines live in 64 KiB `DETOUR_REGION`s (`DETOUR_REGION_SIZE 0x10000`, `src/detours.cpp` l.1333)
  allocated near the target (via `VirtualAlloc2` when available) and flipped `PAGE_EXECUTE_READ` after
  commit with `FlushInstructionCache` (l.1356-1359).
- Detours flushes the instruction cache; SafetyHook and MinHook rely on the page-protection round-trip
  / the OS. On a protected target this matters little for the integrity check (which reads bytes, not
  I-cache).

### PolyHook2 — `D:/GitHub/stevemk14ebr/PolyHook_2_0` @ `49a95d4`

- Multiple hook strategies: `x86Detour`/`x64Detour` (inline), `VEHHook` (page-guard/`PAGE_NOACCESS`
  exception hooks), `HWBreakPointHook` (DR registers), `EatHook`, `VFuncSwap`. The VEH and HWBP
  variants **do not modify `.text`** and therefore sidestep code-integrity CRCs — a candidate
  mitigation if the T026 crash is an integrity check (§7).
- `x64Detour.cpp` l.345 shows it scrounges for nearby `0xCC` padding when space-constrained — a hint
  that tight prologues are handled by splitting the jump.

### Others worth naming

- **detours-style VMT/vftable hooks** and **IAT hooks** avoid code edits but, against Themida's
  Advanced API-Wrapping, the IAT no longer points at the real API, so IAT hooks on wrapped imports
  miss (https://oreans.com/help/tm/hm_protection-options.htm). `nrand` is an internal function, not a
  wrapped import, so an inline hook is the natural choice — which is also the one integrity checks
  catch.
- **Karl's `kiero`** / generic D3D9 present hooks are common in this community because DDON renders
  with Direct3D 9 (confirmed by a ReShade DDON crash log listing D3D9 exports,
  https://reshade.me/forum/troubleshooting/3496-dragons-dogma-online-ddon-continuously-crashing).

---

## 4. Anti-anti-debug tools

### ScyllaHide — `D:/GitHub/x64dbg/ScyllaHide` @ `baa5c8e`

- User-mode (ring 3) library that hooks ntdll to hide a debugger
  (https://github.com/x64dbg/ScyllaHide); x86/x64; plugins for x64dbg, OllyDbg, IDA, TitanEngine, plus
  a CLI injector. Explicitly tested against Themida/VMProtect/Armadillo/ExeCryptor.
- Its shipped **Themida profile** (`ConfigCollection/scylla_hide.ini`) enables PEB `BeingDebugged` /
  heap-flags / `NtGlobalFlag` / startup-info / OS-build spoofing and hooks on
  `NtClose`, `NtQueryInformationProcess`, `NtQuerySystemInformation`, `NtSetInformationThread`,
  `NtCreateThreadEx`, and the `NtUser*` window-enumeration calls; it leaves the timing and
  exception-dispatcher hooks off. Changelog notes: "Stealth hooks for 32-bit targets to defeat
  protectors like Themida" and a PEB-patch fix so "Themida works on WinXP"
  (`changelog.txt` l.81, l.87). Its docs call the heap-flags option "very important ... Themida checks
  for heap artifacts and heap flags" (`ScyllaHideDocumentation.tex` l.125, l.449).
- **Relevance**: ScyllaHide hides a *debugger*; ddon-hook injects without a debugger, so most of this
  is moot unless a debugger is attached for triage. It does nothing about code-integrity CRCs.

### TitanHide — `D:/GitHub/mrexodia/TitanHide` @ `14aee05`

- Kernel driver that hides debuggers system-wide by SSDT-style hooks; documentation sections cover
  PEB, `NtSetInformationThread`, hardware-breakpoint (DRx) protection, timing, and raise-exception.
  Needs driver signing / test-signing on Win7+; hides from a debugger but, again, not from integrity
  checks.

### HyperHide — `D:/GitHub/Air14/HyperHide` @ `cbbf364`

- Hypervisor-based (Intel VT-x) debugger hider with a per-protector INI that includes a `[Themida]`
  section (`HyperHide.ini` l.81). Stealthier than ScyllaHide against timing/DRx checks because it
  virtualizes rather than hooks ntdll. Same limitation re: integrity CRCs.

### Scylla (dumping)

- Scylla / unlicense (https://github.com/ergrelet/unlicense) rebuild the IAT and OEP for a dump;
  unlicense supports Themida 2.x/3.x 32/64-bit but "doesn't produce runnable dumps in most cases".
  The existing DUMP_FIX is such a repaired dump.

**Settings Themida needs**: enable the heap-flags, PEB, and `NtSetInformationThread`/
`NtQueryInformationProcess`/`NtQuerySystemInformation` spoofs; prefer hardware breakpoints over
software so `.text` is not modified and integrity checks are not tripped; leave timing hooks
conservative. None of these addresses a no-debugger inline-hook crash. **[inference]**

---

## 5. Crash triage on Windows for this target

- **WER LocalDumps** (https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps):
  create `HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\DDO.exe`, set `DumpType=2`
  (full), optional `DumpFolder`; dumps land in `%LOCALAPPDATA%\CrashDumps`. **Critical caveat**: WER
  does **not** collect a dump if a postmortem debugger is registered, and apps that do custom crash
  reporting are unsupported — which is likely *why the brief sees "no crash report"*: the game has
  installed its own `SetUnhandledExceptionFilter` and either swallows the fault or fast-fails it
  before WER runs. **[inference]** Confirm with a LocalDumps key and check whether a dump appears at
  all.
- **ProcDump** `-ma -e` captures a full dump on the first-chance (or `-e 1 -f` filtered) access
  violation, catching the fault before any in-process filter can suppress it — the right tool when WER
  is being bypassed. (General ProcDump usage; the search corpus confirms WER/ProcDump mechanics but
  not DDON specifics.)
- **cdb/WinDbg `!analyze -v`** on the dump, plus `.exr`/`.ecxr`, gives the faulting instruction and
  whether the IP is in `.text`, in a trampoline, or in a Themida VM section. For a 32-bit WOW64
  target use the 32-bit debugger.
- **Time Travel Debugging (TTD)** records the whole run; for a delayed integrity crash, TTD lets you
  walk *backward* from the 0xC0000005 to the write that corrupted the pointer and to the thread that
  scheduled it — the single most decisive tool for distinguishing hypotheses in §7, but heavy and
  itself detectable by Themida timing checks. **[inference]**
- **First-chance vs second-chance**: Themida throws and handles its own exceptions (e.g. the TERA
  trampolines use `pushfq`/controlled faults). Attach with "ignore first-chance AV, break on
  second-chance" so you only stop on the fatal one, not Themida's routine ones.
- **AddVectoredExceptionHandler logging**: install a logging VEH *ahead* of SafetyHook's (or hook
  `RtlAddVectoredExceptionHandler`) to record every exception, its address, and code; this reveals
  whether the fatal AV is preceded by Themida integrity-job activity and whether SafetyHook's own trap
  VEH is seeing it.
- **`SetUnhandledExceptionFilter` override**: hook/log `kernel32!SetUnhandledExceptionFilter` and
  `kernelbase` equivalents to learn whether the game replaced the top-level filter (and when), then
  re-install your own after it to capture the crash.

---

## 6. DDON community work

Direct public sourcing is thin — most DDON private-server tooling lives in Discord and private repos,
not indexed by US web search (searches for "Bunie", "techwomanwow", DDON perf patches returned only
the unrelated *Dungeons & Dragons Online* and *Dark Arisen* results). What is citable:

- **DDON uses Direct3D 9**: a ReShade forum DDON crash thread shows a log enumerating D3D9 export
  entries (https://reshade.me/forum/troubleshooting/3496-dragons-dogma-online-ddon-continuously-crashing;
  older: https://reshade.me/forum/troubleshooting/1004-dragons-dogma-online-crashes-1-0). This is why
  community injectors favour a D3D9 or `dinput8.dll` proxy entry point.
- **Local repository evidence**: the Arrowgene server fork clones under `D:/GitHub/Sehkah/` contain
  DTI/research material (`research/dti/dti_prop_dump.h`) but no hook/CRC discussion; the hook work
  itself lives in `C:\Users\morph\CLionProjects\ddon-hook` (not a GitHub survey target here).
- **Analogous protected-game precedent (TERA, also Themida)**: Alex RP, "Neutralizing Protection in
  the TERA Executable" (https://alexrp.substack.com/p/neutralizing-protection-in-the-tera-executable)
  is the closest public case study and strongly informs §7. Key facts: patching `.text` produced
  "seemingly random crashes after a while"; one crash was a **deterministic** fault in virtualized
  code because `S1CheckCodePatchJob` compared the live `.text` against the build-time snapshot; a
  second was a **non-deterministic, delayed** crash — "a memory access to a very low address", i.e. a
  null-ish pointer — produced by `S1SecurityCrashJob0..15` which **overwrite a context pointer** when
  `S1SecurityCheckJob` found token values wrong. The checks ran as scheduled "jobs" (one disguised as
  a UE3 I/O request). Neutralizing meant finding the virtualized trampolines (a `pushfq` byte scan)
  and removing the job scheduler, not fixing the hook.
- **Enigma Protector forum** confirms the general rule that hooking a protected module's code makes
  the protector detect the modification and hang/fail
  (https://forum.enigmaprotector.com/viewtopic.php?p=33245).

---

## 7. Ranked hypotheses for the T026 crash

Symptom recap: inline hook on `nrand` → 0xC0000005 seconds after install (installed ~50 s, DUMP_FIX
~20 s), no crash report, unhooked survives, IDA ruled out CRC-at-known-sites / register clobber /
address space.

**H1 (most likely) — Themida in-memory code-integrity job detects the patched `.text` at the hook
site and fires a deliberate delayed "late crash" (pointer/data corruption → null-ish deref).**
Fit: the 30-60 s cadence Oreans prescribes for the integrity thread
(https://oreans.com/help/tm/hm_checkcodeintegrity-macro.htm) matches the ~50 s installed delay; the
"late crash … initialize data incorrectly" design matches 0xC0000005 with no report and no obvious
check site (why IDA's CRC-site search came up empty — the reaction is decoupled from the check); the
TERA case shows exactly this (§6). DUMP_FIX crashing faster (~20 s) fits a surviving-but-faster check
loop or a shorter token interval in the dump. **[inference]**
*Confirm*: unhook `nrand` at, say, 10 s (installed) and keep running — if it survives past 50 s, the
crash is a delayed reaction to the live patch, not the hook's own code. *Refute*: if it still crashes
after early unhook, the trampoline/relocation (H2) is implicated.
*Also confirm*: TTD or a logging VEH shows a corrupting write to a pointer seconds before the fault,
from a thread other than the one calling `nrand`; snapshot `.text` at the hook site vs build-time.

**H2 — `nrand` is reached through, or sits adjacent to, Themida-virtualized / re-encrypted code, so
the copied trampoline bytes go stale or the `E9` lands in a region Themida re-protects.**
Fit: Themida's "Re-Encrypt after decryption" and VM macros mean some functions' bytes change after
first decryption; SafetyHook copies the original prologue once at install, so if those bytes are later
re-encrypted the trampoline executes garbage → AV. The delay is "time until that region is next
re-encrypted/visited". **[inference]**
*Confirm*: after the crash, compare the trampoline's saved original bytes against the current live
bytes at `m_target`; a mismatch at `nrand`'s prologue confirms it. Check in IDA whether `nrand`'s
caller chain passes through a `pushfq`/VM trampoline.

**H3 — SafetyHook's persistent priority-1 trap VEH collides with Themida's exception-based checks.**
Fit: SafetyHook leaves a process-wide VEH installed for the session (§3, `src/os.windows.cpp` l.176,
never reset); it inspects every first-chance AV. Themida uses controlled exceptions; being preempted
(or having an expected fault "continue-searched" past its handler) could derail a check into a crash.
This explains why *hooking at all* (not the specific target) could matter. **[inference]**
*Confirm*: with a logging VEH installed before SafetyHook, record exception addresses/codes; look for
a Themida AV that changes disposition once SafetyHook's VEH is present. *Refute*: if the crash
reproduces with a hook library that uses SuspendThread and no persistent VEH (MinHook), H3 is out.

**H4 — Hook-induced disturbance of a Themida security-token / timing check (not the code bytes
themselves), as in TERA's `S1SecurityCheckJob`.** The hook's extra work (a call out to the proxy each
`nrand`) perturbs timing or a counter the protector samples, scheduling a crash job.
*Confirm*: a no-op trampoline (hook that immediately calls the original and returns, zero added work)
that still crashes points away from timing; a heavy hook that crashes faster points toward it.

**H5 (least likely, partly ruled out) — relocation/near-trampoline fault specific to a short or
boundary-crossing `nrand` prologue on x86.** SafetyHook widens short branches and relocates
RIP-relative ops, but an x86 mid-hook ESP bug exists (issue #48) and a <5-byte prologue forces awkward
patching. IDA already ruled out plain address-space problems, lowering this.
*Confirm*: inspect `nrand`'s first 5+ bytes; check whether a mid-hook (vs inline) is used; reproduce
with MinHook/Detours — if only SafetyHook crashes, it is library-specific (H5/H3); if all crash, it is
protector-level (H1/H2/H4).

**Decisive single experiment**: run under ProcDump `-ma -e` (bypasses the game's filter) to get a full
dump, then `!analyze -v` the faulting IP. IP in a trampoline → H2/H5; IP in game `.text` on a
null-ish pointer written by another thread → H1/H4; a Themida VM section → H2. Pair with the "early
unhook survives?" test to separate live-patch reaction (H1) from hook-code faults (H2/H5).
