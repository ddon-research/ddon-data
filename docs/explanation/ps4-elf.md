# Structure of the PS4 ELF

This page is for a reverse engineer who knows ELF and DWARF and is about to read `DDOORBIS.elf`, the PS4 client executable of build PS4_02020005, or a tool's output on it: what is unusual about the file and what to expect from its dumps. You need nothing first; the input's hash and the files per category are in [the dump set's README](../../binaries/PS4_02020005/elf-dumps/README.adoc), and the formats of the dumps in [ELF dumps](../reference/elf-dumps.md). The numbers describe that one fixed input, SHA-256 `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`.

## Program headers and sections

Five of the 11 program headers have SCE types:

| Index | Type | Contents |
| --- | --- | --- |
| 1 | `PT_SCE_RELRO` (0x61000010) | `.data.rel.ro` (0x19e5d0 bytes), `.got` (0x368), `.got.plt` (0x10f0) |
| 3 | `PT_SCE_PROCPARAM` (0x61000001) | `.sce_process_param`, 0x40 bytes: size 0x40, magic `ORBI`, SDK version 0x02508051 at offset 0x10 |
| 8 | `PT_SCE_DYNLIBDATA` (0x61000000) | `.sce_special`: the SCE string, symbol, hash and relocation tables (0x3fdef0 bytes) |
| 9 | SCE Comment (0x6FFFFF00) | `.prodg_meta_data`, 0x4c bytes |
| 10 | SCE Version (0x6FFFFF01) | `.sceversion`: component and SDK version table |

The remaining six are two loadable segments, `PT_DYNAMIC`, the interpreter, TLS (empty) and
`PT_GNU_EH_FRAME`. Section totals: text 29,271,064 bytes, data 1,879,376, read-only data
7,797,911, bss 1,098,256.

## Dynamic linking

- `PT_DYNAMIC` holds 234 entries. Library names, symbols and relocations are reached through
  `DT_SCE_*` tags that point into the dynlib data, not through `DT_STRTAB` and `DT_SYMTAB`.
- The module declares 50 `DT_NEEDED`, 50 `DT_SCE_NEEDED_MODULE` and 51 `DT_SCE_IMPORT_LIB`
  entries. Each import library has an `_ATTR` entry, such as `AUTO_EXPORT|LOOSE_IMPORT`. There is
  one export library, `DDOORBIS`.
- The table also records a fingerprint and the original file name
  `D:/publishDDO_PS4_02_02_Master/DDO_02_02/DD_ONLINE/DDOORBIS.elf`.
- The SCE dynamic symbol table has 650 entries (`DT_SCE_SYMTABSZ` 15,600 / 24). 648 are imports
  named by NID, such as `Gl6w5i0JokY#0O#o`. `orbis-bin --dump-dynsym -v` resolves the library and module
  of all 648 and the function name of 543. The other 105 stay `<Unknown NID: ...>`
  (`rg -c '<Unknown NID' symbols/dynsym.orbis-bin.txt`), and no relocation references them.

## Symbols

- `.symtab` has 205,738 entries: 125,352 functions (types t/T), 76,752 data objects
  (d/D/b/B/r/R), and section, file and absolute symbols.
- 14,583 symbols are vtables (`_ZTV`). There is no C++ RTTI: `symbols/rtti-vtables.derived.txt`
  has no `_ZTI` or `_ZTS` symbol, which fits the SDK's `-fno-rtti` default.
- The linker adds 1,187 stub symbols:
  - `/PL<name>`: 539 PLT stubs, one per JMPREL slot;
  - `/PG<name>`: 539 PLT GOT slots;
  - `/G<name>`: GOT slots, including the `/GCALLBACK_…` data pointers.

## Relocations and pointer data

- `DT_SCE_RELA` holds 172,404 relocations:
  - 171,734 `R_X86_64_RELATIVE`;
  - 668 `R_X86_64_64`: 667 `__cxa_pure_virtual` entries in vtables, plus `Need_sceLibc`;
  - 2 `R_X86_64_GLOB_DAT`: `__stack_chk_guard` and `std::nothrow`.
- `DT_SCE_JMPREL` holds 539 `R_X86_64_JUMP_SLOT` relocations.
- In the file, every RELA slot is zero. The pointer value exists only as the relocation addend
  (RELATIVE) or as the symbol (64, GLOB_DAT). So the hex dump of `.data.rel.ro` is mostly zeros:
  only 4,586 of its 106,080 lines are non-zero.
- The 539 `.got.plt` slots are not zero. Each holds the lazy-binding address inside its PLT stub.
  For example, the slot for `strlen` at 0x24fa958 holds 0x1be82b6, inside `/PLstrlen` at
  0x1be82b0.
- **Inferred**: 2,655 RELATIVE slots point at the start of a `.rodata` string
  (`string-refs.derived.tsv`). Code references (RIP-relative operands) and strings shorter than 4
  bytes are not included.

## Strings

- `.rodata` contains 44,527 7-bit strings of 4 or more characters.
- The 8-bit extraction finds 81,798 strings, of which 50,254 contain a byte >= 0x80:
  - 2,050 are valid UTF-8 (Japanese UI text such as `キャンセル`);
  - 26,252 decode as cp932, which accepts most byte pairs;
  - 21,952 decode as neither.

  Many of these are binary data, such as float constants, not text.
- The whole file yields 1,349,746 strings (`strings-all`, listed by file offset).

## Stack sizes

- `.sce_stack_sizes` holds 241,724 entries, each a u64 address followed by a ULEB128 size:
  - 125,984 tombstones (address `u64::MAX`: functions the linker removed);
  - 115,740 live entries.
- `stack-sizes.orbis-bin.txt` prints one row per FUNC symbol in `.symtab` (120,885 rows, names
  only). The 646 `??` rows are FUNC symbols without an entry.
- Example: `cWebsocketClient::move()` at 0xe41300 uses 82,344 bytes.

## Unwind data

- `.eh_frame` holds 115,719 FDE records; `.debug_frame` is 432 bytes.
- `llvm-readelf --unwind` prints DWARF register numbers (6 = rbp, 3 = rbx, 7 = rsp, 16 = return
  address).

## DWARF

- **Sections**: `.debug_info` 671.6 MB, `.debug_loc` 37.6 MB, `.debug_line` 16.6 MB, `.debug_ranges`
  10.0 MB, `.debug_abbrev` 4.6 MB, `.debug_str` 3.7 MB, `.debug_frame` 432 bytes.
- **Absent**: `.debug_aranges`, `.debug_pubnames`, `.debug_pubtypes` and accelerator tables. With
  no address index, address lookups have to walk the compile units' ranges.
- **Statistics**: 159,644 functions, 611,810 inlined instances, 2,602,083 source variables (1,615,676
  with a location), 621,688 parameters, and 25,370,131 bytes with line information.
- **Line tables**: the 2,305 tables (line-table version 3) are not contiguous.
  - A gap follows every table: 318 gaps are 1 byte, 169 are 7 bytes, many are runs of 34–98 zero
   bytes, and 14 contain non-zero bytes (for example 0x62 at offset 0x1fd). The SDK linker's
   `--pad-debug-line` option produces this padding.
  - A reader that walks `.debug_line` front to back therefore decodes only the first table. This
   set copies each table out at its compile unit's `DW_AT_stmt_list` and decodes the copy.
  - The result is 1,679,315 rows: 1,611,308 line entries, which equals the `--statistics` count,
   plus 68,007 end-of-sequence rows.
- **Overlapping compile units**: code shared through inlining and template instantiation is
  attributed to many compile units. For example, address 0x194d8f0 lies within the ranges of
  1,014 compile units, and the line tables hold 2,026 rows for that address.
- **Verifier**: `llvm-dwarfdump --verify` reports 21,330 overlapping address ranges, 3,286 ranges not
  contained in their parent, and 48 overlapping `DW_AT_ranges`. All of them involve
  `inlined_subroutine` or `lexical_block` DIEs. The verifier checks one unit at a time, so it does
  not see the overlap across units.
- **DIE tree**: the dump has 463,660,524 lines.

## Code

- The disassembly covers 116,279 functions and 6,920,426 instructions in the executable sections,
  with demangled names and source-line annotations.
- Calls to imports go through the PLT stubs, and the disassembly labels them with the stub names,
  such as `</PL_init_env>`.

## Why inlined chains come from one address per run

`orbis-addr2line` (binutils 2.22) answers an address according to the addresses that share its run, since a run keeps the compile units it has read and up to 1,014 of them claim one range. An address run alone gets the answer that depends on the address only. On 30,904 addresses of the reconstructor's measurement, 77 answers differ from batches of 256, 75 of them with more frames. So the file of chains pays one process per address, about 2 h 40 min at 16 jobs, and is then read instead of run ([format](../reference/elf-dumps.md#inline-chains)).

## Why IDA's analysis only corroborates

IDA's jump tables and no-return functions are a second opinion on the reconstructor's analysis of every body. The comparison reports counters that gate nothing: DWARF and the bytes decide, and IDA's function boundaries are its own conventions.
