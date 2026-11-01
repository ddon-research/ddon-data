006 T002 (patterns): login group patterns for all 21 uncovered ids

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T002-login.md`
(read it whole: per-id field tables, the PC RES header `s32 Error` then `s32 Result` + body only when
Error == 0, the NTC rule and the 2.3.16 exception, Season 3 differences, the include plan in its
"shared types" section) as one `research/03040008/packets/<RAW_NAME>-pattern.cpp` per id with
`// packet-id:` lines, following the conventions of the existing patterns and
`research/03040008/packets/README.md` (root `packet`, lowercase header keys, `count`/`entries`,
`length`/`value`, inline RES form, `unk_*` placeholders, V/I marks in comments from the report).
Shared types go to the includes the report proposes (`include/Login.hexpat`, `include/GP.hexpat`,
the character-list types reusing `include/Context.hexpat`); avoid include cycles; move types the
existing `C2L_LOGIN_REQ` / `L2C_LOGIN_RES` patterns define inline into the includes only if both
uses match. Header-only REQs get patterns too (header plus nothing).

1.0.1 C2L_CLIENT_CHALLENGE_REQ: write its pattern from the report (V by code), but its 84 raws are
still ciphertext: do not export it (an export of ciphertext would publish garbage JSON); mark it in
the pattern and README as "raws not decrypted, unvalidated" and leave a `// packet-select:` or other
means so `imhex-export.sh` skips it until the raws are fixed. Say in the receipt how you did that.

Export the other 20 ids with plbatch (`packets/imhex-export.sh @ <name>`): every capture fits (per-id
counts, no `.json.err`), and spot-check 2 files per id against the report's walked values. Update the
README pattern table and open items (1.0.1, the error branch untested because no captured RES has
Error != 0).
Owns: the new patterns and includes, the README, the new `packets/decrypted_json/**` files of those
20 ids; edits to existing patterns only to reuse a moved type (unchanged output: re-export and show
the JSON is identical). Never touch raws, client/, other specs; `tasks.md` is the coordinator's.
Commit with `git commit -m <msg> -- <paths>`; stage long lists with
`git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python for the spot checks.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since d7f0cebbf2`; receipt from
`receipt.py --print` with "For Sam's inspection" (new JSON per id: file count, one example file with
a few decoded values such as the error message list text, the character list names). Stop: budget
90 min of work time; finish the scope.
Base: d7f0cebbf2.
