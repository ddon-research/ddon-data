007 T009c: apply the conflict corrections to the work copy and verify everything (batch runs, writes)

Objective (PC 03040008): T009b turned the 61 settled conflicts into `correct`/`replace` rows (plus their comment
rows). Apply the current manifest to `ddon-data-007work` by headless batch only (README; never ida-mcp). Expected
writes: the correction rows and their comments; everything else `already`. This apply log is also the new base
for `--verify` (the T007e log no longer matches the manifest hash).

1. Check the work copy's sha256 is `be0cc624...162f`; `cp` it to
   `ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T009c.i64` (compare sha256). The older rollback copy
   `.before-T007b.i64` may then be deleted.
2. Dry run -> `dumps/apply-dryrun-t009c.jsonl`: only `correct`/`replace` names/prototypes and their comments would
   be written; any other would-write, refusal or `current-changed` is a stop (report it).
3. Apply -> `dumps/apply-t009c.jsonl`; second apply -> `dumps/apply-t009c-2.jsonl` (all `already`); verify with
   `--apply-log dumps/apply-t009c.jsonl` -> `dumps/apply-verify-t009c.jsonl` (all ok, counts, every typed function
   decompiles). On any `failed`: restore `.before-T009c.i64`, stop, report.
4. Spot checks (read-only batch in your scratchpad, pseudocode in the report): `0x7DA410`, `0x833670`,
   `0x8320B0`, `0x87B140`, `0x7D3880`, one of the 50 handlers (argument names `this`/`pPacket`, earlier comment
   kept above the separator).
5. `manifest.py` for `dumps/MANIFEST.tsv`; sha256 of the work copy at each step.

Owns: those dumps and logs, `dumps/MANIFEST.tsv`, the rollback copies named above, the report
`specs/007-pc-handler-annotation/research/T009c-apply.md`. Never touch scripts, manifest, the original or
accepted databases, ddon-hook, client/, packets/.
Libraries: idat batch, jq. Done: the report; final message with the path and at most 15 lines.
Stop: budget 60 min of work time. Base: the head when you start.
