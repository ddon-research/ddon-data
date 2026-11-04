# Triage a client crash

This page is for anyone whose PC 03040008 client died under a hook or an automated run and who must find the cause rather than guess at it. You capture the crash, classify the faulting address, find the writer and record the result in a ledger. Every crash gets a root cause and, where it is a trap, a patch. You need a client you may run: the client runs only from ddon-hook, against the local Arrowgene server, whose own triage page secures a run's evidence first. Background: [Client lineage and protections](../explanation/client-lineage-and-protections.md).

## The protocol

Addresses are virtual addresses in the `f1c9` database.

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
   - in `.text#2` or `.reloc` → a protector check or VM code; map it to the [protection inventory](../reference/protection-inventory.md).
3. **Find the writer** of a corrupted pointer: a TTD recording (`ttd.exe -launch` or `-attach`),
   then a memory breakpoint on the pointer and a reverse run to the writing instruction and thread.
   If it lands in the engine, it is a trap.
4. **Name the trap** in the `f1c9` database (read-only: record addresses in the ledger, never save the
   database) and compare the site against the patch layers (`research/03040008/protections/R3-patches.md` §2) to see whether any build already
   neutralizes it.
5. **Patch it out** as an `.r2` layer on `f1c9` with its SHA-256 chain. Rerun the reproducer the same
   number of times as before, and count a fix only when the crash rate drops.
6. **Record every crash** in a crash ledger, one JSON object per crash:
   `{time, exe_sha256, hooks, uptime_s, code, ip, section, dump, class, root_cause, patch, verified}`.
   Unclassified crashes stay open. ddon-hook keeps the ledger next to its run logs; findings about the
   client come back as rows of the [protection inventory](../reference/protection-inventory.md).

ddon-hook's `run_cycles.py` runs step 1's capture as `procdump -ma -e 1 -f C0000005 -n 5 <pid> <dumps folder>` when given `--procdump`, and appends the ledger row to `build\automation-runs\crash-ledger.jsonl`. Its logging VEH is the switch `DDON_HOOK_EXCEPTION_LOG=1`.

You are done with a crash when its ledger row has `class`, `root_cause` and `verified`. A crash without them stays open.

## When a hook writes `.text`

Any inline patch of `.text` draws the protector's integrity reaction ([why](../explanation/client-lineage-and-protections.md#why-a-code-patch-crashes-the-client)). Take these in order of cost; each has a stop rule.

1. **Base on `f1c9`, never `f2a8`,** for hooked runs: `f2a8` lacks FIX_3's 122 stubs. Pass it to the run with `--exe`.
2. **Tell the kinds of cause apart,** one run each, more samples where needed, since crash times are random:
   - Unhook after 10 s. If the client survives past 60 s, the crash is a reaction to the live patch, not the hook's code.
   - Build the same hook with MinHook. If only SafetyHook crashes, it is the library.
   - A no-op hook that only calls the original. If that still crashes, the cause is the patch itself, not timing or added work.
3. **Try the layer FIX_4 on `f1c9`** if the checksum compares are in question. **Status:** implemented, not tracked at 2026-11-04: `2026_10_17_ddo_dump_fix_4.r2`, recorded in [Client patches](../reference/client-patches.md#a-layer-outside-the-index). It stubs `0x24CD5DE`, `0x3A87F64` and `0x430DF3B` with the bytes of `1c8c`, and in its smoke runs of 2026-10-17 the hooked client still crashed, so it does not stop this crash on its own.
4. **Answer the anti-debug probes in the proxy,** as Bunie and ScyllaHide do (`research/03040008/protections/R1-online.md` §4, `research/03040008/protections/R3-patches.md` §4): fake `NtQueryInformationProcess` for the own process. Needed only when a debugger or TTD is attached. Do not copy Bunie's `NtSetContextThread` mask bug ([what it is](../explanation/client-lineage-and-protections.md#what-bunies-dlls-add)).
5. **Use a hook that does not write `.text`,** when the patch itself is what trips the check:
   - hardware breakpoints in `DR0`–`DR3` with a VEH (PolyHook2 has both kinds), which needs the `NtSetContextThread` fix above. ddon-hook's data watch is this kind, and the protector holds the debug registers of the main thread;
   - a read-only sampler of the data, with no hook at all, which ddon-hook's RNG work ended on;
   - a PAGE_GUARD VEH hook;
   - hooking the callers' data (vtables, function pointers) where one exists. `nrand` is called directly from hundreds of sites, so that does not apply to it.
6. **Only if 2–5 fail: find and disable the scheduler of the integrity jobs.** The method comes from TERA's Themida build: scan for the VM trampolines (`pushfq` sequences) and remove the job that writes the corrupting pointer (`research/03040008/protections/R1-online.md` §6). It needs TTD to find the write.
