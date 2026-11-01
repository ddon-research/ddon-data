# P7: ImHex patterns as a library, not one process per packet

Brief: `specs/005-netmsg-patterns/briefs/P7-imhex-as-library.md` (base 3f9c147b32). Researcher:
repository-researcher, 2026-11-01. Build of the data: client **03040008** packets
(`packets/decrypted_raw`, read only). Nothing was built or committed; scratch work in
`C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/p7/`.

## Answer

The time does not go into the pattern language. A single `imhex --pl format` run of the full
nNetMsg pattern costs the same as `imhex --version` (process start + plugin init, 150-450 ms), the
pattern evaluation itself costs about **0.3 ms per packet**, and the observed 6 packets/s comes from
**Git Bash (MSYS) process creation contention** in `packets/imhex-export.sh`, not from ImHex: with
~30 job shells alive, one `$(dirname …)` subshell took 616 ms and one `cygpath` call 730 ms, and the
script spends about eight process creations per packet.

Recommendation: **option (a)**, a small C++ batch driver (`plbatch`) linking `libpl` + `libpl-gen`
built from PatternLanguage at **`fb6ea061f7c8b66ed94b44ff1d3a10ee63a82612`** (tag `ImHex-v1.38.1`,
the commit ImHex 1.38.1 pins, so JSON output is byte-compatible), MSYS2 **mingw64** gcc + lld +
ninja, one runtime per process, run as N shard processes. Expected 1,000+ packets/s per process
(inferred), so the 110,065-file nNetMsg export drops from hours to minutes. Interim fix with no
build: remove the per-packet subshells from `imhex-export.sh` and lower the job count (see
"Quick win").

## 1. Clones (verified)

| Repo | Path | Commit read | Date |
| --- | --- | --- | --- |
| PatternLanguage | `D:/GitHub/WerWolv/PatternLanguage` | HEAD `300d7388475dd7ffd04239dfc889b72fe08bae18`; also fetched `fb6ea061f7c8b66ed94b44ff1d3a10ee63a82612` | 2026-09-13 / 2025-12-21 |
| ImHex | `D:/GitHub/WerWolv/ImHex` | `34483cb90527cd71c92049ef3b1b2cc27936a1d4` (HEAD, not the 1.38.1 tag) | 2026-10-08 |
| ImHex-Patterns | `D:/GitHub/WerWolv/ImHex-Patterns` | `e07e98adc810f0c052035ee1fdabae7ec65110e2` | 2026-09-22 |
| ImHex-Plugin-Template | `D:/GitHub/WerWolv/ImHex-Plugin-Template` | `79d12a3d88dedf07a64041c4a562d0913e6e4369` | 2025-02-09 |

Four rows appended (CRLF, as the file uses) to `research/external-references.jsonl` (32 -> 36 lines).

Version pin (verified): `gh api repos/WerWolv/ImHex/contents/lib/external/pattern_language?ref=v1.38.1`
gives submodule SHA `fb6ea061…`; `gh api repos/WerWolv/PatternLanguage/git/ref/tags/ImHex-v1.38.1`
gives the same SHA. The installed binary reports `Version 1.38.1, Commit v1.38.X@76cf877, Build
time Dec 21 2025`. The PL release `ImHex-v1.38.1` has **no assets**; CI artifacts "plcli Windows"
(3.4 MB, 2026-10-21) exist but are built from master (300d738), not the pin.

