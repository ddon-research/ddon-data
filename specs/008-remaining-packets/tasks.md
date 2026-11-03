# 008 tasks

Coordinator: main session. One subagent at a time. Method, sources and marks: `spec.md`.

- [x] T001 Triage (`research/T001-triage.md`, `T001-triage.tsv`): 115 ids (70 S2C, 45 C2S), 4,887 files; every id has a
  PC handler or sender; PC layouts fit 4,885/4,887 (29.23.16's handler ignores its body); 5 writer loops inferred;
  Arrowgene names all 115, structures 87 (81 equal to the PC layout); 7 batches. Plan: T002 writer loops (IDA),
  T003 B5+B2, T004 B1+B4, T005 B3+B7+B6 (patterns, JSON, names), then review.
- [x] T002 Writer loops (`research/T002-writer-loops.md`): the 5 lists and `Write_cstr` (u16 BE length, no NUL) read
  in PC code (V); TSV layouts confirmed; fit 370/370.
- [x] T003 B5+B2 (2b5782052c, `research/T003-batches-B5-B2.md`): 33 patterns, 2,677/2,677 fit, 63/63 sample walks;
  I names e.g. 60.0.2 NpcId (7/7 echo), 61.2.2 PawnId (60/60 vs 8.2.2), 31.53.2 item ids (8/8); rest G or unk with
  leads; 11.7.16 named MOB_HUNT_QUEST_LIST_NUM_NTC (I: handler's notice class); 11.88.16/11.118.16 meaning-open.
- [x] T004 B1+B4 (5edf6adf7e, e4f4e5b741, `research/T004-batches-B1-B4.md`): 37 patterns, 1,631/1,631 fit, 68/68
  sample walks; new includes SeasonDungeon/DailyMission/InfinityDelivery; T001 corrected for 72.2.1 (u32 list + u8);
  72.1.16 named DAILY_MISSION_ACHIEVE_NTC (I: listed missions go 1 -> 2 in 113/113); 62.15.16 TrialId (28/28);
  OmState structure from the shared reader `0x766790`; groups 72/59 names I/G (59: one session).
- [x] T005 B3+B7+B6 (6a78dfac56, 391743c734, 3dbfb39755, `research/T005-batches-B3-B7-B6.md`): 45 patterns, 579/579
  fit, 75/75 sample walks; T001 corrected for 34.0.1 (list of u64); new `ChainDungeon.hexpat`; 42 fields I by value
  (e.g. season dungeon buff ids = AbilityIds of `contents_buff_info.abl`, 85/85); 62.39.16 and 63.2.16 renamed (G);
  proposal: rename `Instance.hexpat` `GatheringItemListRes_unk_1` fields (u32 = ItemId 38/38).
  All 115 ids decoded: 4,887 captures.
- [ ] T007 Naming follow-ups (existing includes, review findings). evidence where the dump lacks a reader (`evidence-researcher-ida`), patterns + JSON
  (`implementer`), naming by code / data / extractor / leads; each with its fit counts and JSON changes.
- [ ] Review (adversarial: a sample of V/I/G marks and fits), close, merge and push.

## Running

- T006 (adversarial-reviewer, agent a60ac66e9ecc89462, brief `briefs/T006-adversarial.md`), started 2026-11-03.
  Next: file its report as `research/T006-adversarial.md` (reproduce canaries first), then T007 (implementer): fix the
  findings, rename `Instance.hexpat` `GatheringItemListRes_unk_1` fields (u32 = ItemId 38/38; re-export the users),
  then close (check.sh --all, retro, tasks Close, merge and push without asking).
