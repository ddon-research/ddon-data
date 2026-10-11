# Tasks: PS4 02020005 static ELF dump set and reconstructor handover

**Input**: Design documents from `specs/001-ps4-static-dumps/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md
**Status**: Closed. All tasks are done; the output is `binaries/PS4_02020005/elf-dumps/`.

**Tests**: There are no unit tests. Each phase checkpoint, and the final phase, runs the
quickstart validation steps.

**Path prefix**: `E=binaries/PS4_02020005/elf-dumps`. Paths are relative to the repository root.

**Hard rules for every task**:

- Read the IDA9.3 PS4 folder only to make the staged copy (FR-015). Every tool reads
  `E/.staging/input/DDOORBIS.elf` with its current directory in `E/.staging/input/`.
  Ad-hoc tool runs go through `E/generate-elf-dumps.sh --exec`.
- Never edit `C:/ddon-dwarf-reconstructor-rust` or ddon-hook.
- Tools that read the input never get an output-path option (`orbis-bin -o` is forbidden).
  `llvm-objcopy` may write only inside `E/.staging/`.
- Record every failure; never report one as a pass.

## Phase 1: Setup

- [X] T001 Create the folder tree under `E/`:
  - `headers symbols relocations sce strings stack registers dwarf derived oracles compare tool-help tools handover`;
  - add `E/.gitattributes` with `*.txt text eol=lf`, `*.tsv text eol=lf`, `*.jsonl text eol=lf`, `*.md text eol=lf`, `*.adoc text eol=lf`, `*.sh text eol=lf`, `*.py text eol=lf`, `*.zst binary`.
- [X] T002 [P] Add `binaries/PS4_02020005/elf-dumps/local/` and `binaries/PS4_02020005/elf-dumps/.staging/` to `.gitignore`. Check with `git check-ignore -v binaries/PS4_02020005/elf-dumps/local/x binaries/PS4_02020005/elf-dumps/.staging/x`.
- [X] T003 [P] Write `E/categories.tsv` with columns `category group description primary reason`.
  - One row for every category in data-model.md § Category.
  - `primary` is the dump id from research.md R4. Derived ids such as `dwarf-line.derived` are allowed.
  - For `dwarf-aranges dwarf-pubnames dwarf-pubtypes dwarf-index elf-notes symbol-versioning`, set `primary` to `not-produced` and give a reason citing the evidence dump id.
- [X] T004 [P] Capture help texts into `E/tool-help/<tool>.txt` with line-final CRs stripped.
  - orbis-bin (SDK 12): try `orbis-bin`, then `--help`, `-help`, `-?`, and keep the first one that prints the switch list. Record which switch worked in the file header.
  - orbis-objdump, orbis-readelf, orbis-nm, orbis-strings: `--help`.
  - llvm-readelf, readobj, objdump, dwarfdump, nm, objcopy: `--help`.

## Phase 2: Foundational (generator core; blocks every story)

- [X] T005 Write `E/generate-elf-dumps.sh` with the options, environment defaults and exit codes from contracts/generator-cli.md.
  - Start with `set -o errexit -o nounset -o pipefail` and `export MSYS_NO_PATHCONV=1`.
  - Keep one `REQUIRED_COMMANDS=(jq zstd sha256sum sed rg xxd cut sort comm tee wc timeout uv cp mv ln fd)` array. Check every entry with `command -v`, and every native executable with `[ -x ]`. Exit 1 on the first one missing.
  - Verify the original's size 800622848 and SHA-256 `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`.
  - Copy it to `E/.staging/input/DDOORBIS.elf` with `cp`, unless an existing copy has the same hash. Verify the copy. Exit 1 on any mismatch.
- [X] T006 In `E/generate-elf-dumps.sh`, add the input snapshot.
  - Write name, size, mtime (`stat -c '%n\t%s\t%Y'`) and SHA-256 for every file in the original input folder to `E/.staging/<run>/input-snapshot.before.tsv`, and again to `.after.tsv` after all tools have run.
  - Exit 1 before publishing if the two files differ.
- [X] T007 In `E/generate-elf-dumps.sh`, add `run_dump <id> <cat1,cat2> <role> <expected_exit> <storage-hint auto|local> <tool> <args...>`.
  - Run `rc=0; (cd "$STAGED_DIR" && timeout "$DUMP_TIMEOUT" "$tool" "$@") 2>"$err" | sed 's/\r$//' | tee >(sha256sum >"$h") >(wc -lc >"$n") >"$out" || rc=$?`, then read the tool's own status from `PIPESTATUS[0]`.
  - With the `local` hint, write into `zstd -10 --long=27 -T0` instead of `$out`.
  - Storage rule from the measured size (FR-010): ≤ 10 MB → `txt`. Otherwise `zstd -19 --long=27`; ≤ 50 MB → `zst`; otherwise `local`.
  - Status: `ok` if `rc == expected_exit`, `timeout` if `rc == 124`, else `failed`.
  - Tool identity: the first line of `--version` (binutils, LLVM) or of `orbis-bin -ver`, plus `sha256sum` of the executable.
  - Append the manifest line with `jq -n` as contracts/manifest.schema.json `produced`, `kind: tool`. Required fields: `cwd`, `input{path,origin,sha256,size}`, `output{sha256,size,lines,stored_size}`, `stderr{file,lines,first}`, `seconds`.
- [X] T008 In `E/generate-elf-dumps.sh`, add the remaining helpers:
  - `run_slice <id> <cats> <role> <section> <tool> <args...>`: look up the section's offset and size in the `sections.orbis-bin` dump, then pipe `uv run --no-project --python 3.14 --script E/tools/elfslice.py slice "$STAGED" <off> <size>` into the tool's stdin.
  - `run_derived <id> <cats> <role> <inferred true|false> <input-ids,> <elfslice-subcommand> <args...>`: writes `kind: derived` with `inputs[] {id, sha256}`.
  - `not_produced <id> <cats> <reason> <evidence-id>`.
  - The `run.meta` first line: `zstd --version`, `python --version` via uv, `uv --version`, the script's SHA-256, and `volatile: ["generated","seconds","stderr.first"]`.
- [X] T009 In `E/generate-elf-dumps.sh`, add publishing and the extra modes.
  - For each staged file, keep the published file if its content hash equals the existing manifest entry; otherwise `mv` the new file into place.
  - Write `manifest.jsonl.tmp`, then `mv` it into place. Update `.staging/last` (`ln -sfn`, or record the run id in a file if symlinks fail).
  - `--verify`: re-hash every published file against the manifest, with `zstd -dcqq` for `zst` and `local`.
  - `--exec <tool> <args...>`: run one tool in `$STAGED_DIR` with the snapshot guard.
  - `--only <glob>`: expand the glob through a `DEPENDS` derivation map (id → input ids), adding everything that transitively depends on a match.
  - `--skip-local` and `--dry-run`.
- [X] T010 Write `E/tools/elfslice.py` as a PEP 723 script: stdlib only, with a `# /// script` block that has `requires-python = ">=3.14"` and `dependencies = []`, and argparse subcommands.
  - `slice <elf> <off> <size>`: write the byte range to stdout.
  - `line-copy <elf> <cu-list> <out.bin> <map.tsv> <gaps.tsv>`: copy every `[stmt_list, stmt_list+4+unit_length)` range in order. Write the map (orig_off, new_off, length) and the gaps (offset, length, first 16 bytes as hex).
  - `hashes <elf> <dsh> <dph>`: SHA-256 per section and per segment file range, as TSV.
  - `rebase-strings <strings> <vaddr-base>`: write `vaddr\tstring` TSV.
  - `string-refs <relocs> <rebased-strings>`: RELATIVE relocations whose addend equals a string start. Output columns: slot, target, string. Mark the output inferred.
  - `register-usage <debug-loc>`: count `DW_OP_reg*` and `DW_OP_breg*` by register name.
  - `oracles <outdir> <inputs...>`: the extracts in data-model.md § Oracle, each under 5 MB.
  - `stand-ins <...>`: the stand-ins for local-only dumps from plan.md Phase B.
