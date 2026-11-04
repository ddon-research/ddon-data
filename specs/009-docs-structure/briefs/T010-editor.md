009 T010: editor pass over the documentation

Objective: the pages read as one voice for a reverse-engineering peer, each with one purpose. The facts are settled by the review (`specs/009-docs-structure/research/T009-adversarial.md`, `T009c-ida-claims.md`): you change wording, never facts. The contract: `docs/reference/documentation-style.md`; your role file binds you.

Pages, in this order; when budget or context ends, stop at a page boundary and say which remain:
1. `readme.adoc`, `docs/index.md`, `docs/tutorials/read-one-packet.md`.
2. `docs/explanation/*` (the altitude rule applies hardest here: cut counts, line numbers and task ids, keep the reason; a count goes to Status only if Status lacks it). Start with `two-packet-decodings.md`, `evidence-model.md`, `packet-decoding-method.md`, `wire-protocol.md`.
3. `docs/how-to/*`: opening paragraph, steps numbered, how to tell success from failure.
4. Short READMEs: `packets/README.md`, `packets/patterns/03040008/README.md`, `packets/plbatch/README.md`, `packets/wireshark/README.md`, `research/README.md`, `research/03040008/ida-transfer/README.md`, `patches/README.md`, `tools/README.md`. The sections `research/03040008/protections/README.md` and `binaries/PS4_02020005/elf-dumps/README.adoc` keep for outside readers keep their numbers and substance: read them last, trim only what surrounds them.
5. `docs/reference/*`: only the opening paragraphs, headings and prose. Table rows are checked facts: leave them. `docs/reference/packet-ids.md`'s table is machine-checked: never touch it; `packet-marks.md` is authority for mark wording: never change a mark's meaning.

Also:
- Pages serving two purposes (review's walk): `docs/reference/client-patches.md` (lookup plus lineage), `docs/reference/packet-ids.md` (the report key may stay as its key). Split only where a reader is misled, by moving text to the explanation page that already covers it.
- `docs/how-to/query-ida-read-only.md:14` says executable facts hold in all three PC databases, and only `pc-handlers` was checked: report whether the sentence states more than is known, with a proposal; rewording a claim is not yours.
- `docs/reference/packet-handler-tables.md`: T009c's traps (9 of the 20 login handlers have no IDA function in the annotated database; Hex-Rays leaves out the send and receive logic) are facts a reader needs: if the pages lack them, report it as a fact needing a home.

Consistency: one term per thing across pages (`pattern`, `capture`, `raw file`, `annotated dump`, `mark`, `fit`); the glossary defines terms used on two pages; dates ISO 8601; British with -ize; no serial comma.

Report: `specs/009-docs-structure/research/T010-editor.md` (your role says what it holds). Commit it.
Owns: as your role file's path guard says. Never touch: `tools/`, patterns, specs other than your report.
Done: `bash tools/check.sh --since <base>` with the `docs` line passed, `packet-counts` not needed unless you touched the table (you must not); signed commits with `git commit -m <msg> -- <paths>`, a page or a few per commit; final message: verdict in at most five lines, then the receipt.
Stop: budget 120 min of work time; past 300k context, commit and end `cut short:` with the pages left. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
