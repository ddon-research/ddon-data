006 T007 (patterns): groups 8 PAWN, 58 PAWN_EXPEDITION, 53 PARTNER

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T007-pawn-partner.md`
(read it whole: § 0 method, the per-id sections, § 5 summary, § 6 shared types, § 8 open items; `T007-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R1b: V, I with its basis, or `unk_*`; a server
name alone never becomes a field name) and the T006b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: all 43 ids (all PS4-matched; 8.37.16 = JOIN_PARTY_PAWN_NOTICE and 53.9.16 =
PAWN_LIKABILITY_UP_NTC settled). Shared types per § 6: Season 3 `CDataPawnInfo` and friends in
`include/Pawn.hexpat`, a new expedition include for group 58, `CDataPartnerPawnData` shared by groups
8 and 53; reuse the gathering-item element from `include/Instance.hexpat`; no include cycles, no
duplicate type names (move a type an older pattern defines locally into the include only if both
uses match, and show that pattern's re-exported JSON is byte-identical). Existing patterns change
only where the report shows a layout error (e.g. an existing pattern using the PS4 `CDataPawnInfo`):
list each before/after with re-exported JSON.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 1,569/1,569 fit across the three groups), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a pawn's info with its Season 3 lists, an expedition result). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
