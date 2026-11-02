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
   "Arrowgene" next to a named field; `unk_<Word>` names) and fix each the same way. Re-export the
   patterns whose JSON keys change; 2-file-per-pattern sample: only the renamed keys differ, values
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
Stop: budget 90 min of work time; finish the scope.
Base: the head when you start.
