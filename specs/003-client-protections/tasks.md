# 003 PC client protections: inventory, patches and crash triage

**Status: done** (2026-10-17). Follow-up runs in ddon-hook 009 T026 (README sections 4 and 5).

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

- [x] R1 `general-purpose` (web; 9 min, 43 tool calls, 124k tokens; e529ddf6001): Themida/WinLicense 2.x–3.x anti-debug, anti-dump and
      integrity measures; Windows 7 → 11 behaviour changes that matter to a 2019 Win7 client;
      how SafetyHook, MinHook, Detours and PolyHook2 cope; DDON community projects.
      Brief `briefs/R1-online.md`; output `research/03040008/protections/R1-online.md`.
- [x] R2 `general-purpose` (IDA, PE; 13 min, 37 tool calls, 197k tokens): inventory of the protections in the DUMP_FIX database and
      the PE-level traits of every PC executable. Brief `briefs/R2-static.md`; output
      `R2-static.md`.
- [x] R3 `general-purpose` (patches; 16 min, 75 tool calls, 267k tokens): every patch layer from vanilla to Bunie v7 and ChatEdit,
      each site classified. Brief `briefs/R3-patches.md`; output `R3-patches.md`.
- [x] S1 Coordinator: synthesis `research/03040008/protections/README.md` with the crash-triage protocol; handed to ddon-hook.
- [x] S2 Correct `patches/README.md` (README §6: f1c9 parent, 4GB = checksum, vanilla path, Win7 parent, missing v7 and 100FPS rows, UTF-16 files).
- [x] C1 Closing: index in `research/external-references.md`, pointer in `CLAUDE.md` Resume, light
      retro below.

## Running

- (none)

## Retro (light)

- Three sequential general-purpose agents: 38 min, 155 tool calls, 588k subagent tokens in all
  (R1 124k, R2 197k, R3 267k). No overruns of the 40/60/60 min budgets.
- What worked: each brief reused the previous report and gained an "Added after" section, so R2 and
  R3 tested R1's hypothesis instead of resurveying. R3 corrected R2 twice (vanilla build, `.reloc`).
- Inefficiency: R1 left a background shell, so the cap kept its record and refused R2; the cap now
  clears receiptless roles on stop (b027312a1e0, ddon-hook cb66d89). Sam's clone and manifest rules
  arrived mid-R1 and were delivered by message, not in the brief.
- Learning: the reconstructor's prior-art pattern (local clones, a references manifest, per-topic
  reports) is now ddon-data's (`research/external-references.md`).
