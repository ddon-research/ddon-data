006 T009 (patterns): groups 37 MAIL, 45 STAMP, 2 CHARACTER

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md`
(read it whole: § 0 method, the per-id sections, § 21 summary, § 22 shared types, § 24 open items; `T009-walk.py` re-runs the walk) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` (naming rule after R2b: V, I with its basis, or `unk_*`; a server
name never becomes a field name, nor part of an `unk_` name: it goes to a `// server: … (lead)` comment) and the T008b patterns (RES header `s32 Error` then `s32 Result`
+ body only when Error == 0; NTCs per the report).

Scope: the PS4-matched ids of groups 37, 45 and 2, incl. the settled 2.6.16, 2.27-2.28, 2.31-2.32
(V by behaviour) and 2.29/2.30 (matched by ordering only: names I with that basis). Out of scope:
45.3.1/2, 45.4.1/2 (Season 3-exclusive, code-confirmed) and 2.5.16 (no PS4 counterpart, I); list them in
the README notes with their report sections. Shared types per § 22: mail attachment classes (their
own, not the item types), the Season 3 stamp types, the `CDataCharacterInfo` addition (the {u8, u16}
list reader the pawn info uses: reuse that type from `include/Pawn.hexpat` or move it to a shared
include) and the trailing u8 of `CDataCharacterListElement`; no include cycles, no duplicate type names.
Existing patterns that use `CDataCharacterListElement` or `CDataCharacterInfo` (search the patterns:
e.g. 31.29.2, 31.4.2, 18.0.2, 8.37.16, the login character list) must follow the Season 3 layout:
check each against the report, fix and re-export what differs, list each before/after with fit counts
(a type change that leaves output identical needs only the byte-identical check).

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`): per-id fit counts (the
report: 1,342/1,342 fit across the three groups, minus the out-of-scope ids), no `.json.err`; spot-check 2 files per id against the
report's samples (end offset, a few values). README table, notes, open items (§ 8).
Owns: the new patterns, the include additions and new includes, changed patterns as above, the
packets README, the JSON of these ids. Never touch raws, client/, other specs,
`packets/imhex-export.sh`; `tasks.md` is the coordinator's. Commit with `git commit -m <msg> -- <paths>`;
long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values, e.g. a mail with its attachments, a stamp bonus, a character info). Stop: budget 120 min of work time;
finish the scope. If your context passes 300k tokens, commit what is done and end `cut short:` with
the next id.
Base: the head when you start.
