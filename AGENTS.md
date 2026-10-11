# DDON Data agent guide

Canonical instructions for every coding agent in this repository. `CLAUDE.md` imports this file;
`research/knowledge-graph/AGENTS.md` adds rules for that subproject. Human-facing overview:
`readme.adoc`.

This repository is the aggregated **output** of Dragon's Dogma Online (DDON) reverse-engineering
tools: extracted client resources, disassembler exports, decrypted network traffic, client patches,
and research notes. Most content is produced elsewhere on this machine and copied or written here.
Treat it as versioned evidence, not as source code.

## Facts

- Remote `git@github-ddon:ddon-research/ddon-data.git`, branch `main`. Season 1 and 2 data live in
  sibling repos `D:\ddon-data-s1` (client 01010004) and `D:\ddon-data-s2` (client 02030004,
  `recompilation/`). This repo holds Season 3 (client **03040008**) plus the PS4 **02020005** export.
- Versions are client build numbers (`03040008`, `02030004`, `PS4_02020005`). Always name the
  build when reading, writing, or comparing data.

| Path | Contents | Producer |
| --- | --- | --- |
| `client/03040008/` | ~173k JSON files mirroring the `nativePC/rom` tree, plus `*-resources.csv`, `*-headers.csv`, `*-extensions.txt` summaries | `D:\ddon-extractor` (Java CLI); input `D:\DDON_03040008`, translations `D:\DDON-translation\gmd.csv` |
| `binaries/PS4_02020005/` | IDA export `DDOORBIS.elf.h` + `DDOORBIS_{1,2,3}.elf.c` (split for size) | IDA 9.3 dump of `D:\research\DDON-binaries\IDA9.3\PS4_DDON_02020005_2016_12_21\DDOORBIS.elf` |
| `binaries/ANDROID_1500/` | Decompiled Unity C# and `path_id_map.json` | `D:\research\DDON-binaries\Android` tools |
| `packets/` | `encrypted_streams/`, `decrypted_{raw,json,annotated}/`, `keys/`, packet statistics | `D:\research\DDON-pcaps` toolchain: `ddon_pcap_split`, `ddon_common_key_bruteforce`, `Arrowgene.Ddon.Cli` |
| `patches/` | radare2 `.r2` patch scripts + `.json` metadata for Windows `DDO.exe` builds | Hand-authored; see `patches/README.md` |
| `research/<build>/` | ImHex patterns `r<Type>-pattern.cpp`, packet patterns, notes, DTI dumps | Hand-authored |
| `research/03040008/flags/` | `ddon-flags` Python project (quest/layout flag investigation) and `generated/` reports | This repo |
| `research/knowledge-graph/` | `ddon-knowledge-graph` Python project (Neo4j evidence graph + MCP), own Spec Kit project | This repo |
| `research/ghidra/`, `research/ida/`, `research/pharos/` | PyGhidra headless analyzer, IDA helpers, Pharos OOAnalyzer (Docker) | This repo |
| `plan/` | Older flag-investigation plans | Historical |

