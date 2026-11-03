007 T007e: roll the work copy back and re-apply the corrected wave-1 transfer (batch runs, writes)

Objective (PC 03040008): T007b run 3 applied a type later found contradicted (`CHANGE_JOB_RES`); T006b/T006c
(`tasks.md`) fixed the access check and regenerated `manifest/transfer/`. Restore the clean point and apply
the corrected rows, exactly as T007b's brief (`briefs/T007b-apply-run.md`) steps 2-7, with these changes:

1. Rollback: the work copy is now sha256 `f17d0745...7829` (after run 3); the rollback copy
   `ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64` must be `65120b34...8b9111`. Keep the run-3
   database as `...exe.run3-T007b.i64` (`mv`), then `cp` the rollback copy to the work copy name and check
   its sha256 is `65120b34...`. Rename the run-3 dumps/logs `*.run3.*`.
2. Steps 2-7 of T007b (dry run, apply, second apply, verify with `--apply-log`, re-extract and compare both
   ways, spot checks). Stop conditions as there; on any `failed` restore the rollback copy and stop.
3. Extra spot checks: `0x80cf80` and the CHANGE_JOB_RES handler now show no transferred struct layout (the
   argument is an opaque pointer); one `MtTypedArray<...>` member access in a reader decompiles to its member
   name; the 6 lea-only types are absent from the local types.
4. When all checks pass, delete the run-3 database copy (`...run3-T007b.i64`); keep the rollback copy.

Owns: the dumps and logs, `dumps/MANIFEST.tsv`, the database files named above, and the report
`specs/007-pc-handler-annotation/research/T007e-reapply.md`. Never touch scripts, the manifest, the original
or accepted databases, ddon-hook, client/, packets/; never open the work copy in ida-mcp.
Libraries: idat batch, jq. Done: the report; final message with the path and at most 15 lines.
Stop: budget 75 min of work time. Base: the head when you start.