- [X] T011 Smoke test.
  - Run `E/generate-elf-dumps.sh --dry-run`, then `--only 'file-header.*'`.
  - Validate `E/manifest.jsonl` per line (quickstart §3 schema loop), and run `--verify`.
  - Confirm the snapshot diff is empty and the manifest's `cwd` is the staged folder.

**Checkpoint**: one dump is published with a valid manifest, and the input is untouched.

## Phase 3: User Story 1 - Look up any binary fact (Priority: P1) 🎯 MVP

**Goal**: every catalogue category has a primary dump with `status: ok`, or a not-produced entry, with full provenance.
**Independent Test**: quickstart §3 (coverage, schema, `--verify`) and §5 (expected counts).

- [X] T012 [US1] In `E/generate-elf-dumps.sh`, add one `run_dump` per id, in `E/headers/`. orbis-bin:
  - `file-header.orbis-bin` `-dh`
  - `program-headers.orbis-bin` `-dph`
  - `sections.orbis-bin` `-dsh`
  - `section-sizes.orbis-bin` `-dsi` (segment size totals)
  - `section-segment-map.orbis-bin.memory` `-dml`
  - `section-segment-map.orbis-bin.file` `-dfl`
  - `dynamic.orbis-bin` `-ddy` (categories `dynamic,dynlib`)
  - `dynsym.orbis-bin` `--dump-dynsym -v`
  - `dynstr.orbis-bin` `--dump-dynstr`

  LLVM:
  - `headers.llvm-readelf` `-h -l -S -d -W`
  - `headers.llvm-readobj.json` `--elf-output-style=JSON --file-headers --program-headers --sections --dynamic-table` (stderr in its own file)
  - `elf-notes.llvm-readelf` `-n -V`: the evidence for the not-produced `elf-notes` and `symbol-versioning` entries