- **Disassembler databases** (inputs, never copy them here): `D:\research\DDON-binaries\` holds
  `IDA9.3\` (packed `.i64` + `.c`/`.h` exports per build), `IDA9.5\` (live databases, see below),
  `Ghidra11.4\` projects, and raw `PC\`, `PS4\`, `PS3\`, `PSV\`, `Android\` dumps. In the canonical
  PS4 folder, `DDOORBIS.elf.llvmdwarfdump.zst` (1.1 GB) must be streamed, never decompressed.
- **Game clients** (inputs): `D:\DDON_01010004`, `D:\DDON_02030004`, `D:\DDON_02030010`,
  `D:\DDON_03040008`, each with `nativePC/rom`.
- **Readers of this repo**: `D:\ddon-explorer-server` (reads `client/03040008`),
  `D:\DDON-translation` tools (read `client/03040008/quest`), the Arrowgene server docs, and
  DDOn-Tools hex patterns (read `research/02030004/`). Moving or renaming those paths breaks them.
- **Related tools**: `C:\ddon-dwarf-reconstructor-rust` rebuilds C++ for resource classes from the
  PS4 DWARF and reads `D:\ddon-data-s2\client\02030004` as an oracle; `D:\ddon-dwarf-reconstructor`
  is the archived Python predecessor, still used by knowledge-graph enrichment. Server emulator:
  `D:\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline` (fork) and its `.Upstream` clone.

## Evidence rules

- Treat source-derived facts as immutable, versioned observations: never replace an address,
  layout, or relationship with an inference. Semantic conclusions must cite evidence and stay
  separately revisioned; mark an inference as inferred.
- Authority by fact type, not by producer: DWARF/ELF for declared class structure and field layout,
  pinned disassembly for instruction coverage. IDA, Ghidra, and reconstructor observations stay
  distinct and cross-validated. ddon-extractor JSON corroborates layouts; it does not prove them.
  Missing decompiler output is a coverage gap, not negative evidence.
- Season 2 debug symbols (PS4 02020005) describe Season 3 PC formats only approximately: verify
  per format before carrying a layout across seasons or platforms.
- A check that did not run is "not run", never "passed". Report results with the command, the
  input/output identity (build, path, hash), and counts.

## Preservation and git hygiene

- This is an intentionally active research worktree with large staged and unstaged changes
  (e.g. full `client/03040008` re-extractions). Preserve unrelated changes; never bulk `revert`,
  `checkout --`, `clean`, or `reset` without listing exact paths and asking first.
- `client/` and `packets/` hold hundreds of thousands of files: never list or `git diff` them
  unbounded. Use `git diff --stat -- <subdir>`, `rg -c`, `fd -d 2`, and `dust`.
- Never commit credentials, `.env` files, Neo4j volumes, game assets (`.arc`, `.pkg`, executables,
  disassembler databases), or runtime caches. Do keep deterministic, reproducible caches, SQLite
  indexes, source inventories, and bundles locally; routine cleanup must preserve them.
- Bind durable derived artifacts to source content, producer/schema version, and output-affecting
  configuration; validate before reuse and publish atomically. Record source revisions and SHA-256
  hashes at ingestion boundaries. Rebuild or purge only the affected artifact, explicitly.
- Commit only when asked. Commit subjects are short, imperative, sentence case, no prefix
  ("Update client dump", "Fix EST param parsing order").

## Shell tools

The agent shell is **Git Bash**; WSL `Ubuntu` 26.04 is available for Linux-only tooling. Prefer
POSIX shell and Linux tools over PowerShell; use PowerShell only for Windows-only tasks with no
POSIX equivalent.

- Write automation as bash `.sh` scripts, not `.ps1` or `.bat`. Existing PowerShell helpers
  (`research/knowledge-graph/scripts/*.ps1`) stay until replaced. Scripts start with
  `set -o errexit -o nounset -o pipefail`, check every external command with `command -v` before
  use, and never follow a step that can fail with a destructive one (`rm -rf`) unguarded.
- Git Bash lacks some tools (notably `rsync`). Use MSYS2 (`/c/msys64/usr/bin/rsync`) or WSL
  (`wsl.exe -d Ubuntu -e rsync ...`) for them; never assume a command exists.
- Native Windows programs (ImHex, Arrowgene CLI) fail on paths of 260+ characters; keep output
  trees short.
- Search with `rg` (`git grep -n` for tracked files only), find with `fd`, replace with `sd -F`
  (keeps CRLF; never `sed -i` a CRLF file), measure with `dust`, JSON with `jq`, compressed dumps
  with `zstd -dcqq <file> | rg -m1 ...`. Limit output inside the tool (`rg -c`, `rg -m N`,
  `--max-columns`) rather than piping huge output to `head`.
- Paths: Git Bash uses `/d/ddon-data/...`; native Windows programs take `D:/...`; WSL sees
  `/mnt/d/...`. Set `MSYS_NO_PATHCONV=1` when passing a `/`-prefixed argument to a native program.
  From a native program, `bash` means WSL's bash.
- Run WSL commands as `wsl.exe -d Ubuntu -e bash -lc '<cmd>'`. Prefer WSL for heavy Linux
  pipelines over `/mnt/d` only when Git Bash lacks the tool; cross-filesystem I/O is slow.
- Python: each project uses its own `uv` environment (`uv run` from the project directory) and
  CPython 3.14. Run ad-hoc scripts as `python -X utf8 -I <script>`. The root `.venv` is a legacy
  PyGhidra stub environment; do not install into it.
- No TTY: leave `PAGER`/`GIT_PAGER` unset and avoid interactive or ANSI-only tools.
- Available in Git Bash: `rg fd sd jq dust zstd xxd tshark radare2 uv gh docker`. ImHex CLI is
  not on `PATH`; say so instead of assuming pattern validation ran.

## Workflows

- **Client extraction**: run ddon-extractor against `D:\DDON_<build>` with `gmd.csv`
  (`ddon-extractor resource -p true -o -m -f json -u -x D:\DDON_03040008 D:\DDON-translation\gmd.csv <out>`;
  see `D:\ddon-extractor\README.md`), then replace `client/<build>/`. Review the change with
  `git diff --stat` per resource type before committing.
- **Resource format research**: identify the extension (`research/find-unsupported-extensions.sh`),
  get the class layout from DWARF and its `load`/`save` methods (IDA MCP or
  `research/ghidra/headless-scripts/run_ghidra_analysis.sh dwarf|function <name> DDOORBIS.elf`),
  write `research/<build>/r<Type>-pattern.cpp`, validate with
  `imhex --pl format --pattern <pattern> --input <file>` (`research/validate_pattern.sh`), and
  cross-check against the extractor JSON. See `research/README.adoc`.
- **Packets**: `packets/keys/decrypt-pcapng-streams-all-in-one.sh <capture.pcapng|dir> [out]`
  needs `tshark`, `Arrowgene.Ddon.Cli`, and `ddon_common_key_bruteforce`. Key search uses expected
  plaintext `0100000234000000` (login) and `2C00000234000000` (game-select/game), bounded to
  about 15k depth and 40 s per stream. `packets/decrypt-annotate-streams.sh` re-annotates streams
  in parallel (`packets/README-decrypt-annotate-streams.adoc`). Exports need the locally patched
  Arrowgene CLI described in that README (error responses stop after `Error`); split dumps over
  50 MiB with `packets/split-annotated.sh` and decode structures with `packets/imhex-export.sh`.
- **Patches**: apply with `radare2 -qnw -i <patch>.r2 <target>.exe`; keep the SHA-256 chain in
  each `.json` correct (`patches/README.md`).
- **IDA**: the live IDA 9.5 databases are
  `D:\research\DDON-binaries\IDA9.5\PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.i64` and
  `D:\research\DDON-binaries\IDA9.5\PS4_DDON_02020005_2016_12_21\DDOORBIS.elf.i64`. Query them
  read-only unless asked to annotate; never overwrite them from a headless copy.

## Conventions

- Resource classes use the `r<Name>` prefix (`rItemList`, `rLayout`); enums keep their DWARF names
  (`rItemList_ITEM_CATEGORY`). Each file extension maps to one resource class.
- ImHex patterns: `r<ResourceType>-pattern.cpp`, enums from debug symbols, `#pragma pattern_limit`
  for large files, structure following the binary layout exactly.
- CSV exports: `<build>-<type>.csv` (`03040008-headers.csv`); hex dumps as `00000000: 0100 0000 ....`.
- Cross-source keys: `NpcId`, `ItemId`, `QuestId`, stage numbers; positions as `{X, Y, Z}`.

## Planning with Spec Kit

Spec Kit 1.1.3 (bash scripts, Claude integration) is installed in two projects. The scripts use the
nearest `.specify/` above the current directory, or `SPECIFY_INIT_DIR` when set.

- **Repo root** (`.specify/`, features in `specs/NNN-slug/`): repo-wide work such as extraction,
  packet, patch, or flag-investigation features. Constitution: `.specify/memory/constitution.md`.
- **Knowledge graph** (`research/knowledge-graph/.specify/`, features in
  `research/knowledge-graph/specs/`): run Spec Kit commands from that directory or with
  `SPECIFY_INIT_DIR=research/knowledge-graph`. `specs/001-pre-extraction-knowledge-graph/` is the
  active feature; `specs/README.md` maps 002-004.

When a folder has Spec Kit artifacts, they are part of the working loop, not follow-up
documentation:

1. Identify the active feature and read its `spec.md`, `plan.md`, and `tasks.md` before
   substantive changes.
2. Update `research.md`, `data-model.md`, `quickstart.md`, and `contracts/` when a change alters
   scope, architecture, artifact flow, or operator commands.
3. Record task state and blockers in `tasks.md` in the same session; do not leave progress only in
   chat.
4. Keep features separate; do not mix work from different features in one directory.

Use the steps that add value and skip the rest. Measure before optimizing, and optimize measured
hot paths first.

## Subprojects

- `research/knowledge-graph/`: read its `AGENTS.md`. Gates from that directory: `uv sync --all-groups`,
  `uv run pytest`, `uv run ruff check --no-fix .`, `uv run mypy src tests`. Neo4j and
  real-artifact tests are opt-in; do not create or remove persistent Docker state unless the task
  requires it. Generated wiki context may be rebuilt; authored semantic narrative must survive
  rebuilds, carry evidence IDs, and never mutate deterministic graph properties.
- `research/03040008/flags/`: read its `README.md` and `TODO.md`. CPython 3.14 only, environment
  `.venv-cpython314` (setup in the README); tests:
  `.venv-cpython314/Scripts/python.exe -m unittest discover -s tests -v`. Regenerating `generated/` rewrites thousands of
  reports: run it only when asked.
- `research/ghidra/headless-scripts/`: configure `.env` from `.env.template` (PyGhidra path).
