# Regenerate the ELF dumps

This page is for anyone who must rebuild or check the static dump set of `DDOORBIS.elf`, the PS4 client of build PS4_02020005. You check the tools, verify or regenerate, and read the exit status. You need the Orbis SDK 12.000 under `D:/SCE/ORBIS SDKs/`, LLVM 23 in `C:/msys64/ucrt64/bin`, and the tools below in Git Bash. The option list is § 7 of [the set's README](../../binaries/PS4_02020005/elf-dumps/README.adoc#7-use-and-regeneration), and the formats are in [ELF dumps](../reference/elf-dumps.md).

## Tools

| Tool | Version | Categories |
| --- | --- | --- |
| `orbis-bin` (Orbis SDK 12.000) | 12.00.0.2 | SCE-specific structures: file and program headers, sections, the dynamic table and dynlib data, dynamic symbols and NIDs, relocations, stack sizes, `.sceversion`. It is the only tool that names the SCE segment types and dynamic tags and reads the SCE symbol and relocation tables. |
| `orbis-strings` (Orbis SDK 12.000) | binutils 2.22, Orbis 12.00.0.540 | String constants |
| LLVM: `llvm-readelf`, `llvm-objdump`, `llvm-dwarfdump`, `llvm-nm`, `llvm-objcopy` | 23.1.3 (MSYS2 ucrt64) | Static symbol table, section hex dumps, unwind tables, all DWARF sections, disassembly with source lines |
| `binaries/PS4_02020005/elf-dumps/tools/elfslice.py` | CPython 3.14, standard library only | Byte-level work: section slices, line-table extraction, hashes, string-reference join, disassembly index |

The script checks every external command before it does any work.

## Steps

Run from `binaries/PS4_02020005/elf-dumps/`.

1. Check tools and input; this writes nothing:

   ```bash
   ./generate-elf-dumps.sh --dry-run
   ```

   Success ends with `dry-run: tools and input OK, nothing written`.

2. To check what is published, re-hash it against the manifest, local-only dumps included:

   ```bash
   ./generate-elf-dumps.sh --verify
   ```

3. To regenerate, choose the scope:

   | Command | Scope | Time |
   | --- | --- | --- |
   | `./generate-elf-dumps.sh --skip-local` | committed files only | a few minutes |
   | `./generate-elf-dumps.sh --only 'dynsym.*'` | one id (glob) and everything derived from it | |
   | `./generate-elf-dumps.sh` | everything | about 70 minutes; the DIE tree dump takes about an hour |

   An interrupted publish finishes with `./generate-elf-dumps.sh --publish-run .staging/run-<stamp>`.

4. Read the exit status:

   | Status | Meaning |
   | --- | --- |
   | 0 | every entry is `ok` |
   | 2 | at least one dump failed, which is recorded in the manifest; the rest were published |
   | 1 | a precondition or the input guard failed, and nothing was published |

5. Regenerating without the local-only dumps must reproduce every committed file byte for byte, so `git status -- binaries/PS4_02020005/elf-dumps` lists nothing when no tool changed. Any file it lists needs a reason.

## What the script does

1. Copies the ELF to `.staging/input/DDOORBIS.elf` and checks its SHA-256.
2. Runs every tool in that directory, so outputs name the input only as `DDOORBIS.elf`.
3. Records name, size, mtime and SHA-256 of every file in the input folder before and after the run, and publishes nothing if anything changed.
4. Removes the line-final CR from the orbis tools' output; LLVM writes LF.
5. Hashes each output, applies the [storage rule](../reference/elf-dumps.md#storage), publishes only files whose content changed, and writes `manifest.jsonl` last.

## Two files the script does not produce

`--verify` re-hashes both, like every published file. After regenerating either, update the hashes of its manifest entry.

**Inlined call chains.** Run from the reconstructor's checkout (about 2 h 40 min at 16 jobs; 63,315 addresses took 2 h 2 min). `--append` answers only the addresses the file lacks and rewrites it in address order:

```bash
ddon-dwarf-reconstructor inline-dump 'D:\research\DDON-binaries\IDA9.3\PS4_DDON_02020005_2016_12_21\DDOORBIS.elf' --every-method --out dwarf/inline-chains.orbis-addr2line.tsv --jobs 16
```

**IDA's jump tables and no-return functions.** Run from the reconstructor's checkout after the IDA 9.5 database changes (about 30 s). Its `export.py` works through headless idalib on a private copy, opened without auto-analysis and closed without saving, so the database `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/DDOORBIS.elf.i64` is only read:

```bash
bash tools/ida/export.sh --out 'D:/ddon-data/binaries/PS4_02020005/elf-dumps/ida/functions.ida-9.5.jsonl'
```
