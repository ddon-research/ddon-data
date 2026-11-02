006 T012 (patterns): groups 27, 29, 19, 39, 25, 43, 20

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md`
(read it whole: § 0 method, the per-id sections, § 18 summary, § 19 shared types, § 21 open items; `T012-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R2b: V, I with its basis, or `unk_*`; a server
name never becomes a field name, nor part of an `unk_` name: it goes to a `// server: … (lead)` comment) and the T011b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids of groups 27, 29, 19, 39, 25, 43 and 20, incl. 27.8.16 =
ACHIEVEMENT_COMPLETE_NTC and 27.9.16 = RECEIVABLE_REWARD_NTC (settled, V). Out of scope: 27.10.1/2
(Season 3-exclusive, V) and 29.23.16 (PC handler ignores the body, PS4 candidate rejected); list them
in the README notes with their report sections. Shared types per § 19 (the Season 3
`CDataEquipItemInfo` already in `include/Login.hexpat`; `EquipElementParam` with its extra u16; the
{u8, list {u8, u16}} tail of reader `0x765f70`, which has 12 callers: give it one shared type);
no include cycles, no duplicate type names. Existing patterns that use a type the report changes
(search the patterns for `EquipElementParam`, the skill and orb types): check each, fix and
re-export what differs, list each before/after with fit counts (an unchanged output needs only the
byte-identical check).

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 688/688 fit across the groups, minus the out-of-scope ids), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Run `packets/imhex-export.sh` with `</dev/null` inside any loop (it reads stdin).
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. an achievement completion, an equipment change, a gacha result). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
