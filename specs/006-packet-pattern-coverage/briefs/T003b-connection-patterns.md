006 T003 (patterns): groups 0 CONNECTION, 1 SERVER, 44 CERT

Objective (build 03040008): implement `specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md`
(read it whole; § 2-16 field tables, § 18 shared types, § 20 open items) as one
`research/03040008/packets/<RAW_NAME>-pattern.cpp` per uncovered id with `// packet-id:` lines,
following `research/03040008/packets/README.md` and the login patterns of T002b (RES header
`s32 Error` then `s32 Result` + body only when Error == 0; NTCs per the report; V/I marks in
comments; `unk_*` placeholders). Shared structs go to a new `include/Server.hexpat` (or the include
§ 18 proposes); reuse `include/Login.hexpat`, `Cert.hexpat`, `Context.hexpat`; no include cycles.

- Ids the login server reuses (0.0.x, 0.1.x, 0.2.x, 1.0.x) need `// packet-select:` (see
  `packets/imhex-export.sh` usage and `tests/imhex-export-select.sh`).
- 44.0.1 C2S_CERT_CLIENT_CHALLENGE_REQ: header-less 324-byte body like
  `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp` (the 304-byte files are now 44.1.16, done in T002e).
  44.0.2 and the rest per the report.
- 0.10.16: the raw name stays `S2C_CONNECTION_0_10_16_NTC` (file names are the CLI's); name the
  pattern after the raw name and put the code-backed name `SESSION_STATUS_NTC` (V, § 9) in its
  header comment and the README.
- Existing patterns for these groups (if any, e.g. `C2S_CONNECTION_LOGIN_REQ`) change only where the
  report shows a layout error; list each such change with before/after JSON.
- `packets/imhex-export.sh` usage lines 11-12 still give 1.0.1 as the `packet-size` example (no
  longer true since T002e): make it a generic example.

Export each new pattern with plbatch (`packets/imhex-export.sh @ <name>`; plbatch pinned to
PatternLanguage 300d7388, UTF-8 strings): per-id fit counts, no `.json.err`; spot-check 2 files per
id against the report's walked values. README pattern table and open items (§ 20).
Owns: the new and changed patterns + includes, the packets README, `packets/imhex-export.sh` usage
text, the JSON of these ids. Never touch raws, client/, other specs; `tasks.md` is the coordinator's.
Commit with `git commit -m <msg> -- <paths>`; long lists via `git update-index --add --remove -z --stdin`.
Libraries: ImHex std, plbatch, stdlib Python/jq for spot checks.
Done: signed commits; per-id fit counts; `bash tools/check.sh --since <base>`; receipt from
`receipt.py --print` with "For Sam's inspection" (per id: file count, one example with a few decoded
values, e.g. the login announcement text, the game setting tail, the weather forecast).
Stop: budget 90 min of work time; finish the scope.
Base: 70201832e1.
