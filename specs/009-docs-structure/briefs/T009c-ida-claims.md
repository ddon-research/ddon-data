009 T009c: the page claims only IDA can settle

Question (PC 03040008, PS4 02020005): do the database facts stated on the new pages hold? The T009 review read raw bytes of `f1c9` but could not open a database (`specs/009-docs-structure/research/T009-adversarial.md`, intro and "Checked and right").

Check, each with its VA and what the database shows:
1. `0x9d6a20` and `0x9d6d20`: the send and receive claims on `docs/reference/packet-wire-format.md` or `docs/explanation/wire-protocol.md` (find them with `rg`).
2. `docs/explanation/ida-transfer-method.md:71` (the shift claim): read the page's sentence, then test it.
3. A sample of 20 addresses across `docs/reference/packet-handler-tables.md`, `docs/explanation/packet-decoding-method.md`, `docs/explanation/two-packet-decodings.md` (`0x76f820`, `0x766790`, `0x840080`, `0x81dc00`), `docs/how-to/write-a-packet-pattern.md`, `docs/reference/packet-wire-format.md`: the function or data is what the page says, in the annotated database. For the first-party handler names the page gives, the name matches.
4. Pages stating which database holds what (`docs/reference/inputs-and-builds.md`, `docs/how-to/query-ida-read-only.md`): `private-copy.sh pc-handlers` opens the database they describe; `idc.get_idb_path()`, image base and architecture as stated. PS4: one address on `docs/explanation/ps4-elf.md`, by `private-copy.sh ps4`.

Report: `specs/009-docs-structure/research/T009c-ida-claims.md`: a table (claim, page:line, VA, what IDA shows, verdict holds / wrong / not settled), and for each wrong one the sentence's fix. Do not edit pages.
Source boundary: private copies only: `bash research/ida/private-copy.sh pc-handlers t009c`, `bash research/ida/private-copy.sh ps4 t009c`; read-only; delete both copies at the end. Never another database or copy.
Libraries: ida-mcp `execute_python`.
Done: the report; final message: path, counts, wrong claims. Stop: budget 30 min of work time. Base: the head when you start.
