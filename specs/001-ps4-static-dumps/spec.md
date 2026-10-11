# Feature Specification: PS4 02020005 static ELF dump set and reconstructor handover

**Feature Branch**: `001-ps4-static-dumps` (spec directory only; no git branch)

**Created**: 2026-10-11

**Status**: Complete (all tasks done, T001–T049; the reconstructor handover is closed)

**Input**: User description: "PS4 02020005 static ELF dump set and reconstructor handover. Produce a
documented, reproducible set of the most accurate and informative static text dumps of the PS4
client ELF `DDOORBIS.elf` under `binaries/PS4_02020005/`: functions, symbols, sections, registers,
program headers including proprietary SCE segments, dynamic table, imports/exports, relocations,
GOT/PLT and RELRO contents, string constants, stack sizes, unwind data, and DWARF sections. Compare
the available tools and document which is most accurate per information category, with evidence.
Document what information external tools lose, and prepare a handover for
ddon-dwarf-reconstructor-rust (not edited now) so it can implement a complete SCE-aware dumper."

## Clarifications

### Session 2026-10-11

- Q: How are multi-GB dumps stored (no Git LFS, GitHub limit 100 MB)? → A: Local-only for all
  big dumps. Commit only small and medium dumps, at most 50 MB per committed file. Record the rest
  in the manifest with their hash and regeneration command.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Look up any binary fact in a trustworthy dump (Priority: P1)

A researcher (or an agent) needs a section address, a symbol's size, a program header, a dynamic
tag, the register rules at an address, or the source line for an address. They open the dump set
in `binaries/PS4_02020005/elf-dumps/`, find the file for that information category from its index,
and get the answer together with the exact command, tool version, and input hash that produced it.

**Why this priority**: Every other use (comparison, handover, cross-validation in the knowledge
graph) builds on a complete, provenance-bound dump set. It supersedes undocumented dumps that
already caused confusion.

**Independent Test**: Answer the pre-registered fact list (FR-013) from the dump set alone and
confirm each fact against its registered independent source.

**Acceptance Scenarios**:

1. **Given** the dump set, **When** a reader opens its index, **Then** every category in the
   category catalogue maps to at least one dump file, or to an explicit "not produced, because ..."
   entry.
2. **Given** any dump file, **When** a reader checks its manifest entry, **Then** they find the
   exact command line, tool path, version and hash, input path and SHA-256, output SHA-256, size,
   line count, exit status and expected exit status, and generation date.
3. **Given** the manifest, **When** the documented generation script is rerun on the same input
   with the same tools, **Then** every dump's content hash is unchanged. Only the manifest fields
   documented as volatile may differ.

---

### User Story 2 - Know which tool to trust for which information (Priority: P1)

A researcher needs to know whether to believe `orbis-bin`, `orbis-readelf`, `orbis-objdump`, LLVM,
or GNU output for a given category, and which Orbis SDK version to use.

**Why this priority**: The user's working assumption (Orbis SDK 12 gives the best output) must be
confirmed or refuted with evidence before anyone builds on it.

**Independent Test**: The comparison document names one recommended tool and flag set per category,
with counts (named vs unnamed SCE values, entries listed vs expected, decoded vs raw) and short
excerpts. Each claim can be rechecked from the committed outputs.

**Acceptance Scenarios**:

1. **Given** the comparison document, **When** a reader looks up a category, **Then** it names the
   most accurate tool, the runners-up, and each tool's defects for that category, with evidence.
2. **Given** the four Orbis SDK versions, **When** their dump tools run on the same input, **Then**
   the document gives, per tool and flag set, whether the outputs differ (hash and diff line
   count). It also states whether SDK 12 is the best choice.
3. **Given** a defect claim (e.g. truncated dynamic section), **When** a reader checks it, **Then**
   it is backed by a count against the ELF's own header fields (e.g. `PT_DYNAMIC` size / 16).

---

### User Story 3 - Hand over to ddon-dwarf-reconstructor-rust (Priority: P2)

The ddon-dwarf-reconstructor-rust maintainers (human or agent) will later expose an SCE-aware
dumper. They read one handover package in this repository, shaped like their own Spec Kit
artifacts. From it they learn:

- what each external tool gets wrong;
- for each SCE structure, whether the reconstructor already decodes it, decodes it without
  exposing it, or does not decode it;
- the expected output of each proposed capability;
- the committed, machine-readable oracle file to test it against.

**Why this priority**: It is the long-term fix, but the reconstructor cannot be edited now because
other agents are working in it. The handover must be complete without this conversation, and must
fit the reconstructor's own planning conventions.

**Independent Test**: A reader with no prior context can derive from the handover alone a list of
proposals. Each proposal has a status (exists / exposed / missing), an expected output, and a
committed oracle file that runs on Linux CI without local-only data.

**Acceptance Scenarios**:

