006 T002d: re-decrypt the first packet of each direction with the fixed key

Objective: implement the fix in `specs/006-packet-pattern-coverage/research/T002c-challenge-decrypt.md`
§ the fix (read the whole report). The locally patched Arrowgene CLI (`packets/README-decrypt-annotate-streams.adoc`
§ arrowgene-patches says where its source lives and how it is built) decodes the first packet of each
direction with the session key; it must use the fixed Camellia-256-CBC key/IV the report cites for
that first packet, then switch to the session key. Keep file names unchanged in this package (no
invented packet names; Sam decides the naming separately).

1. Patch `PacketCommand.cs` (the report's lines) in the patched-CLI source, as a new entry of the
   README's arrowgene-patches list (what, why, the T002c report); rebuild the CLI the way the README
   says; record the binary's SHA-256.
2. Export to a scratch `OUT_DIR` (the script refuses existing folders), all streams the toolchain
   normally processes. Compare scratch vs `packets/decrypted_raw/` by name: exactly the 84 login
   (`.1_0_1`) and 166 game (`.44_0_1`) files differ, names and sizes unchanged, every other file is
   byte-identical (hash compare, not diff). Any other difference: stop and report.
3. Copy those 250 files into `packets/decrypted_raw/`. Check: the 42 336-byte login files decode with
   `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp` on a scratch plbatch run (the 324-byte body has no header:
   adapt the pattern per the report, which says the wire body starts at byte 0, and say how), and
   the 304-byte files show the server key layout (exponent 0x11, SHA-1 matches) by a stdlib check.
   Do the same for the 44.0.1 pair if a pattern exists; otherwise only the stdlib check.
4. Re-annotate only the affected streams if `packets/decrypted_annotated/` holds them
   (`packets/decrypt-annotate-streams.sh`, its README); list the touched files.
5. Restore the 1.0.1 pattern's `// packet-id:` with a selector that picks only the client's
   336-byte files (not the 304-byte server key files sharing the name), export its JSON, and update
   README open items. The 304-byte files get no JSON in this package.

Owns: the patched-CLI source change and its README entry, the 250 raws, the affected annotated
files, `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp` (+ a 44.0.1 pattern only if one exists), the README,
the new JSON. Never touch other raws, client/, other specs; `tasks.md` is the coordinator's. Stage
with explicit paths or `git update-index --add --remove -z --stdin`; commit with
`git commit -m <msg> -- <paths>`.
Libraries: the existing CLI, scripts and plbatch; stdlib Python (hashlib) for the checks.
Done: signed commits; the scratch-vs-repo comparison counts (identical / differing / missing);
fit counts; `bash tools/check.sh --since <base>`; receipt from `receipt.py --print` with "For Sam's
inspection" (one login and one game file: first 16 bytes before/after; decoded fields of one
challenge). Stop: budget 90 min of work time; finish the scope.
Base: 707ef3594c.
