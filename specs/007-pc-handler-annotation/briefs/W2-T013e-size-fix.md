007 W2 T013e: partial-type sizes cover every access; re-apply wave 2 from the rollback point

Objective (PC 03040008): T015 (`research/W2-T015-adversarial.md`, canary `.agent-ledger/canaries/007-W2/test_lower_bound.py`,
reproduced: 42 of 48) found that `transfer/wave2.py` `_access_check` (~628-631) counts accesses at or past a
lower-bound size as gaps, so 42 packet types are declared too small and Hex-Rays splits the retyped `packet`
locals.

1. Fix: an access (paired-function width access through the object, and a `lea` destination at `disp` as at least
   `disp + 1`) that ends past a lower-bound size extends the size to that end, with the farthest access as
   `size_evidence`; past a proved size it contradicts. Also include the handlers' own accesses to the retyped stack
   object (frame-relative, e.g. the inline constructor's word store at the last u8 member and the member-array
   constructor/destructor calls T015 saw in `0x7e3c10`) where the v6 dump records them relative to the local; say
   if it does not. The canary becomes a test (fails on the old code); a test for a proved size contradicted.
2. `apply_transfer.py --verify`: each retyped local's width equals its type's size (after this fix).
3. Regenerate `manifest/transfer/wave2/` (deterministic) and report the size changes (old -> new, evidence).
4. Re-apply by headless batch: restore the work copy from `ddon-data-007work/...exe.before-W2.i64` (`cp`, sha256
   `f7f3a219...3c25`; keep the current one as `...exe.w2-undersized.i64` until the checks pass), then dry run,
   apply, second apply, verify, the canary against the new state (pass), spot checks of `0x7e3c10`, `0x7fae10`,
   `0x7d73b0`, `0x7e9ef0` (no split lvars past `packet`, no `OVERLAPPED`). Then delete `...w2-undersized.i64` and
   republish: replace `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64` with
   the work copy (compare sha256). Never open the work copy in ida-mcp.
Owns: `research/03040008/ida-transfer/{transfer/**,apply_transfer.py,tests/**,manifest/transfer/wave2/**,README.md}`,
the dumps/logs of the re-apply, `dumps/MANIFEST.tsv`, the work-copy and wave-2 snapshot files named above, the report
`specs/007-pc-handler-annotation/research/W2-T013e-reapply.md`. Never touch the extractor, matcher, wave-1 manifest,
the original or accepted databases, the wave-1 snapshot, ddon-hook, client/, packets/.
Libraries: stdlib, pytest, ruff; idat batch.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; the re-apply checks in the report; signed
commits with `git commit -m <msg> -- <paths>`; receipt. Stop: budget 150 min of work time; on any `failed` in the
re-apply restore the rollback copy and stop.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
