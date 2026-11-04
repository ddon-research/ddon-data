# PS4 ELF dump choices

This page is for a reverse engineer who reads the static dumps of `DDOORBIS.elf`, the PS4 client executable of build PS4_02020005: why its chains of inlined calls come from one process per address, and why IDA's analysis is only a second opinion. Read [Structure of the PS4 ELF](../reference/ps4-elf-structure.md) first for the file itself; the formats of the dumps are in [ELF dumps](../reference/elf-dumps.md). The numbers describe that one fixed input, SHA-256 `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`.

## Why inlined chains come from one address per run

`orbis-addr2line` (binutils 2.22) answers an address according to the addresses that share its run, since a run keeps the compile units it has read and up to 1,014 of them [claim one range](../reference/ps4-elf-structure.md#dwarf). An address run alone gets the answer that depends on the address only. On 30,904 addresses of the reconstructor's measurement, 77 answers differ from batches of 256, 75 of them with more frames. So the file of chains pays one process per address, about 2 h 40 min at 16 jobs, and is then read instead of run ([format](../reference/elf-dumps.md#inline-chains)).

## Why IDA's analysis only corroborates

IDA's jump tables and no-return functions are a second opinion on the reconstructor's analysis of every body. The comparison reports counters that gate nothing: DWARF and the bytes decide, and IDA's function boundaries are its own conventions.
