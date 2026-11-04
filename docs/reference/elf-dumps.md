# ELF dumps

Provenance, storage and verification of the static dump set of `DDOORBIS.elf` (PS4_02020005), and the format of its two files that are not produced by its script. It is for anyone who reads the set and must know where a file came from and how far to trust it. You need nothing first. [The set's README](../../binaries/PS4_02020005/elf-dumps/README.adoc) holds the input (§ 1), the file per category (§ 3), the preferred tool per question (§ 5) and the commands to search it (§ 7); [Regenerate the ELF dumps](../how-to/regenerate-elf-dumps.md) rebuilds it; [Structure of the PS4 ELF](ps4-elf-structure.md) describes the binary.

## Provenance

Each entry in `binaries/PS4_02020005/elf-dumps/manifest.jsonl` records:

- the categories, the command line, and the tool's path, version and SHA-256;
- the input hash;
- the output's content hash, size and line count;
- the exit status and the expected exit status, the run time and the date.

Derived files also list the ids and hashes of their inputs. They carry `inferred: true` when they hold a join rather than a decoded value. Three intermediate tool outputs (`symtab.llvm-nm` and two `.rodata` string extractions with slice-relative offsets) feed derived files. They are recorded with storage `staging` and are not published. `binaries/PS4_02020005/elf-dumps/categories.tsv` maps every category to its dump id. The manifest schema is `specs/001-ps4-static-dumps/contracts/manifest.schema.json`.

## Storage

| Dump | Stored as |
| --- | --- |
| Text up to 10 MiB | committed as is (`.txt`, `.tsv`, `.json`) |
| Larger text | committed zstd-compressed (`-19 --long=27`) if the result is 50 MiB or less |
| The two multi-GB dumps (DIE tree, disassembly) | in `binaries/PS4_02020005/elf-dumps/local/`, which is gitignored (zstd `-10`) |

The DIE tree is summarized by the committed compile-unit list and statistics, the disassembly by a per-function index in `derived/`. A file's identity is the SHA-256 of its uncompressed content (`output.sha256`). Sizes and counts of the set are in [Status](status.md#elf-dump-set-ps4_02020005).

## Inline chains

`binaries/PS4_02020005/elf-dumps/dwarf/inline-chains.orbis-addr2line.tsv`, plain text (about 27 MiB), written by the reconstructor's `inline-dump`.

| Part | Content |
| --- | --- |
| Header (format 2) | the format; the ELF's and the tool's SHA-256; the tool's path and version line; the flags (`-a -f -i -e <ELF> <address>`); "one address per run"; the record count; `records_sha256`, the SHA-256 of the records as rendered, which the reconstructor checks on load, so an edited record fails closed |
| Records | one tab-separated line per address in address order: addr2line's function and location pairs verbatim, innermost first |

No date, so the same inputs give the same bytes.

The addresses are every address the reconstructor's inline check reads for any bundle: each inlined function's first copy (by caller address and range), at its first range, over the whole ELF (`inline-dump --every-method`), 94,568 addresses: 30,904 from the bundle `golden/029-t11`, 349 appended for later bundles, 63,315 for the rest of the ELF. A growing bundle adds no address, so `validate` runs `orbis-addr2line` live only for a changed reconstructor rule. Why one address per run: [the explanation](../explanation/ps4-elf.md#why-inlined-chains-come-from-one-address-per-run). The reconstructor's records of these measurements are its `spec 029 plan-P23` step 1 and `spec 026 plan-P148`.

## IDA export

`binaries/PS4_02020005/elf-dumps/ida/functions.ida-9.5.jsonl`, JSON lines (about 10 MiB), written by the reconstructor's `export.py`.

| Line | Content |
| --- | --- |
| Header | the format (1), the tool, the ELF's SHA-256 (the export refuses a database of another input), the database's path and SHA-256, IDA's version |
| One per IDA function, in address order | its start; its `FUNC_NORET`; its switches (jump, table address, element size, case count, the sorted case targets); its direct calls to `FUNC_NORET` callees |

Use: corroboration only. The reconstructor's `validate --ida-export` (or `DDON_IDA_EXPORT`) compares it with its own analysis of every body and reports the counters `ida.noret_fallthrough`, `ida.noret_only_lift` and `ida.switch_differ`, which gate nothing (its `spec 026 P23, P25`).

## Verification

| Check | What it does |
| --- | --- |
| Spot checks | 16 values, at least one per category group, against the raw ELF bytes or a second tool family: the entry point, a program header type, a section header, dynamic-table sizes, a symbol, a string, a stack-size entry, a CFA rule, a compile unit, a line entry and the compile-unit count among them. All agree, at the date of the dump set. |
| Reproducibility | regenerating without the local-only dumps reproduces every committed file byte for byte |
| Integrity | `./generate-elf-dumps.sh --verify` re-hashes every published file, including the local-only ones, against the manifest |
| Input | the snapshot of the input folder is compared before and after every run |

The last runs are in [Status](status.md#elf-dump-set-ps4_02020005).
