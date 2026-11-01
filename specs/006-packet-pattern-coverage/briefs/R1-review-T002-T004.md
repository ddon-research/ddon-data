006 R1: review the login, connection-setup and instance patterns (T002-T004)

Objective: an independent read of the patterns added by 006 T002b, T002e, T003b and T004b against
their evidence reports and the repository's evidence rules. Find what is wrong, not what is right.

Inputs: reports `specs/006-packet-pattern-coverage/research/{T002-login,T002c-challenge-decrypt,
T003-connection-server-cert,T004-instance}.md`; the patterns and includes those packages added or
changed in `research/03040008/packets/` (`git log --stat 5421fdf867^..HEAD -- research/03040008/packets`);
`research/03040008/packets/README.md`; `AGENTS.md` § Evidence rules; spec `specs/006-packet-pattern-coverage/spec.md`.

Check, per pattern: field order and widths equal the report's table (the report is the claim; where
the report cites a VA or a recompilation line, say if the pattern departs from it); RES/NTC header
handling per the report; V/I marks carried over (no inference presented as fact; Arrowgene names
only as marked leads); `// packet-id:` / `// packet-select:` correct for ids the login and game
servers share; includes without duplicate or conflicting struct definitions; README rows and open
items match the patterns. Sample the JSON: 2 files per pattern under `packets/decrypted_json/`
(bounded: select by id suffix) and check that the decoded values are plausible and that keys follow
the README conventions (root `packet`, lowercase header keys, `count`/`entries`, `length`/`value`).

Owns nothing: read-only. Report findings in your final message: each with file:line, what is
wrong, the evidence (report section / VA), severity (wrong data / misleading / cosmetic). No
findings for style alone. Stop: budget 45 min of work time.
Base: the head when you start.
