007 T007c: treat IDA's vptr/base member conventions as equal; emit them

Objective (PC 03040008): T007b's dry run (`research/T007b-apply-run.md`) refused 105 of 189 type rows:
`MtObject`, `CPacketDataBase` and `MtArray` already exist in the work copy with the same size, member
offsets and sizes, and differ only in member names (`_vptr$MtObject` vs `__vftable`, an unnamed base vs
`baseclass_0`); 102 structs and 99 prototypes that use them were refused in turn.

Fix in `apply_transfer.py` (and in `transfer/` if the names are produced there):
- Write types the way IDA represents them: the vptr member named `__vftable` (pointer to an opaque
  `<Class>_vtbl`, or `void *` if no vtable type is transferred), base classes as udt base-class members
  (`udm_t` with the base-class flag, IDA names them `baseclass_<off>`), so a type IDA created and a type we
  create compare equal.
- Equality for an existing local type: same size and the same members by (offset, size), names equal except
  that a vptr member at 0 (`__vftable` / `_vptr$*` / `vfptr`) and base-class members (`baseclass_*` / unnamed
  base / the base class name) are equal to each other when their sizes match and, for a base, its type name
  matches. Anything else differing still refuses.
- Tests: the three T007b cases (each now `already`), a vptr name difference with a size difference (refused),
  a base of another type at the same offset (refused), and the knock-on structs no longer refused in a
  fixture.
Then the dry run on the work copy is T007b's rerun (coordinator).

Owns: `research/03040008/ida-transfer/{apply_transfer.py,transfer/**,tests/**,README.md,manifest/transfer/**}`
(regenerate `manifest/transfer/` if `transfer/` changes, deterministic). Never touch the dumps, the
databases, ddon-hook, client/, packets/.
Libraries: IDAPython (`ida_typeinf` udt), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 60 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
