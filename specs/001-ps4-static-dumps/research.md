# Research: PS4 02020005 static ELF dump set

## Scope of this evidence

- **Input**: `D:/research/DDON-binaries/IDA9.3/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf`, SHA-256
  `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`, 800,622,848 bytes.
- **Date**: all measurements were taken on 2026-10-11, in three passes: a pilot, a feasibility
  review, and a consistency review.
- **How it was measured**: output was streamed into `wc`, `zstd | wc -c`, `sha256sum` or short
  excerpts. No numbers here are backed by a committed file yet. Implementation re-measures every
  count it publishes.
- **Inputs not modified**: after every tool run, the input folder's listing matched the
  session-start listing, and the ELF hash was unchanged.

## R1. ELF identity

- `e_type` 0xFE10 is **ET_SCE_DYNEXEC** ("Main module - ASLR", `orbis-bin -dh`).
- Basic layout: OSABI 9 (FreeBSD), x86-64, entry point 0xd5a8d0, 11 program headers and 36
  sections, with the section-name table at index 33.
- Every tool reads the plain ELF; none needs a SELF or PRX container.
- **DWARF**: version 4, DWARF32, producer `clang version 3.5.0 (PS4 clang version 2.50.0.2333)`,
  2305 CUs, 2305 distinct `DW_AT_stmt_list` values.
  - Sections present: `.debug_info` 671.6 MB, `.debug_loc` 37.6 MB, `.debug_line` 16.6 MB at file
    offset 0x2a9c36c9 (size 0xfd2479), `.debug_ranges` 10.0 MB, `.debug_abbrev` 4.6 MB,
    `.debug_str` 3.7 MB, `.debug_frame` 432 B.
  - Absent: aranges, pubnames, pubtypes, apple_*, debug_names, gdb_index, macro, rnglists,
    loclists, types.
- **Not present**: ELF notes, GNU symbol versioning (`llvm-readelf -n -V` prints nothing), and
  `.note.GNU-stack` (size 0).
- **SCE sections**:
  - `.sceversion`: 99 KB, a component/SDK version table;
  - `.sce_process_param`: `ORBI` magic;
  - `.prodg_meta_data`;
  - `.sce_special`: 4 MB, dynlib data;
  - `.sce_stack_sizes`;
  - `.ctors`: 0x9878 bytes.
- **RELRO**: `PT_SCE_RELRO` (program header 1) holds `.data.rel.ro` (0x19e5d0), `.got` (0x368)
  and `.got.plt` (0x10f0).

## R2. Tool inventory

| Tool set | Location | Version |
|---|---|---|
| Orbis SDK 2.500, 3.500, 8.000, 12.000 binutils | `D:/SCE/ORBIS SDKs/<ver>/host_tools/bin/orbis-{objdump,readelf,nm,addr2line,strings,c++filt}.exe` | GNU Binutils 2.22 + SCE patches (`PS4 version 2.50.0.2516` … `Orbis 12.00.0.540`) |
| orbis-bin | same folder | 2.50.0.1952 … 12.00.0.2 |
| LLVM | `C:/msys64/ucrt64/bin/llvm-{readelf,readobj,objdump,dwarfdump,nm,addr2line,objcopy}.exe` | 23.1.3 |
| GNU binutils | `C:/msys64/ucrt64/bin/{objdump,readelf}.exe` | 2.47 (comparison only) |

- `orbis-bin` is Sony's own SCE-aware dumper. Its docs are in
  `D:/SCE/ORBIS/documentation/chm/en/extracted/en/System/Compiling_Linking_and_Building/Build_Utilities-Users_Guide/`.
- `orbis-bin` version: `-ver`, not `-h`, which fails with "Switch 'h' not found".
- `orbis-bin` switch syntax: switches that take a value need the long form, e.g.
  `--dump-sections=X`, `--addr2line=X`; the short forms `-ds=` and `-a2l=` are rejected.
- `orbis-bin -o/--outfile` exists. Never use it, because it could write next to the input.
- Help texts were captured to the session scratchpad. Implementation copies the ones it uses into
  `elf-dumps/tool-help/`.

## R3. Is Orbis SDK 12 the best choice?

