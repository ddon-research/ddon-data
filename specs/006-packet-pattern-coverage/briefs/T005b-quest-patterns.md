006 T005 (patterns): group 11 QUEST

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T005-quest.md`
(704 lines: read § 0-1 method, the per-id sections you implement, § 43 summary, § 44 shared types,
§ 46 open items) as one `research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with
`// packet-id:` lines, following `research/03040008/packets/README.md` (its naming rule after R1b:
a field name is code-backed (V), inferred and marked (I) with its basis, or `unk_*`; a server name
alone never becomes a field name) and the T004b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids, including the 9 the report settled (11.39.16, 11.60.16, 11.70.16,
11.83.16, 11.95.16, 11.103.16, 11.117.16, …; the summary table is authoritative). Out of scope:
Season 3-exclusive 11.5.x, 11.121-123.x, 11.7.16, 11.68.16, and the unresolved 11.88.16 and
11.118.16; list them in the README's "Season 3-exclusive, not patterned" / "unresolved" notes with
their report sections. Shared types: the Season 3 `CDataQuestList` (PC `0x774530`) and its entries
in `include/Quest.hexpat` beside (not replacing) `CDataQuestOrderList`; reuse wallet/exp types from
existing includes; no include cycles. Existing quest patterns (11.x already covered) change only
where the report shows a layout error; list each before/after with re-exported JSON.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 4,352/4,352 fit across the group), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 46).
Owns: the new patterns, `include/Quest.hexpat` additions, changed quest patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a quest list entry with its wallet/exp lists). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: 1159abe264.
