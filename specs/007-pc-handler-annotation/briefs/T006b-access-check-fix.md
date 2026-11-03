007 T006b: the type access check accepted a contradicted layout; fix it and requalify every type

Objective (PC 03040008 <- PS4 02020005): T007b run 3 (`research/T007b-apply-run.md` § Run 3, spot checks)
found that the transferred layout of `nUserSession::CPacket_S2C_CHANGE_JOB_RES` does not fit the PC reader
`0x80cf80`: on PC the job data starts at +0x18 (transferred +0xc), every array starts 0xc later, the received
flag is at +0xEC (transferred +0x114). T006 accepted the type with "no contradiction": an access landing
inside a member (not at its start) passed. A type layout stated as fact that the PC code contradicts is the
false positive spec 007 exists to prevent.

1. Find and state the exact cause in `transfer/` (which recursion or member kind let these accesses pass:
   arrays, embedded structs, `MtTypedArray`, indexed accesses, a width rule), with the access records of
   `0x80cf80` that should have refused it.
2. Fix the rule: an access must land on the start of a leaf member (recursing through embedded structs,
   arrays of structs at element boundaries, arrays of scalars at element starts) with exactly the leaf's
   width, or the vptr; an indexed access must have its scale equal to the element size and its displacement
   on an element start of an array member; anything else, including padding and gaps, contradicts. Keep
   "at least one checked access" and add the coverage (checked member bytes / size) per type to `types.tsv`.
3. Regression tests: CHANGE_JOB_RES from the real access records (a fixture cut from the dumps), an access
   at +2 into a 4-byte member, an access into padding, an indexed access with the wrong scale, an access at an
   array element start (accepted).
4. Re-run `transfer.py`; report which types change status (old accepted -> refused, with the first
   contradicting access each) and the knock-on changes to `prototypes.tsv` and `comments.tsv`. Deterministic.
5. Independent check: for 5 still-accepted packet or element types, list each access record that supports
   them; the coordinator will have them re-derived by a reviewer.

Owns: `research/03040008/ida-transfer/{transfer/**,transfer.py,tests/**,manifest/transfer/**,README.md}`. Never
touch the apply script, dumps, databases, ddon-hook, client/, packets/.
Libraries: stdlib, pytest, ruff.
Done: the cause stated; tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; the status changes in
the receipt; signed commits with `git commit -m <msg> -- <paths>`. Stop: budget 90 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
