007 W2 T013d: apply wave 2 (partial layouts, locals) to the work copy and verify (batch runs, writes)

Objective (PC 03040008): apply `research/03040008/ida-transfer/manifest/transfer/wave2/` (T013c, c2bbfd18a7: 48
partial packet types, 24 locals; see the README for the wave-2 apply arguments)
to `ddon-data-007work` by headless batch only (README), exactly as `briefs/T009c-apply-corrections.md` steps 1-5,
with:
1. Start sha256 `f7f3a219...3c25`; rollback copy `...exe.before-W2.i64` (`cp`, compare); then delete
   `.before-T009c.i64`.
2. Dry run: expected writes are only the new types (definitions of formerly forward-declared classes), the
   locals rows, and comment rows for them; anything else, any refusal or `current-changed` is a stop.
3. Apply, second apply (all `already`), verify against the new apply log (all ok, counts, every typed function
   decompiles). On any `failed`: restore the rollback copy, stop, report.
4. Spot checks (read-only batch, pseudocode in the report): 3 handlers with a renamed and retyped `packet` local
   (members by name in the pseudocode), 2 readers whose object argument now has a partial type,
   `0x80cf80` (CHANGE_JOB_RES: partial or still opaque, as the manifest says), 2 R1/R2 locals.
5. Publish: when all checks pass, copy the work copy to
   `PC_DDON_03040008/spec007-packet-handlers-<date>-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` (sha256 equal).
Owns: the dumps, logs, `dumps/MANIFEST.tsv`, the rollback/published database files named above, the report
`specs/007-pc-handler-annotation/research/W2-T013d-apply.md`. Never touch scripts, manifest, the original or
accepted databases, the wave-1 snapshot folder, ddon-hook, client/, packets/; never open the work copy in ida-mcp.
Libraries: idat batch, jq. Done: the report; final message with the path and at most 15 lines.
Stop: budget 75 min of work time. Base: the head when you start.
