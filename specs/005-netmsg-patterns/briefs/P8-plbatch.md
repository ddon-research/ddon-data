005 P8: plbatch, a libpl batch driver for the ImHex pattern exports

Objective: build the long-lived pattern runner that `research/P7-imhex-as-library.md` recommends
(option a; read its sections 2c, 3, 5 and "Quick win" first) and switch `packets/imhex-export.sh`
to it, so an export runs at hundreds of packets/s per process instead of ~6/s (Sam, 2026-11-01:
"use it more like a library instead of spawning new executable instances").

Do:
1. Driver `research/imhex/plbatch/` (`plbatch.cpp`, `CMakeLists.txt`, `README.md`, `build.sh`):
   PatternLanguage pinned at `fb6ea061f7c8b66ed94b44ff1d3a10ee63a82612` (the commit ImHex 1.38.1
   uses; the newer HEAD changes JSON string escaping), fetched by `build.sh` into a gitignored
   build folder (or CMake FetchContent at that commit); never build inside the reference clone
   `D:/GitHub/WerWolv/PatternLanguage`. Interface and per-file sequence as P7 section 5 step 2
   (one runtime per process, `reset()` per file, JSON via `FormatterJson`, `ok|FAIL rel` lines,
   `.json.err` on failure, temp file + rename, no per-file exit). Build with MSYS2 mingw64 by full
   path (`/c/msys64/mingw64/bin/...`; `g++`/`cmake` on PATH are Strawberry's), `command -v` checks
   in `build.sh`, static runtime or the DLLs beside the exe. Install a missing MSYS2 package with
   `pacman` only if needed and say so in the receipt.
2. Acceptance before any wiring: on the 20 P7 sample files and a 1,000-file sample per nNetMsg
   type, plbatch JSON is byte-identical (`cmp`) to `imhex --pl format` JSON (same patterns,
   `-I research/03040008/packets/include` + ImHex 1.38.1's `includes/`), and failures match. Output
   to a scratch folder, never `packets/`. Measure throughput with `/c/Tools/hyperfine`; time parse
   vs evaluate once (P7's open test).
3. Wire `packets/imhex-export.sh`: use plbatch when built (env `PLBATCH`, else the built path),
   else the current ImHex path; build the file list in bash without per-file forks, shard it into
   `JOBS` plbatch processes; apply P7's quick win to the fallback path. **Before editing the script,
   confirm no export runs** (`ps -ef | rg -c imhex-export`; P3's export of the four types may still
   be running from it, and editing a running bash script corrupts it). If one runs, finish steps 1-2,
   end your turn with `waiting: export still running`, and the coordinator wakes you.
4. Document the build and the switch in `packets/README-decrypt-annotate-streams.adoc` (the ImHex
   export section) and `research/imhex/plbatch/README.md`.

Owns: `research/imhex/plbatch/**`, `packets/imhex-export.sh`, the ImHex section of
`packets/README-decrypt-annotate-streams.adoc`, a `.gitignore` line for the build folder. Never
touch: `packets/decrypted_json/` (P3's export output, uncommitted, the coordinator commits it),
`packets/decrypted_raw/`, `packets/decrypt-annotate-streams.sh` (another session's edit),
`research/03040008/packets/` patterns, client/. The index holds three files staged by other work
(`binaries/.../functions.ida-9.5.jsonl`, `research/external/*`): commit only with `-- <paths>`.
Libraries: PatternLanguage (libpl) at the pin, its bundled deps; own code is only the driver.
Done: signed commits with explicit paths; receipt with the build command and toolchain versions,
`cmp` results (files compared, identical, differing), throughput (plbatch vs imhex.exe, measured),
and `bash tools/check.sh --since <base>`.
Stop: budget 90 min of work time. Stop and report if the pinned PL does not build with mingw64
within 30 min (say what failed), or if any JSON differs from ImHex's in a way you cannot explain.
Base: 359bfe7b7a.
