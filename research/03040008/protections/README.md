# PC client protections, patch layers and crash triage (03040008)

Synthesis of spec `specs/003-client-protections/` (2026-10-17). The three reports hold the
evidence; this page holds the conclusions, the corrections and the working protocol.

| Report | Contents |
| --- | --- |
| `R1-online.md` | Themida/WinLicense measures, Windows 7 → 11 behaviour, SafetyHook, MinHook, Detours, PolyHook2, ScyllaHide, TitanHide, HyperHide (clones and SHAs in `research/external-references.jsonl`), crash-triage tools, the TERA precedent |
| `R2-static.md` | PE traits of every executable in `D:\research\DDON-binaries\PC`; protections still present in the DUMP_FIX database (f1c9, IDA 9.5, read-only); `nrand` hook mechanics |
| `R3-patches.md` | The lineage by hash and diff, every patch layer site by site, Bunie's DLL hooks, protections no layer touches |

Facts carry addresses in the f1c9 database (image base 0x400000, no relocations). "[inference]"
marks conclusions.

## 1. What the client is

- **Vanilla 03040008** (01dc41a9, PE timestamp 2019-01-25) is Themida-packed. It is
  `D:\DDON_03040008\DDO.exe.bak`. `PC\DDO_v3.05.exe` (c93f7e4d) is an older 2017 build, not the dump's
  source (R3 §1; R2's table calls it vanilla, which is wrong).
- **Every `*DUMP*` executable is one Scylla dump** of the unpacked client (OEP `0xB89168`, 7
  sections with `.SCY`, all RWX), differing only by hand patches. The dump keeps Themida's
  **SecureEngine image** as a second `.text` at `0x200F000` (patched stubs from `0x240F000`), with
  the IAT and more protector code in `.reloc` (`0x2231000`–`0x240EFFF`). Game code reaches the
  engine through ~1.5k calls, ~14.8k jumps and ~32.6k mutation-dispatch stubs, so it is live, not
  orphaned (R2 §2, R3 §6).
- No game build has ASLR, CFG, SafeSEH or TLS callbacks. LARGEADDRESSAWARE is already set in the
  plain dump (R2 §1). Bunie PerfPatch v7's exe is **not** Themida-packed: it is PerfPatch v1 plus 98
  bytes, and its `dinput8.dll` is a plain MSVC build (R3 §2.10, §4).

### Lineage (R3 §1)

```
01dc41a9 vanilla (packed) -> 0a7c plain dump -> ef9d FIX2 -> e50d FIX_3 -> f1c9 DUMP_FIX (= FIX_3 + 2 B)
                                                  |                          |-> ChatEdit, ChatEdit_4GB
                                                  |                          |-> Bunie 3-in-1 (= 100FPS), 5-in-1
                                                  |                          `-> PerfPatch v1=v2=v3 exe (ac83) -> v7 (0306)
                                                  `-> 1c8c Win7 dump (filmmachine_, IAT rebuild) -> f2a8 installed DDO.exe
```

- **f1c9 has no Mutex patch**: its `.r2` replays from the Mutex build but writes all 35 Mutex bytes
  back. So f1c9 has no instance-limit removal (`patches/README.md` says otherwise).
- **The installed f2a8 descends from FIX2 only**: it has none of FIX_3's or FIX's bytes, despite
  "Patch3" in its name.

## 2. Protection inventory

| Mechanism | Where | State in f1c9 | In f2a8 | Source |
| --- | --- | --- | --- | --- |
| Checksum compares in the engine | 536 sites, `.text#2` and `.reloc` | forced by FIX2 | forced (FIX2) | R3 §2.1 |
| `int 1` debugger traps | 12 sites | removed by FIX2 | removed | R3 §2.1 |
| Checksum reads `mov eax,[edx]` → `xor eax,eax` | 122 sites, 120 from `0x22CE8E9` | stubbed by FIX_3 | **live** | R3 §2.2, §3 |
| Protector descriptor fields in game padding | `0x738B76`, `0xD5C79A` | zeroed by FIX | live | R3 §2.5 |
| **Three remaining checksum compares** | `0x24CD5DE`, `0x3A87F64` (guards the `cmovz` at `0x3A87F85` that the Mutex layer forces), `0x430DF3B` | **live** | stubbed (Win7 lineage) | R3 §6 |
| PEB `BeingDebugged` reads `fs:[30h]` | 23 sites in `.text#2` (list in R3 §6) | live | live | R2 §3 |
| Nt* debug probes (NtQueryInformationProcess, NtSetInformationThread, ...) | resolved dynamically by the engine; absent from the IAT | live | live | R2 §3 |
| Code-integrity / VM jobs (Themida `CHECK_CODE_INTEGRITY` style, 30–60 s period) | inside the engine; thread or timer not visible statically | presumed live [inference] | presumed live | R1 §1, §7; R2 §7 |
| rdtsc timing busy-wait | `0x180DB03` | live | live | R2 §4 |
| CRT `IsDebuggerPresent` | `sub_19A7F4B`, `sub_19AE207`, `sub_19C1338` | live, low value | live | R2 §3 |
| Game VEH crash reporter (AddVectoredExceptionHandler, Get/SetThreadContext) | `sub_145Cxxx`/`sub_145Dxxx` | live | live | R2 §6 |
| CRT `SetUnhandledExceptionFilter` → `TerminateProcess` fast-fail | `sub_19AB8EB`, `sub_19AB8D6` | live: ends the process before WER | live | R2 §6 |
| SHA-256 helper | `sub_A0F280`, `sub_A0F3A0` | live, purpose unknown | live | R3 §6 |
| Page-RWX helper (only VirtualProtect user) | `sub_13EE875` | live, benign | live | R2 §7 |

No PAGE_GUARD or NOACCESS tripwire was found on the `nrand` path, and no routine reads `nrand`'s
bytes as data (R2 §5, §7, §8). A section-wide hash is not excluded.

### What Bunie's DLLs add (R3 §4)

- PerfPatch v1–v3 hook with their own 5-byte jump; **only v7 uses MinHook**.
- Nt* "Themida compatibility" hooks that answer "no debugger" for the own process only:
  `NtQueryInformationProcess` (debug port → 0, debug object handle → `STATUS_PORT_NOT_SET`, debug
  flags → 1), and `NtSetContextThread` (own thread; zeroes the debug registers, but its mask also
  clears `CONTEXT_i386`, the bug ddon-hook 009 T014 found).
- A 100 ms watchdog that clears `PEB.BeingDebugged`. In v7 it runs only with `Debugging=1`, together
  with a 5-byte NOP at `0xF09655`.

## 3. The T026 crash: where the evidence points

Symptom (ddon-hook 009 T026): an inline hook on `MtRandom::nrand` (`sub_13B5E10`) alone crashes
f2a8 at ~50 s and f1c9 at ~20 s with 0xC0000005 and usually no dump. Unhooked runs survive.

1. **The hook is mechanically clean** (R2 §8). The 5-byte `E9` covers exactly `push esi; mov
   esi,ecx; mov edx,[esi]`, with no split instruction and no branch. Registers and address space
   were already ruled out.
2. **The leading cause is a delayed integrity reaction** [inference]. Themida documents a check
   that runs every 30–60 s and answers a mismatch by corrupting data later, so the program crashes
   far from the check. TERA's Themida build behaved exactly like this. E4's fault site `sub_18C6490`
   is ordinary SIMD gameplay maths, not a check. f2a8 has 122 more live checksum reads than f1c9. f1c9
   still has three live compares (§2), plus whatever the VM'd jobs do.
3. **The other candidates, in order:**
   - the engine re-protects or re-encrypts the hooked region;
   - SafetyHook's process-wide VEH stays installed for the whole run (MinHook has none, and Bunie's
     MinHook builds run stable);
   - the fast-fail path hides the fault, which explains the missing crash report.

