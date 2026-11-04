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
| Fit of the 115 ids decoded last against their PC layouts, of 4,887 captures | 4,885 | 2026-11-03 | `specs/008-remaining-packets/tasks.md` |

The 2 captures outside that fit are of 29.23.16, whose PC handler returns without reading its body. A fit of every export says that no decode overruns its file; it does not prove widths ([fit](glossary.md#packets)).

**Status:** open. Decoded without settled meaning at 2026-11-03: 29.23.16 (no reader), 11.88.16 and 11.118.16 (layout decoded, meaning unknown), and the `G` names whose consumers were not traced.

## Resource extensions, client 03040008

| What | Count | Date | How to recount |
| --- | --- | --- | --- |
| Extensions ddon-extractor supports | 186 | 2026-11-04 | `research/scripts/find-unsupported-extensions.sh 03040008` |
| Extensions it does not support | 145 | 2026-11-04 | the same |
| Coverage | 56% | 2026-11-04 | the same |

## Not run

| Check | State | Date |
| --- | --- | --- |
| ImHex validation of the packet patterns | not run: ImHex is not on `PATH`, and plbatch is the parser of the export | 2026-11-03 |
| Consumers of the role-only `V` marks of 28.34.2 and 11.68.16 | not run | 2026-11-03 |
| The `ValueOld` check of 13.23.16 | not run | 2026-11-03 |
| Coverage of client 02030004 with `research/scripts/find-unsupported-extensions.sh` | not run | 2026-11-04 |