1. **Given** the handover, **When** a reconstructor maintainer reads it, **Then** each loss maps to
   a proposal with status, expected output, and oracle; each proposal cites reconstructor code
   observed read-only at a stated commit and date.
2. **Given** the reconstructor's existing dependence on the old `DDOORBIS.elf.objdump.zst` and
   other old dumps, **When** the handover is read, **Then** it states which new dump, if any,
   supersedes each one, and what format differences matter.

---

### User Story 4 - Additional static exports (Priority: P3)

A researcher benefits from static exports that do not exist yet:
- a function list and a data-object list;
- RTTI and vtable symbols;
- a decoded SCE version table;
- per-section and per-segment hashes;
- a source-file list;
- complete DWARF line tables;
- UTF-8 (Japanese) string constants;
- register-rule (CFA) and register-location information.

**Why this priority**: Useful, but only after the core dump set and comparison exist.

**Independent Test**: Each added export is listed in the index with its producer, and at least one
fact from it is in the pre-registered fact list.

**Acceptance Scenarios**:

1. **Given** the dump set, **When** a reader needs the callers of an import or the referents of a
   string, **Then** a committed export answers it, or the handover records it as a proposal.

### Edge Cases

- A tool crashes, hangs, or truncates on the 800 MB input (e.g. `orbis-addr2line` on large
  batches). The run is recorded with its exit status and partial size, never as passed.
- A tool exits non-zero by design: for example, `llvm-dwarfdump --verify` exits 1 when it finds
  errors. The expected exit status is recorded, and success is judged against it.
- An output exceeds 50 MB even compressed. It stays local-only per FR-010; the manifest still
  records it, and a committed summary or sample stands in for it.
- Two tools disagree on a value. Both outputs are kept, and the comparison records which side the
  ELF bytes support.
- A tool emits CRLF. Only line-final CRs are removed; other bytes are preserved.
- The ELF has no structure for a category (e.g. no aranges or pubnames; no ELF notes or symbol
  versioning). The category gets a `not-produced` entry with evidence.
