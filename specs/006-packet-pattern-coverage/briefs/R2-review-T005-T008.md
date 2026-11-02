006 R2: review the quest, job/lobby/area/stage, pawn/partner and warp/item patterns (T005-T008)

Objective: an independent read of the patterns added by 006 T005b, T006b, T007b and T008b against
their evidence reports and the repository's evidence rules. Find what is wrong, not what is right.

Inputs: reports `specs/006-packet-pattern-coverage/research/{T005-quest,T006-job-lobby-area-stage,
T007-pawn-partner,T008-warp-item}.md`; the patterns and includes those packages added or
changed in `research/03040008/packets/` (the README table rows for groups 11, 33, 3, 23, 12, 8, 58, 53, 14, 10, 50 and the includes
`Quest`, `Job`, `Stage`, `Character`, `Pawn`, `PawnExpedition` and the T008 ones);
`research/03040008/packets/README.md`; `AGENTS.md` § Evidence rules; spec `specs/006-packet-pattern-coverage/spec.md`.

Check, per pattern: field order and widths equal the report's table (the report is the claim; where
the report cites a VA or a recompilation line, say if the pattern departs from it); RES/NTC header
handling per the report; V/I marks carried over (no inference presented as fact; Arrowgene names
only as marked leads); `// packet-id:` / `// packet-select:` correct for ids the login and game
servers share; includes without duplicate or conflicting struct definitions; README rows and open
items match the patterns. Sample the JSON: 2 files per pattern under `packets/decrypted_json/`
(bounded: select by id suffix) and check that the decoded values are plausible and that keys follow
the README conventions and its naming rule (V, I with basis, or `unk_*`; a server
name alone never becomes a field name; R1 found this broken once) (root `packet`, lowercase header keys, `count`/`entries`, `length`/`value`).

Owns nothing: read-only. Report findings in your final message: each with file:line, what is
wrong, the evidence (report section / VA), severity (wrong data / misleading / cosmetic). No
findings for style alone. Also check the moved shared types (T005b moved 4 quest types into `Quest.hexpat`) are
defined once. Stop: budget 60 min of work time.
Base: the head when you start.
