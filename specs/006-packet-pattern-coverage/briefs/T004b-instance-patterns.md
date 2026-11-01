006 T004 (patterns): group 13 INSTANCE

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T004-instance.md`
(read it whole; per-id field tables, § 19 summary, § 20 shared types, § 22 open items) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with `// packet-id:` lines, following
`research/03040008/packets/README.md` and the T002b/T003b patterns (RES header `s32 Error` then
`s32 Result` + body only when Error == 0; NTCs per the report; V/I marks in comments; `unk_*`
placeholders; Season 3 fields named only where code names them, otherwise `unk_*` with the
Arrowgene name in a comment marked "lead").

Scope: the 27 PS4-matched ids (incl. the 6 the report settled: 13.1.16, 13.2.16, 13.20.16,
13.31.16, 13.32.16, 13.42.16). Out of scope (Sam: Season 3-exclusive ids go to a later spec):
13.16.1/2, 13.17.1/2 and 13.23.16; list them with their report section in the README's
"Season 3-exclusive, not patterned" note. Shared structs: new `include/Instance.hexpat` per § 20,
reusing existing includes (`CDataWalletPoint` …); no include cycles. Existing patterns that the
report's Season 3 widths touch (e.g. a shared 17-byte item element also used by 10.2) change only
where the report shows it; list each before/after.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`, UTF-8 strings): per-id
fit counts (the report: all 5,617 fit), no `.json.err`; spot-check 2 files per id against the
report's walked values. README table and open items (§ 22; the three widths that fit either way
and rest on code alone; the two lists never non-empty in captures).
Owns: the new patterns + include, changed patterns as above, the packets README, the JSON of these
ids. Never touch raws, client/, other specs, `packets/imhex-export.sh`; `tasks.md` is the
coordinator's. Commit with `git commit -m <msg> -- <paths>`; long lists via
`git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with decoded
values). Stop: budget 90 min of work time; finish the scope.
Base: f7efade6c6.
