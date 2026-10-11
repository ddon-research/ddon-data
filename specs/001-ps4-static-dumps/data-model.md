# Data model: PS4 02020005 static ELF dump set

## Category (`elf-dumps/categories.tsv`)

Columns: `category`, `group`, `description`, `primary` (the id of a dump, or `not-produced`), `reason`
(required when the category is not produced).

| Group | Categories |
|---|---|
| headers | `file-header`, `program-headers`, `sections`, `section-sizes`, `section-segment-map`, `section-hashes`, `segment-hashes` |
| dynamic | `dynamic`, `dynlib`, `dynsym`, `dynstr` |
| symbols | `symtab`, `functions`, `data-objects`, `rtti-vtables`, `plt-stubs` |
| relocations | `relocations`, `relro-got`, `ctors`, `string-refs` (derived, inferred) |
| sce | `sce-version`, `sce-process-param`, `sce-comment`, `prodg-metadata` |
| strings | `strings-rodata`, `strings-rodata-utf8`, `strings-all` |
| stack | `stack-sizes` |
| registers | `unwind-cfa`, `register-locations`, `register-usage` (derived) |
| dwarf | `dwarf-cu-list`, `dwarf-source-files`, `dwarf-info`, `dwarf-abbrev`, `dwarf-line`, `dwarf-line-gaps`, `dwarf-loc`, `dwarf-ranges`, `dwarf-str`, `dwarf-frame`, `dwarf-statistics`, `dwarf-verify`, `dwarf-section-sizes`, `dwarf-aranges`, `dwarf-pubnames`, `dwarf-pubtypes`, `dwarf-index` |
| absent | `elf-notes`, `symbol-versioning` |
| code | `disassembly`, `disassembly-orbis`, `everything` |

The categories `dwarf-aranges`, `dwarf-pubnames`, `dwarf-pubtypes`, `dwarf-index`, `elf-notes` and
`symbol-versioning` are expected to be `not-produced`, because those structures are absent from
the ELF (research R1). The `reason` column cites the evidence dump that shows this, such as
`--show-section-sizes` or `llvm-readelf -n -V`.

## Dump and manifest entry (`elf-dumps/manifest.jsonl`)

There is one JSON object per line. The schema is `contracts/manifest.schema.json`. Every entry
has a `kind`; produced entries also have a `role` (`primary`, `supplement`, `comparison`).

| `kind` | Required fields |
|---|---|
| `meta` (id `run.meta`, first line) | `id`, `kind`, `generated`, `zstd_version`, `python_version`, `uv_version`, `script_sha256`, `volatile[]` |
| `tool` | `id`, `kind`, `categories[]`, `role`, `file`, `storage`, `tool{name,path,version,sha256}`, `argv[]`, `cwd`, `input{path,sha256,size}`, `output{sha256,size,lines,stored_size}`, `stderr{file,lines,first}`, `exit`, `expected_exit`, `status`, `seconds`, `generated` |
| `derived` | as `tool`, where `tool` is the helper (`elfslice.py` + Python version), plus `inputs[]` (`{id, sha256}`) and `inferred` (bool) |
| `not-produced` | `id`, `kind`, `categories[]`, `reason`, `evidence` (dump id), `generated` |

**Fields**

- `id`: `<category>.<tool>[.<variant>]`, for example `dynamic.orbis-bin` or `dwarf-line.derived`.
- `storage`: `txt`, `zst` or `local` (FR-010). `file` is relative to `elf-dumps/`.
- `status`: `ok` when `exit == expected_exit`, `failed` otherwise, and `timeout` for exit 124.
  - A `failed` or `timeout` entry never counts as a category's primary, whatever its `role`.
- `input.path` is the staged copy (`.staging/input/DDOORBIS.elf`); `input.origin` records the
  original path.
  - `expected_exit` defaults to 0. `llvm-dwarfdump --verify` uses 1.
- `output.sha256`: the hash of the decompressed content after line-final CRs are stripped. It is
  the content identity.
- Volatile fields: `generated`, `seconds`, `stderr.first`. The rerun check ignores them.
- `tool.version`: the first line of `--version`, or `orbis-bin -ver`. Run-wide versions (zstd,
  Python, uv) live in the `run.meta` entry.

## Loss (`elf-dumps/LOSSES.adoc`)

| Field | Rule |
|---|---|
| `id` | `L-NN`, stable once published |
| kind | `tool-loss` (a tool drops or misreports data) or `producer-quirk` (the DWARF itself is unusual, found by `--verify` or by the gap scan) |
| structure | the affected ELF/DWARF structure |
| tools | the tools and versions affected |
| evidence | a count against an ELF header field, or an excerpt, with the dump id |
| correct form | the value from the best tool or the ELF bytes; marked *inferred* if derived |
| oracle | a committed file id, or an ELF byte range |
| proposal | `ddon-data-P<n>`, or `out-of-scope` with a reason |

## Proposal (`elf-dumps/handover/spec.md`)

`ddon-data-P<n>`: title, linked losses, status (`exists` / `exposed-gap` / `missing`),
reconstructor code (path:line at commit `<sha>`), proposed output (text that mirrors orbis-bin,
plus JSONL), oracle files (`elf-dumps/oracles/*.tsv|jsonl`, committed, small, fixed-width hex),
and acceptance check.

## Oracle (`elf-dumps/oracles/`)

These are small, machine-readable extracts of primary dumps, sized for Linux CI. Examples:
- `dynamic.tsv` (234 rows: tag, value, name);
- `phdrs.tsv`;
- `relocations-sample.tsv` (a fixed stratified sample of every type);
- `dynsym.tsv` (650 rows: NID, name, library, module);
- `stack-sizes-sample.tsv`;
- `line-sample.tsv` (address → file:line for a fixed address set);
- `string-refs-sample.tsv`.

Each oracle is listed in the manifest with `kind: derived` and its inputs, and stays under 5 MB.

## Derivation map

The generator holds one table `id → input ids`. `--only <glob>` expands to the matching ids plus
every id that transitively depends on them.

## Fact (`elf-dumps/facts.tsv`)

Columns:
- `fact_id`, `group`, `question`, `dump_id`, `expected`;
- `independent_source`: either `elf:<offset>:<len>` or `tool:<name> <args>`;
- `result` (`agree` / `disagree` / `not-run`), `checked` (date).

There are at least 12 rows, at least one per category group except `absent`, and two for `dwarf`.
They are registered (committed or time-stamped) before the check runs.

## SDK comparison row (`elf-dumps/compare/sdk-matrix.tsv`)

Columns: `tool`, `flags`, `sdk`, `exit`, `output_sha256`, `size`, `lines`, `diff_lines_vs_12000`.
