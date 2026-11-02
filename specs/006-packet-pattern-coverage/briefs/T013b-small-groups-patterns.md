006 T013 (patterns): the small groups 30, 34, 9, 18, 52, 15, 41, 54, 57, 51

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T013-small-groups.md`
(read it whole: § 0 method, the per-id sections, § 15 summary, § 16 shared types, § 18 open items; `T013-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R2b: V, I with its basis, or `unk_*`; a server
name never becomes a field name, nor part of an `unk_` name: it goes to a `// server: … (lead)` comment) and the T012b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids of groups 30, 34, 9, 18, 52, 15, 41, 54, 57, 51, incl. 15.0.16/15.1.16
(event start/end, V by call graph), 34.6.16 (V by behaviour) and 34.16.16 (I: unique {u32, u32} shape;
names I with that basis). Out of scope: 63.x (no PS4 counterpart), 34.0.x, 41.5.x, 41.8.x (PC-only);
list them in the README notes with their report sections. 9.1.2 is the save-blob response: its request
9.1.1 is covered (T001b); reuse its includes. Shared types per § 16 (craft progress / setting / recipe
materials, entry-board records, dispel); no include cycles, no duplicate type names. Existing patterns
that use a type the report changes (search the patterns for the craft, entry-board, dispel types):
check each, fix and re-export what differs, list each before/after with fit counts (an unchanged
output needs only the byte-identical check).

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 242/242 fit across the groups, minus the out-of-scope ids), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Run `packets/imhex-export.sh` with `</dev/null` inside any loop (it reads stdin).
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a craft progress, an entry-board recruit, an event start). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
