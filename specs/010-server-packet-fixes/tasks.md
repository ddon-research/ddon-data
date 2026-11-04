# 010 tasks

Coordinator: main session. One subagent at a time. Goal, error classes, method and PR rules: `spec.md`.

- [x] T000 Clean clone: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, `develop` at `e2411fe8f9`, equal to upstream.
- [x] T001 Inventory (`research/T001-inventory.md`, `T001-candidates.tsv`): 64 candidates (framework 17, table 8, dispatch 8,
  robustness 9, wire lead 22). Top: F06 error RES sent twice; D01/R01 no serializer for `CDataOcdImmuneLv`, huge count stalls the single
  lane without login; F01 TCP split in a length prefix; R02 bad frame length, buffer grows; W01 0.1.2 u16 vs PC bool. Refuted: 34.0.1,
  stamp. No wrong group/id/sub. 19.28.2: do **not** swap the wire on current evidence. Baseline not run (role cannot build): moved to T002.
- [x] T002 Baseline and differential (1c3e5fc68d; harness `7d114a556b` on local `harness/differential`): Debug and Release exit 0, 521 warnings,
  52/52 tests. All 160,615 captures: 0 exceptions outside 63 `Error != 0` (13.3.2, 18.0.2, 19.1.2, 19.2.2, the CLI patch's four); 23 ids diverge, 7 new.
  New: 62.33.2 `CDataSeasonDungeonBuffEffectReward.cs:24` writes `BuffId` where the official server sends `Level`. Confirmed by bytes: W01-W03, W08-W11,
  W14, W17. Failing proofs: D01 (2), R01 (OOM at 512 MiB in 675 ms), F06 (2 frames, needs a real seam). Same-width names and order: no signal by construction.
- [ ] T003 Evidence: PC 03040008 consumer per candidate, verdict error / harmless / not an error / not settled (`evidence-researcher-ida`,
  `briefs/T003-pc-evidence.md`).
- [ ] T004 Patch: branch `fix/packet-handling`, a test per fix (`implementer`).
- [ ] T005 Adversarial review: which fix would break a working client? (`adversarial-reviewer`), then fixes.
- [ ] T006 Impact outline and PR body (`research/impact.md`); push the branch, open the draft PR on the fork.
- [ ] T007 Close; ask Sam about upstream.

## Running

- T003 (evidence-researcher-ida, brief `briefs/T003-pc-evidence.md`), started 2026-11-04; copies `ddon-data-t003`, deleted at landing.
  Next: rule which candidates get patched, brief T004. To carry: `docs/reference/status.md` says `ag_vs_pc` 3 differ, T001 says 2 (34.0.1 was
  corrected, TSV not regenerated); `docs/explanation/two-packet-decodings.md`'s 19.28.2 example hangs on T003's read of PC consumers of
  `+8`, `+0xc`: fix both pages when settled. R01/R02 are pre-login: ask Sam how to disclose before anything goes upstream.
