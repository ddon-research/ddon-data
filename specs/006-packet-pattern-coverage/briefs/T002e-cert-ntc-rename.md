006 T002e: file the server's first packet under its code-backed id and name

Objective (Sam, 2026-11-01: "rename them"): the 125 304-byte first-packet raws the CLI files as
`*_C2L_CLIENT_CHALLENGE_REQ_*.1_0_1` (42 login) and `*_C2S_CERT_CLIENT_CHALLENGE_REQ_*.44_0_1`
(83 game) are the server's certificate notice. `specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md`
§ 15 and its "Consequences" paragraph (read both) show the PC receive path `0x9d6d20` gives this
packet the synthetic header 44.1.16 (game) / 1.1.16 (login): `S2C_CERT_GAME_SERVER_CERT_NTC`
(Arrowgene `PacketId.cs:1737`; PS4 `S2C_GAME_SERVER_CERT_NOTICE`) and `L2C_LOGIN_SERVER_CERT_NTC`.

1. In the patched CLI (`packets/README-decrypt-annotate-streams.adoc` § arrowgene-patches; T002d's
   entry is the model), label the server's first packet with those ids and names (look them up in
   `PacketId.cs`; if the login one is missing there, add it to the CLI's local patch and say so).
   The file stays header-less, as today. Add the entry to the README; rebuild; record the DLL SHA-256.
2. Export all streams to a scratch `OUT_DIR`; compare with `packets/decrypted_raw/` by content hash:
   the 125 files must reappear byte-identical under the new names (`.1_1_16`, `.44_1_16`), nothing
   else may change. Then replace them in `packets/decrypted_raw/` (git sees renames); re-annotate the
   affected streams as T002d did and list the touched files.
3. Patterns (`research/03040008/packets/`): `L2C_LOGIN_SERVER_CERT_NTC-pattern.cpp` and
   `S2C_CERT_GAME_SERVER_CERT_NTC-pattern.cpp` from T003 § 15 (u8[256] modulus, u8[16] exponent,
   u32[5] hash = 292 bytes, no header, the rest cipher padding), shared struct in an include; export
   with plbatch: n/n fit. The `// packet-size: 336` selector on `C2L_CLIENT_CHALLENGE_REQ` is no
   longer needed: drop it only if its export output stays identical, and keep the selector feature
   and its tests. Update the README pattern table and open items.

Order: this runs after 006 T001d (UTF-8 JSON) has landed; build plbatch from the pin T001d set.
Owns: the CLI local patch + README entry, the 125 raws (rename), affected annotated files, the two
new patterns + include, `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp`, the packets README, the new JSON.
Never touch other raws, client/, other specs; `tasks.md` is the coordinator's. Commit with
`git commit -m <msg> -- <paths>`.
Libraries: the existing CLI, scripts, plbatch; stdlib Python (hashlib) for the comparison.
Done: signed commits; comparison counts (identical / renamed / other); fit counts;
`bash tools/check.sh --since <base>`; receipt from `receipt.py --print` with "For Sam's inspection"
(old → new name of one login and one game file; decoded exponent and hash of one).
Stop: budget 90 min of work time; finish the scope.
Base: the head when you start.
