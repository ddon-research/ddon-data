007 T007: the apply script (headless batch, idempotent, undo log, verify mode)

Objective (PC 03040008): `research/03040008/ida-transfer/apply_transfer.py`, an IDAPython batch script that
writes T006's rows (`manifest/transfer/{names,prototypes,types,comments}.tsv`, `types.h`) to the work copy
`ddon-data-007work` and checks them back (spec 007 § Method step 4). Read the spec § 4-5, the README (write
path: batch only, `idat -A -S"<script> <args>"`, ends with `qexit(0)`; on error `DBFL_KILL`), T006's README
section and `manifest/transfer/` headers.

T006 (95bd50d7b4) notes: template type names (`MtTypedArray<CDataX>`, 84 of the 106 structs) stay verbatim,
so declare them through the `ida_typeinf` tinfo/udt API rather than the C parser where the parser rejects
them; names use the PS4 IDA form (`nPacket::Read_CDataX_`). Rows with status `conflict` (7 names, 54
prototypes) are never written by this script; they are only reported.

Behaviour:
- Args: `<manifest/transfer dir> <OUT jsonl> [--apply] [--verify]`; default is a dry run (computes every
  action and its before-state, writes nothing, exits with `DBFL_KILL` so the copy is untouched; unlike
  `repair_functions.py`'s dry run, which re-saved the copy).
- Precheck: the database input sha256 is the PC exe's (`f1c974d0...fa20`), the idb path is under
  `ddon-data-007work`; the manifest files' sha256 are recorded in the header.
- Order: types (`ida_typeinf` parse of `types.h` into the local type library; an existing local type of the
  same name: equal -> skip; different -> refuse unless its T006 row says `replace` with the reason), then
  `remove-label` rows, names (`ida_name.set_name`; refuse if the name is used at another address), prototypes
  (`apply_tinfo` with `TINFO_DEFINITE`, from the parsed declaration; refuse if parsing fails), comments
  (function comments; append below a separator, never replace).
- Every write: before-state into the undo record first (flushed), then the write, then a read-back
  (name, printed type, comment) compared with the row; mismatch -> `failed` with both values, no retry.
- Idempotent: a second `--apply` run finds everything `already` and changes nothing.
- `--verify` (read-only, `DBFL_KILL` at the end): for every row, the database state equals the row; counts of
  non-default names, typed functions and local types before vs after (from the undo log header) so that
  nothing outside the rows changed; decompile every function that got a prototype and report failures.
- An `--undo <apply jsonl>` mode that restores the before-state from an apply log (tested with fakes; it is
  the recovery path, not run in this package).
Tests with fakes for each step, including: a name already used elsewhere, an existing different local type,
an existing comment kept, a failed read-back, a second apply being a no-op, undo restoring the before-state.

Owns: `research/03040008/ida-transfer/{apply_transfer.py,tests/**,README.md}`. Never touch the manifest,
the matcher, the extractors, the dumps, the databases (the run is T007b), ddon-hook, client/, packets/.
Libraries: IDAPython (`ida_typeinf`, `ida_name`, `ida_funcs`, `ida_hexrays`, `ida_loader`, `idc`), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 120 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
