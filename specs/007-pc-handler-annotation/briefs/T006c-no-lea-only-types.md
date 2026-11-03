007 T006c: a type needs a width access; lea-only types stay unwritten

Objective (PC 03040008): after T006b (e49ae1b341) 96 types are accepted: 90 `MtTypedArray<X>` instantiations
(13/20 bytes checked by width accesses) and 6 `CData*` element types (`CDataClanSearchResult`,
`CDataGPShopLineupElementBase`, `CDataGameTimeBaseInfo`, `CDataMailInfo`, `CDataOrbGainExtendParam`,
`CDataWorldInfo`) whose only evidence is `lea` records (coverage 0%). `lea` coincidences are what let
`CHANGE_JOB_RES` through. Decision (coordinator): `lea` records may contradict a type but never accept one;
acceptance needs at least one width-carrying load/store access that lands on a leaf start.

Change `transfer/` accordingly: the 6 become status `unchecked` with reason `lea-only`; their dependants
(prototypes keep an opaque pointer, as for any unwritten type). Add to the README a "later rule" note: a
typed `lea` (the address is passed as the argument of a paired callee whose PS4 parameter type is the member's
type) could accept such types in wave 2. Test: a lea-only fixture type is `unchecked`; a type with one width
access plus leas is accepted; a lea that contradicts still refuses. Re-run `transfer.py` (deterministic) and
report the status changes and the changed rows of `prototypes.tsv`/`comments.tsv`/`types.h`.

Owns: `research/03040008/ida-transfer/{transfer/**,transfer.py,tests/**,manifest/transfer/**,README.md}`. Never
touch the apply script, dumps, databases, ddon-hook, client/, packets/.
Libraries: stdlib, pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commit with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 30 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
