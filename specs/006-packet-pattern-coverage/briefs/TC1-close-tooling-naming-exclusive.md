006 TC1 (closing): export tooling fixes, naming sweep, Season 3-exclusive list

Objective (build 03040008): three closing items of spec 006 (`tasks.md` Tn lines).

1. Tooling.
   - `packets/imhex-export.sh` reads stdin, so a `while read` loop around it loses its input (T011b).
     Make the script and its children read nothing from stdin; add a check to
     `research/03040008/packets/tests/imhex-export-select.sh` that a `while read` loop over two
     pattern names exports both.
   - `research/03040008/packets/tests/imhex-export-select.sh` is not run by `tools/check.sh`: add it
     (when `packets/imhex-export.sh` or `research/03040008/packets/` changed, and with `--all`), with a
     hook test if `tools/check.sh` has tests for its sections.
2. Naming sweep (README rule after R2b: a field name is code-backed (V), inferred and marked (I) with its
   basis, or `unk_*`; a server name never becomes a field name nor part of an `unk_` name).
   Known: `unk_SpSkillList` / type `SpSkill` (`include/Context.hexpat`, `include/Pawn.hexpat`), 13.6.2
   `unk_RestrictionList`, `CDataDeliveredItem.ItemNum/NeedNum` (`include/Quest.hexpat`). Then grep every
   include and pattern for names whose only basis is a server lead (comments `server:` / `(lead)` /
   "Arrowgene" next to a named field; `unk_<Word>` names) and fix each the same way.
   R3 review findings (2026-11-02; quoted, the reviewer's message is not in the repository), part of
   this sweep:
   - `include/EntryBoard.hexpat:18-23` `EnableJobList` (I "element type") is exactly Arrowgene's
     `CDataEntryRecruitData.cs:15` name; the basis does not give "Enable". Use the PS4 DWARF member name
     if it exists, else a neutral name; fix T013 § 16 by errata and `README.md:981`.
   - `include/CharacterInfo.hexpat:51-52` `ShortCutList`, `CommunicationShortCutList` and
     `include/Character.hexpat:179` `CharacterMessageList` equal Arrowgene's names; T011 § 15 found the
     PS4 member `m_ShortcutList` (V) and 26.12.1/26.14.1 use `ShortcutList`: one key for one element
     type; use the DWARF names where they exist, else neutral names.
   - 19.1.1/19.2.1 `CharacterId` (I from one constant value, also the server name): `unk_u32_0` with
     the observation in a comment (T012 § 2 recommended `unk_*`); `README.md:940`.
   - `include/Context.hexpat:359ff` (`CDataEditInfo` and the resist block) keeps `m_uc*`/`m_us*`
     member names, against the README rule that names drop `m_`; drop the prefixes (this re-exports
     spec 005's context packets too: predict the changed files and verify by sample).
   - `README.md:62-64` lists only 0.0.x, 0.2.x, 1.0.x, 3.0.x as ids the login and game servers share;
     `PacketId.cs:164-187` (lead) also has login 2.0.1/2.0.2 and 5.3.16: add `// packet-select:` to
     the game patterns 2.0.1, 2.0.2, 5.3.16 (check whether login files with those suffixes exist) and
     widen the sentence.
   - Errata (dated "## Errata (R3, 2026-11-02)" sections, original text untouched): T009 § 19 sample
     10426 reads `4D 01 01` (both flags 1), not "u8 0, u8 1"; T013 § 8 sample 138932's trailing
     list-element byte is 1 (`09 64 00 00 00 00 01`), not 0.
   Re-export the patterns whose JSON keys change; 2-file-per-pattern sample: only the renamed keys differ, values
   identical, every file still fits.
3. Season 3-exclusive list (spec deliverable): `specs/006-packet-pattern-coverage/research/season3-exclusive.tsv`
   + a short `.md` beside it: every id the spec left unpatterned (Season 3-exclusive by code or by
   inference, PC-only, unresolved), from the T001 triage (all-exclusive groups 62, 70, 72, 60, 71, 61,
   64, 59, 65 included) and the per-batch reports T002-T013 (their out-of-scope lists): id, raw name,
   group, captured count, PC handler/reader VA, status (exclusive V / exclusive I / unresolved), the
   report section, and what the PC code shows of its layout. Counts per status; check the total against
   the triage (526 uncovered ids) minus the patterned ones.

Owns: `packets/imhex-export.sh`, `research/03040008/packets/tests/`, `tools/check.sh` (+ its tests), the
includes/patterns the sweep touches, the packets README, the re-exported JSON, the two new research
files. Never touch raws, client/, other specs; `tasks.md` is the coordinator's. Commit with
`git commit -m <msg> -- <paths>`; long lists via `git update-index --add --remove -z --stdin`.
Libraries: plbatch via `packets/imhex-export.sh`; jq / stdlib Python (csv) for the list and samples.
Done: signed commits; tests; re-export counts and fit; sample result; `bash tools/check.sh --since <base>`;
receipt from `receipt.py --print` with "For Sam's inspection" (old -> new keys; exclusive counts).
Stop: budget 150 min of work time; finish the scope.
Base: the head when you start.
