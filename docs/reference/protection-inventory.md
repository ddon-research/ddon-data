# Protection inventory

The mechanisms still present in the PC 03040008 dumps and what each layer did to them, for anyone classifying a fault or choosing a layer. Addresses are virtual addresses in the `f1c9` database (image base `0x400000`, no relocations). You need the executables' names from [Client patches](client-patches.md). Why they are there: [Client lineage and protections](../explanation/client-lineage-and-protections.md). "[inference]" marks a conclusion, as in the reports. The evidence is in `research/03040008/protections/`: `R2-static.md` and `R3-patches.md`, with `R1-online.md` for the outside sources.

## Mechanisms

`f1c9` is the DUMP_FIX executable, `f2a8` the installed `DDO.exe`.

| Mechanism | Where | State in f1c9 | In f2a8 | Source |
| --- | --- | --- | --- | --- |
| Checksum compares in the engine | 536 sites, `.text#2` and `.reloc` | forced by FIX2 | forced (FIX2) | `R3-patches.md` §2.1 |
| `int 1` debugger traps | 12 sites | removed by FIX2 | removed | `R3-patches.md` §2.1 |
| Checksum reads `mov eax,[edx]` → `xor eax,eax` | 122 sites, 120 from `0x22CE8E9` | stubbed by FIX_3 | **live** | `R3-patches.md` §2.2, §3 |
| Protector descriptor fields in game padding | `0x738B76`, `0xD5C79A` | zeroed by FIX | live | `R3-patches.md` §2.5 |
| **Three remaining checksum compares** | `0x24CD5DE`, `0x3A87F64` (guards the `cmovz` at `0x3A87F85` that the Mutex layer forces), `0x430DF3B` | **live** | stubbed (Win7 lineage) | `R3-patches.md` §6 |
| PEB reads `fs:[30h]`, then `[eax+0Ch]` (`PEB.Ldr`) | 23 sites in `.text#2`: [listed below](#the-23-peb-reads) | live | live | below |
| Nt* debug probes (NtQueryInformationProcess, NtSetInformationThread, ...) | resolved dynamically by the engine; absent from the IAT | live | live | `R2-static.md` §3 |
| Code-integrity / VM jobs (Themida `CHECK_CODE_INTEGRITY` style, 30–60 s period) | inside the engine; thread or timer not visible statically | presumed live [inference] | presumed live | `R1-online.md` §1, §7; `R2-static.md` §7 |
| rdtsc timing busy-wait | `0x180DB03` | live | live | `R2-static.md` §4 |
| CRT `IsDebuggerPresent` | `sub_19A7F4B`, `sub_19AE207`, `sub_19C1338` | live, low value | live | `R2-static.md` §3 |
| Game VEH crash reporter (AddVectoredExceptionHandler, Get/SetThreadContext) | `sub_145Cxxx`/`sub_145Dxxx` | live | live | `R2-static.md` §6 |
| CRT `SetUnhandledExceptionFilter` → `TerminateProcess` fast-fail | `sub_19AB8EB`, `sub_19AB8D6` | live: ends the process before WER | live | `R2-static.md` §6 |
| SHA-256 helper | `sub_A0F280`, `sub_A0F3A0` | live, purpose unknown | live | `R3-patches.md` §6 |
| Page-RWX helper (only VirtualProtect user) | `sub_13EE875` | live, benign | live | `R2-static.md` §7 |


No PAGE_GUARD or NOACCESS tripwire was found on the `nrand` path, and no routine reads `nrand`'s
bytes as data (`R2-static.md` §5, §7, §8). A section-wide hash is not excluded.

## Other sites no layer touches

From `R3-patches.md` §6, each checked against every diff run of every layer.

| Protection | Location | Touched by | Note |
| --- | --- | --- | --- |
| Padding descriptors in the style of FIX and FIX_3 | other `… c3 [len] 00 00 00 …` blocks next to DTI getters, read by engine code (pattern of `0x738B66`, `0x738B7A`) | only two zeroed (FIX), two set to -1 (FIX_3, unconfirmed) | **not run**: a scan for more such blocks |
| Mutation dispatch and cross-segment edges | ~32.6k `lea esp,[esp+4]; jmp [esp-4]`; ~16k `E8`/`E9` into `.text#2` | only the 9 macro-entry skips (FIX2) and the runtime patch at `0xF09655` (v3, v7 with `Debugging=1`) | the engine stays reachable everywhere |
| Game `IsDebuggerPresent` call | `0xBEEA24`, in `sub_BEEA00` | the layer FIX_4 alone (`2026_10_17_ddo_dump_fix_4.json`) | the CRT's three calls are at `0x19A7F4E`, `0x19AE2F1`, `0x19C1429` |

## The 23 PEB reads

`0x246A13B`, `0x24A1000`, `0x24BF352`, `0x24C9D83`, `0x24CEB5C`, `0x24D0150`, `0x2527530`, `0x2F487A4`, `0x33CF678`, `0x33D9701`, `0x350E390`, `0x35125C5`, `0x3645E41`, `0x3A8644F`, `0x3B1667C`, `0x3C06CA0`, `0x3C0714F`, `0x3D2C8AA`, `0x40861F3`, `0x4092D1E`, `0x412C3EF`, `0x41B6891`, `0x4225011`.

Each is `64 A1 30 00 00 00` (`mov eax,fs:[30h]`) followed by `8B 40 0C` (`mov eax,[eax+0Ch]`), directly at 20 sites and after one `jmp` at `0x3A8644F`, `0x3B1667C`, `0x3C06CA0`: read from the bytes of `f1c9` on 2026-11-04. So they read `PEB.Ldr`, the module list, and not `PEB.BeingDebugged` at `PEB+2`. `R2-static.md` §3 and `R3-patches.md` §6 call them `BeingDebugged` reads, and ddon-hook's spec 009 records the same correction. Patching them out would break the engine's import resolution [inference].
