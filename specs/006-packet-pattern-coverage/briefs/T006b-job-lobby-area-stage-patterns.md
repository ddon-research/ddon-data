006 T006 (patterns): groups 33 JOB, 3 LOBBY, 23 AREA, 12 STAGE

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md`
(read it whole: § 0 method, the per-id sections, § 5 summary, § 6 shared types, § 8 open items) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R1b: V, I with its basis, or `unk_*`; a server
name alone never becomes a field name) and the T005b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids incl. 33.20.16 (settled). Out of scope: Season 3-exclusive 12.5.1/12.5.2
and 12.9.16 (exclusive by absence, X(I)); list them in the README notes with their report sections.
`.3_0_1`/`.3_0_2` also match 41 + 41 login-server files: select the LOBBY ones with
`// packet-select:` (see the login patterns). Shared types per § 6: `CDataCharacterLevelParam` and
`CDataLobbyMemberInfo` in `include/Character.hexpat`, new `include/Job.hexpat` and
`include/Stage.hexpat`; reuse `CDataEquipItemInfo` from `include/Login.hexpat`; no include cycles,
no duplicate type names (move a type an older pattern defines locally into the include only if both
uses match, and show that pattern's re-exported JSON is byte-identical). Existing patterns change
only where the report shows a layout error; list each before/after.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 3,712/3,712 fit across the four groups), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a job change with its equipment, a lobby chat message). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
