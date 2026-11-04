# PC client protections, patch layers and crash triage (03040008)

The evidence on the PC client's protections, and the numbered map that ddon-hook cites. Each numbered section keeps its number and links to the page that holds its content. Addresses are in the `f1c9` database (image base `0x400000`, no relocations). "[inference]" marks a conclusion.

| Report | Contents |
| --- | --- |
| `R1-online.md` | Themida/WinLicense measures, Windows 7 → 11 behaviour, SafetyHook, MinHook, Detours, PolyHook2, ScyllaHide, TitanHide, HyperHide (clones and SHAs in `research/external-references.jsonl`), crash-triage tools, the TERA precedent |
| `R2-static.md` | PE traits of every executable in `D:\research\DDON-binaries\PC`; protections still present in the DUMP_FIX database (`f1c9`, IDA 9.5, read-only); `nrand` hook mechanics |
| `R3-patches.md` | The lineage by hash and diff, every patch layer site by site, Bunie's DLL hooks, protections no layer touches |

The reports are fixed evidence of 2026-10-17, cited by section. Where a page disagrees with them, it says so and names the check.

## 1. What the client is

Vanilla 03040008 (`01dc41a9`) is Themida-packed. Every `*DUMP*` executable is one Scylla dump of the unpacked client, differing only by hand patches, and it keeps the protector's engine live. `f1c9` is FIX_3 plus 2 bytes, with no Mutex patch. The installed `f2a8` descends from FIX2 only and has none of FIX_3's or FIX's bytes. See [Client lineage and protections](../../../docs/explanation/client-lineage-and-protections.md) and [the lineage by hash](../../../docs/reference/client-patches.md#lineage).

## 2. Protection inventory

The table of mechanisms, sites and their state in `f1c9` and `f2a8` is [Protection inventory](../../../docs/reference/protection-inventory.md). Findings about the client become rows there.

## 3. Why a hook crashes the client

An inline hook on `MtRandom::nrand` (`sub_13B5E10`) alone crashes the client within tens of seconds, usually with no dump: a deliberate reaction of the protector's integrity check to the patched `.text`, far from the check. See [Why a code patch crashes the client](../../../docs/explanation/client-lineage-and-protections.md#why-a-code-patch-crashes-the-client).

## 4. What to do on top

Base hooked runs on `f1c9`, never `f2a8`: `f2a8` lacks FIX_3's 122 checksum stubs. The steps, in order of cost, are in [When a hook writes `.text`](../../../docs/how-to/triage-a-client-crash.md#when-a-hook-writes-text).

## 5. Crash-triage protocol

Every crash gets a root cause and, where it is a trap, a patch: capture before the game's handlers can hide it, classify the faulting IP, find the writer, name the trap, patch it out, record every crash in a ledger. The six steps, with these numbers and commands, are in [Triage a client crash](../../../docs/how-to/triage-a-client-crash.md#the-protocol). ddon-hook runs them.

## 6. Corrections to earlier records

Corrected facts stand on the pages named here; the list of what was wrong is `R3-patches.md` §7. For the lineage of the two executables: `f1c9`'s parent by content is FIX_3 and `f2a8`'s line is FIX2 → the Win7 dump `1c8c` → `f2a8`, neither on the other ([lineage](../../../docs/reference/client-patches.md#lineage)). A count in ddon-hook's spec 011 ("155 diff sites, 135 equal") does not reproduce: v7 against `f1c9` is 175 bytes in 25 runs. Its substance stands: `f2a8` lacks the 122 FIX_3 stubs. Bunie v7's exe is not Themida-protected, and `f2a8` does not build on `f1c9` (`R3-patches.md` §1, §2.10). The 23 PEB reads are `PEB.Ldr` reads, not `BeingDebugged` reads ([inventory](../../../docs/reference/protection-inventory.md#the-23-peb-reads)).
