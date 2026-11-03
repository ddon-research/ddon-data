007 T007f: an untransferred base compares equal to the database's base of the same class

Objective (PC 03040008): T007e's dry run (`research/T007e-reapply.md`) refused 91 of 181 type rows and 92
prototypes because of one refusal: `MtArray`. Since T006b, `MtObject` is not transferred, so `types.h` renders
`MtArray`'s base as `unsigned __int8 baseclass_0[4]` with the comment `base MtObject (not transferred)`; the
database's existing `MtArray` has a real `MtObject` base of the same offset and size, and `member_equal`
(`apply_transfer.py` ~179-182) requires the base types to match.

Fix in `apply_transfer.py`: a row member that is an untransferred base (byte array, base-class flag or
`baseclass_*` name, comment `base X (not transferred)` or the equivalent field T006 writes; read how T006 marks it)
equals an existing base-class member at the same offset and size whose type name is `X`. A different class name,
offset or size still refuses; nothing else in the comparison changes. When planning, such a type stays
`already` (the database's richer base is kept, never overwritten by the blob). Tests: the T007e case (`already`,
dependents planned), a base of class `Y` refused, a size mismatch refused. Note also T007e's point 4 in the
README: lea-only and refused types are written as forward declarations without members.

Owns: `research/03040008/ida-transfer/{apply_transfer.py,tests/**,README.md}`. Never touch `transfer/`, the
manifest, dumps, databases, ddon-hook, client/, packets/.
Libraries: IDAPython `ida_typeinf`, pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commit with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 30 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
