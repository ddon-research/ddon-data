# Client lineage and protections

What the PC 03040008 client executables are, what the patch layers do to them, and why a hook that writes code crashes the client. It is for a reverse engineer about to hook, patch or debug this client. You need nothing first; hashes are in [Client patches](../reference/client-patches.md), sites in [Protection inventory](../reference/protection-inventory.md), and the steps in [Triage a client crash](../how-to/triage-a-client-crash.md). Facts carry addresses in the `f1c9` database. The evidence reports are in `research/03040008/protections/`: `R1-online.md`, `R2-static.md` and `R3-patches.md`. "[inference]" marks a conclusion.

## What the client is

Vanilla 03040008 (`01dc41a9`, PE timestamp 2019-01-25) is Themida-packed: uniform entropy across its sections, two `.text` sections, an entry point in the second. It is `D:\DDON_03040008\DDO.exe.bak`. `DDO_v3.05.exe` (`c93f7e4d`) is an older 2017 build, not the dump's source (`R3-patches.md` §1; the table of `R2-static.md` calls it vanilla, which is wrong).

Every `*DUMP*` executable is one Scylla dump of the unpacked client (OEP `0xB89168`, 7 sections with `.SCY`, all RWX), differing only by hand patches. Dumping does not remove the protector. The dump keeps Themida's **SecureEngine image** as a second `.text` at VA `0x240F000` (RVA `0x200F000`), with the IAT and more protector code in `.reloc` (`0x2231000`–`0x240EFFF`). Game code reaches the engine through ~1.5k calls, ~14.8k jumps and ~32.6k mutation-dispatch stubs, so it is live, not orphaned (`R2-static.md` §2, `R3-patches.md` §6). `.SCY` at `0x45A4000` is data: no relative call or jump from the first `.text` lands in it.

No game build has ASLR, CFG, SafeSEH or TLS callbacks. LARGEADDRESSAWARE is already set in the plain dump (`R2-static.md` §1), which is why the "4GB" write at `0x1B8` of the patches only rewrites the PE checksum. Bunie PerfPatch v7's exe is **not** Themida-packed: it is PerfPatch v1 plus 98 bytes, and its `dinput8.dll` is a plain MSVC build (`R3-patches.md` §2.10, §4). What stays protected is the game: the engine's code in `.text#2` is mutated and mostly undisassembled in the database.

## Why the layers stack as they do

The layers of 2021 and 2022 remove what stops research: FIX2 forces the engine's checksum compares and removes its `int 1` traps, and FIX_3 stubs its checksum reads. A later layer did not always build on the one before. `f1c9` is FIX_3 plus 2 bytes in content, because its script replays from the Mutex build and writes the Mutex bytes back, so it has no instance-limit removal. The installed `f2a8` descends from a Windows 7 re-dump of FIX2 and has none of FIX_3's or FIX's bytes, despite "Patch3" in its name.

So the two executables differ in the integrity checks that remain, not by one being newer. `f2a8` has 122 more live checksum reads than `f1c9`, and `f1c9` has three live compares that `f2a8`'s line stubbed. That is why hooked runs base on `f1c9`.

## What cannot be read statically

A byte diff means nothing against a packed original, since Themida encrypts every section; the plain dump's descent from `01dc41a9` rests on the PE timestamp and section RVAs alone. Three things are out of static reach: what each checksum compare covers, whether more compares or reads sit in the undisassembled islands of the engine, and which code each descriptor of FIX and FIX_3 describes. Runtime patches appear in no executable diff: the Mutex cave's write to `0x15BFFEF`, the patch at `0xF09655` of v3 and v7, and every MinHook, IAT or float write of the DLLs. They are listed from code and were never observed at runtime (`R3-patches.md` §5).

## What Bunie's DLLs add

PerfPatch v1–v3 hook with their own 5-byte jump; **only v7 uses MinHook**. The DLLs carry Nt* "Themida compatibility" hooks that answer "no debugger" for the own process only: `NtQueryInformationProcess` (debug port → 0, debug object handle → `STATUS_PORT_NOT_SET`, debug flags → 1), and `NtSetContextThread` (own thread; zeroes the debug registers, but its mask also clears `CONTEXT_i386`, a bug). A 100 ms watchdog clears `PEB.BeingDebugged`. In v7 it runs only with `Debugging=1`, together with a 5-byte NOP at `0xF09655` (`R3-patches.md` §4).

## Why a code patch crashes the client

An inline hook on `MtRandom::nrand` (`sub_13B5E10`) alone, with SafetyHook or MinHook, crashes the client 18 to 100 s after install in ddon-hook's recorded runs, on `f1c9` and on `f2a8`, with `0xC0000005` and usually no dump, while unhooked runs survive. The crash site is ordinary code far from any check, such as SIMD gameplay maths at `sub_18C6490`.

The hook itself is mechanically clean: the 5-byte `E9` covers exactly `push esi; mov esi,ecx; mov edx,[esi]`, with no split instruction and no branch (`R2-static.md` §8). The cause is the protector. Themida documents a check that runs every 30–60 s and answers a mismatch by corrupting data later, so that the program crashes far from the check, and TERA's Themida build behaved the same way (`R1-online.md` §1, §6). ddon-hook then caught it in a run on `f1c9` (its spec 009, `tasks.md`, of 2026-10-18, and its page `04-anti-debug-strategy.md`): a per-thread event ring at the fatal fault shows the protector's integrity worker single-stepping its own verification stubs with hardware breakpoints, then loading a wrong `eip`, which faults. An alternative a peer would propose first, a bug in the hook library, is out: SafetyHook and MinHook die at one address, and one soak survived with the hook removed after 10 s, so the patched page is what the check sees.

The missing crash report has its own cause: the CRT's `SetUnhandledExceptionFilter` path ends in `TerminateProcess` before Windows Error Reporting sees the fault. That is why the [protocol](../how-to/triage-a-client-crash.md#the-protocol) captures first-chance exceptions.

Removing the checks that can be found does not cure it. The layer FIX_4 stubs the three remaining compares and the `IsDebuggerPresent` calls, and the hooked client crashed in all three runs of 2026-10-17 that its JSON records: the compares alone, this layer, and this layer plus an `rdtsc` jump. The jobs run inside the engine and are not visible statically, which would explain it [inference]. A monitor that leaves `.text` alone does not trip the check, which is where ddon-hook's RNG work went: see [RNG race](rng-race.md).

## Anti-debug checks are a separate matter

The anti-debug checks fire only with a debugger attached, so they cannot explain a crash without one. Removing them buys debugger and TTD triage only. The Nt* probes go through ntdll and are not reachable by an executable layer: a proxy answers them, as Bunie's DLLs do. The `fs:[30h]` reads that the reports call debugger checks, 26 by the bytes, read the module list ([bytes](../reference/protection-inventory.md#the-26-peb-reads)).
