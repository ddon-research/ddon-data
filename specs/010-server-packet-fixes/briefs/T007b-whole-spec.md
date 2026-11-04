010 T007b: whole-spec review and audit of the docs it touched

Question: does spec 010's output do what `specs/010-server-packet-fixes/spec.md` asks, and is everything a reader would take from it true as evidenced? Build: PC 03040008 client; server `fix/packet-handling`.

You are read-only, with no git and no IDA. The server clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean` has head `64c676b9` checked out, so read its files directly. Draft PR 8 on the fork carries `research/pr-body.md` as its body. T005 reviewed the code adversarially and T005a fixed its findings: do not repeat that. Check what came after it.

Read: `spec.md`, `tasks.md`, then `research/pr-body.md` and `research/impact.md`, checking them against `research/T002-differential.md`, `T003-pc-evidence.md`, `T004a-patch.md`, `T004b-patch.md`, `T005-adversarial.md`, `T005a-fixes.md`, `T005b-live-smoke.md`, `T006a-branch-wording.md`.

Check, and report only what you can show:
1. **Spec coverage**: every field the spec's "Impact outline" requires, per change; the effect on `packets/decrypted_annotated/`; candidates not patched, with reasons. Each row of `tasks.md`'s Ruling is either patched or listed as not patched, and none is missing.
2. **PR body against its evidence**: sample at least 15 claims across the table, "How to verify" and "Deliberately not changed": numbers, addresses, "seen live" against "read" against "not run". A claim stronger than its report is a finding. Read the server code for at least 5 of the rows and confirm the code does what the row says: 27.8.16, 11.45.16, the `MtString` cap, a close case, the one-response path.
3. **Public wording**: the body and the code comments in the changed files named in `T006a-branch-wording.md`. Anything that is a reproduction recipe, a count value that abuses a reader, a statement of what is reachable before login, a machine path, a task id, or a claim of client memory unsafety. `impact.md` may hold these; the body and the branch may not.
4. **Docs the spec touched**: `docs/reference/packet-handler-tables.md` § What ends a served connection, `packet-wire-format.md` § Padding, `status.md`, `docs/explanation/two-packet-decodings.md`, `docs/reference/inputs-and-builds.md`, against T003 and T001. Marks `V`/`I` honest; no reader can take 19.28.2's text as "swap the wire". Then, read-only: do `readme.adoc`, `packets/README.md`, `docs/index.md`, `AGENTS.md`, `CLAUDE.md` need a change for this spec? Say which line and why. Anything in `docs/` that a public reader could use as an abuse recipe: list it, the coordinator rules.

Evidence level for each finding: where you read it, file and line. Rank by what a maintainer or Sam would be misled by. A claim you could not check goes under "Not checked", never "holds".

Owns: nothing; you write no files. Your final message is the report: the coordinator files it as `research/T007b-review.md`. Never touch: anything.
Done: findings ranked, then a short list of what you checked and found right, then "Not checked". Stop: budget 45 min of work time.
