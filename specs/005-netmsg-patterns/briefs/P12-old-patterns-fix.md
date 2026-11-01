005 P12 (T022): fix, complete and refactor the 36 old packet patterns, two batches

Objective (build 03040008): apply `research/P11a-old-patterns.md` (batch A) or
`research/P11b-old-patterns.md` (batch B) to the patterns in `research/03040008/packets/`, the way
spec 005's newer patterns are built (`include/Packet.hexpat`, `include/nNetMsg.hexpat`,
`include/Context.hexpat`, P9/P10): read the report and two of the newer patterns first.

Do, per batch (commit per group):
1. Shared includes (batch A creates them, batch B extends them): the RES header as the PC reads it
   (`s32 Error`; Result and the body only when Error == 0; both reports' G1) in `Packet.hexpat`; the
   CData structures of the reports' shared-structure tables in topic includes (e.g.
   `include/Quest.hexpat`, `include/Area.hexpat`, `include/Clan.hexpat`, `include/Character.hexpat`),
   each with a comment naming the PC reader VA, the PS4 match and V/I marks.
2. Each pattern: fix every error the report lists, complete partial/stub patterns as far as the
   report reaches (unnamed Season 3 fields stay `unk_*` with a comment), enums from PS4 DWARF only
   (values not in DWARF: `UNK_<value>` or a comment "not in PS4 DWARF, server lead"), drop invented
   fields (e.g. 19.2.2's s16 Result branch, L2C_LOGIN_RES's 14-byte pad), header comment with the
   evidence (report section, VAs), `// packet-id: g.id.sub`, exported `sourceOk`, `paddingSize`
   and `fits` as P10 defined them.
3. Rename each pattern file to the raw name it selects (reports' item 7; use `git mv`), keep
   history; update any reference to the old names in this repo (rg).
4. Re-export the batch's types with `packets/imhex-export.sh @...` (plbatch); counts per type
   (exported, failed, fit, nonfinite). A captured type fitting under 95% stops the batch: report it.
5. Verify by prediction + stratified sample (fixed seed, about 20 per type; key-set or jq
   comparison), never per-file diffs. Receipt section **"For Sam's inspection"**: per type each JSON
   change (field added/removed/retyped/renamed, enum names, error-case handling), why (report
   item), sampled count, one example file with before/after values. Sam expects these changes and
   wants to inspect them.

Owns: `research/03040008/packets/**` (the batch's patterns and the includes), `packets/decrypted_json/**`
for the batch's types, `packets/README-decrypt-annotate-streams.adoc` pattern list. Never touch:
`packets/decrypted_raw/`, client/, other research, other work's uncommitted files (commit only with
`-- <paths>`; large path lists via `git update-index --add --remove -z --stdin`).
Libraries: ImHex std includes, plbatch; no new tooling.
Done: signed commits; counts; sample verification; `bash tools/check.sh --since <base>`; receipt
(from git if `receipt.py --print` fails). Stop: budget 100 min of work time per batch; past 300k
tokens of context commit and hand off with `cut short:`.
Base: 3726f6fe94.
