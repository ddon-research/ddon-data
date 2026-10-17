# R3 Patch inventory: every layer from vanilla to Bunie v7

Role: general-purpose researcher (radare2, IDA). Time budget: 60 minutes of wall clock.
Read-only everywhere except the output file and your scratchpad.

## Question

What does each DDO PC patch layer change, site by site, and why? Above all: what does DUMP_FIX
(2022_01_29, f1c9) change relative to the plain dump, and what do Bunie's builds (3-in-1, 5-in-1,
100FPS, PerfPatch v1–v3, v7) and the ChatEdit / 4GB / Win7 / mutex builds add on top?

## Inputs

- `patches/*.r2` and `*.json` (radiff2 `wx` scripts with SHA-256 chain) and `patches/README.md`.
- Executables in `D:\research\DDON-binaries\PC` (never run them). Builds without a `.r2` here: diff
  them yourself with `radiff2` against their parent (pick the parent by hash chain or by fewest
  diffs, and say how you chose). Bunie v7 is Themida-protected: say which parts cannot be diffed.
- IDA: the DUMP_FIX database (`D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.i64`),
  headless via ida-mcp `open_database`, **read-only, never save**, `close_database` at the end.
  Map file offsets to VAs with the section table, then name the function at each site.
- Reuse, do not redo: `research/03040008/protections/R2-static.md` (protection inventory) and
  ddon-hook `specs/009-rng-race-monitor/tasks.md` (the 155 v7 diff sites, 135 of them DUMP_FIX,
  about 120 neutralising CRC reads).

## Output

`D:\ddon-data\research\03040008\protections\R3-patches.md`:
- a lineage diagram (text) with hashes and parents;
- per layer: site count, then a table of sites grouped by purpose (CRC/integrity, anti-debug,
  mutex/multi-instance, Win7 compat, launcher/boot checks, chat, memory/4GB, FPS/perf, foreground
  spoof, unknown), each row VA, file offset, function, old → new bytes summary, and purpose with
  evidence or an inference mark;
- protections that no layer touches (from R2), as candidates for crash traps;
- discrepancies with `patches/README.md`.
At most 800 lines; group repetitive CRC sites into ranges instead of one row each.

Do not commit. Final message: path, line count, and the five most important findings in at most
ten lines.

## Added after R2 (2026-10-17)

R2 (`R2-static.md`) says the installed `D:\DDON_03040008\DDO.exe` (f2a8) descends from filmmachine's
dump, not from f1c9, and lacks the ~120 CRC-read stubs in the second `.text` (`0x240F000+`, the
captured SecureEngine image). Settle the lineage of every dump by hash and diff, and say which
layers carry those stubs. Note which hooking library each Bunie build embeds (R2: MinHook) and
what its Nt* "Themida compatibility" hooks in v7 do, site by site where it can be read.
