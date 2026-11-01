# plbatch

A batch driver for ImHex patterns: one process runs one pattern over many files and writes one JSON
file per input, byte-identical to `imhex --pl format`. `packets/imhex-export.sh` uses it when it is
built. Background and the measurements behind the design:
`specs/005-netmsg-patterns/research/P7-imhex-as-library.md`.

## Why

`imhex --pl format` per packet costs 150-450 ms of process start and plugin init, and the old
export script added about eight MSYS process creations per packet; P3's export ran at ~6 packets/s.
plbatch links PatternLanguage (`libpl`, `libpl-gen`) directly, keeps one runtime per process and
never forks per file.

## Build

```sh
bash research/imhex/plbatch/build.sh
```

- Fetches PatternLanguage at **`fb6ea061f7c8b66ed94b44ff1d3a10ee63a82612`** (tag `ImHex-v1.38.1`,
  the commit ImHex 1.38.1 embeds) with its submodules into `research/imhex/plbatch/build/pl-src`
  (gitignored). Do not move the pin: newer PatternLanguage changes the JSON string escaping and
  the `executeString` return type. Never build in the reference clone
  `D:/GitHub/WerWolv/PatternLanguage`.
- Compiles with MSYS2 **mingw64** by full path (`/c/msys64/mingw64/bin`: gcc 16.2.0, cmake 4.4.4,
  ninja 1.13.2, lld), never the Strawberry `g++`/`cmake` on `PATH`. Override with `MINGW_BIN`.
  Missing tools: `pacman -S mingw-w64-x86_64-{gcc,cmake,ninja,lld}`.
- Output `research/imhex/plbatch/build/bin/plbatch.exe`, statically linked (imports only
  `KERNEL32.dll` and `msvcrt.dll`), so it runs from any shell without DLLs beside it.

## Use

```sh
plbatch --pattern P [-I DIR]... --in-root IN --out-root OUT [--force] [--time] < list
```

- `list`: newline-separated paths relative to `IN`.
- For each `rel`: `OUT/rel.json`, written to `OUT/rel.json.tmp.<pid>` and renamed into place; on
  failure no JSON and `OUT/rel.json.err` with the compile or evaluation error and the stack trace.
  Paths of 260+ characters fail like the export script's guard.
- stdout: `ok   rel`, `skip rel` (JSON exists, no `--force`) or `FAIL rel (see <err>)`, one line
  per file. Exit 0 when nothing failed, 1 when a file failed, 2 on a usage error.
- `-I`: pass the ImHex std library (`<imhex>/includes`, which `imhex --pl` adds by itself) and the
  pattern includes (`research/03040008/packets/include`).
- `--time`: also parse each pattern once more on its own and print parse, execute and format
  totals to stderr (it doubles the parse work: measurement only).

Per file the driver does what ImHex does per run: `reset()`, dangerous functions refused, include
paths, `setDataSource` over the file in memory, `executeString(pattern, patternPath)`, then
`FormatterJson::format()`. Nothing calls `std::exit` per file.

## Verification (2026-11-01, client 03040008 packets)

`imhex.exe` 1.38.1 (portable NoGPU) `--pl format` against plbatch, same patterns, `-I
research/03040008/packets/include` (plbatch also `-I <imhex>/includes`), byte comparison of every
output: 3,028 files (1,000 each of `C2S_PARTY_SEND_BINARY_MSG_NTC`, `S2C_LOBBY_LOBBY_DATA_MSG_NTC`,
`C2S_LOBBY_LOBBY_DATA_MSG_REQ`, every 1,000th-ish file of the sorted `packets/decrypted_raw` list;
all 8 `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC`; P7's 20 samples): 3,028 identical, 0 differing, 0
failures on either side. A deliberately truncated packet failed in both, through
`packets/imhex-export.sh` with each engine, and the two output trees were otherwise identical. The
`.err` text differs (plbatch adds the stack trace from the log).

Throughput (hyperfine 2.0.0, `-N`, contended 32-CPU machine): plbatch over 100 packets 2.837 s ±
0.111 (5 runs, ~35 packets/s per process); `imhex.exe --pl format` over one packet 534.0 ms ± 317.0
(15 runs, ~1.9 packets/s per process, before any shell overhead).

## Cost per file

Measured with `--time` over 1,000 packets per nNetMsg type: parse (preprocess + parse + validate of
the ~1,000-line `nNetMsg.hexpat` and its std imports) ~24-25 ms, evaluation ~0.5-0.7 ms, JSON
~0.05 ms. Parsing dominates; so one process does about 40 files/s and the export scales by shards.
Parsing once and evaluating many (`parseString` once, `evaluator->evaluate(ast)` per file) would
give roughly 1,000 files/s per process, but uses PatternLanguage internals and must replicate the
pragma and data-source setup that `executeString` and `reset()` do (P7 section 3): not done.
