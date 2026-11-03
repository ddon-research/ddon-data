007 T003: private copy of ddon-hook's accepted PC database

Objective (PC 03040008): `research/ida/private-copy.sh` gains a third target, `pc-accepted`: the
database `accepted_PC.path` of `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/CURRENT-RECOVERY.json`
(today `.../feature008-field-map-property-working-20261029T161123Z/2022_01_29_DDO_DUMP_FIX.exe.i64`).
- Read the path and `accepted_PC.sha256` with `jq`; refuse (exit 2, nothing copied) if the file's
  sha256 differs from the recorded one, or the path is outside `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/`.
- The copy goes to `PC_DDON_03040008/ddon-data-<name>/2022_01_29_DDO_DUMP_FIX.exe.i64` (the folder the
  `guard_ida` hook already allows: `tools/hooks/guard_ida.py` COPY), not inside the feature008 folder.
  Keep every existing rule (open-copy check, link refusal, hash of the copy).
- Usage text and header comment updated. `pc` and `ps4` behave exactly as before.
- Test: a bash test (`research/ida/tests/private-copy.sh` or the repo's existing test location for
  shell; look how `tests/imhex-export-select.sh` is wired into `tools/check.sh`) covering: bad target,
  bad name, sha mismatch refused (use a temp fake `CURRENT-RECOVERY.json` via an env override such as
  `DDON_RECOVERY_JSON`, documented as test-only), and a successful copy of a small fake database in a
  temp dir if the script can be pointed there without weakening the real path check; otherwise say why.
Owns: `research/ida/private-copy.sh`, its new test, the `tools/check.sh` line that runs it. Never touch the
databases (no real copy in the test), ddon-hook, client/, packets/, other specs.
Libraries: bash, jq, sha256sum.
Done: `bash tools/check.sh --since <base>` green; signed commit with `git commit -m <msg> -- <paths>`;
receipt. Stop: budget 30 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