- [X] T013 [US1] Add the symbol dumps to `E/symbols/`:
  - `symtab.llvm-readelf` `-s -W`, `symtab.orbis-bin` `-dsy -v`, `symtab.llvm-nm` `-C -S --defined-only -n`.
  - `run_derived` subsets, built with `rg`:
    - `functions.derived`: `llvm-nm` types t/T;
    - `data-objects.derived`: types d/D/b/B/r/R;
    - `rtti-vtables.derived`: mangled `_ZTV|_ZTI|_ZTS` from `symtab.llvm-readelf`;
    - `plt-stubs.derived`: names starting `/PL`, `/PG`, `/G`, `/GC`.
- [X] T014 [US1] Add the relocation dumps to `E/relocations/`:
  - `relocations.orbis-bin` `-r`;
  - `relro-got.llvm-objdump` `-s -j .data.rel.ro -j .got -j .got.plt`;
  - `ctors.llvm-objdump` `-s -j .ctors`.

  Record in the README that `.got` and `.got.plt` lie inside `PT_SCE_RELRO` (join `-dfl` with `-dph`).
- [X] T015 [US1] Add the SCE dumps to `E/sce/`:
  - `sce-version.orbis-bin` `--dump-sections=.sceversion`;
  - `sce-process-param.llvm-objdump` `-s -j .sce_process_param -j .prodg_meta_data` (categories `sce-process-param,prodg-metadata`);
  - `sce-comment.xxd` and `sce-version-segment.xxd`: `xxd -s <off> -l <filesz>` of the staged copy, with offsets from `program-headers.orbis-bin`.
- [X] T016 [US1] Add the string dumps to `E/strings/`:
  - `strings-rodata.orbis-strings`: `run_slice .rodata orbis-strings -a -t x`;
  - `strings-rodata-utf8.orbis-strings`: the same with `-e S`;
  - `strings-all.orbis-strings`: `-a -t x` on the whole file;
  - `run_derived` rebased tables `strings-rodata.rebased` and `strings-rodata-utf8.rebased`, with base = the `.rodata` vaddr from `sections.orbis-bin`.
- [X] T017 [US1] Add the stack and register dumps:
  - `E/stack/`: `stack-sizes.orbis-bin` `-dss`;
  - `E/registers/`: `unwind-cfa.llvm-readelf` `--unwind`, and `register-usage.derived` from `dwarf-loc`;
  - in `categories.tsv`, map `register-locations` to `dwarf-loc.llvm-dwarfdump`.
