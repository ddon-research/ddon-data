007 T005e: role anchors in the matcher, the real precision check, the pairs manifest v2

Objective (PC 03040008 <-> PS4 02020005): add the role anchors of
`specs/007-pc-handler-annotation/research/T005b-role-anchors.md` § 6 to the matcher (T005, 499f7c701d)
over the v3 dumps (T005d, `research/T005d-batch-v3.md`), keeping every T005 gate. Read T005b § 0-6 and
the T005d report first.

Codec widths: PC from the dump's `codec` field (20 functions, all agree with T005b § 2.1); PS4 from the
codec symbols (T005b § 2.2 table, DWARF-named `nPacket::Read_*`/`Write_*`), because T005c's shape
classifier recognises only 4 of 22 PS4 codecs (T005d: cursor stored with `mov`, bound by `cmp`/`jz`); use
the PS4 `codec` field only as a cross-check and list disagreements.

Rules (each a function with tests, each pair carries the rule and its witnesses):
1. **Reader anchor** (T005b rule 1): in an accepted handler pair, the PC handler's unique callee that
   reaches codecs (depth <= 2) pairs with the one PS4 `CPacket_<NAME>::ReadPacket` the PS4 handler calls,
   class name = the handler's packet. PS4 handlers with an inlined reader: no pair; list "inlined on PS4".
2. **Element-reader anchor** (rule 2): in reader pairs whose codec width sequences are equal under the
   header rule (PC `44` <-> PS4 `24`/`2`), a PS4 `nPacket::Read_CData*` call and the PC callee covering the
   same codec positions (outermost when nested) propose a pair; accepted only if it is the same pair at
   every occurrence (global uniqueness, gate (b)) and gate (c) holds. Apply recursively inside accepted
   element readers. Unequal sequences: only when the embedding of the PS4 sequence into the PC one is
   unique; mark those pairs `season3-extended`.
3. **Codec-position naming** (rule 3): no function pairs; for equal sequences record per PC codec call site
   the PS4 overload at the same position (`callsites.tsv`), for T007 comments. Never name the shared PC
   codec functions from it.
4. **Listener-slot anchor** (rule 4): PC requester (calls the error-dialog reserve with the slot of an
   accepted RES handler) and its single sender whose `WritePacket` constant key is `(g,id,1)` for the
   handler's `(g,id,2)` pair with the PS4 requester of the PS4 slot and its single `Send_C2S_*`, when both
   reach exactly one sender, the payload write widths are equal, and the PS4 -> PC slot map stays
   monotonic (an inversion rejects both). Refuse shared slots, the login manager ranges, keys with a
   second sender, width mismatches. PC sender name source: the PS4 symbol (the pairing is by code).
5. Rule 5 (packet object) is out of scope here; list it in the README as a later rule.
6. **Precision check, now meaningful**: withhold 20% of the seeds (5 RNG seeds); the derived pairs that
   depend on a withheld seed must either not appear or reappear with the same partner via other witnesses.
   Also a **negative control**: shuffle the PS4 side of the seeds (pair each PC handler with a random other
   PS4 handler); the role anchors must then propose few pairs and the gates must reject nearly all; report
   the counts. A wrong pair in the holdout or a control pair accepted is a failure: tighten, test, rerun;
   stop and ask after two failures.
7. Cross-checks as in T005 (006 matched, T002 holds/wrong, T005b's 117 element-reader pairs).

Outputs `manifest/`: `pairs.tsv` v2 (rule column), `callsites.tsv`, `rejected.tsv`, `conflicts.tsv`,
`precision.tsv`, `control.tsv`, `crosscheck.tsv`, `summary.tsv`; deterministic. Update the README (the
import/extern anchor line T005c made stale).

Owns: `research/03040008/ida-transfer/{match.py,matcher/**,tests/**,manifest/**,README.md}`. Never touch the
extractors, dumps, databases, ddon-hook, client/, packets/.
Libraries: stdlib, pytest, ruff (the T005 own-code reasons stand).
Done: tests per rule incl. near-misses; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`;
`match.py` twice, identical; counts per rule, precision and control tables in the receipt; signed commits
with `git commit -m <msg> -- <paths>`. Stop: budget 180 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
