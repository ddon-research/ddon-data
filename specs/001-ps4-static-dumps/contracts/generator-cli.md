# Contract: `generate-elf-dumps.sh` and the `elf-dumps/` layout

## Command line

```text
binaries/PS4_02020005/elf-dumps/generate-elf-dumps.sh [--only <id-glob>] [--skip-local] [--dry-run]
```

**Revision 2026-10-11 (after the handover closed):** the generator publishes only the preferred
dump per category, the derived files and the local-only stand-ins. Intermediate inputs (`role:
intermediate`, `storage: staging`, `file: null`) are recorded but not published, and always run
so that `--only` can rebuild their consumers. `--compare-sdks`, the comparison runs, the
supplements and the oracles moved to `elf-dumps/archive/` together with the generator that made
them (`archive/generate-elf-dumps.full.sh`). The layout below is the original one; the current
layout is in `elf-dumps/README.adoc` § 3.

| Option | Effect |
|---|---|
| (none) | Generates every dump and derived file in the catalogue, including local-only dumps. |
| `--only <glob>` | Regenerates only the dump ids that match, plus everything derived from them. The other manifest entries are kept. |
| `--skip-local` | Skips the local-only dumps. Their manifest entries stay as they are. Derived files that need them are skipped too. |
| `--dry-run` | Prints the planned commands and output paths, checks the tools and the input hash, and writes nothing. |
| `--verify` | Re-hashes every published file (decompressing `.zst`) against the manifest; writes nothing. |
| `--exec <tool> <args…>` | Runs one tool on the staged input copy and prints its output; used for fact checks. |
| `--publish-run <dir>` | Re-checks the input snapshot and publishes a finished staging run whose publish step was interrupted. |

**Environment** (default in brackets):

- `DDON_PS4_ELF` [`D:/research/DDON-binaries/IDA9.3/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf`]
- `SCE_SDK_ROOT` [`D:/SCE/ORBIS SDKs`]
- `LLVM_BIN` [`C:/msys64/ucrt64/bin`]
- `DUMP_TIMEOUT`, `LOCAL_TIMEOUT` [unset] (seconds per tool run; unset means no time limit, the default since 2026-10-11)

**Exit status**:

- **0**: every entry has `status: ok`.
- **1**: precondition or guard failure: a tool is missing, the input hash is wrong, or the input
  folder changed. Nothing is published.
- **2**: at least one entry is `failed` or `timeout`. Those entries are recorded and everything else
  is published.

## Guarantees

1. Before any work, the script checks every tool and helper: `[ -x ]` for each native executable,
   and `command -v` for every name in its single `REQUIRED_COMMANDS` array (at least `jq zstd
   sha256sum sed rg xxd cut sort comm tee wc timeout uv cp mv ln`). It also checks the input's
   SHA-256 and size.
2. The script copies the input once to `.staging/input/DDOORBIS.elf` and verifies the copy's hash.
   Tools run with the current directory `.staging/input/` and argument `DDOORBIS.elf`; no tool runs
   in the input folder. Tools that read the input never get an output-path option (`orbis-bin -o`
   is forbidden); `llvm-objcopy` writes only inside staging.
3. Output is streamed: tool → `sed 's/\r$//'` → `tee >(sha256sum) >(wc -lc)` → file or zstd. The
   storage class comes from the measured size (local-only dumps are known up front and streamed
   straight into `zstd -10 --long=27 -T0`). Each tool's exit code is captured with `|| rc=$?`, so a
   failure never aborts the run.
4. The script snapshots the input folder (name, size, mtime and SHA-256 of every file) before and
   after the run. If the snapshots differ, the script exits 1 and publishes nothing.
5. If a dump's content hash matches its existing manifest entry, the published file is left alone.
   A `.zst` therefore never changes just because zstd was rerun.
6. Publishing moves each changed file into place, then the manifest last. The set is not atomic
   as a whole: if a run is interrupted while publishing, the old manifest still describes the old
   files, and `generate-elf-dumps.sh --verify` (re-hash every published file against the manifest)
   reports the mismatches; rerunning the generator repairs them.
7. Ad-hoc commands (fact checks, samples) use `generate-elf-dumps.sh --exec <tool> <args...>`, which
   runs the tool on the staged copy with the same guard.

## Layout

```text
binaries/PS4_02020005/elf-dumps/
├── README.adoc                 # index category → id → file; storage rule; regenerate; search tips; old-dump coverage
├── COMPARISON.adoc             # per-category ranking, SDK verdict, fact check results
├── LOSSES.adoc                 # L-NN register (tool-loss / producer-quirk)
├── handover/
│   ├── spec.md                 # draft spec for ddon-dwarf-reconstructor-rust (unnumbered, ddon-data-P<n>)
│   └── research.md             # evidence, reconstructor coverage at commit <sha>
├── generate-elf-dumps.sh
├── tools/elfslice.py           # PEP 723 uv script: byte slices, debug_line copy, hashes, joins
├── categories.tsv  facts.tsv  manifest.jsonl  .gitattributes
├── tool-help/<tool>.txt
├── headers/  symbols/  relocations/  sce/  strings/  stack/  registers/  dwarf/
├── derived/                    # kind: derived (line tables, gap list, rebased strings, string refs, hashes, register usage)
├── oracles/                    # small TSV/JSONL extracts for Linux CI
├── compare/                    # sdk-matrix.tsv, differing SDK outputs ≤ 10 MB, GNU sample
├── local/                      # gitignored: everything.orbis-bin, dwarf-info, disassembly (llvm, orbis)
└── .staging/                   # gitignored: input/ (verified copy), run directories, snapshots
```

The longest path is about 95 characters.
