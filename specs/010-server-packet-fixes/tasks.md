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
- [x] T003 PC evidence (`research/T003-pc-evidence.md`): error F06, W02, W16 (+ N1), W21, D06; harmless 15 (incl. 62.33.2, W01); not an error W06, W15, W22, D08,
  T05; not settled F09 (scan), W05. General rule: an S2C key with no client record or a read past the frame end ends the session (3001); padding rescues short layouts.
- [x] T004a Patch part 1 (`research/T004a-patch.md`; clone `fix/packet-handling` at `c423c48b`, 9 signed commits, unpushed): 125/125 in Debug and Release, 520
  warnings, 52 new tests fail on develop (21 pass there, explained); differential: nothing that agreed now differs. Newly closes a connection on a bad frame length, bad
  source byte, a factory exception, a failed challenge. F09: relayed text has no cap: fixed in part 2. N3: none of the 6 ids is sent. Limits: F08's queue half, `CreateCharacter`
  Result 1 untested; F12 fails only at its reflection check.
- [ ] T004b Patch part 2: wire layouts and F09 cap (`implementer`, `briefs/T004b-layout-patch.md`).
- [ ] T005 Adversarial review: which fix would break a working client? (`adversarial-reviewer`), then fixes.
- [ ] T005b Live smoke on `C:\ddon-automation`: patched server, real client, a game login (W01 touches every one), one error path, one quest end (W16).
- [ ] T006 Impact outline and PR body (`research/impact.md`); push the branch, open the draft PR on the fork.
- [ ] T007 Close; ask Sam about upstream and disclosure of the pre-login rows; docs follow-ups.

## Ruling on the patch set (coordinator, 2026-11-04, from T003)

- **Fix**: F06, F07, F08, D06, D01, R01, D02, F01, R02, R03, R04, R05, R06, R07, F03, F11, F12 (part 1). W02, W16 + N1, W01, W03, W04, W10, W11, W12, 62.33.2, 31.17.2 excess byte; readers W08, W09, W14, W17, 11.4.2, 11.60.16; F05 with the 4 guards (part 2). Harmless rows are in because the wire should match the client and a test costs little; each is its own commit so a maintainer can drop it.
- **Do not fix**: F02 (real risk, no client benefit); W06, W15 (bytes are right: swapping breaks skills and spawns); W22, D08, T05 (not errors); W05 (40 known for one dungeon only); R08 (design); renames (out of scope, listed in the PR as follow-ups).
- **Decide after a look**: W21 (which goods should show the line: compare captures' `+20` with server goods; fix only if data says which); F09 (scan first); F10 (throw only if proven safe).

## Running

- T004b (implementer, brief `briefs/T004b-layout-patch.md`), started 2026-11-04. Next: land, T005 adversarial review, T005b live smoke, T006 impact and draft PR. To carry: `docs/reference/status.md` says `ag_vs_pc` 3 differ, T001 says 2 (34.0.1 was
  corrected, TSV not regenerated); `docs/explanation/two-packet-decodings.md`'s 19.28.2 example hangs on T003's read of PC consumers of
  `+8`, `+0xc`: fix both pages when settled. R01/R02 are pre-login: ask Sam how to disclose before anything goes upstream.
