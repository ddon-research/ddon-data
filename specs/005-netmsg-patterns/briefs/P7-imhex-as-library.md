005 P7: run ImHex patterns as a library, not one process per packet

Question/objective: `packets/imhex-export.sh` starts one `imhex.exe --pl format` process per packet
file (ImHex 1.38.1 portable, `/e/Software/imhex-1.38.1-Windows-Portable-NoGPU-x86_64/imhex.exe`,
`xargs -P`). P3's export of the four nNetMsg packet types (110,065 files) has run over 2 h: about
40 packets/s at 32 jobs in P3's sample, about 6/s observed later (12:01-12:26, while
`tasklist` showed one imhex.exe). Sam (2026-11-01) wants the pattern language used like a library,
parsing a pattern once and evaluating it over many inputs in one long-lived process, for future
exports over all packet types and `client/` resources. Find the way and recommend one.

Do:
1. Clone (AGENTS.md "Clone what you analyse": `git clone --depth 1 --filter=blob:none` into
   `D:/GitHub/WerWolv/<repo>`, or `git pull --ff-only` if present): PatternLanguage, ImHex,
   ImHex-Patterns, ImHex-Plugin-Template (https://github.com/WerWolv/...). Append one line per clone
   to `research/external-references.jsonl` (format in `research/external-references.md`; the file
   has other uncommitted lines: append only). Clones are read-only reference: never build them in
   place.
2. Measure where the time goes now, on 20 files of one type (e.g.
   `C2S_PARTY_SEND_BINARY_MSG_NTC`), output to your scratch folder, never `packets/`: wall time of
   one `--pl format` run, how much is process start, pattern parse with the `include/nNetMsg.hexpat`
   + std imports, evaluation, JSON output; and why the observed rate fell to about 6/s (job count,
   disk, the script). Use `hyperfine` if present, else `time`.
3. Map the library route in PatternLanguage: the `pl::PatternLanguage` runtime API (parse once,
   set the data source, execute, read the patterns, the JSON formatter `plcli` uses), whether the
   parsed AST or runtime can be reused across inputs or must be re-run, how `plcli` (the PL repo's
   CLI) is built and whether it accepts many inputs; any existing bindings (Python, Rust, C) or
   forks that batch. Note the build toolchain it needs on this machine (C++ standard, compiler:
   MSYS2 MinGW / clang / MSVC / WSL gcc), and the version matching ImHex 1.38.1's pattern language.
4. Compare the options with expected throughput: (a) a small C++ batch driver linking libpl
   (pattern once, N files, JSON per file), (b) a `plcli` per file, (c) an ImHex plugin or script,
   (d) a server mode, (e) anything better you find. Prototype nothing beyond reading; if a 10-line
   test would settle a claim, say what it is.

Owns: only `specs/005-netmsg-patterns/research/P7-imhex-as-library.md` (the report) and the
appended lines in `research/external-references.jsonl`; clones under `D:/GitHub/WerWolv/`; a scratch
folder under your temp dir. Never touch: `packets/` (an export is still writing
`packets/decrypted_json`; read `packets/decrypted_raw` only), `research/03040008/packets/`, client/.
Libraries: the PatternLanguage library itself; no own tooling in this package.
Done: the report has the measurements (command, input, counts), the API map with file:line in the
clones (commit hashes), the option table with throughput estimates marked measured or inferred, a
recommendation, and the build plan an implementer would follow. Final message: the report path and
at most 15 lines.
Stop: budget 45 min of work time. Stop and report if cloning fails.
Base: 3f9c147b32.