- [X] T018 [US1] Add the DWARF dumps to `E/dwarf/`, all with `llvm-dwarfdump`:
  - `dwarf-section-sizes` `--show-section-sizes`;
  - `dwarf-statistics` `--statistics`;
  - `dwarf-verify` `--verify`, with expected_exit 1;
  - `dwarf-abbrev`, `dwarf-loc`, `dwarf-ranges`, `dwarf-str` and `dwarf-frame`, each with its `--debug-*` flag;
  - `dwarf-cu-list` `--debug-info --recurse-depth=0`;
  - derived `dwarf-source-files`: DW_AT_name and DW_AT_comp_dir per CU, from the CU list.
- [X] T019 [US1] Add the derived line tables.
  - Run `elfslice.py line-copy` into `E/.staging/<run>/line.bin`.
  - Wrap it: `llvm-objcopy -I binary -O elf64-x86-64 --rename-section .data=.debug_line,contents,readonly line.bin line.elf`, inside staging.
  - Run `llvm-dwarfdump --debug-line line.elf` and publish `dwarf-line.derived`, `dwarf-line-map.derived` and `dwarf-line-gaps.derived`.
  - Record the measured table and row counts; research R7 expects 2305 and 1,679,315.
- [X] T020 [US1] Add the local-only dumps (storage hint `local`):
  - `everything.orbis-bin` `-de`;
  - `dwarf-info.llvm-dwarfdump` `--debug-info -v`;
  - `disassembly.llvm-objdump` `-d -l --demangle -w`;
  - `disassembly-orbis.orbis-objdump` `-d -w`.

  Record each one's time and size.
- [X] T021 [US1] Add the derived files `section-hashes.derived` and `segment-hashes.derived` (`elfslice.py hashes`), the `E/oracles/` extracts (`elfslice.py oracles`), and the committed stand-ins for every local-only dump (`elfslice.py stand-ins`, FR-010).
- [X] T022 [US1] Run the full generation with `E/generate-elf-dumps.sh`.
  - Record the exit code, and list every `failed` or `timeout` id in the Notes below.
  - Run quickstart §2, §3 and §5.
  - Update the oracle columns and patterns in quickstart §5 to match the real files.
- [X] T023 [US1] Write the first version of `E/README.adoc`:
  - the layout;
  - the index of category → dump id → file, generated from `categories.tsv` and the manifest;
  - the storage rule and the volatile fields;
  - how to regenerate, with `--verify` and `--exec`;
  - search tips (`zstd -dcqq <f> | rg -m N`);
  - the mapping from `llvm-readobj` JSON numeric SCE types to orbis-bin names;
  - the recovery procedure for an interrupted publish.

**Checkpoint**: SC-001 and SC-003 pass, and every published count has been re-measured.

## Phase 4: User Story 2 - Know which tool to trust (Priority: P1)

**Goal**: an evidence-backed ranking for each category, and an SDK verdict.
**Independent Test**: quickstart §6 (fact check); every claim in COMPARISON.adoc cites a dump id and a count.

- [X] T024 [US2] Add the comparison runs (`role: comparison`) to `E/generate-elf-dumps.sh`:
  - `headers.orbis-readelf` `-h -l -S -d -r -u -I --dyn-syms -W`;
  - `symtab.orbis-readelf` `-s -W`;
  - `dynamic.orbis-objdump` `-p`;
  - `sections.orbis-objdump` `-h`;
  - `symtab.orbis-objdump` `-t -C`;
  - `allheaders.orbis-objdump` `-x`, for the old-dump check.
- [X] T025 [US2] Implement `--compare-sdks` per research R14.
  - Run the orbis-bin flag matrix, excluding `-de`, and the binutils hash check across SDK 2.500, 3.500, 8.000 and 12.000.
  - Write `E/compare/sdk-matrix.tsv` with columns `tool flags sdk exit output_sha256 size lines diff_lines_vs_12000`.
  - Copy differing outputs of 10 MB or less into `E/compare/<sdk>/`.
