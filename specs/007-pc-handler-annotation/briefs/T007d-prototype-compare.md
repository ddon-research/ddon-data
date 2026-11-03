007 T007d: compare prototypes as types, not printed text

Objective (PC 03040008): T007b's rerun (`research/T007b-apply-run.md` § Rerun) wrote every row, but 171
prototype read-backs were reported `failed`: exactly the rows whose types contain `::` or `<...>`; IDA prints
them with a `struct ` prefix the row text lacks, and `apply_transfer.py` compares whitespace-collapsed text
(read-back at line ~550, the `already` check at ~518, `--verify` at ~678). The writes themselves were right
(4 checked and decompiled). The copy was restored.

Fix: compare a prototype by parsing the row into a `tinfo_t` (the same parse used for writing, incl. the
template/`::` patch) and comparing it with the function's `tinfo_t` (`tinfo_t.compare_with` with flags that
ignore only naming of the function itself, or an equivalent structural comparison: calling convention,
return type, argument count, each argument's type identity and name); use it in all three places. Keep the
text in the logs. Tests (fakes): a `struct `-prefixed print equal, a template/`::` argument equal, a different
argument type still unequal, a different argument name unequal, `already` on a second apply.
Check against the IDA 9.5 Python stubs which comparison API exists; cite it.

Owns: `research/03040008/ida-transfer/{apply_transfer.py,tests/**,README.md}`. Never touch the manifest,
dumps, databases, ddon-hook, client/, packets/.
Libraries: IDAPython `ida_typeinf`, pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commit with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 45 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
