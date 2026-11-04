# Inputs and builds

What this repository's data is made from: the builds, the game clients, the disassembler databases, the PS4 ELF, the captures and the longplay videos, with where each lives on the research machine. It is for anyone reproducing a result or naming its input. All of it stays outside the repository and is never copied in. The [glossary](glossary.md#builds-and-clients) defines the terms.

## Builds

A version is a client build number. Name the build whenever you read, write or compare data.

| Build | Client | Season | Where the data is |
| --- | --- | --- | --- |
| `03040008` | PC | 3 | this repository |
| `PS4_02020005` | PS4, with debug symbols; a Season 2 build | 2 | `binaries/PS4_02020005/` here |
| `02030004` | PC | 2 | `D:\ddon-data-s2`, with its `recompilation/` |
| `02030010` | PC | 2 | client only |
| `01010004` | PC | 1 | `D:\ddon-data-s1` |
| `ANDROID_1500` | Android companion app | | `binaries/ANDROID_1500/` here |
| Benchmark | the benchmark client | | statistics in `client/Benchmark.csv` |

Season 2 debug symbols describe Season 3 PC formats only approximately: verify per format before carrying a layout across ([Evidence model](../explanation/evidence-model.md)).

## Game clients

| Path | Build |
| --- | --- |
| `D:\DDON_01010004` | 01010004 |
| `D:\DDON_02030004` | 02030004 |
| `D:\DDON_02030010` | 02030010 |
| `D:\DDON_03040008` | 03040008 |
| `D:\DDON_Benchmark` | Benchmark |

Each holds `nativePC/rom`. The translations are `D:\DDON-translation\gmd.csv`. The PC executables and their hash chain are on [Client patches](client-patches.md).

## Disassembler databases

Under `D:\research\DDON-binaries\`, read-only input:

| Path | Holds |
| --- | --- |
| `IDA9.5\` | the live databases, below |
| `IDA9.3\` | packed `.i64` with `.c` and `.h` exports per build: `PC_DDON_03040008`, `PS4_DDON_00020004_2015-07-24`, `PS4_DDON_01000006_2015_09_08`, `PS4_DDON_01020003_2015-12-15`, `PS4_DDON_02000004_2016_06_15`, `PS4_DDON_02020005_2016_12_21` |
| `Ghidra11.4\` | projects `PS4_DDON_02020005_2016_12_21`, `PS3_DD_2012_03_29`, `XBOX360_DD_2012-02-08` |
| `PC\`, `PS4\`, `PS3\`, `PSV\`, `Android\` | raw dumps; `Android\` also holds its tools |

The targets of `research/ida/private-copy.sh`, each opened only as a private copy ([Query an IDA database read-only](../how-to/query-ida-read-only.md)):

| Target | Build | Database, under `IDA9.5\` |
| --- | --- | --- |
| `pc` | PC 03040008 | `PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.i64`, the live PC database |
| `pc-accepted` | PC 03040008 | ddon-hook's accepted database: `accepted_PC.path` of `PC_DDON_03040008\CURRENT-RECOVERY.json`, refused unless it lies inside `PC_DDON_03040008\` and its SHA-256 equals `accepted_PC.sha256` |
| `pc-handlers` | PC 03040008 | `PC_DDON_03040008\spec007-packet-handlers-20261103-wave2\2022_01_29_DDO_DUMP_FIX.exe.i64`, the database with the transferred annotations |
| `ps4` | PS4 02020005 | `PS4_DDON_02020005_2016_12_21\DDOORBIS.elf.i64` |

`CURRENT-RECOVERY.json` also sits in `PS4_DDON_02020005_2016_12_21\`, and `feature*` and `spec007-*` folders beside the databases are feature copies. Never overwrite a live database from a headless copy.

## PS4 ELF

| Path | Holds |
| --- | --- |
| `D:\research\DDON-binaries\IDA9.3\PS4_DDON_02020005_2016_12_21\DDOORBIS.elf` | the canonical `DDOORBIS.elf`; [`generate-elf-dumps.sh`](../how-to/regenerate-elf-dumps.md) reads only a hash-verified copy of it |
| `DDOORBIS.elf.llvmdwarfdump.zst`, same folder | 1.1 GB; stream it, never decompress it |
| the undocumented `*.objdump.*` and `*.readelf.*` dumps, same folder | superseded by `binaries/PS4_02020005/elf-dumps/`, whose [README](../../binaries/PS4_02020005/elf-dumps/README.adoc) maps each to its successor |

## Captures

`D:\research\DDON-pcaps\ddpkg\` holds the packet captures as `stream<N>-<label>-marked.pcapng`: 87 `.pcapng` files, counted on 2026-11-04. Beside them in `D:\research\DDON-pcaps\` are the toolchain (`ddon_pcap_split.exe`, `ddon_common_key_bruteforce.exe`, `SeededXorshift128.exe`, an `Arrowgene.Ddon.Cli.exe` build) and a `keys-all-in-one.csv`. The patched CLI is built elsewhere: [Patch the Arrowgene CLI](../how-to/patch-the-arrowgene-cli.md). What they became is in `packets/`: [Decrypt a capture](../how-to/decrypt-a-capture.md).

## Longplay videos

`D:\ddon-longplay\ddon longplay\` holds screen recordings that match the pcaps: 87 `.mkv` files on 2026-11-04, 182 GiB, up to 15 GiB and 3.5 h per file, each `NNN - Dragon's Dogma Online N [id].mkv` with a `.info.json`. They show what happened in game around a capture time, such as a login or a key burst. The only clock is the Windows 7 taskbar clock, accurate to the minute.

Never copy or decode a whole file. Read `.info.json` with `jq`, and take single frames:

```bash
ffmpeg -ss <t> -i <mkv> -frames:v 1 <png>
```

## Related repositories on this machine

| Path | What it is |
| --- | --- |
| `D:\ddon-extractor` | the Java CLI behind `client/` |
| `C:\ddon-dwarf-reconstructor-rust` | rebuilds C++ for resource classes from the PS4 DWARF; reads `D:\ddon-data-s2\client\02030004` as an oracle |
| `D:\ddon-dwarf-reconstructor` | its archived Python predecessor, still used by knowledge-graph enrichment |
| `D:\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline` | the server emulator's fork; `.Upstream` is its unpatched clone |
| `C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream` | the patched CLI build, with uncommitted patches |
| `D:\ddon-ghidra-scripts` | the archived PyGhidra analyzer and Script Manager scripts |