- [X] T026 [P] [US2] Add the GNU 2.47 sample to `E/compare/` with `run_dump` (`role: comparison`):
  - `symtab.gnu-objdump.start`: `objdump -t`, filtered to ` _start$`;
  - `disassembly.gnu-objdump.entry`: `objdump -d --start-address=0xd5a8d0 --stop-address=0xd5acd0`.
- [X] T027 [US2] Register `E/facts.tsv` **before** checking anything.
  - At least 12 rows, at least one per group (headers, dynamic, symbols, relocations, sce, strings, stack, registers, dwarf, code), and two for dwarf (info and line).
  - Each row names an independent source: `elf:<off>:<len>` on the staged copy, or `tool:<name> <args>` from a different tool family run through `--exec`. Use `orbis-bin --addr2line=` for line facts. IDA alone does not count for DWARF facts.
  - Record the registration time in the file header.
- [X] T028 [US2] Run the fact check through `--exec` and `xxd`, and fill in `result` and `checked` in `E/facts.tsv`. IDA MCP may be used, read-only, as an extra cross-check.
- [X] T029 [US2] Write `E/COMPARISON.adoc`:
  - for each category, the primary, the runners-up and the defects, with counts;
  - the SDK verdict, from `sdk-matrix.tsv`;
  - the line oracle: orbis-bin vs `llvm-addr2line` at 0x194d8f0;
  - a summary of the fact check.
- [X] T030 [US2] Reconcile `E/categories.tsv` with COMPARISON.adoc. If a primary changed, update the manifest roles with `--only <ids>` and rerun quickstart §3.
- [X] T031 [US2] Write `E/LOSSES.adoc` from every seed in plan.md Phase C.3.
  - Mark each entry `tool-loss` or `producer-quirk`.
  - Give it evidence (dump id with a count or excerpt), the correct form (*inferred* where derived), an oracle, and a proposal label or `out-of-scope` with a reason.
  - Include every `failed` or `timeout` id from T022.

**Checkpoint**: SC-004 passes, and every loss has evidence and an oracle.

## Phase 5: User Story 3 - Hand over to ddon-dwarf-reconstructor-rust (Priority: P2)

**Goal**: a self-contained handover in the reconstructor's Spec Kit shape.
**Independent Test**: quickstart §8.

- [X] T032 [P] [US3] Read the reconstructor at its current commit, read-only.
  - Record `git -C C:/ddon-dwarf-reconstructor-rust rev-parse HEAD` and the date.
  - Read `crates/reconstructor-storage/src/sce/*.rs`, `specs/orchestration.md`, `docs/reference/markers-and-inferences.md`, `docs/reference/prerequisites.md`, `docs/reference/environment.md`, and its spec template under `.specify/templates/`.
  - Note the path and line of each existing decode and exposure.
- [X] T033 [US3] Write `E/handover/research.md`:
  - the reconstructor coverage, with commit and paths;
  - the old-input → new-dump mapping, e.g. `DDON_OBJDUMP_ZST` → `local/disassembly-orbis.orbis-objdump` (same orbis-objdump `-d` format; the old one used `-D`);
  - links to LOSSES and COMPARISON as evidence.
- [X] T034 [US3] Write `E/handover/spec.md` in the reconstructor's spec template shape: unnumbered, with user stories, FRs and SCs.
  - Label each proposal `ddon-data-P<n>`. Give it a status (`exists`, `exposed-gap` or `missing`), the linked losses, the proposed output (text that mirrors orbis-bin, plus JSONL), the oracle files in `E/oracles/`, and an acceptance check.
  - Include a "callers of an import / referents of a string" proposal (US4-AS1).
  - Follow-ups: the PC `DDO.exe` exports for ddon-hook, and repinning the knowledge graph's SDK 8 objdump and old llvmdwarfdump index.
- [X] T035 [US3] Run quickstart §8 and fix any unmapped loss or missing oracle.

**Checkpoint**: SC-005 passes.

## Phase 6: User Story 4 - Additional static exports (Priority: P3)

**Goal**: the extra exports are indexed and fact-checked.
**Independent Test**: each one has a README index entry and at least one row in `facts.tsv`.

