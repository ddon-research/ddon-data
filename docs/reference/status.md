# Status

The dated counts of this repository, for a reader who wants to know how far the decoding reaches before relying on it. The other pages give orders of magnitude and link here, so a re-export changes this page alone. The [glossary](glossary.md) defines the terms.

> **Work in progress.** Packet counts from the close of `specs/008-remaining-packets/` on 2026-11-03, recounted on 2026-11-04 where a row says so.

## Packets, client 03040008

| What | Count | Date | How to recount |
| --- | --- | --- | --- |
| Packet patterns | 595 | 2026-11-04 | `ls packets/patterns/03040008/*-pattern.cpp \| wc -l` |
| Shared includes | 36 | 2026-11-04 | `ls packets/patterns/03040008/include \| wc -l` |
| Raw packet files | 160,615 | 2026-11-04 | `fd -t f . packets/decrypted_raw \| wc -l` |
| JSON exports | 160,615 | 2026-11-04 | `fd -t f . packets/decrypted_json \| wc -l` |
| JSON exports with `"fits": true` | 160,615 | 2026-11-04 | `rg -l -F '"fits": true' packets/decrypted_json \| wc -l` |
| Captured streams with a JSON folder | 125 | 2026-11-04 | `fd -d 1 -t d . packets/decrypted_json \| wc -l` |
| Fit of the 115 ids decoded last against their PC layouts, of 4,887 captures | 4,885 | 2026-11-03 | `specs/008-remaining-packets/tasks.md` |

The 2 captures outside that fit are of 29.23.16, whose PC handler returns without reading its body. A fit of every export says that no decode overruns its file; it does not prove widths ([fit](glossary.md#packets)).

**Status:** open. Decoded without settled meaning at 2026-11-03: 29.23.16 (no reader), 11.88.16 and 11.118.16 (layout decoded, meaning unknown), and the `G` names whose consumers were not traced.

## The two packet decodings

How often the server's structures agree with the PC 03040008 layouts, over the 115 ids decoded last, measured on 2026-11-03 against the server fork `88d82caf07`. Source: columns `ag_vs_pc` and `ag_*` of `specs/008-remaining-packets/research/T001-triage.tsv`, recounted on 2026-11-04. What the numbers mean: [Two packet decodings](../explanation/two-packet-decodings.md). The other ids of the table were not measured this way.

| `ag_vs_pc` | Ids |
| --- | --- |
| same | 81 |
| differs | 3: 14.11.16, 10.14.16, 34.0.1 |
| empty: the comparison's parser did not know a statement of the structure | 31 |

## Export engine, measured 2026-11-01

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

## Resource extensions, client 03040008

| What | Count | Date | How to recount |
| --- | --- | --- | --- |
| Extensions ddon-extractor supports | 186 | 2026-11-04 | `research/scripts/find-unsupported-extensions.sh 03040008` |
| Extensions it does not support | 145 | 2026-11-04 | the same |
| Coverage | 56% | 2026-11-04 | the same |

## Not run

| Check | State | Date |
| --- | --- | --- |
| The steps of the how-tos that rewrite tracked data: [Decrypt a capture](../how-to/decrypt-a-capture.md), [Re-annotate streams](../how-to/reannotate-streams.md) (annotate, raw export), [Refresh packet statistics](../how-to/refresh-packet-statistics.md), [Patch the Arrowgene CLI](../how-to/patch-the-arrowgene-cli.md) (build) | not run: their commands are read against the scripts | 2026-11-04 |
| Applying `packets/tools/arrowgene-cli.patch` and building from it; `git apply --check` on a clean `e2411fe8` passed | not run | 2026-11-04 |
| ImHex validation of the packet patterns | not run: ImHex is not on `PATH`, and plbatch is the parser of the export | 2026-11-03 |
| Consumers of the role-only `V` marks of 28.34.2 and 11.68.16 | not run | 2026-11-03 |
| The `ValueOld` check of 13.23.16 | not run | 2026-11-03 |
| Coverage of client 02030004 with `research/scripts/find-unsupported-extensions.sh` | not run | 2026-11-04 |
