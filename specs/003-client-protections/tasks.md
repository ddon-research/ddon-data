# 003 PC client protections: inventory, patches and crash triage

A research feature with no `spec.md`. Sam asked on 2026-10-17 for an independent inventory of the
PC `DDO.exe` builds' anti-tamper and anti-debug measures, and the Windows-specific ones: traps,
debugger checks, memory protections, integrity checks. It also asks for online and GitHub research
on how hooking frameworks cope with such measures, and an inventory of the patches each DDO
executable applies, the unpacked DUMP_FIX base of Bunie's builds above all. The goal is to stop the
random crashes: find each crash's root cause, patch out the trap, and hand the results to ddon-hook,
whose 009 T026 found that the `nrand` hook alone crashes both exes with 0xC0000005.

The last PC build was produced in 2019 for Windows 7 (client 03040008).

Output: `research/03040008/protections/`. Static work only. Never launch the client. IDA is
read-only: the GUI is not running, so use ida-mcp `open_database` on the 9.5 `.i64` (headless,
read-only, never save, `close_database` at the end). One subagent at a time.

## Research (sequential)

- [ ] R1 `general-purpose` (web): Themida/WinLicense 2.x–3.x anti-debug, anti-dump and
      integrity measures; Windows 7 → 11 behaviour changes that matter to a 2019 Win7 client;
      how SafetyHook, MinHook, Detours and PolyHook2 cope; DDON community projects.
      Brief `briefs/R1-online.md`; output `research/03040008/protections/R1-online.md`.
- [ ] R2 `general-purpose` (IDA, PE): inventory of the protections in the DUMP_FIX database and
      the PE-level traits of every PC executable. Brief `briefs/R2-static.md`; output
      `R2-static.md`.
- [ ] R3 `general-purpose` (patches): every patch layer from vanilla to Bunie v7 and ChatEdit,
      each site classified. Brief `briefs/R3-patches.md`; output `R3-patches.md`.
- [ ] S1 Coordinator: synthesis `README.md` with the crash-triage protocol; hand it to ddon-hook.

## Running

- R1 general-purpose (web), started 2026-10-17; R2 and R3 wait for it (one subagent at a time).
