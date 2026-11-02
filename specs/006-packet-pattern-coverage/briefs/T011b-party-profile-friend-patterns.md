006 T011 (patterns): groups 6 PARTY, 26 PROFILE, 16 FRIEND, 17 BLACK, 5

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md`
(read it whole: § 0 method, the per-id sections, § 17 summary, § 18 shared types, § 20 open items; `T011-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R2b: V, I with its basis, or `unk_*`; a server
name never becomes a field name, nor part of an `unk_` name: it goes to a `// server: … (lead)` comment) and the T010b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids of groups 6, 26, 16, 17 and 5, incl. 5.2.16, 5.3.16, 6.8.16, 6.10.16,
6.18.16 (settled, V). Out of scope: 24.6.16 (PC-only, V; group 24 is JOB_MASTER); list it in the
README notes with its report section. Shared types per § 18: `CDataFriendInfo`,
`CDataHistoryElement`, `CDataAchieveCategoryStatus` in `include/Character.hexpat`; reuse the job-orb
types for 26.1.2's second list, `CDataCharacterListElement` and the 3-u8 `CDataLobbyMemberInfo` (5.2.16
now settles it: say so in its comment); no include cycles, no duplicate type names. Existing patterns
whose output a moved or changed type touches: check each, fix and re-export what differs, list each
before/after with fit counts (an unchanged output needs only the byte-identical check).

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 1,151/1,151 fit across the groups, minus 24.6.16), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a friend list entry, a party join notice, a profile). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
