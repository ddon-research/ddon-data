# R1 Online and GitHub research: protections and how hookers cope

Role: general-purpose researcher (web). Time budget: 40 minutes of wall clock. Read-only on this
repository except the one output file.

## Question

What anti-tamper, anti-debug, anti-dump and integrity measures can a 2019 DDO PC client (03040008,
32-bit, built for Windows 7, Themida/WinLicense-packed vanilla, also unpacked dumps) contain? How do
hooking and anti-anti-debug tools deal with each one? Which of them could make an inline hook crash
the client with an access violation (0xC0000005) seconds after install, while unhooked runs survive?

## Context

- ddon-hook (`C:\Users\morph\CLionProjects\ddon-hook`) is a `dinput8.dll` proxy that hooks DDO.exe
  with SafetyHook (inline hooks, uses a process-wide VEH when it traps threads during install).
- Its 009 T026 matrix: the `nrand` hook alone crashes both the installed exe (techwomanwow Win7
  build, 50 s) and the DUMP_FIX dump (20 s) with 0xC0000005 and no crash report; no hooks survive
  4–6 min. IDA ruled out the CRC checks, register clobbering and address space.
- Executables: `D:\research\DDON-binaries\PC` (vanilla `DDO_v3.05.exe`, the dumps and fixes,
  Bunie's builds). Bunie PerfPatch v7 is itself Themida-protected and fakes the foreground window in
  the IAT.

## Cover

1. Themida/WinLicense 2.x and 3.x: anti-debug checks (PEB, heap flags, NtQueryInformationProcess
   classes, NtSetInformationThread HideFromDebugger, debug registers, int 2d/int3, timing, parent
   process), anti-dump, VM macros, CRC/integrity of code and of its own stubs, memory guards and
   guard pages, thread checks, what survives in an unpacked dump (VM'd functions, SDK markers,
   checks that call back into removed stubs).
2. Windows specifics, Win7 vs Win10/11: VEH/SEH/SafeSEH, DEP, CFG, ASLR, `/LARGEADDRESSAWARE`,
   WOW64 and its syscall layer, fibers, TLS callbacks, ntdll hook detection, instrumentation
   callbacks.
3. Hooking libraries: SafetyHook, MinHook, Microsoft Detours, PolyHook2, and others worth naming.
   For each: trampoline allocation (near-memory search), thread suspension and IP fix-up, VEH use,
   relocation of RIP-relative / short jumps, known incompatibilities with Themida or anti-tamper,
   issues on GitHub about crashes after install.
4. Anti-anti-debug tools: ScyllaHide, TitanHide, HyperHide, x64dbg plugins, Scylla (dumping);
   what each hides and how, and which settings Themida needs.
5. Crash triage on Windows for such a target: WER LocalDumps registry key, ProcDump, cdb/WinDbg
   `!analyze`, Time Travel Debugging, AddVectoredExceptionHandler logging, `SetUnhandledExceptionFilter`
   being overridden by the game, first-chance vs second-chance.
6. DDON community work: Bunie/Buns perf patches, techwomanwow, rootofallthings, mr.september,
   Arrowgene and DDOn-Tools discussions of crashes, CRC or "dump fix" patches. GitHub searches.

## Output

`D:\ddon-data\research\03040008\protections\R1-online.md` (create the folder): one section per
item above, each claim with its URL, and an "inference" mark where you conclude rather than cite.
End with a ranked list of hypotheses for the T026 crash and the observation that would confirm or
refute each one. At most 600 lines. Do not quote more than a line from any source.

Never download or run binaries. Do not commit. Final message: the path, line count and the five
most important findings in at most ten lines.