- Windows path length: output paths stay under 260 characters.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dump set MUST be generated only from `DDOORBIS.elf` with SHA-256
  `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`, read in place. Nothing in
  `D:\research\DDON-binaries\IDA9.3\PS4_DDON_02020005_2016_12_21\` may be created, modified, or
  deleted, and no other folder under `D:\research\DDON-binaries\` is touched.
- **FR-002**: The dump set MUST cover every category in the committed category catalogue
  (`elf-dumps/categories.tsv`; initial content in `data-model.md`). The catalogue covers at least:
  - file, program and section headers, including SCE segment types;
  - the full dynamic table, including `DT_SCE_*`;
  - SCE dynlib data: modules, libraries, NIDs;
  - static and dynamic symbols; functions; data objects; RTTI/vtable symbols;
  - relocations (SCE RELA and JMPREL); RELRO/GOT contents; PLT stubs;
  - SCE version, process-param and comment data;
  - string constants (ASCII and UTF-8); stack sizes;
  - unwind and register rules; register locations;
  - every DWARF section present, plus a CU and source-file list, statistics and verification;
  - disassembly; per-section and per-segment hashes.
- **FR-003**: For each category, the dump set MUST hold the output of the tool the comparison
  ranks most accurate (`role: primary`). It MAY also hold other tools' outputs when they add
  unique information (`supplement`) or serve as evidence (`comparison`).
- **FR-004**: Every dump MUST have a manifest entry. It records:
  - the command line and categories;
  - the tool's path, version and SHA-256;
  - the input's path and SHA-256;
  - the output's content SHA-256, size and line count;
  - the exit status and expected exit status, plus a stderr summary;
  - the generation date.

  Derived files also list their input dump ids and hashes.
- **FR-005**: The dump set MUST be produced by committed automation. The automation:
  - checks every tool before doing any work;
  - writes only to a staging location inside the dump folder;
  - publishes atomically;
  - fails without publishing if the input folder changed during the run.
- **FR-006**: A comparison document MUST rank, per category, the tools that can produce it (Orbis
  SDK 12 tools, LLVM 23, and GNU binutils 2.47 where it applies), with counts and excerpts. It MUST
  also include an SDK-version matrix: the SCE-aware dumper across SDK 2.500, 3.500, 8.000 and
  12.000 per flag set, and a hash check of the binutils header and symbol outputs across the four
  SDKs. It MUST state whether the SDK 12 assumption holds.
- **FR-007**: A loss register MUST list each piece of information that external tools lose or
  misreport. Each entry has an ID, the affected structure, the evidence, the tools affected, the
  correct value or decoded form (marked *inferred* when derived), and an oracle. Producer quirks
  found by DWARF verification are listed separately from tool losses.
- **FR-008**: A handover package for ddon-dwarf-reconstructor-rust MUST be shaped like that
  project's Spec Kit artifacts: a draft spec (user stories, requirements, success criteria) and a
  research note, with unnumbered proposal labels. It MUST:
  - map each loss to a proposal with status exists / exposed / missing;
  - give each proposal an expected output and a committed machine-readable oracle;
  - cite reconstructor code observed read-only at a stated commit;
  - require no changes outside this repository.
- **FR-009**: A README in the dump folder MUST describe:
  - the layout and the index of categories to files;
  - the storage rule, and how to regenerate;
  - how to search compressed dumps without decompressing them;
  - for each old file beside the ELF, which new dump supersedes it and how the two differ. Old
    files are never deleted.
- **FR-010**: Storage: plain text up to 10 MB is committed as text, and larger outputs are
  committed compressed when the compressed file is at most 50 MB. Anything larger stays local-only
  (gitignored) with a full manifest entry. Each local-only dump has a committed stand-in: a
  statistic, an index, or a bounded sample.
- **FR-011**: The old exports' contents MUST be checked against the new ones (after ignoring the
  input-path line) and the result recorded in the README.
- **FR-012**: `AGENTS.md` and `readme.adoc` MUST point to the new dump set.
- **FR-013**: A fact list MUST be registered before the spot check (`elf-dumps/facts.tsv`).
  - At least one fact per category group in `categories.tsv` (headers, dynamic, symbols,
    relocations, sce, strings, stack, registers, dwarf, code), and at least two for `dwarf` (one
    info, one line).
  - Each fact gives its dump, its expected value, and an independent source: ELF bytes at a stated
    offset, or a different tool family. IDA alone does not count for DWARF-derived facts.
- **FR-014**: Derived files, built by joining, slicing, or reshaping tool output, MUST live in a
  separate `derived/` area with `kind: derived`, MUST name their inputs, and MUST mark any inferred
  content. A derived file may be a category's primary dump.
- **FR-015**: Every tool MUST read a hash-verified copy of the input held in the dump folder's
  staging area, never the input folder itself; ad-hoc checks (fact checks, comparison samples)
  MUST use the same copy.

### Key Entities

- **Category**: an information kind from the catalogue; maps to one primary dump (or a
  not-produced entry) and optional extras.
- **Dump**: one tool's output for one or more categories; identified by a stable id.
- **Manifest entry**: provenance for one dump, derived file, or not-produced category.
- **Loss**: information an external tool drops or misreports; links to evidence and an oracle.
- **Proposal**: a reconstructor capability derived from one or more losses, with status and oracle.
- **Fact**: a pre-registered spot-check item with an expected value and an independent source.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of catalogue categories map to a primary dump or a not-produced entry.
- **SC-002**: 100% of dumps have a complete manifest entry. A rerun leaves every dump's content
  hash unchanged; only volatile manifest fields differ.
- **SC-003**: The primary dynamic-table dump lists all 234 `PT_DYNAMIC` entries, and the primary
  program-header dump names all 11 segments, the 5 SCE types included.
- **SC-004**: Every fact in the registered fact list (at least 12 facts) agrees with its
  independent source.
- **SC-005**: Every loss links to evidence and an oracle, and 100% of losses map to a handover
  proposal or are recorded as out of scope.
- **SC-006**: Every file in the input folder has the same size, mtime and SHA-256 before and after
  each generation run, and no tool's working directory is the input folder.

## Assumptions

- The available tools are:
  - the Orbis SDK 2.500, 3.500, 8.000 and 12.000 host tools in `D:\SCE\ORBIS SDKs\`;
  - LLVM 23.1.3 and GNU binutils 2.47 in MSYS2.

  All four SDKs ship GNU binutils 2.22 with SCE patches. `orbis-bin` is Sony's own SCE-aware
  dumper.
- IDA 9.5 (via MCP) may be used read-only as an additional cross-check.
- ddon-dwarf-reconstructor-rust and ddon-hook are read, never edited.
- The PC client 03040008 binary is out of scope. ddon-hook's PC needs are noted as a follow-up in
  the handover only.
- The dump folder is `binaries/PS4_02020005/elf-dumps/`, next to the existing IDA exports.
- An x86-64 ELF has no register table. "Registers" means CFA and register rules from the unwind
  data, and register locations in DWARF location expressions.
- Background:
  - **Old dumps.** The undocumented dumps beside the ELF (`*.objdump.allheaders.txt`,
    `*.objdump.symbols.txt`, `*.readelf.headers.txt`, `*.readelf.symbols.txt`, `*.objdump.zst`,
    `*.llvmdwarfdump.zst`) name an older `IDA9.2\` input path. They record no command or version.
  - **SCE segments and tags.** `readelf` leaves 5 SCE segment types and 172 SCE dynamic tags
    unnamed, and `objdump -x` stops at the first `NEEDED` (26 of 234 entries).
  - **Relocations and DWARF.** Both report "no relocations". The DWARF dump has `.debug_info`
    only.
