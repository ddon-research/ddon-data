# 010 tasks

Coordinator: main session. One subagent at a time. Goal, error classes, method and PR rules: `spec.md`.

- [x] T000 Clean clone: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, `develop` at `e2411fe8f9`, equal to upstream.
- [x] T001 Inventory (`research/T001-inventory.md`, `T001-candidates.tsv`): 64 candidates (framework 17, table 8, dispatch 8,
  robustness 9, wire lead 22). Top: F06 error RES sent twice; D01/R01 no serializer for `CDataOcdImmuneLv`, huge count stalls the single
  lane without login; F01 TCP split in a length prefix; R02 bad frame length, buffer grows; W01 0.1.2 u16 vs PC bool. Refuted: 34.0.1,
  stamp. No wrong group/id/sub. 19.28.2: do **not** swap the wire on current evidence. Baseline not run (role cannot build): moved to T002.
- [ ] T002 Baseline and differential (`implementer`, `briefs/T002-baseline-differential.md`): build and tests, then server serializers over the
  captures, read and re-encode, values against the JSON; per-id table, on a scratch branch that is not part of the PR.
- [ ] T003 Evidence: PC 03040008 reader or writer per candidate, verdict `V` / `I` / not an error (`evidence-researcher-ida`).
- [ ] T004 Patch: branch `fix/packet-handling`, a test per fix (`implementer`).
- [ ] T005 Adversarial review: which fix would break a working client? (`adversarial-reviewer`), then fixes.
- [ ] T006 Impact outline and PR body (`research/impact.md`); push the branch, open the draft PR on the fork.
- [ ] T007 Close; ask Sam about upstream.

## Running

- T002 (implementer, brief `briefs/T002-baseline-differential.md`), started 2026-11-04. Next: brief T003 with the IDA questions
  of T001 § 7 plus T002's new divergences. To carry: `docs/reference/status.md` says `ag_vs_pc` 3 differ, T001 says 2 (34.0.1 was
  corrected, TSV not regenerated); `docs/explanation/two-packet-decodings.md`'s 19.28.2 example hangs on T003's read of PC consumers of
  `+8`, `+0xc`: fix both pages when settled. R01/R02 are pre-login: ask Sam how to disclose before anything goes upstream.