- [X] T036 [US4] Add `string-refs.derived` (`elfslice.py string-refs`, `inferred: true`) to `E/derived/`. Check 10 entries against the staged copy's bytes and, read-only, against IDA MCP, and record the result in `E/COMPARISON.adoc`.
- [X] T037 [US4] Make sure every User Story 4 export has a README index entry and a facts row. Register any missing rows in `E/facts.tsv` before checking them, then check them.

## Phase 7: Polish and cross-cutting

- [X] T038 Complete `E/README.adoc` with the old-dump coverage (FR-011). For each pair, drop the input-path line and record the diff result:
  - `objdump.allheaders.txt` vs `allheaders.orbis-objdump`, cut to the same extent;
  - `objdump.symbols.txt` vs `symtab.orbis-objdump`;
  - `readelf.headers.txt` vs `headers.orbis-readelf`;
  - `readelf.symbols.txt` vs `symtab.orbis-readelf`;
  - `objdump.zst` vs `disassembly-orbis.orbis-objdump`, `.text` part only;
  - `llvmdwarfdump.zst` vs `dwarf-info.llvm-dwarfdump`.

  Read the old files in place, read-only. They are never moved or deleted.
- [X] T039 [P] Update `AGENTS.md`:
  - add a layout row for `binaries/PS4_02020005/elf-dumps/`;
  - note that the old dumps beside the ELF are superseded;
  - add a regeneration line under Workflows.
- [X] T040 [P] Update `readme.adoc`: add a layout row and a data-flow line for `elf-dumps/`.
- [X] T041 Run quickstart §4, the `--skip-local` rerun. Expected: identical file hashes, and manifest changes only in the volatile fields.
- [X] T042 Run quickstart §2 (path length, leaks) and §7 (input snapshot, `cwd`). Then run `fd -t f -S +50m . binaries/PS4_02020005/elf-dumps -E local -E .staging` and expect no output.
- [X] T043 Record the final state in this file: the checkboxes, any measured numbers that differ from research.md, and open blockers. Leave committing to the user.

## Dependencies and execution order

- **Order:** Setup (T001–T004), then Foundational (T005–T011), then US1 (T012–T023).
- **US2:** T024–T026 can start after T011. T027–T031 need T022.
- **US3:** T033–T035 need T031. T032 is read-only and can run at any time.
- **US4:** needs T016 and T019.
- **Polish:** comes last, except T039 and T040, which can run in parallel with US3.

## Parallel opportunities

- T002, T003 and T004 can run in parallel.
- T026 and T032 can run alongside US1.
- T012–T021 all edit `generate-elf-dumps.sh`, so they run in sequence. Each one can be tested on its own with `--only`.

## Implementation strategy

1. **MVP**: Phases 1–3, a complete, provenance-bound dump set (SC-001, SC-002, SC-003, SC-006).
2. **Phase 4**: settles the SDK 12 question and produces the loss register.
3. **Phase 5**: the handover.
4. **Phases 6–7**: the extra exports and polish.
5. **Stopping points**: stop at each checkpoint and report the measured numbers.

## Notes

- Commit only when the user asks. Suggested split: first the generator and docs, then the dump set (review it with `git diff --stat -- binaries/PS4_02020005/elf-dumps`).
- Record task notes and blockers here during implementation.

### Implementation notes (2026-10-11)

- Full run 19:41–21:09 (`--compare-sdks`): 89 manifest entries, all `status: ok`, 0 failures.
  The `orbis-bin -de` dump took 15.5 min, `llvm-dwarfdump --debug-info -v` 58 min (27.8 GB raw,
  1.18 GB zstd). The first publish failed because native `jq` cannot read `/dev/fd` process
  substitutions; the finished run was published with the new `--publish-run` mode. Input-folder
  snapshot unchanged (generator guard, plus a separate `ls --full-time` from before the first run).
- Changes from the plan made during implementation: no time limits by default; CR stripping only
  for orbis-* and GNU output; `jq` runs with `--binary` (Windows jq writes CRLF otherwise);
  `HERE` uses `pwd -W` so native tools get `D:/` paths; SDK comparison keeps unified diffs
  (`compare/sdk-diff/`) instead of whole outputs, and is a manifest entry (`sdk-matrix.derived`);
  added `unwind-cfa.gnu-readelf` (CFA table with register names) and `allheaders` uses `-x -w`
  so it supersedes the old file exactly; Orbis SDK help texts are "SIE CONFIDENTIAL" and stay in
  `local/tool-help/`.
