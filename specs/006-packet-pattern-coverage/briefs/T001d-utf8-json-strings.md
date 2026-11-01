006 T001d: plain UTF-8 strings in the JSON (PatternLanguage bump) and full re-export

Objective (Sam, 2026-11-01): the JSON strings are percent-encoded (`"Rumi%20Amestris"`,
`"%E9%80%9A%E4%BF%A1…"`; 110,872 files under `packets/decrypted_json/` hold such strings). Cause:
plbatch links PatternLanguage at `fb6ea061` (ImHex 1.38.1), whose
`generators/include/pl/formatters/formatter_json.hpp` `formatString` writes every byte outside
`[A-Za-z0-9-_.~]` as `%XX`. Upstream master replaced it: valid UTF-8 is written as is, with the
standard JSON escapes (`\"`, `\\`, `\n`, `\r`, `\t`, `\u00XX` for control characters) and
`\u00XX` for each byte of invalid UTF-8.

1. `git -C D:/GitHub/WerWolv/PatternLanguage pull --ff-only` (reference clone: read only, never
   build in it); pick the latest master commit and read the changes since `fb6ea061` that can change
   evaluation or output (formatter, string/char patterns, bitfields, `std::mem`, pragmas the
   patterns use). Pin it in `research/imhex/plbatch/build.sh` (`PL_COMMIT`), the `CMakeLists.txt`
   comment and `research/imhex/plbatch/README.md` (why, the formatter change). Rebuild; run
   `research/imhex/plbatch/test.sh` and `research/03040008/packets/tests/imhex-export-select.sh`.
   If the newer library breaks a pattern or the build, fix plbatch or the pattern, or fall back to the
   oldest upstream commit with the UTF-8 formatter, and say which.
2. Invalid UTF-8: `\u00XX` per byte is ambiguous with the real code point U+00XX. Count the strings
   that hit it in the new export (a byte >= 0x80 decoded as `\u0080`-`\u00ff`); if any, name the
   fields and say whether they are binary data typed as `char` (those should become `u8` arrays in
   the pattern, with Sam informed) or real text.
3. Re-export every pattern with `packets/imhex-export.sh --force @ <name>` (all patterns that declare
   `// packet-id:`; background, sharded as usual). Verify by prediction + stratified sample (2 files
   per pattern, never an exhaustive diff): parse old and new JSON; same key paths, same numbers and
   booleans; each old string, percent-decoded as UTF-8, equals the new string. Any other difference:
   stop and report it with the file. Counts: exported, failed, `.json.err`, per pattern fit unchanged.
4. Update the README conventions (strings are UTF-8 JSON strings; no percent encoding) in
   `research/03040008/packets/README.md` and the export README if it mentions the encoding.

Owns: `research/imhex/plbatch/**`, the two READMEs, patterns only where step 1 forces a fix, and
`packets/decrypted_json/**` (full rewrite). Never touch raws, client/, other specs; `tasks.md` is the
coordinator's. Stage the JSON with `git update-index --add --remove -z --stdin` (never
`--pathspec-from-file`); commit with `git commit -m <msg> -- <paths>`.
Libraries: PatternLanguage (upstream), plbatch, stdlib Python (`json`, `urllib.parse.unquote`).
Done: signed commits; the new pin and what changed upstream; test results; export counts; sample
comparison counts; `bash tools/check.sh --since <base>`; receipt from `receipt.py --print` with
"For Sam's inspection" (one Japanese and one ASCII example, before/after).
Stop: budget 120 min of work time; finish the scope.
Base: the head when you start (after 006 T003).
