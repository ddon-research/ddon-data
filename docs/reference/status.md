# Status

The dated counts of this repository, for a reader who wants to know how far the decoding reaches before relying on it. The other pages give orders of magnitude and link here, so a re-export changes this page alone. The [glossary](glossary.md) defines the terms.

> **As of 2026-11-04.** Each block below names the date of its run in its own banner; a row with another date says so.

## Packets, client 03040008

> Recounted on 2026-11-04.

| What | Count | How to recount |
| --- | --- | --- |
| Packet patterns | 595 | `ls packets/patterns/03040008/*-pattern.cpp \| wc -l` |
| Shared includes | 36 | `ls packets/patterns/03040008/include \| wc -l` |
| Raw packet files | 160,615 | `fd -t f . packets/decrypted_raw \| wc -l` |
| JSON exports | 160,615 | `fd -t f . packets/decrypted_json \| wc -l` |
| JSON exports with `"fits": true` | 160,615 | `rg -l -F '"fits": true' packets/decrypted_json \| wc -l` |
| Captured streams with a JSON folder | 125 | `fd -d 1 -t d . packets/decrypted_json \| wc -l` |
| Fit of the 115 ids decoded last against their PC layouts, of 4,887 captures; counted 2026-11-03 | 4,885 | `specs/008-remaining-packets/tasks.md` |