**Decision**: Yes for `orbis-bin`. For the SDK binutils the choice makes no difference.

**Rationale**:
- **binutils**: the four SDKs ship four different builds of GNU 2.22 (different hashes and
  sizes). Their help texts are identical, and the header and symbol outputs that were compared are
  byte-identical across all four; disassembly, addr2line and DWARF output were not compared.
  (Corrected after the reconstructor's review, 2026-10-11.)
- **`orbis-bin` NID resolution**: with `-v`, 3.500 and later resolve all 648 imported NIDs to
  names; 2.500 resolves none. (Corrected after implementation: the pilot's "105 unresolved" came from
  the non-verbose output, which maps imports to *static* symbol names and leaves the 105 imports
  that have no static symbol.)
- **`orbis-bin` other differences in 12.000**: it adds an ABI Version line, uses a newer
  demangler, and its `-de` output is 7,340 bytes larger.

**Alternatives**:
- SDK 2.500, which matches the game's era. It is worse at NID resolution.
- SDK 8.000. The knowledge graph pins its `orbis-objdump`; its header and symbol output matches
  12.000's.

## R4. Best tool per category (feeds `categories.tsv`)

| Category | Primary | Evidence | Rejected / notes |
|---|---|---|---|
| File header | `orbis-bin -dh` | Names ET_SCE_DYNEXEC and the ABI version | readelf: `OS Specific: (fe10)` |
| Program headers | `orbis-bin -dph` | Names all 5 SCE types | readelf, GNU and LLVM leave them unnamed; orbis-objdump leaves RELRO raw |
| Sections | `orbis-bin -dsh` + `llvm-readelf -S -W` (flags) | Both list the same 36 sections | |
| Section ↔ segment map | `orbis-bin -dfl` (file) and `-dml` (memory) | | `-dml` puts `.interp`/`.init` under DYNAMIC (L-xx); `-dfl` prints phdr numbers without types, so it needs a join with `-dph` |
| Dynamic table, dynlib | `orbis-bin -ddy` | All 234 entries, with named NEEDED, NEEDED_MODULE, IMPORT/EXPORT_LIB (+ATTR), FINGERPRINT, ORIGINAL_FILENAME, MODULE_INFO | objdump: stops at NEEDED (26/234); readelf: 172 unnamed tags; LLVM: `<unknown:>` |
| Dynamic symbols, NIDs | `orbis-bin --dump-dynsym -v`, `--dump-dynstr` | 650 entries; all 648 NIDs resolved (with `-v`); 2,600 lines | No other tool shows any |
| Relocations | `orbis-bin -r` | 172,943 entries, 7 lines each: 171,734 RELATIVE, 668 `R_X86_64_64`, 2 GLOB_DAT, 539 JUMP_SLOT | Every other tool shows none |
| RELRO/GOT contents | `llvm-objdump -s -j .data.rel.ro -j .got -j .got.plt` | 6.68 MB; only 4,586 of 106,080 lines are non-zero | The slots hold 0 on disk; the targets live in the `-r` addends (R10) |
| PLT stubs | Subset of the symtab: `/PL*` (539), `/PG*` (539), `/G*` (about 105), `/GC*` (4) | | |
| symtab | `llvm-readelf -s -W` (mangled) + `orbis-bin -dsy -v` (demangled, 822,952 lines) | 205,738 entries | GNU objdump `-t`: values shifted (R6) |
| Functions, data objects, RTTI/vtables | Subsets of `llvm-nm -C -S --defined-only -n` (t/T; d/D/b/B/r/R) and of `llvm-readelf -s` (`_ZTV`, `_ZTI`, `_ZTS`) | | |
| SCE version table | `orbis-bin --dump-sections=.sceversion` | Decodes a component/SDK table (71 lines) | |
| Process param, prodg metadata, comment | `llvm-objdump -s -j .sce_process_param -j .prodg_meta_data`, plus hex of the SCE Comment segment (from the `-dph` offsets) | | Not decoded; becomes a handover proposal |
| `.ctors` | `llvm-objdump -s -j .ctors` + its `-r` entries | About 154 KB of hex | |
| Strings (ASCII) | `orbis-strings -a -t x` on the `.rodata` range, piped from stdin and rebased (vaddr = 0x1bea460 + offset) | 44,527 strings, 1.31 MB | GNU `strings`: identical counts |
| Strings (UTF-8/SJIS) | `orbis-strings -a -t x -e S` on `.rodata`, rebased | 81,798 strings; at least 931 are real UTF-8 Japanese, about 650 more look like Shift-JIS | The 7-bit default misses all of them (loss) |
| Strings (whole file) | `orbis-strings -a -t x` | 1,349,746 strings, 33.5 MB (6.6 MB zst) | |
| Stack sizes | `orbis-bin -dss` | 120,888 lines | The only reader of `.sce_stack_sizes` |
| Unwind and register rules | `llvm-readelf --unwind` (`.eh_frame`, CFA rules such as `DW_CFA_def_cfa: RSP +8`) | 47.8 MB, 2.1 MB zst | `llvm-dwarfdump --debug-frame`: same data |
| Register locations | `llvm-dwarfdump --debug-loc` (`DW_OP_reg5 RDI`) + a derived register-usage count (R13) | | `DW_AT_location`/`frame_base` are only in the local-only info dump |
| Address → line oracle | `orbis-addr2line -i` (inline chain); `orbis-bin --addr2line=<a,b,…>` (single file/line) | At 0x194d8f0, where 1,014 CUs overlap, `orbis-addr2line -i` matches the DIE tree (corrected after the reconstructor's review) | `llvm-addr2line` returns `??:0` there; the `orbis-addr2line` batch crash is quoted from the reconstructor, not reproduced |
| DWARF CU list, source files | `llvm-dwarfdump --debug-info --recurse-depth=0` | 2305 CUs, 6.0 MB, 1.9 s | |
| DWARF line | Derived: contiguous copy, then `llvm-dwarfdump --debug-line` (R7) | 2305 tables, 1,679,315 rows, 178 MB raw / 5.9 MB zst | Sequential readers fail |
| DWARF loc/ranges/abbrev/str | `llvm-dwarfdump --debug-<sec>` | Compressed: 6.26 / 1.5 / 0.5 / 1.4 MB | |
| DWARF statistics, verify, section sizes | `llvm-dwarfdump --statistics`, `--verify` (exit 1 expected; 21.0 MB, 0.67 MB zst), `--show-section-sizes` | | |
| DWARF info | `llvm-dwarfdump --debug-info -v` | About 1.1 GB zst | Local-only; stand-ins are the CU list and statistics |
| Disassembly | `llvm-objdump -d -l --demangle -w` | 578 MB, 65 MB zst, 37 s; correct PLT/GOT names | Local-only; orbis-objdump `-l` takes >600 s; GNU labels are wrong |
| Disassembly (reconstructor-compatible) | `orbis-objdump -d -w` (no `-l`) | Same format as the old `objdump.zst` that the reconstructor's agreement test parses | Local-only; size measured at run time |
| Everything | `orbis-bin -de` | 4.24 GB, 969 MB zst | Local-only, as a supplement |
| Section and segment hashes | Derived: SHA-256 of each file range, from the `-dsh`/`-dph` offsets | | |

## R5. Machine-readable headers

`llvm-readobj --elf-output-style=JSON` (28.7 KB) is valid JSON once stderr is kept separate. It is
committed as a supplement; SCE values appear as numbers (`"Unknown",1627389968`), which the README
maps to the orbis-bin names.

## R6. GNU binutils 2.47 symbol shift

BFD doesn't recognise the e_type, so it adds the section VMA to every symbol value. `_start` is
reported at 0xd5a970 instead of 0xd5a8d0 (+0xa0, the `.text` VMA), and disassembly labels point
at the wrong functions. The SDK's patched BFD and LLVM are not affected. GNU output is kept only
as one bounded comparison sample.

## R7. `.debug_line` is not contiguous

**Finding**: there is a gap after every line table:
- 318 one-byte gaps (for example 0x62 at 0x1fd);
- 169 seven-byte gaps;
- many zero runs of 34–98 bytes;
- 14 gaps that start with non-zero bytes.

A sequential walk, as done by `llvm-dwarfdump --debug-line` or GNU `readelf -wl`, fails after 3
units. `--debug-line=<off>` doesn't help: it only filters the sequential walk, and if the option is
repeated, the last one wins.

**Decision**: a small helper (R13) does the following.
1. Read every `DW_AT_stmt_list` from the committed CU list.
2. Copy each table's bytes `[stmt_list, stmt_list + 4 + unit_length)` from the ELF into a contiguous
   scratch file in staging.
3. Wrap that file in an ELF with `llvm-objcopy -I binary -O elf64-x86-64 --rename-section
   .data=.debug_line,contents,readonly`.
4. Run `llvm-dwarfdump --debug-line` on it.

The output is `derived/` (FR-014). It is committed alongside a map from original to copied offset
and the gap list (offset, length, first bytes). The feasibility test gave 2305 tables, 1.35 s, and
empty stderr. The bytes are copied, not changed.

**Alternative**: patching the gaps in place. Rejected; there is no need to change any byte.

## R8. Storage

- **Rule (FR-010)**: committed `.txt` up to 10 MB; committed `.txt.zst` when it compresses to
  50 MB or less; otherwise `local/`.
- **Committed size**: measured compressed sizes are 0.1–6.6 MB per file, about 40 MB in total.
- **Local-only**: `orbis-bin -de`, `llvm-dwarfdump --debug-info -v`, `llvm-objdump -d -l`, and
  `orbis-objdump -d -w`.
- **Compression**: zstd `-19 --long=27` for committed files, and `-10 --long=27 -T0` for local
  files.
- **Identity**: a file is identified by the SHA-256 of its decompressed, normalised content, and
  the zstd version is recorded. A rerun with an identical content hash keeps the existing `.zst`,
  so git sees no change.

## R9. Byte-stable output

- **Relative input path**: tools run with the input folder as the current directory and the
  argument `DDOORBIS.elf`. They read only; stdout and stderr go to staging. The output then
  contains no input path. The only absolute paths left are the `W:/Build/...crt*.c` file-symbol
  names, which are content.
- **Determinism**: two runs of each orbis-bin flag gave identical SHA-256s.
- **Line endings**: orbis-* tools print CRLF and MSYS2 LLVM prints LF. Only line-final CR is
  stripped, streaming (`sed 's/\r$//'`; `sd` would load whole files into memory); there are no lone `\r` bytes in the strings output.
- **`.gitattributes`** in `elf-dumps/`: `*.txt text eol=lf`, `*.tsv text eol=lf`,
  `*.jsonl text eol=lf`, `*.zst binary`.
- **Volatile manifest fields**: `generated`, `seconds`, and `stderr.first` when it contains
  timings. These are declared in the README and ignored by the rerun check.

## R10. RELRO/GOT contents and string constants

- **Where the targets are**: relocated slots hold 0 on disk; the target is the relocation addend.
  The reconstructor's `relocations.rs` header says the same.
  - The 171,734 RELATIVE entries give slot → target for all of RELRO.
  - The 539 JUMP_SLOT and 2 GLOB_DAT entries give the import slots.
- **Hex dumps**: the RELRO hex dump is small (98 KB zst). It is kept to show the zeros and the
  few non-relocated constants.
- **Derived string-reference table** (`derived/`, *inferred*): RELATIVE relocations whose addend
  equals the start of a rebased `.rodata` string. Code references (RIP-relative `lea`) need
  disassembly and are left to the handover proposal.
- **Check**: ten entries are verified against IDA MCP and the ELF bytes.

## R11. The reconstructor today (read-only, commit `f8a155d5`, 2026-10-11)

- **Inputs**: it reads the ELF directly (gimli 0.34, object 0.40).
- **Existing SCE code** in `crates/reconstructor-storage/src/sce/`:
  - `mod.rs`;
  - `dynlib.rs`: dynlib data;
  - `nid.rs`: NIDs; it checks that all 539 `/PL` stubs hash to their JMPREL NIDs;
  - `relocations.rs`: RELA/JMPREL; it applies RELRO pointers;
  - `stack_sizes.rs`: spec 022 task T411;
  - `symbols.rs`: GOT, `/G`, `/PG`, `/PL` slots and data symbols; spec 022 task T358.
- **Not found**:
  - a `debug_line`/LineProgram reader;
  - SCE phdr and DT naming as a dump;
  - PROCPARAM, `.sceversion`, and string-reference decoding;
  - a `dump` CLI surface.
- **Dump inputs**:
  - `DDOORBIS.elf.objdump.zst`, through `DDON_OBJDUMP_ZST`, for the iced-x86 agreement test. That
    test parses orbis-objdump `.text` lines, so a reconstructor-compatible `orbis-objdump -d -w`
    dump is kept (R4).
  - the IDA `.h`, through `DDON_IDA_HEADER`.
- **Live tools**: SDK 12 `orbis-objdump` and `orbis-addr2line`, located through
  `SCE_ORBIS_SDK_DIR` and `SCE_ORBIS_COMPARE_SDK_DIR`.
- **Conventions**:
  - It runs Spec Kit: `.specify/`, `specs/001–028`, `specs/orchestration.md`.
  - The coordinator owns spec and task numbers, and agents label proposals `<package>-P<n>`.
  - Inferences are marked per `docs/reference/markers-and-inferences.md`.
  - CI runs on Linux, so oracles must be small committed files, not local-only dumps.
- **Decision**: write the handover as an unnumbered draft spec plus research note, with proposal
  labels `ddon-data-P<n>`. Rate each proposal *exists* (decoded and exposed), *exposed-gap*
  (decoded in the library but not dumped), or *missing*. Re-read and cite the reconstructor files
  at implementation time.
- **Other consumers**:
  - The knowledge graph pins SDK 8.000 `orbis-objdump` and the old llvmdwarfdump index. Changing
    that is a follow-up, not part of this feature.
  - ddon-hook (PC) is a follow-up.

## R12. Input guard

**Staged copy**: the generator copies the ELF once into `elf-dumps/.staging/input/DDOORBIS.elf`,
verifies its SHA-256, and reuses it while the hash matches. Every tool runs with the current
directory in staging and reads that copy; nothing runs with the input folder as its working
directory. Hardlinks were rejected: creating one updates the original file's metadata.

Before and after each run, the script writes the name, size, mtime and SHA-256 of **every** file in
the IDA9.3 PS4 folder to `input-snapshot.{before,after}.tsv`, about 2.4 GB of hashing, ~10 s. The
run publishes nothing if the two differ.

## R13. Language choice

**Decision**: bash orchestrates the run. One stdlib-only Python helper,
`elf-dumps/tools/elfslice.py`, is a PEP 723 script (`# /// script` with `requires-python = ">=3.14"`,
no dependencies) run as `uv run --no-project --python 3.14 --script tools/elfslice.py`. That
satisfies the constitution's "uv-managed Python on CPython 3.14" and avoids the legacy root
`.venv`. It does these byte-level jobs:
0. byte-range slicing of the input for tools that read stdin (`slice`; avoids the SIGPIPE 141
   that `tail | head` returns under `pipefail`);
1. the `.debug_line` slicing and gap list (R7);
2. section and segment SHA-256s;
3. the string-reference join and register-usage count.

**Rationale**:
- Byte offsets and a join over 172k relocations against 44k strings are fragile in awk.
- The constitution allows Python on CPython 3.14.
- A PEP 723 script is the smallest uv-managed form; it needs no `pyproject.toml`.

**Alternative**: pure bash with `dd`. Rejected as error-prone.

## R14. SDK comparison scope

- **`orbis-bin` matrix**: run across all four SDKs for `-dh -dph -dsh -ddy --dump-dynsym -v
  --dump-dynstr -dsi -dml -dfl -dss -dsy -v -r`, excluding `-de`.
- **binutils hash check**: run across all four SDKs for `orbis-objdump -p`, `-h`, `-t -C`, and
  `orbis-readelf -h -l -S -d -W`, `-s -W`.
- **Output**: `compare/sdk-matrix.tsv` with hashes and diff line counts, plus copies of differing
  outputs ≤ 10 MB.
- **Run time**: a few minutes, since every step except `-dss` and `-dsy` takes under 1 s.
