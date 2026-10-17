# R2 Static inventory: protections in the PC executables

Role: general-purpose researcher (IDA, PE tooling). Time budget: 60 minutes of wall clock.
Read-only everywhere except the output file and your scratchpad.

## Question

Which anti-debug, anti-tamper, integrity, exception-trap and memory-protection mechanisms are still
present in the unpacked DUMP_FIX client (03040008, SHA-256 prefix f1c9), and which PE-level traits
distinguish each PC executable? Which of them can turn an inline hook on `nrand` into an access
violation within 20–50 s?

## Inputs

- IDA: `D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.i64` (32-bit,
  base 0x400000). No GUI is running. Use ida-mcp `open_database` on it (headless idalib, allowed),
  **read-only: no renames, comments, patches or saves**, and `close_database` at the end. Call
  `reference(query)` before guessing an API.
- Executables: `D:\research\DDON-binaries\PC\*.exe` and subfolders, plus the installed
  `D:\DDON_03040008\DDO.exe` (f2a8). Never run them. For PE analysis use a library: `uv run --with
  pefile` (or LIEF) on a script in your scratchpad, with `python -X utf8 -I`.
- Earlier results to reuse, not redo: `research/03040008/protections/R1-online.md` (the online
  survey), ddon-hook `specs/009-rng-race-monitor/tasks.md` (T026 and the 155 v7 diff sites) and
  `specs/011-client-automation/tasks.md`.

## Cover

1. Per executable (table): SHA-256, size, timestamp, sections (names, flags, entropy), entry point
   section, TLS callbacks, DllCharacteristics (ASLR, DEP, NX, CFG, SafeSEH table),
   LARGEADDRESSAWARE, import count and notable imports (anti-debug, VirtualProtect/Alloc,
   exception, thread, timing, crypto, window APIs), Themida/WinLicense markers.
2. In the DUMP_FIX database: every call site or inline instance of debugger checks
   (IsDebuggerPresent, CheckRemoteDebuggerPresent, NtQueryInformationProcess, NtSetInformationThread,
   PEB reads `fs:[30h]`, heap flags, OutputDebugString tricks, int 2d / int3 / `ud2` / icebp, debug
   registers via GetThreadContext), timing checks (rdtsc, QueryPerformanceCounter, GetTickCount
   deltas), integrity checks (the CRC routines DUMP_FIX neutralises, any still live, what they hash),
   exception handling (SEH frames that catch faults on purpose, AddVectoredExceptionHandler,
   SetUnhandledExceptionFilter, the game's own crash reporter), memory protection changes
   (VirtualProtect, PAGE_GUARD, NOACCESS), watchdog or check threads, code that reads its own
   `.text`, and leftovers of the Themida stubs (calls into removed sections, VM entry stubs).
3. `nrand` specifically: its address, its callers and which threads call it, what reads its bytes
   (xrefs to its range as data), whether any routine hashes the page it is on, and what the hook's
   first 5+ bytes overwrite (instruction boundaries, jump targets inside the patched range).

## Output

`D:\ddon-data\research\03040008\protections\R2-static.md`: the per-executable table, then one
section per mechanism with address, function, evidence (instruction or xref) and state (live,
neutralised by DUMP_FIX, unreachable, unknown), and a final "T026 candidates" section ranked by
evidence. Facts carry addresses and the database; mark inferences. At most 700 lines. A check you
could not run is "not run".

Do not commit. Final message: path, line count, and the five most important findings in at most
ten lines.

## Added after R1 (2026-10-17)

R1's leading hypothesis (H1, `R1-online.md` section 7) is Themida's delayed integrity response:
a `CHECK_CODE_INTEGRITY`-style check on a 30–60 s thread or timer that corrupts a pointer instead of
crashing at once. Test it statically: thread and timer creation sites (CreateThread, _beginthreadex,
timeSetEvent, CreateTimerQueueTimer, SetTimer) and what each thread body does; routines that read
`.text` bytes as data or hash code ranges, including any not neutralised by DUMP_FIX; SecureEngine
VM entry stubs or calls into the removed Themida sections that survived the dump; writes that clear
or overwrite global context pointers from such routines. Also record whether the dump's
`SetUnhandledExceptionFilter` or crash handler would suppress WER dumps (R1 H-section 5).
Record any external document you rely on in `research/external-references.jsonl`
(format: `research/external-references.md`).