- Measured numbers that differ from research.md: the pilot's "105 unresolved NIDs" is the
  non-verbose `--dump-dynsym`; with `-v` SDK ≥ 3.500 resolves all 648 (research R3 corrected).
  `--verify` output is 21.0 MB. Committed set: 106.9 MB (git compresses the plain text);
  local-only: 2.0 GB.
- T041 rerun (`--skip-local --compare-sdks`): all 105 published dump files byte-identical; the
  manifest differs only in the volatile fields and in the helper/script SHA-256 (the helper's
  instruction regex was fixed after the first run, so the stand-ins were regenerated once).
- The local-only dumps were produced by the script revision before those fixes; their content is
  unaffected (LLVM output was LF already, `sed` on it was a no-op) and `--verify` confirms their
  hashes.
- Not done: committing (left to the user).
- Reconstructor review (2026-10-11, `binaries/PS4_02020005/elf-dumps/handover/reply-from-reconstructor.md`):
  verified here before applying (JUMP_SLOT slots non-zero on disk: 539 of 542 `.got.plt` qwords;
  `dynamic.tsv` has `-` for TEXTREL and NULL; F13 held a BEL byte; 120,885 FUNC symbols;
  `llvm-dwarfdump --debug-line` prints 3 headings, 1 real; `orbis-addr2line -i` chains). Corrected
  LOSSES (L-09, L-10, L-15, L-16, L-19, L-21, L-22), COMPARISON (SDK binutils are four builds,
  line oracle, GOT), handover research/spec (`/GC`, `elf.rs:146-152`, FR-003, review outcome),
  research.md R3/R4, facts.tsv F13. Added comparison dumps `line-oracle.orbis-addr2line.inline`
  and `line-oracle.llvm-addr2line.inline`. Figures the review computed that were not re-derived
  here are attributed to it in the text.

## Phase 8: Consolidation (2026-10-11, after the handover closed)

- [X] T044 Split `binaries/PS4_02020005/elf-dumps/` into the preferred outputs and `archive/`: keep
  every `role: primary` dump, the four local-only stand-ins and `dwarf-line-map.derived`; move the
  comparison runs, supplements, oracles, `compare/`, `COMPARISON.adoc`, `LOSSES.adoc`,
  `facts.tsv`, `handover/` and `tool-help/` to `archive/` with their manifest entries
  (`archive/manifest.jsonl`, paths prefixed `archive/`) and `archive/SHA256SUMS`.
- [X] T045 Trim `generate-elf-dumps.sh` to the preferred outputs (archived copy:
  `archive/generate-elf-dumps.full.sh`). `symtab.llvm-nm` and the two slice-relative
  `orbis-strings` runs become `role: intermediate`, `storage: staging` (schema updated). The
  not-produced evidence for notes/versioning now cites `sections.orbis-bin`.
- [X] T046 Rerun `--skip-local`: all 47 kept files byte-identical to before the split; manifest 58
  entries, schema-valid; `--verify` passes; `sha256sum -c archive/SHA256SUMS` passes.
- [X] T047 Rewrite `elf-dumps/README.adoc` as an as-is status report; add `archive/README.adoc`;
  update `AGENTS.md`, `readme.adoc`, `CLAUDE.md`, and `contracts/generator-cli.md`.
- [X] T048 Drop non-reference leftovers: `stderr/` is no longer published (the only content was
  helper counters, already in each manifest entry's `stderr.first`); the orbis-objdump
  disassembly (`local/archive/`) and its summary, and the one-line `dwarf-info.standin`, move to
  the archive. Rerun `--skip-local`: kept files byte-identical, 55 manifest entries, `--verify`
  passes.
- [X] T049 Move the `orbis-bin -de` dump and its heading index to the archive (a superset of the
  individual orbis-bin dumps, not the reference for any category). Gitignore
  `elf-dumps/archive/`; the archived local-only dumps live in `archive/local/`. 53 manifest
  entries; `--verify` and `archive/SHA256SUMS` pass.
