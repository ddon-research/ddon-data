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
- [x] T006 Adversarial review (`research/T006-adversarial.md`): no layout defect (independent width walk 4,885/4,887;
  IDA re-read of 19 ids matches); F1 item/stage-id value bases with few distinct values are chance-level; F2 small
  enums named only by the server; F3 counts repeat identical captures. Canaries reproduced by the coordinator.
- [x] T007 Mark fixes + `Instance.hexpat` renaming (94c4d7ca80, 117ce2822e; `briefs/T007-mark-fixes.md`): 123 value
  marks state distinct counts (43 I -> G, 10.14.16 ItemId V (consumer)); F2 applied; Instance ItemId/Num (G); 62.18.2
  duplicate-type compile break fixed (`CDataSoulOrdealTrialCostItem`); 7,477/7,477 re-exported fit, 119 JSON changed
  (renames only). Gate `check.sh --since 81ade7b4c4`: hooks, shell, export, mcp passed.
- [x] Review (adversarial: a sample of V/I/G marks and fits): T006 above; its fixes are T007.
- [x] Close: `check.sh --all`, retro, Close section, merge and push.

## Close (2026-11-03)

- Result: all 115 remaining ids (70 S2C, 45 C2S; 4,887 captures) have patterns and JSON. PC layouts fit 4,885/4,887
  (the other 2 are 29.23.16, whose handler `return 1`s without reading its body: captures only, marks G); the T006
  independent width walk matches the same 4,885 leaf by leaf; after T007 every re-exported file fits (7,477/7,477).
- Marks: V where PC code was read, I with a stated basis (value bases give distinct counts; 3 or fewer distinct or
  chance above 0.05 -> G), G for guesses and server-only names (`G (lead)`). Renamed packets: 11.7.16, 72.1.16 (I);
  62.39.16, 63.2.16, 63.5.16 (G).
- Remaining unknowns: 29.23.16 (no reader); 11.88.16 and 11.118.16 decode but their meaning is open; G names whose
  consumers were not traced (role-only V of 28.34.2 / 11.68.16 consumers, the 13.23.16 ValueOld check: not run).
- Not run: ImHex GUI validation (plbatch export is the parser; ImHex CLI is not on PATH).
- Gate: `bash tools/check.sh --all` at 117ce2822e: hooks, shell, flags, export, idacopy, xfer (473), mcp passed;
  kg failed (`test_production_size_budgets`: `bundle_io.py` 853 lines) in the untracked `research/knowledge-graph/`
  tree of other work, which no 008 commit touches; imhex not run (not on PATH).
- Retro (`retro.py --since 2026-11-03T20:52 --label 008`): 7 agents, about $40 of agent spend, 2.1 h wall. Findings:
  (1) edits of `research/03040008/packets/README.md` echo about 29k tokens each: the id table should move to its own
  file (or a TSV the README links) before the next packet spec; (2) T004/T005 implementers peaked at 294k/298k, at
  the 300k resume limit: briefs over ~35 ids get split; (3) T005 added a structure to a shared include that clashed
  with a pattern's local one and T006 missed it: after any include change, re-export every pattern that includes it
  (T007 did; carried as a brief rule).

## Running

- (none). Spec closed 2026-11-03.
