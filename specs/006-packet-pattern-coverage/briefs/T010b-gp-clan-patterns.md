006 T010 (patterns): groups 28 GP, 31 CLAN

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T010-gp-clan.md`
(read it whole: § 0 method, the per-id sections, § 24 summary, § 25 shared types, § 27 open items; `T010-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R2b: V, I with its basis, or `unk_*`; a server
name never becomes a field name, nor part of an `unk_` name: it goes to a `// server: … (lead)` comment) and the T009b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids of groups 28 and 31, incl. 28.25.16 = GP_COURSE_START_NTC and
28.26.16 = GP_COURSE_EXTEND_NTC (V by behaviour) and 31.40.1 (matched by PS4 DWARF
`CPacket_C2S_CLAN_PARTNER_PAWN_DATA_GET_REQ`; the triage's exclusive mark was wrong). Out of scope:
28.24.16 (I), 31.53.2 (V), 28.23.x, 28.34.x, 31.53.1 (Season 3-exclusive); list them in the README
notes with their report sections. Shared types per § 25: extend `include/GP.hexpat` (the login GP
course types) and `include/Clan.hexpat`; reuse the furniture-layout and equipment types where § 25
says; no include cycles, no duplicate type names. Existing patterns that use a type whose Season 3
layout the report changes (e.g. `CDataGPCourseAvailable` / course types used by the login patterns,
clan member/info types used by existing clan patterns): check each, fix and re-export what differs,
list each before/after with fit counts (an unchanged output needs only the byte-identical check).
StatusInfo (§ 23): no change; add the report's basis (MaxHp is a base value) to the comment at
`include/Character.hexpat:136`.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 792/792 fit across both groups, minus the out-of-scope ids), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a GP course lineup, a clan shop entry). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