Pin vs HEAD matters (verified, `git diff fb6ea061 300d738`): `executeString`/`executeFile` return
`bool` at the pin and `int` at HEAD; `formatter_json.hpp` changed string escaping (pin
percent-encodes every non-`[A-Za-z0-9-_.~]` byte, e.g. `"NET_MSG_ID%3A%3ANET_MSG_ID_ENEMYSTATUS_CTRL"`
in today's output; HEAD decodes UTF-8 instead). A driver built from HEAD would change existing JSON.

## 2. Measurements

Machine: 32 logical CPUs; **contended**: P3's export (`xargs -P 32`, started 10:56) and other jobs
(uv, ddon-harness-orchestration) were running throughout, so absolute numbers are noisy (σ ≈ 50-70 %
of the mean). Input: 20 `C2S_PARTY_SEND_BINARY_MSG_NTC` files copied from `packets/decrypted_raw`
to `scratchpad/p7/in/01..20.bin` (2,368 bytes total, 64-160 bytes each). Pattern: copy of
`research/03040008/packets/C2S_PARTY_SEND_BINARY_MSG_NTC-pattern.cpp` (29 lines) with
`-I research/03040008/packets/include` (`nNetMsg.hexpat`, 962 lines; imports std.mem, std.bit,
std.io, std.math). ImHex `E:/Software/imhex-1.38.1-Windows-Portable-NoGPU-x86_64/imhex.exe`.

### 2a. One `--pl format` run, by stage (measured)

`hyperfine -N --warmup 2 --runs 15` (script `scratchpad/p7/bench1.sh`, JSON `bench1.json`), input
`01.bin`, output to stdout:

| Command | Mean | σ | Min |
| --- | --- | --- | --- |
| `imhex --version` (process start, no plugins) | 453.9 ms | 339.4 | 161.0 |
| `imhex --pl --help` (+ settings load, all 11 plugins initialised) | 552.1 ms | 284.4 | 184.3 |
| `--pl format` trivial pattern `u8 x @ 0x00;` | 398.5 ms | 275.6 | 143.6 |
| `--pl format` trivial + the 4 std imports | 441.5 ms | 251.8 | 221.9 |
| `--pl format` full nNetMsg pattern | 356.0 ms | 181.4 | 148.3 |

The five are indistinguishable: per-packet wall time is all process start and plugin init
(`InitPlugins` flag on `pl`, ImHex `plugins/builtin/source/plugin_builtin.cpp:36`; init at
`lib/libimhex/source/subcommands/subcommands.cpp:111-114`, which also loads settings and the .NET
`script_loader`). Parse of ~1,000 lines + std imports is below the noise floor (not separable here).

### 2b. Evaluation cost per packet (measured, transfer inferred)

Pattern `loopN.hexpat` = the full pattern with the top-level placement replaced by
`fn main() { for (u32 i = 0, i < N, i += 1) { C2S_PARTY_SEND_BINARY_MSG_NTC p @ 0x00; } };`
(one process, one parse, N evaluations of the packet struct), three rounds:

| N | Wall (3 runs) |
| --- | --- |
| 1 | 729, 1180, 658 ms |
| 1000 | 1244, 1103, 1325 ms |
| 4000 | 1990, 2001, 1919 ms |

4000 evaluations add ~1.1-1.3 s → **~0.3 ms per packet evaluation**. (N = 5000 fails: loop limit
4096, `#pragma loop_limit`.) Inferred: a real per-file evaluation also does the JSON formatting and
`flattenPatterns`, a few hundred patterns per packet, so well under 1 ms.

### 2c. Why the export fell to ~6/s (measured)

Sampled while P3's export ran (12:44): `ps` showed 2 `xargs`, 28-33 `/usr/bin/bash`, and **0-1**
`imhex.exe` alive at any sample (8 samples, plus `tasklist`). So 32 job slots, but almost all of
them are blocked inside bash, not in ImHex. In the same shell at the same time:

- 50 `x=$(dirname /a/b/c)` subshells: 30,815 ms → **616 ms per fork**;
- 20 `cygpath -aw /c/x`: 14,621 ms → **730 ms per call**.

`export_one` (`packets/imhex-export.sh:89-124`) per packet: `bash -c` from xargs, `$(dirname …)`
(l. 97), `mkdir -p`, `$(cygpath -aw …)` (l. 102), `rm -f`, ImHex, `mv -f`, `rm -f` — about 8
Cygwin process creations. Cygwin/MSYS `fork` gets slower with the number of concurrently forking
processes (it copies the parent's address space and walks shared state; inferred cause), so 32
jobs make each job slower, not the export faster. At ~0.6 s per creation × 8 ≈ 5 s per packet
spread over the slots, the system lands near the observed 6/s (inferred arithmetic, consistent
with the samples). Disk is not the limit (inputs are 64-160 bytes; outputs a few KB). Windows
Defender (`MsMpEng.exe`, 3 h CPU time) scanning each of 110k ImHex launches with ~40 DLLs and 11
plugins adds to process start (inferred, not measured).

## 3. Library route in PatternLanguage (verified by reading; pin `fb6ea061`, HEAD in brackets)

| Step | API | Location (pin) |
| --- | --- | --- |
| Runtime | `pl::PatternLanguage runtime;` (ctor registers std builtins, calls `reset()`) | `lib/source/pl/pattern_language.cpp` ctor [HEAD :35-56] |
| Not thread safe | "the runtime is not thread safe in general" → one runtime per thread/process | `lib/include/pl/pattern_language.hpp:47` |
| Includes | `setIncludePaths(std::vector<fs::path>)` | `pattern_language.hpp:202` |
| Data source | `setDataSource(base, size, readFn, writeFn?)` — a lambda over a memory buffer | `pattern_language.hpp:144` |
| Parse only | `parseString(code, source)` → AST (`m_currAST`) | `pattern_language.hpp:86`, `.cpp:156` |
| Parse + evaluate | `executeString(code, source, env, in, checkResult)` → `bool` [`int`] | `pattern_language.hpp:96`, `.cpp:193` [HEAD :205-333] |
| Evaluate | `Evaluator::evaluate(ast)` clears its own state (sections, scopes, heap, patterns) at entry | `lib/source/pl/core/evaluator.cpp:931` [HEAD :1048-1077] |
| Results | `getPatterns(section)`; `getCompileErrors()`, `getEvalError()` | `pattern_language.hpp:273` |
| Reset | `reset()` clears patterns, errors, parser state and **restores evaluator limits/endian** | `.cpp:497-500` |
| JSON | `pl::gen::fmt::createFormatters()` → `FormatterJson::format(const PatternLanguage&)` → `std::vector<u8>` | `generators/include/pl/formatters.hpp`, `formatters/formatter.hpp:67` |
| plcli `format` | one input, one pattern, one output per process; on error `std::exit(EXIT_FAILURE)` inside the helper | `cli/source/subcommands/format.cpp:14,101,107`; `cli/source/helpers/utils.cpp:49,65-78` |
| Example embedder | `example/` builds `pattern_language_example` against `libpl` | `example/CMakeLists.txt:11`, `example/source/*.cpp` |

Reuse across inputs:

- **Supported path**: per file `reset()` → `setDataSource(...)` → `executeString(code, path)` →
  `formatter.format(runtime)`. This is exactly what ImHex does per run (`configureRuntime` calls
  `runtime.reset()` first, ImHex `lib/libimhex/source/api/content_registry.cpp:732-733`; the pattern
  editor then calls `executeString`, `view_pattern_editor.cpp:2041`). It re-preprocesses and
  re-parses the pattern each time. `reset()` is required: `executeString` appends to `m_patterns`
  without clearing (HEAD `.cpp:316`), and only `reset()` clears it.
- **Parse once, evaluate many**: no public API. `executeString` always calls `parseString`. A
  driver could call `parseString` once and then `getInternals().evaluator->evaluate(ast)` per file
  (the `Internals` accessor is `const`, but it holds `unique_ptr`s to non-const objects), reading
  `evaluator->getPatterns()` and running `JsonPatternVisitor` over them. Caveats: pragmas
  (`endian`, `loop_limit`, `pattern_limit`, … in `lib/source/pl/lib/std/pragmas.cpp:27-78`) are
  applied to the evaluator during preprocessing, and `reset()` undoes them, so this path must not
  call `reset()`; it must replicate `executeString`'s data-source/start-address setup
  (HEAD `.cpp:250-270`); and the stock `FormatterJson` takes the whole runtime, so the driver would
  bypass it. Worth it only if the 10-line test below shows parse ≫ evaluate.
- **std library**: everything our patterns import resolves to `builtin::std::…` functions that live
  in libpl itself (`lib/source/pl/lib/std/{core,mem,math,string,…}.cpp`), not in ImHex plugins
  (verified for std.mem/bit/io/math in ImHex-Patterns). No repo pattern uses `hex::` functions
  (`rg 'hex::'` over `research/`: 0 hits). So plcli/libpl + `-I ImHex-Patterns/includes` (or the
  portable install's `includes/`) is enough; ImHex's `configureRuntime` additions are not needed.

Existing bindings (searched `gh search repos`, verified by README): none usable.
`MattMills/py-imhex-pattern` (Cython, "WIP", last push 2024-02-10, 0 stars);
`Calcoph/hexpyt` (translates hexpat to Python, "incomplete"); `sergii-ziborov/ferrosift` (Rust,
"ImHex-style" patterns, alpha, own implementation, not PL-compatible). No batching fork found.

Toolchain (verified present): PL needs C++23 (`lib/CMakeLists.txt:4`), fmt, nlohmann_json, libwolv,
CLI11 (submodules; `--depth 1` clone has them uninitialised). Its Windows CI builds with **MSYS2
mingw64** gcc + lld + cmake + ninja (`.github/workflows/build.yml:12-57`); ImHex 1.38.1 portable is
a MinGW build too (ships `libstdc++-6.dll`, `libgcc_s_seh-1.dll`). On this machine:
`/c/msys64/{ucrt64,mingw64,clang64}/bin/{g++,clang++,cmake,ninja}` (ucrt64 g++ 16.2.0); WSL Ubuntu
g++ 15.2.0, clang 22.1.8, cmake 4.2.3; VS 2022 and VS 18 installed (MSVC not tried). Note:
`command -v g++/cmake/ninja` in Git Bash resolves to **Strawberry** (`/c/Strawberry/c/bin`), which
must not be used (memory "Tool install sources"): call the MSYS2 binaries by full path.

## 4. Options

| Option | How | Throughput (110,065 nNetMsg files) | Basis | Build / risk |
| --- | --- | --- | --- | --- |
| Today | `imhex --pl format` per file, `xargs -P 32` from Git Bash | ~6/s (≈5 h) | measured (brief, samples) | none; fork-bound |
| Quick win | same ImHex, but no subshells per packet, native-ish driver, fewer jobs | ImHex launch 150-450 ms → ~30-80/s at 16-32 jobs (≈25-60 min) | inferred from 2a | edit one script; output unchanged |
| (b) plcli per file | PL's own CLI (no plugin init), still one process per file | Windows spawn + parse, ~20-60 ms → ~300-800/s at 16 jobs, if driven natively | inferred | build plcli at pin; output identical to ImHex (same libpl-gen); still pays per-file spawn and Defender |
| **(a) batch driver** | one process: runtime once, per file `reset` + `setDataSource` + `executeString` + JSON, file list on stdin | parse (unknown, likely ms) + 0.3 ms eval + format → ~200-2,000/s per process; ×8-16 shards → 110k in 1-10 min | eval measured (2b), rest inferred | ~150 lines C++ against libpl/libpl-gen at pin; mingw64 |
| (a') parse once | as (a) but `parseString` once, `evaluator->evaluate(ast)` per file | ~2,000-3,000/s per process | inferred | uses internals; pragmas/reset caveats (§3); only if parse dominates |
| (c) ImHex plugin subcommand | `IMHEX_PLUGIN_SUBCOMMANDS()` (`lib/libimhex/include/hex/plugin.hpp:158-163`) adding `--pl-batch`, built with the portable `sdk/` (`liblibimhex.dll.a`, MinGW) or the Plugin Template | as (a), plus one ~0.3 s plugin init per run | inferred | must match ImHex 1.38.1 ABI exactly; breaks on ImHex upgrade; no gain over (a) since no `hex::` functions are needed |
| (d) server mode | ImHex network endpoint `pattern_editor/set_code` (`plugins/builtin/source/content/communication_interface.cpp:10`) or the `--mcp` server (HEAD) | low; one GUI instance, one provider at a time | inferred | GUI-bound, single instance (global mutex, `main/gui/source/messaging/windows.cpp:71-89`); unsuited |
| (e) container input | concatenate packets into one file per type, a wrapper pattern with sections per packet, one ImHex run | high, but one JSON for all | inferred | rewrites patterns (`std::mem::size() - $` padding, `@ 0x00`), pattern limit 0x100000, output split needed; not recommended |

## 5. Build plan for an implementer (option a)

1. Source: `git -C D:/GitHub/WerWolv/PatternLanguage` is a read-only reference clone; build from a
   separate checkout, e.g. `D:/build/pl-1.38.1` (or a tool dir the coordinator names):
   `git clone https://github.com/WerWolv/PatternLanguage D:/build/pl-1.38.1 && git -C … checkout
   fb6ea061f7c8b66ed94b44ff1d3a10ee63a82612 && git -C … submodule update --init --recursive`.
2. Driver source (owned file in this repo, e.g. `tools/plbatch/plbatch.cpp` + `CMakeLists.txt`
   that `add_subdirectory`s the PL checkout with `LIBPL_ENABLE_CLI=OFF` and links `libpl`
   `libpl-gen`). Interface mirrors `imhex --pl format`: `plbatch --pattern P -I DIR... --out-root
   DIR --in-root DIR < list` (NUL- or newline-separated relative paths). Per file: read into a
   `std::vector<u8>`, `runtime.reset()`, `setIncludePaths`, `setDangerousFunctionCallHandler(→false)`,
   `setDataSource(0, size, memcpy-lambda)`, `executeString(patternText, patternPath)`; on success
   `FormatterJson{}.format(runtime)` → write `out.tmp` → rename; on failure write
   `getCompileErrors()`/`getEvalError()` to `.json.err`; print `ok|FAIL rel` lines exactly like
   `imhex-export.sh` so its counting stays. Never `std::exit` per file (the plcli helper does).
3. Build with MSYS2 mingw64 by full path (not Strawberry): `/c/msys64/mingw64/bin/cmake -G Ninja
   -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-fuse-ld=lld -DLIBPL_ENABLE_CLI=OFF …` then
   `ninja`; static-link libstdc++ (`-static`) or copy the mingw64 runtime DLLs next to the exe.
   Requires the `mingw-w64-x86_64-lld` package (check with `command -v`).
4. Includes: `-I research/03040008/packets/include -I E:/Software/imhex-1.38.1-Windows-Portable-NoGPU-x86_64/includes`
   (the std library ImHex 1.38.1 ships; ImHex's `--pl` adds its `includes` paths the same way,
   `command_line_interface.cpp:366-367`).
5. Wire `packets/imhex-export.sh` to use `plbatch` when present: build the file list in bash
   (no per-file forks), split into `JOBS` shards, run one `plbatch` per shard.
6. Acceptance: on the 20 sample files and a 1,000-file sample per nNetMsg type, `plbatch` JSON is
   byte-identical to `imhex --pl format` JSON (`cmp`); failures match; record throughput with
   `hyperfine` and the counts in the receipt.

### 10-line tests that would settle the open claims

- Parse vs evaluate share: in the driver, time `parseString` and the full `executeString` over the
  20 files (`std::chrono` around each) — decides whether (a') is worth its caveats.
- Byte compatibility: `cmp` plbatch vs `imhex --pl format` output on the 20 samples.
- Fork contention: rerun the 50-subshell loop when no export runs; expected tens of ms per fork,
  confirming contention rather than a slow machine.

## Quick win (no build, inferred gain)

In `imhex-export.sh`: compute `dirname` and the Windows path with parameter expansion (one
`cygpath -w` of the roots at startup, then string concatenation), create all output directories
once before `xargs`, and drop the per-packet `rm`; that leaves `bash -c` + ImHex + `mv` per packet.
Use ~8-16 jobs, not 32. Not measured; the per-file ImHex start (150-450 ms) remains the floor.

## Contradictions and gaps

- Brief's "about 40 packets/s at 32 jobs in P3's sample" vs ~6/s later: consistent with the fork
  explanation if P3's sample ran with fewer concurrent shells or on a smaller set (not checked).
- All timings were taken under the concurrent export; a quiet-machine rerun of `bench1.sh` is
  **not run**.
- Parse cost of the 962-line `nNetMsg.hexpat` is **not measured** separately (below noise).
- MSVC build of PL: **not tried**. plcli build: **not run** (brief: prototype nothing).
- ImHex line references are at HEAD `34483cb`, not the 1.38.1 tag; PL references are at the pin
  where marked and at HEAD in brackets.