## 4. What to do on top

Ordered by cost; each step has a stop rule.

1. **Base on f1c9, never f2a8** for hooked runs: f2a8 lacks FIX_3's 122 stubs.
2. **Discriminators** (one run each, more samples where needed; Sam says crashes "have always
   been random"):
   - Unhook after 10 s. If the client survives past 60 s, the crash is a reaction to the live patch
     (cause 2), not the hook's code.
   - Build the same hook with MinHook. If only SafetyHook crashes, it is the library.
   - A no-op hook that only calls the original. If that still crashes, the cause is the patch
     itself, not timing or added work.
3. **Patch the three remaining compares** (`0x24CD5DE`, `0x3A87F64`, `0x430DF3B`) as a new layer on
   f1c9. Copy the Win7 lineage's stub bytes from 1c8c. Record it as `patches/<date>_ddo_dump_fix_4.r2`
   with its SHA-256 chain (`patches/README.md`), and never overwrite the originals.
4. **Anti-debug answers in the proxy**, as Bunie and ScyllaHide do (R1 §4, R3 §4): fake
   `NtQueryInformationProcess` for the own process and clear `PEB.BeingDebugged`. Needed only when a
   debugger or TTD is attached. Do not copy Bunie's `NtSetContextThread` mask bug.
5. **Hooks that don't write `.text`**, if the patch itself is what trips the check:
   - hardware breakpoints in DR0–DR3 with a VEH (PolyHook2 has both kinds), which needs the
     `NtSetContextThread` fix above;
   - a PAGE_GUARD VEH hook;
   - hooking the callers' data (vtables, function pointers) where one exists. `nrand` is called
     directly from ~420 sites, so that does not apply to it.
6. **Only if 2–5 fail: find and disable the scheduler of the integrity jobs.** The TERA precedent
   did this: scan for the VM trampolines (`pushfq` sequences) and remove the job that writes the
   corrupting pointer (R1 §6). It needs TTD to find the write.

## 5. Crash-triage protocol

Every crash gets a root cause and, where it is a trap, a patch. ddon-hook runs this (the client
runs only there, against the local Arrowgene server).

1. **Capture before the game's handlers can hide it.**
   - `procdump -accepteula -ma -e 1 -f C0000005 -x <dumpdir> DDO.exe "<args>"` catches the first
     first-chance AV. Themida raises AVs on purpose, so log them all with `-e 1 -n 5` and keep the
     last.
   - Set WER LocalDumps (`DumpType=2`) as a fallback, knowing the CRT fast-fail bypasses it.
   - In the proxy, a logging VEH registered first, ahead of SafetyHook's, writes the code, address,
     thread, module and section of every exception to the run log.
2. **Classify the faulting IP** with cdb `!analyze -v`, `.ecxr`, `kb` (32-bit cdb):
   - in a trampoline or the proxy → hook mechanics or library;
   - in game `.text` on a bad or low pointer → delayed corruption; find who wrote it;
   - in `.text#2` or `.reloc` → a protector check or VM code; map it to §2's table.
3. **Find the writer** of a corrupted pointer: a TTD recording (`ttd.exe -launch` or `-attach`),
   then a memory breakpoint on the pointer and a reverse run to the writing instruction and thread.
   If it lands in the engine, it is a trap.
4. **Name the trap** in the f1c9 database (read-only: record addresses in the ledger, never save the
   database) and compare the site against the patch layers (R3 §2) to see whether any build already
   neutralises it.
5. **Patch it out** as an `.r2` layer on f1c9 with its SHA-256 chain. Rerun the reproducer the same
   number of times as before, and count a fix only when the crash rate drops.
6. **Record every crash** in a crash ledger, one JSON object per crash:
   `{time, exe_sha256, hooks, uptime_s, code, ip, section, dump, class, root_cause, patch, verified}`.
   Unclassified crashes stay open. ddon-hook keeps the ledger next to its run logs; findings about the
   client come back here as rows in §2.

## 6. Corrections to earlier records

- `patches/README.md`:
  - f1c9's content is FIX_3 plus 2 bytes, with no Mutex patch.
  - The "4GB RAM" patch only rewrites the PE checksum (`0x1B8`); LAA was already set.
  - The vanilla client is `D:\DDON_03040008\DDO.exe.bak`.
  - The Win7 dump's parent is FIX2.
  - Bunie PerfPatch v7 and the 100FPS build have no rows.
  - 10 of the 12 `.r2` files are UTF-16LE. All 12 replay to their stated hashes (R3 §7).
- **ddon-hook 011's "155 diff sites, 135 equal"** does not reproduce. v7 against f1c9 is 175 bytes in
  25 runs. The substance stands: f2a8 lacks the 122 FIX_3 stubs.
- **Earlier coordinator notes** said Bunie v7 is Themida-protected and that f2a8 builds on f1c9.
  Both are wrong (R3 §1, §2.10).