The 2 captures outside that fit are of 29.23.16, whose PC handler returns without reading its body. A fit of every export says that no decode overruns its file; it does not prove widths ([fit](glossary.md#packets)).

**Status:** open. Decoded without settled meaning at 2026-11-03: 29.23.16 (no reader), 11.88.16 and 11.118.16 (layout decoded, meaning unknown), and the `G` names whose consumers were not traced.

## The two packet decodings

> Measured on 2026-11-03 against the server fork `88d82caf07`; recounted on 2026-11-04.

How often the server's structures agree with the PC 03040008 layouts, over the 115 ids decoded last. Source: columns `ag_vs_pc` and `ag_*` of `specs/008-remaining-packets/research/T001-triage.tsv`, with one correction. What the numbers mean: [Two packet decodings](../explanation/two-packet-decodings.md). The other ids of the table were not measured this way.

| `ag_vs_pc` | Ids |
| --- | --- |
| same | 82 |
| differs | 2 of the 84 compared: 14.11.16, 10.14.16 |
| empty: the comparison's parser did not know a statement of the structure | 31 |

The TSV still marks 34.0.1 as differing, and was not regenerated. Its PC shape was corrected afterwards to a u32 count plus a u64 per element (`specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md`), which is the server's list of `CDataCommonU64`, so this table counts it as same.

## Export engine

> Measured on 2026-11-01.

Client 03040008 packets on a contended 32-CPU machine, with hyperfine 2.0.0, `-N`. plbatch was at PatternLanguage `fb6ea061` for these runs, the pin ImHex 1.38.1 embeds, so both engines ran one parser.

| What | Result |
| --- | --- |
| Byte comparison of `imhex.exe` 1.38.1 (portable NoGPU) `--pl format` with plbatch, same patterns, over 3,028 files: 1,000 each of `C2S_PARTY_SEND_BINARY_MSG_NTC`, `S2C_LOBBY_LOBBY_DATA_MSG_NTC` and `C2S_LOBBY_LOBBY_DATA_MSG_REQ`, all 8 `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC`, 20 samples of `specs/005-netmsg-patterns/research/P7-imhex-as-library.md` | 3,028 identical, 0 differing, 0 failures on either side |
| plbatch over 100 `S2C_LOBBY_LOBBY_DATA_MSG_NTC` packets | 2.837 s ± 0.111, 5 runs: about 35 packets/s per process |
| `imhex.exe --pl format` over one packet | 534.0 ms ± 317.0, 15 runs: about 1.9 packets/s per process, before any shell overhead |
| `--time`, 1,000 packets per nNetMsg type: parse of the roughly 1,000-line `nNetMsg.hexpat` and its std imports | about 24-25 ms per file |
| The same: evaluation | about 0.5-0.7 ms per file |
| The same: JSON | about 0.05 ms per file |
| One process, per-file parsing as built | about 40 files/s |
| Parsing once and evaluating many, not built, estimated | roughly 1,000 files/s per process |

## Client resources

> Counted on 2026-11-04.

| What | Count | How to recount |
| --- | --- | --- |
| Files of `client/03040008/` in the git index | 173,454 | `git ls-files -- client/03040008 \| wc -l` |

## Resource extensions

> Measured on 2026-11-04, against ddon-extractor `e6c358ea`.

| What | Client 03040008 | Client 02030004 |
| --- | --- | --- |
| Extensions in the client's `-resources.csv` | 331 | 291 |
| Extensions ddon-extractor supports | 186 | 176 |
| Extensions it does not support | 145 | 115 |
| Coverage | 56% | 60% |

Recount with `research/scripts/find-unsupported-extensions.sh <build>`. Client 02030004 reads `D:\ddon-data-s2`.

## Annotated database, PC 03040008

> Output of the runs of 2026-11-03; a row dated 2026-11-04 was rerun then.

`match.py` and `transfer.py --wave2` were rerun on 2026-11-04 into a scratch folder and gave identical files. From `research/03040008/ida-transfer/`:

| What | Count | Date | How to recount |
| --- | --- | --- | --- |
| Handler-table callbacks | 1,040 | 2026-11-03 | `jq -r 'select(.kind=="summary").table_callbacks' dumps/pc-ida.jsonl` |
| Function starts repaired: callbacks, call targets | 130, 118 | 2026-11-03 | `dumps/logs/repair-apply.log`, `dumps/logs/repair3-apply.log` |
| Tier 0 handlers named, listed without a name | 669, 371 | 2026-11-04 | `rg '^tier0_' manifest/summary.tsv` |
| Accepted pairs | 972 | 2026-11-04 | `rg -c '\taccepted$' manifest/pairs.tsv` |
| of those by rule: seed, reader, element reader, requester, sender | 467, 69, 95, 107, 234 | 2026-11-04 | `cut -f6 manifest/pairs.tsv \| sort \| uniq -c` |
| of those by propagation or anchored gap | 0 | 2026-11-04 | the same |
| Wrong pairs in 5 holdout runs; withheld seeds recovered | 0; 0 | 2026-11-04 | `manifest/precision.tsv` |
| Pairs accepted in 5 shuffled-partner runs | 0 | 2026-11-04 | `manifest/control.tsv` |
| Names: set, corrected, labels removed | 1,077, 9, 3 | 2026-11-03 | `manifest/transfer/summary.tsv` |
| Prototypes: set, replaced, skipped | 1,011, 54, 109 | 2026-11-03 | the same |
| Whole types accepted, embedded, declared opaque | 90, 1, 90 | 2026-11-03 | `cut -f3 manifest/transfer/types.tsv \| sort \| uniq -c` |
| Function comments | 1,174 | 2026-11-03 | `manifest/transfer/summary.tsv` |
| Partial types, member links | 48, 163 | 2026-11-03 | `manifest/transfer/wave2/summary.tsv` |
| Partial types whose size an access extended | 42 | 2026-11-03 | the same |
| `packet` locals named and retyped; refused at the apply | 23; 1 | 2026-11-03 | `dumps/logs/apply-w2e.log` |
| Reviewer's sample of pairs and types, wrong on PC | 70, 0 | 2026-11-03 | `specs/007-pc-handler-annotation/research/T008-adversarial.md` |

### Transfer commands of the how-to

On 2026-11-04, against the committed manifest and the local dumps:

| Command | Result |
| --- | --- |
| `uv run python match.py --help`, `transfer.py --help`, `extract_dwarf.py --help` | the flags on the how-to |
| `uv run python match.py --out <scratch>` | exit status 0; all 8 files equal `manifest/` |
| `uv run python transfer.py --wave2 --out <scratch>` | exit status 0; the 7 `.tsv` files compared equal `manifest/transfer/wave2/` |
| `uv run python transfer.py --no-holdout --out <scratch>` | exit status 2: the message quoted in the how-to, step 4, as designed for these dumps |
| `parse_batch_args` of `apply_transfer.py` and `repair_functions.py`, called on the how-to's argument lists | parsed into its modes; `--verify` without `--apply-log`, `--apply-log` without `--verify`, and `--apply --verify` refused |

**Status:** not run for [Transfer annotations from PS4 to PC](../how-to/transfer-annotations-ps4-to-pc.md): `extract_ida.py`, `extract_dwarf.py`, `manifest.py`, `repair_functions.py` and `apply_transfer.py` in any mode, since they would rewrite the dumps or need a database. Their commands are those of `specs/007-pc-handler-annotation/research/T004f-repair-batch.md`, `T005g-extract-v4.md` and `W2-T013e-reapply.md` there.

## Client patches

> Measured on 2026-11-04; the replay row is of 2026-10-17.

The `.r2` and `.json` files of `patches/`, against the hash tables of [Client patches](client-patches.md).

| What | Result | Date | How to recount |
| --- | --- | --- | --- |
| `.r2` files tracked; on disk | 12; 13 | 2026-11-04 | `git ls-files 'patches/*.r2' \| wc -l`, `ls patches/*.r2 \| wc -l` |
| Tracked `.r2` files in UTF-16LE with a BOM | 10 | 2026-11-04 | `research/03040008/protections/R3-patches.md` §7, recounted on the first two bytes |
| `.json` hashes equal to the table rows' Starting and Target hashes | 15 rows of 15 with a `.r2` | 2026-11-04 | `files[].sha256` of each `.json` |
| Each tracked `.r2` replayed in memory on its stated parent, hashed | 12 of 12 reach the target | 2026-10-17 | `research/03040008/protections/R3-patches.md` |
| A UTF-16 `.r2` run by `radare2 -qnw -i` (6.1.0), on a blank scratch file of the executable's size | 0 bytes written, `Invalid command` | 2026-11-04 | `2022_01_21_ddo_dump_fix_mutex_e.r2` |
| The same file after `iconv -f UTF-16 -t UTF-8`; `rootofallthings_chat_edit.r2` as it is | 1 byte written each | 2026-11-04 | the same |
| `radiff2 -r`, `radiff2 -j`, `rahash2 -a sha256` and the replay of [Add a client patch layer](../how-to/add-a-client-patch-layer.md), on two 16-byte scratch files | the replay equals the modified file | 2026-11-04 | the same commands |

## ELF dump set, PS4_02020005

> Measured on 2026-11-04.

| What | Result | Date | How to recount |
| --- | --- | --- | --- |
| Dumps committed, as stored | 43, 116 MiB: the script's 41 (79 MiB at its run) and the two the reconstructor writes | 2026-11-04 | `jq 'select(.storage=="txt" or .storage=="zst")' binaries/PS4_02020005/elf-dumps/manifest.jsonl` |
| Local-only dumps, compressed | 2, 1.15 GiB | at the same run | `dust -d 0 binaries/PS4_02020005/elf-dumps/local` |
| `./generate-elf-dumps.sh --dry-run` | tools and input OK | 2026-11-04 | |
| `./generate-elf-dumps.sh --verify` | all published files match the manifest | 2026-11-04 | |

## Not run

> The state on 2026-11-04; a row names when it was last judged.

| Check | State | Date |
| --- | --- | --- |
| The steps of the how-tos that rewrite tracked data: [Decrypt a capture](../how-to/decrypt-a-capture.md), [Re-annotate streams](../how-to/reannotate-streams.md) (annotate, raw export), [Refresh packet statistics](../how-to/refresh-packet-statistics.md), [Patch the Arrowgene CLI](../how-to/patch-the-arrowgene-cli.md) (build) | not run: their commands are read against the scripts | 2026-11-04 |
| Applying `packets/tools/arrowgene-cli.patch` and building from it; `git apply --check` on a clean `e2411fe8` passed | not run | 2026-11-04 |
| ImHex validation of the packet patterns | not run: ImHex is not on `PATH`, and plbatch is the parser of the export | 2026-11-03 |
| Consumers of the role-only `V` marks of 28.34.2 and 11.68.16 | not run | 2026-11-03 |
| The `ValueOld` check of 13.23.16 | not run | 2026-11-03 |
| The IDA steps of [Transfer annotations from PS4 to PC](../how-to/transfer-annotations-ps4-to-pc.md) since their runs of 2026-11-03: `repair_functions.py`, `extract_ida.py`, `apply_transfer.py`; and the read-only batch example of [Query an IDA database read-only](../how-to/query-ida-read-only.md) | not run | 2026-11-04 |
| Full `generate-elf-dumps.sh` and `--skip-local`; the reconstructor's `inline-dump` and `export.sh` | not run: read against the sources | 2026-11-04 |
| Any `.r2` applied with radare2 to a client executable, for [Apply a client patch](../how-to/apply-a-client-patch.md) | not run | 2026-11-04 |
| The steps of [Triage a client crash](../how-to/triage-a-client-crash.md) | not run: no client here; the commands are checked against ddon-hook's `run_cycles.py` where it has them | 2026-11-04 |
| [Run Pharos](../how-to/run-pharos.md) | not run: `run.sh --help` only; `docker-compose` is on `PATH`; its times are estimates | 2026-11-04 |
| [Convert textures](../how-to/convert-textures.md) | not run: both scripts' `--help` only; ARCtool not checked, `magick`, `texconv.exe` and `texdiag.exe` are on `PATH` | 2026-11-04 |
| [Extract client resources](../how-to/extract-client-resources.md) | not run: no re-extraction; read against `ExtractResourceCommand.java` | 2026-11-04 |
| [Decode a resource format](../how-to/decode-a-resource-format.md): ImHex validation of any resource pattern, its IDA reads | not run: ImHex is not on `PATH`; the example's bytes and JSON were read | 2026-11-04 |
| The addresses of [Packet handler tables](packet-handler-tables.md) in the databases `pc` and `pc-accepted`; they were checked in `pc-handlers` | not run | 2026-11-04 |
| The URLs of [Community resources](community-resources.md) | not run | 2026-11-04 |
| The C# lines of [Quest flag sources](quest-flag-sources.md) against a server source | not run; each file example was searched for its value | 2026-11-04 |
| The whole-type `transfer.py` on the committed dumps: it refuses them with exit status 2, as designed, so `manifest/transfer/` could not be compared | not run | 2026-11-04 |
