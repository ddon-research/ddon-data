006 T001c (patterns): apply the T001c findings to the patterns and re-export

Objective (build 03040008): implement every "Pattern change" paragraph of
`specs/006-packet-pattern-coverage/research/T001c-parked-static-items.md` (read it whole; items 1-6,
lines 86, 130, 188, 223, 249, 271) in `research/03040008/packets/`:

1. 35.12.16: the second structure (15 named fields, the OcdImmuneLv list, the fixed u32[4]) in
   `include/Context.hexpat` and the 35.12.16 pattern; no captures exist, so check it on a synthetic
   file built from the report's field table and say so.
2. The 35.0.2 / 35.1.x / 35.2.x / 35.4.x body variants (Resist placement, pawn layout) as types in
   `include/Context.hexpat`, marked "no captures, unvalidated"; no new pattern files.
3. 13.44-13.47: start/end and own-player/enemy comments and field names per the report (status ID,
   the always-0 fifth field); correct the P5 claims the report contradicts. Packet names stay open.
4. `PRTSet` float order: drop "inferred", cite the PS4 `stPRTData` evidence.
5. `include/Quest.hexpat` QuestEnemyInfo order {GroupId, Season 3 u32, Lv, IsPartyRecommend}.
6. `include/nNetMsg.hexpat` names/comments (`cpCatchCtrl::mCaughtInfo` V, the SetCreateContext
   triple I, 0x3C = cContextInstEm array); list the rest unresolved with what they feed.

Every name keeps its V/I mark from the report. Re-export only the patterns whose JSON output changes
(renamed or reordered fields), with plbatch via `packets/imhex-export.sh @ <name>`; field names in
nNetMsg change only for the message types that carry them: re-export those packets, not all 110k,
and verify by prediction + a stratified sample (old vs new JSON differ only in the predicted keys),
never by an exhaustive diff. All captures of each re-exported id still fit (counts per id).
Update the README rows/open items those changes touch; record T001c done in
`specs/006-packet-pattern-coverage/tasks.md` (that one checkbox line only).
Owns: `research/03040008/packets/**` (patterns, includes, README), the re-exported
`packets/decrypted_json/**` files, that tasks.md line. Never touch raws, client/, other specs.
Stage large path lists with `git update-index --add --remove -z --stdin`; commit with
`git commit -m <msg> -- <paths>`.
Libraries: ImHex std, plbatch, stdlib Python for the sample comparison.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since 3ef33ecaff`; receipt from
`receipt.py --print` with a section "For Sam's inspection" (changed JSON keys per id, one example
file with before/after values). Stop: budget 90 min of work time; finish the scope.
Base: 3ef33ecaff.
