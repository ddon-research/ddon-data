007 T009: settle the name and prototype conflicts with the earlier annotations (evidence)

Question (PC 03040008, PS4 02020005): T006/T007e left 7 name rows and 54 prototype rows unwritten because the
work copy already carries a different non-default name or a hand-set prototype from the earlier work
(ddon-hook specs 006-008). For each, which is right on PC, by code? Rows: `research/03040008/ida-transfer/manifest/transfer/names.tsv`
and `prototypes.tsv`, status `conflict` (with the current value recorded); context: `research/T002-audit.md`
(the earlier work's verdicts), `research/T001-prior-method.md`.

Step 0 (read-only check of the work copy after T006d, 733a4c77e6): run `apply_transfer.py` as a dry run and as
`--verify --apply-log dumps/apply.jsonl` on `ddon-data-007work` by headless batch only (both end with
`DBFL_KILL`; check the copy's sha256 `be0cc624...162f` is unchanged after). Expected: every row `already` / `ok`
(including `MtArray`, now compared by member type), conflicts still reported. Output `dumps/apply-dryrun-t009.jsonl`,
`dumps/apply-verify-t009.jsonl`; any non-`already` row is a finding (report it, do not apply).

Per row decide `ours` (our row is right, the current value is wrong: say what the code shows against it),
`theirs` (the current value is right or more precise: say why, and whether our row is wrong or only less
specific), `merge` (e.g. our name with their better argument types: give the exact declaration), or
`undecided` (what would settle it). Evidence from PC code only (callers' pushes and cleanup, `ret N`, ecx use,
argument uses, the string the name repeats), PS4 DWARF for argument names/types, never Arrowgene names.
T006 noted examples: senders spelled `Send_C2S_ACHIEVEMENT_ACHIEVEMENT_...` and `0x7DA410`
`OnPacket_S2C_STAY_INN_RES`.

Databases: read-only, `bash research/ida/private-copy.sh pc-accepted t009` and `... ps4 t009` (ida-mcp or
batch; delete the copies at the end; never open `ddon-data-007work`); the applied state is in
`research/03040008/ida-transfer/dumps/pc-ida-applied.jsonl`.
Output: `specs/007-pc-handler-annotation/research/T009-conflicts.md` and `T009-decisions.tsv` (kind, pc_va,
current, ours, decision, final value, evidence VAs, reason). Owns only those. Never touch scripts, manifest,
dumps, databases other than your private copies, ddon-hook, client/, packets/.
Libraries: ida-mcp `execute_python` or idat batch; stdlib.
Done: all 61 rows decided or undecided with reason; final message with the paths and at most 15 lines.
Stop: budget 90 min of work time; batch lookups. Base: the head when you start.
