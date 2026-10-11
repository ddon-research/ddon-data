# Implementation Plan: PS4 02020005 static ELF dump set and reconstructor handover

**Branch**: `001-ps4-static-dumps` (no git branch; work on `main`) | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-ps4-static-dumps/spec.md`

## Summary

A bash generator writes provenance-bound static dumps of `DDOORBIS.elf` into
`binaries/PS4_02020005/elf-dumps/`. Each category uses the best tool from research R4:

- SDK 12 `orbis-bin` covers the SCE-specific data: headers, dynamic table, dynlib, NIDs, SCE
  relocations, stack sizes, `.sceversion`, and its own addr2line.
- LLVM 23 covers DWARF, symbols, unwind and register rules, hex dumps and disassembly.
- `orbis-strings` extracts the ASCII and UTF-8 string constants.

One stdlib Python helper does byte-level work that no tool does correctly:
- copying out the non-contiguous `.debug_line` tables;
- section and segment hashes;
- the RELRO string-reference join;
- register-usage counts.

The SDK binutils and GNU outputs serve as comparison evidence only. The documents are:
- `COMPARISON.adoc`, including the SDK-version matrix;
- `LOSSES.adoc`;
- a handover package for ddon-dwarf-reconstructor-rust in its own Spec Kit shape, with small
  committed oracles.

Dumps larger than 50 MB compressed stay local-only. The input folder is only read, once, to make
a hash-verified copy in staging; every tool reads that copy.

## Technical Context

**Language/Version**:
- bash (Git Bash, `set -o errexit -o nounset -o pipefail`);
- one stdlib-only Python 3.14 helper, a PEP 723 script run with
  `uv run --no-project --python 3.14 --script`;
- `jq`, `zstd`, `sd`, `sha256sum`.

**Primary Dependencies** (research R2):
- `D:/SCE/ORBIS SDKs/<2.500|3.500|8.000|12.000>/host_tools/bin/orbis-{bin,objdump,readelf,nm,strings}.exe`;
- `C:/msys64/ucrt64/bin/llvm-{readelf,readobj,objdump,dwarfdump,nm,objcopy}.exe` (23.1.3);
- GNU binutils 2.47 (one comparison sample).

**Storage**:
- committed `.txt` up to 10 MB;
- committed `.txt.zst` up to 50 MB (about 40 MB in total);
- `local/` otherwise, gitignored, about 2.2 GB as zst.

**Testing**: the steps in quickstart.md: manifest coverage and hash checks, a rerun diff, expected
counts, the registered fact check, the input snapshot diff, and the loss→proposal mapping.

**Target Platform**: Windows 11 with Git Bash. Native tools take `D:/...` paths, and
`MSYS_NO_PATHCONV=1` is set.

**Project Type**: a data-generation script plus documentation, in a data repository.

**Performance Goals**:
- a full run in under 30 minutes, dominated by `orbis-bin -de` (~5 min), `--debug-info -v`
  (*measure*), and `llvm-objdump -d -l` (37 s);
- `--skip-local` in under 5 minutes;
- `--compare-sdks` adds a few minutes.

**Constraints**:
- Only read the IDA9.3 PS4 folder (FR-001).
- Make no edits in the reconstructor or ddon-hook.
- Keep paths under 260 characters.
- Commit no file over 50 MB.
- Stream `-de` (4.2 GB raw) straight into zstd.

**Scale/Scope**: about 45 committed files, 4 local-only dumps, about 60 categories.

## Constitution Check

*Gate before Phase 0; re-checked after Phase 1.*

| Principle | How the plan satisfies it | Status |
|---|---|---|
| I. Source-derived facts immutable | Tool dumps are never edited. Joins, slices and reshaping happen only in `derived/` with `kind: derived`, named inputs and an `inferred` flag (FR-014). Bytes are copied, never altered (R7). | Pass |
| II. Authority by fact type | Tool outputs stay distinct. The ELF bytes decide disagreements. IDA is a secondary cross-check and does not count as independent for DWARF facts (FR-013). | Pass |
| III. Builds and producers explicit | The manifest records the tool path, version and hash, argv, input hash, the expected and actual exit, and the zstd and Python versions. | Pass |
| IV. Reproducible, streaming, preserving | One script. Output is staged, then moved atomically, with the manifest last. Unchanged content keeps its files. Old dumps are kept. The input is guarded by a hash snapshot. | Pass |
| V. Honest verification | Failures and timeouts are recorded with their status. Every published count is re-measured. Facts are registered before checking. | Pass |
| Repo constraints | The SCE dumper itself is a producer change, so it is handed over to the reconstructor. Automation is POSIX shell plus a uv-managed (PEP 723) Python script on CPython 3.14. | Pass |

Post-design re-check: pass. Complexity: the single Python helper is justified in research R13.

## Project Structure

### Documentation (this feature)

```text
specs/001-ps4-static-dumps/
├── spec.md  plan.md  research.md  data-model.md  quickstart.md
├── contracts/manifest.schema.json  contracts/generator-cli.md
├── checklists/requirements.md
└── tasks.md                 # /speckit-tasks
```

### Repository changes

```text
binaries/PS4_02020005/elf-dumps/    # new; layout in contracts/generator-cli.md
.gitignore                          # + binaries/PS4_02020005/elf-dumps/{local,.staging}/
AGENTS.md, readme.adoc              # point to elf-dumps/ (FR-012)
```

**Structure Decision**: the dump folder sits next to the existing IDA exports in
`binaries/PS4_02020005/`. The generator, helper, and documents live inside it, so the data and its
recipe travel together.

## Phases

### Phase A: Generator foundation (FR-004, FR-005)

1. Write the script skeleton:
   - parse the options;
   - check every tool (`[ -x ]`) and every name in one `REQUIRED_COMMANDS` array (`command -v`),
     and the input hash and size;
   - copy the input once to `.staging/input/DDOORBIS.elf` (reused while its hash matches) and
     verify the copy (FR-015);
   - take the input snapshot (every file: name, size, mtime, SHA-256);
   - create `.staging/<run>/`;
   - write a `run.meta` entry with the zstd and Python versions and the script hash.
2. Write `run_dump <id> <categories> <role> <expected_exit> <tool> <args...>`. It:
   - runs the tool with the current directory `.staging/input/` and no time limit unless
     `DUMP_TIMEOUT` or `LOCAL_TIMEOUT` is set (changed during implementation: the DWARF info dump
     takes about an hour);
   - streams stdout through `sed 's/\r$//'` and `tee` into `sha256sum`, `wc -lc` and the output
     file (or straight into `zstd -10 --long=27 -T0` for dumps declared local-only, such as `-de`);
   - captures stderr to staging and the exit code with `|| rc=$?`, so `errexit` never aborts the
     run;
   - applies the storage rule from the measured size;
   - appends a manifest line built with `jq -n`.

   Variants: `run_slice`, which pipes `elfslice.py slice` (a byte range of the staged copy) into a
   tool, used for strings; `run_derived` for helper outputs; `not_produced`.
3. Tool identity: `--version` first line for binutils and LLVM, `orbis-bin -ver` for orbis-bin,
   plus the executable's SHA-256. Run-wide: zstd, Python, and uv versions in `run.meta`.
4. Publish:
   - compare the input snapshot again;
   - for each file, keep the existing file if the content hash is unchanged, otherwise `mv` the
     new one in;
   - write the manifest to a temporary file, then `mv` it into place;
   - point `.staging/last` at this run;
   - also provide `--verify` (re-hash all published files) and `--exec` (one tool on the staged
     copy, for fact checks), and the derivation map used by `--only`.
5. Add `.gitattributes` and the `.gitignore` entries.

### Phase B: Dump catalogue (FR-002, FR-003; ids in `categories.tsv`)

- **headers/**:
  - orbis-bin `-dh`, `-dph`, `-dsh`, `-dsi`, `-dml`, `-dfl`;
  - `llvm-readelf -h -l -S -d -W`;
  - `llvm-readobj --elf-output-style=JSON --file-headers --program-headers --sections --dynamic-table`
    (stderr kept apart);
  - comparison: `orbis-readelf -h -l -S -d -r -u -I --dyn-syms -W`, and `orbis-objdump -p` / `-h`;
  - not-produced evidence: `llvm-readelf -n -V`.
- **dynamic**: orbis-bin `-ddy`, `--dump-dynsym -v`, `--dump-dynstr`.
- **symbols/**:
  - `llvm-readelf -s -W`;
  - `orbis-bin -dsy -v`;
  - `llvm-nm -C -S --defined-only -n`;
  - subsets extracted with `rg` from those outputs: functions, data objects, RTTI/vtables, PLT stubs;
  - comparison: `orbis-objdump -t -C` (supersedes the old `objdump.symbols.txt`), `orbis-readelf -s -W`.
- **relocations/**:
  - `orbis-bin -r`;
  - `llvm-objdump -s -j .data.rel.ro -j .got -j .got.plt`;
  - `llvm-objdump -s -j .ctors`.
- **sce/**:
  - `orbis-bin --dump-sections=.sceversion`;
  - `llvm-objdump -s -j .sce_process_param -j .prodg_meta_data`;
  - the SCE Comment and SCE Version segments as `xxd` byte ranges of the staged copy, using the
    offsets from `-dph`.
- **strings/**:
  - `.rodata` through `run_slice`, with `orbis-strings -a -t x`, then with `-e S`;
  - both rebased to virtual addresses by the helper, into `derived/`;
  - the whole file with `orbis-strings -a -t x`.
- **stack/**: `orbis-bin -dss`.
- **registers/**:
  - `llvm-readelf --unwind` (CFA rules);
  - the `--debug-loc` dump doubles as register locations;
  - derived register-usage counts per DWARF register.
- **dwarf/**:
  - `llvm-dwarfdump` with `--show-section-sizes`, `--statistics`, `--verify` (expected exit 1),
    `--debug-abbrev`, `--debug-loc`, `--debug-ranges`, `--debug-str`, `--debug-frame`;
  - the CU list (`--debug-info --recurse-depth=0`).
- **derived/**:
  - `dwarf-line` and `dwarf-line-gaps` (R7);
  - `dwarf-source-files`, from the CU list;
  - section and segment hashes;
  - rebased strings;
  - string references (R10, *inferred*);
  - register usage.
- **local/**:
  - `orbis-bin -de`;
  - `llvm-dwarfdump --debug-info -v`;
  - `llvm-objdump -d -l --demangle -w`;
  - `orbis-objdump -d -w`, compatible with the reconstructor's agreement test.
- **oracles/**: extracts per data-model, built by the helper from the primary dumps.
- **Stand-ins for local-only dumps** (FR-010): the section list of `-de` with per-section line
  counts; for each disassembly, a per-function index (address, size, line count) and the `.text`
  instruction count; for the DWARF info dump, the CU list and `--statistics` (already committed).
- **compare/** (`--compare-sdks`):
  - the matrix from research R14;
  - a bounded GNU 2.47 sample (`objdump -t | rg ' _start$'` and 1 KB of disassembly at the entry).
- **tool-help/**: `--help` of every tool and flag set used.

### Phase C: Documents (FR-006–FR-009, FR-011, FR-013)

1. **`facts.tsv`**: register at least 12 facts across all groups *before* checking (quickstart
   §6). Use `xxd` on the ELF or a different tool family as the source, e.g. `orbis-bin --addr2line`
   against the derived line table.
2. **`COMPARISON.adoc`**:
   - the per-category ranking with counts;
   - the SDK verdict;
   - the fact-check results;
   - the orbis-bin vs `llvm-addr2line` line oracle.

   Afterwards, reconcile `categories.tsv`: if the ranking changes any primary, update the
   catalogue and the manifest roles, and rerun the affected ids.
3. **`LOSSES.adoc`**: L-NN entries, each with a kind, evidence, an oracle, and a proposal.
   - Seed `tool-loss` entries:
     - SCE phdr types unnamed (readelf, GNU, LLVM); RELRO raw in orbis-objdump;
     - DT_SCE_* unnamed (readelf, LLVM);
     - dynamic table truncated at NEEDED (orbis-objdump, GNU objdump);
     - NEEDED names unresolved (readelf, LLVM);
     - no relocations or dynsym outside orbis-bin; orbis-objdump `-R`/`-T` fail;
     - NID resolution depends on the SDK: none with 2.500 (corrected after implementation; see research R3);
     - GNU symbol-value shift;
     - sequential `.debug_line` readers fail;
     - `llvm-addr2line` gives `??:0` where CUs overlap, and orbis-addr2line crashes on large batches;
     - `-dml` misattributes sections, `-dfl` omits phdr types, and orbis-bin `-r` prints
       "Unknown Section Name";
     - orbis-objdump `-l` is too slow;
     - `-D` disassembles data;
     - 7-bit strings miss UTF-8/SJIS text;
     - no tool decodes RELRO targets, string references, PROCPARAM, or the SCE Comment.
   - `producer-quirk` entries:
     - `.debug_line` gaps;
     - the `--verify` findings (21,330 overlapping inlined ranges, 3,286 not contained in their
       parent);
     - the quirks the reconstructor already documents: no `DW_AT_linkage_name`, tombstone
       addresses.
4. **`handover/spec.md` and `handover/research.md`**: in the reconstructor's Spec Kit shape,
   unnumbered.
   - Proposals `ddon-data-P<n>`, each with a status, as observed read-only at a recorded commit:
     - SCE phdr and DT naming;
     - full dynamic and dynlib dump;
     - NID dump with a NID → name table;
     - relocation dump;
     - RELRO target and string-reference table;
     - PLT↔import map (exists: `nid.rs`);
     - stack sizes (exists: `stack_sizes.rs`);
     - PROCPARAM, `.sceversion` and Comment decoding;
     - a robust `.debug_line` reader through `stmt_list`;
     - symtab values and e_type handling;
     - UTF-8/SJIS strings;
     - a `dump` CLI surface;
     - oracle parity tests.
   - Also state:
     - which new dump supersedes each old input, e.g. `DDON_OBJDUMP_ZST` → `local/disassembly-orbis.orbis-objdump`;
     - format differences that matter.
   - Follow-ups: the PC `DDO.exe` exports for ddon-hook, and repinning the knowledge graph.
5. **`README.adoc`**:
   - the index;
   - the storage rule and volatile fields;
   - regeneration;
   - search tips (`zstd -dcqq … | rg -m`);
   - old-dump coverage (FR-011): each old file is diffed against its successor after the
     `IDA9.2` path line is dropped, and the result is recorded.

### Phase D: Integration (FR-012)

1. Add a row for `elf-dumps/` to the `AGENTS.md` layout table, and note that the old dumps beside
   the ELF are superseded.
2. Add a `readme.adoc` layout row.
3. Leave the knowledge-graph pins unchanged; repinning them is a handover follow-up.

## Risks

| Risk | Mitigation |
|---|---|
| A tool writes next to its input | Never pass output options. The snapshot guard (R12) aborts publishing. The feasibility review saw no writes. |
| `-de` fills the disk | Stream it into zstd; peak scratch is under 2 GB |
| A tool hangs | No limit by default; the optional `DUMP_TIMEOUT`/`LOCAL_TIMEOUT` records `status: timeout` |
| Committed files churn on reruns | Content-hash identity, and unchanged files are kept |
| Measured sizes differ from the estimates | The storage rule is applied to the measured sizes at run time |
| The reconstructor changes during the handover | Cite its commit and date. The handover relies only on committed code. |
| `--debug-info -v` takes too long | Measure it. It is local-only, can be skipped with `--skip-local`, and the old dump stays as the fallback reference. |

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| A Python helper next to bash | Byte-range copies and a 172k × 44k join | awk/dd arithmetic over offsets is fragile and hard to verify, and `tail \| head` slicing returns SIGPIPE 141 under `pipefail` (R13) |
| An 800 MB copy of the input in staging | No tool may run in, or write next to, the input folder (FR-015) | Running in the input folder only detects writes after the fact; a hardlink changes the original's metadata |
