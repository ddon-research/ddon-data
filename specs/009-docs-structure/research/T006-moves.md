# 009 T006: where the sections of `research/03040008/ida-transfer/README.md` went

Base `a65d0d0b934`. Spot check: `python -X utf8 -I specs/009-docs-structure/research/T006-spotcheck.py a65d0d0b934`.

| Old section (lines at base) | Went to | Left out, and why |
| --- | --- | --- |
| Title, intro 1-6 | the short README | |
| Read path and write path 7-30 | `docs/how-to/query-ida-read-only.md` (read path), `docs/how-to/write-to-an-ida-database.md` (write path, killed worker), `docs/reference/ida-transfer-tools.md` (exit logic) | |
| Function repair 31-68 | `docs/reference/ida-transfer-tools.md` § Function repair, `docs/how-to/transfer-annotations-ps4-to-pc.md` step 1 | the `exec` dry-run route: see Cut |
| Version 3 69-102 | reference § What the extractor emits; repair's roots to § Function repair | version labels |
| Version 4 103-145 | reference § `object_accesses`, § Scope, § Records | version labels; run counts: see Cut |
| Version 5 146-162 | reference § `object_accesses` (decoding rules) | the v4 defect story: see Cut |
| Version 6 163-193 | reference § Call sites, kinds of `args` | |
| Matcher 194-222 | reference § Matching rules; reasons to `docs/explanation/ida-transfer-method.md` | |
| Role anchors 223-302 | reference § Role anchors, § Controls, § Matcher output; reasons to the explanation | run counts: see Cut |
| Transfer rules 303-357 | reference § Transfer rules, § Transfer output | run counts: see Cut |
| Layout rules 358-428 | reference § Layout rules, § Access check, § `types.h`; `CHANGE_JOB_RES` and the `lea` rule to the explanation | the addresses of the story: see Cut |
| Wave 2 429-475 | reference § Partial types and locals, § Transfer output; reasons to the explanation | run counts: see Cut |
| Apply script 476-577 | reference § Apply rules, § Libraries and own code; how-to steps 5-9 | smoke and re-apply stories: see Cut |

Counts that stay facts went to `docs/reference/status.md` § Annotated database. The labels of reports (`T005b`, `T006c`) are out of the pages except as paths in code spans.

## Disagreements between the old README or spec and the code

The pages follow the code.

- The old heading said `repair_functions.py` script version 2; the code has `SCRIPT_VERSION = "3"`.
- The old README: "The PC dump stays v4". `dumps/MANIFEST.tsv` holds `pc-ida.jsonl` at script version 6.
- Spec § Method 5 and the old apply section do not say the apply's order; the docstring of `apply_transfer.py` says comments last, and `run_apply` runs `do_comments` then `do_locals`. The page follows `run_apply`.
- The spec's `transfer.py` holdout says "every withheld seed the matcher pairs must come back". `manifest/precision.tsv` has `seeds_recovered` 0 in all 5 runs, and `pairs.tsv` has no `propagation` row: the holdout tests role pairs only. The explanation says so.

## Cut

Tokens the spot check accepts here are history or run details, kept in the sources named.

- `exec(open(path).read(), {"OUT": ".../repair-dryrun.jsonl", "APPLY": False})`: the repair's dry run through ida-mcp. Still in the docstring of `repair_functions.py`; the pages use the batch.
- `T004e`, `T004d`, `T004f`, `T005b`, `T005c`, `T005e`, `T005f`, `T005g`, `T005h`, `T006b`, `T006c`, `T006d`, `T007`, `T007b`, `T007c`, `T007d`, `T007f`, `T008`, `F1`, `F2`, `T009`, `T009b`, `T010`, `T012`, `T013a`, `T013c`, `T013e`, `T002`: report labels; `specs/007-pc-handler-annotation/tasks.md`.
- Version 4 run: `675` sites in the PC dump, `581` caller sites. Version 5 run: PS4 722 records before the fix, 30,587 after, 2,839 functions, 1,772 indexed, 7,345 via a pointer load, 2,685 stores via `mpManager`, and the `sub_4169B0` fixture: `specs/007-pc-handler-annotation/tasks.md` T005h, `research/T005g-extract-v4.md`.
- Role anchors run: 83 reader contexts then 3 as coverage gaps, 20 codec functions, 4 of 22 PS4 codecs known to the classifier, 497 PS4 functions with a slot, 245 candidates, 138 requesters failing gate (c), 33 reserve call sites outside functions; the anchored gap run: 108 1:1 gaps, 5 proposals, four fail (a), `0xbb21a0` <-> `sNetworkExt::cancelReserveNetworkErrorDialog` fails (d) with 5 instructions and 544 PC callers: `specs/007-pc-handler-annotation/research/W2-T012-evidence.md`, `tasks.md`, `manifest/summary.tsv`, `manifest/rejected.tsv`.
- T009 run: 7 names `correct`, 54 prototypes `replace`, 0 conflicts left: `research/T009c-apply.md`.
- Layout story: PC `0x80cf80`'s `lea`s at +0x18, +0x60, +0x74, inner leaves `m_unJobPoint`, `mAutoDelete`, sub-objects at +0xc, +0x54, +0x68: `research/T007b-apply-run.md`, `research/T008-adversarial.md`. The argument stands on the explanation page. `mpArray[i] = p` as vptr writes: the rule stands in the reference.
- Evidence report names: `W2-T012-evidence.md`, `W2-T013b-run.md`, `T010-locals.md`, `T005b-role-anchors.md`, `W2-T013e-reapply.md`.
- Wave 2: "42 of 48 sizes stopped short" and T013e: `research/W2-T013e-reapply.md`; `packet` locals: `in_PawnFeedbackList`, `sendFeedbackList` refused for a user name; smoke `f7f3a219...3c25`, ordinal count 965 -> 970, `apply-*-w2e.jsonl`, `ee07f0b6...8c1d`: `research/W2-T013d-apply.md`, `W2-T013e-reapply.md`; the rest in the reference.
- `f1c974d0...fa20`: the pages give the full hash. `OUT.jsonl`: a placeholder of the old commands, written `<OUT>` or as a named log on the pages.
- `T006 run` pointer to `manifest/transfer/summary.tsv`: Status.
- `0x7EDF80` keeps its row in the reference; `171` read-backs that `failed` on printed text: `tasks.md` T007b.
