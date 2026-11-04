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
- [x] T004b Patch part 2 (`research/T004b-patch.md`; clone head `924094e0`, 26 signed commits in all, unpushed): 170/170 in Debug and Release, 520 warnings; differential agrees
  494 -> 511 plus 2 headerless, re-encode 159,008/159,008, 63/63 `Error != 0` read. W21 left unfixed: all 1,443 goods in `Shop.json` have an empty requirement list, the data is
  missing. F09 cap 0x7FF. F05 by a private exception, one catch over 492 call sites. `TestBase` could kill the Debug test host: fixed.
- [x] T005 Adversarial review (`research/T005-adversarial.md`): F1 **blocks**: R05's `!= 32` check refuses every real client (the PC encrypts 48 bytes; reproduced by the coordinator). F2:
  fixtures hold session tokens and padding that looks like an IP tail. Held: 125 streams replayed, 116,523 C2S packets, 0 closes or throws; split reads 130,521 packets, 0 mismatches.
- [x] T005a Review fixes (`research/T005a-fixes.md`; clone head `b8be1e19`, 29 signed commits, unpushed; earlier hashes rewritten, look up by subject): F1 fixed, mutation fails 6 and 7 tests; 177/177
  Debug and Release; fixtures filled, 0 token hits in history (old objects stay in this clone's reflog only). Canned dumps 851: 2 of 18.0.2 escape through direct `Read`, production reads neither. Open risk,
  as on `develop`: a RES is lost to a reset if the client is still sending at a close (0/20 on loopback; 125/125 captures send nothing between). R03, R04 rest on captures only.
- [x] T005b Live smoke (`research/T005b-live-smoke.md`, evidence `C:\ddon-automation\t005b-evidence\`): real client logs in (same 40 ids in order as `develop`), plays, moves worlds; F06 1 RES and 1 dialog vs 2 RES on `develop`;
  category 6 banner shown; R05, R02, R03 close only the bad connection; R01 no stall, sender stays open; no 3001 or 33001. Not reached: quest-end time (W16), once flag, category 6 catch-up flood. All runs used f2a8, not f1c9. Client restored. No patch defect.
- [x] T006 Impact outline and PR body (`research/impact.md`, `pr-body.md`, `T006-commit-messages.md`; 6a9e2fe6e6): body clean, all 29 subjects found, no token, key, IP, path or task id. CLI patch applies, 16 of 16 hunks, 4 become dead code by reading; patched CLI on 3 streams: same packets and order, 16 of 1,053 `StructDump` lines change; full re-annotate not run. Found: five commit messages and a test comment state what the body leaves out, `f8683307` is wrong at the head, 18 lines carry task ids.
- [x] T006a Make the branch fit to publish (`research/T006a-branch-wording.md`; 0c4f582231, 47fe810aab): clone head `64c676b9`, 29 of 29 signed, subjects identical, tree differs from `b8be1e19` in 6 files, 9 lines each side, comments only; Debug and Release 0 errors, 520 warnings, 177/177. Ruled by the coordinator: the client stack buffer note also goes, as a server diff needs the limit only. Local `backup/before-wording` at `b8be1e19` is never pushed.
- [x] T006b Pushed `fix/packet-handling` to the fork; draft [PR 8](https://github.com/Sehkah/Arrowgene.DragonsDogmaOnline/pull/8), base `develop` (fork `develop` = `e2411fe8f9`), 29 commits, 97 files, +2,688/-174, mergeable, bound in the app; none on upstream. `impact.md`'s hashes remapped by subject to the pushed ones.
- [ ] T007a `check.sh --all`.
- [ ] T007b Whole-spec review and audit of the docs the spec touched (`reviewer`, `briefs/T007b-whole-spec.md`), then fixes. No guard or check was added by this spec, so no guard review.
- [ ] T007c Retrospective (`retro.py`, one `repository-researcher` on the outliers), learnings.
- [ ] T007d Close section, `**Status: done**`, `CLAUDE.md` Resume, `AGENTS.md`'s `.Clean` line; scratch cleaned.
- [ ] T007e Ask Sam: upstream and how to disclose; merging spec 010's reports to the public `main`.

## Ruling on the patch set (coordinator, 2026-11-04, from T003)

- **Fix**: F06, F07, F08, D06, D01, R01, D02, F01, R02, R03, R04, R05, R06, R07, F03, F11, F12 (part 1). W02, W16 + N1, W01, W03, W04, W10, W11, W12, 62.33.2, 31.17.2 excess byte; readers W08, W09, W14, W17, 11.4.2, 11.60.16; F05 with the 4 guards (part 2). Harmless rows are in because the wire should match the client and a test costs little; each is its own commit so a maintainer can drop it.
- **Do not fix**: F02 (real risk, no client benefit); W06, W15 (bytes are right: swapping breaks skills and spawns); W22, D08, T05 (not errors); W05 (40 known for one dungeon only); R08 (design); renames (out of scope, listed in the PR as follow-ups).
- **Decide after a look**: W21 (which goods should show the line: compare captures' `+20` with server goods; fix only if data says which); F09 (scan first); F10 (throw only if proven safe).

## Running

- T007b (reviewer, brief `briefs/T007b-whole-spec.md`), started 2026-11-04; `check.sh --all` running beside it. This repository's branch is unpushed and `main` is at `78466dfe8e`. Next: land, T007c, T007d; then **ask Sam before merging spec 010 to ddon-data `main`, since its reports hold pre-login reproduction detail and that repository is public, and before anything goes upstream.**
