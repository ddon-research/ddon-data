006 R3: review the mail/stamp/character, GP/clan, party/profile/friend, achievement/equip/skill and small-group patterns (T009-T013)

Objective: an independent read of the patterns added by 006 T009b, T010b, T011b, T012b and T013b against
their evidence reports and the repository's evidence rules. Find what is wrong, not what is right.

Inputs: reports `specs/006-packet-pattern-coverage/research/{T009-mail-stamp-character,T010-gp-clan,
T011-party-profile-friend,T012-achievement-equip-skill,T013-small-groups}.md`; the patterns and includes those packages added or
changed in `research/03040008/packets/` (the README table rows for groups 37, 45, 2, 28, 31, 6, 26, 16, 17, 5, 27, 29, 19, 39, 25, 43, 20
and the T013 groups, and the includes `Mail`, `Stamp`, `CharacterInfo`, `Character`, `GP`, `Clan`,
`Furniture` and the ones T012b/T013b add);
`research/03040008/packets/README.md`; `AGENTS.md` § Evidence rules; spec `specs/006-packet-pattern-coverage/spec.md`.

Check, per pattern: field order and widths equal the report's table (the report is the claim; where
the report cites a VA or a recompilation line, say if the pattern departs from it); RES/NTC header
handling per the report; V/I marks carried over (no inference presented as fact; Arrowgene names
only as marked leads); `// packet-id:` / `// packet-select:` correct for ids the login and game
servers share; includes without duplicate or conflicting struct definitions; README rows and open
items match the patterns. Sample the JSON: 2 files per pattern under `packets/decrypted_json/`
(bounded: select by id suffix) and check that the decoded values are plausible and that keys follow
the README conventions and its naming rule (V, I with basis, or `unk_*`; a server
name alone never becomes a field name; R1 and R2 found it broken) (root `packet`, lowercase header keys, `count`/`entries`, `length`/`value`).

Owns nothing: read-only. Report findings in your final message: each with file:line, what is
wrong, the evidence (report section / VA), severity (wrong data / misleading / cosmetic). No
findings for style alone. Also check the moved shared types (T010b moved `CDataFurnitureLayout` into `Furniture.hexpat`) are
defined once. Stop: budget 60 min of work time.
Base: the head when you start.
