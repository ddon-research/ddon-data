007 T005h: fix PS4 object-access parsing, re-extract PS4, matcher rule 4 on the v4 dumps

Objective (PC 03040008 <-> PS4 02020005): T005g (`research/T005g-extract-v4.md`) found that `extract_ida.py`
v4 drops almost all PS4 object accesses: the PS4 database names argument registers (`[this+cArcLoaderBase.mNum]`)
and `parse_mem_text` finds no base register in that text (722 records instead of about 30,587; 0 slot stores
instead of about 2,685; PC unaffected). Then finish T005e's rule 4.

1. Extractor: take base, index, scale and displacement from the decoded operand (`ida_ua` `op_t`:
   `o_displ`/`o_phrase`, `x86` SIB via `ida_ua`/`idaapi` helpers such as `x86_base_reg`/`x86_index_reg`/
   `x86_scale` if available in IDA 9.5; check with `ida_ua`/`idaapi` dir, cite what you used), not from the
   operand text; register names then cannot matter. If no such helper exists, map register-variable names
   back with `ida_frame.find_regvar` before parsing (T005g's what-if). Tests: a renamed-register operand, a
   structure-offset operand (`[rdi+Class.member]`), PC unchanged (same records on a fixture).
2. Re-extract PS4 by a read-only batch run on a private copy (`bash research/ida/private-copy.sh ps4 t005h`;
   `idat -A -S"extract_ida.py ..."`, see the README; delete the copy after). Expect about 30k access
   records and about 2.7k slot stores; update `dumps/MANIFEST.tsv` (`manifest.py`). The PC dump stays.
3. Matcher (`matcher/`): rule 4 (T005e brief § 4) on the v4 records: PC slot = `const_stack` slot 0 of the
   `callOnPacketFunc` `0x878860` call in the RES handler and the `reserveNetworkErrorDialog` (`0xBB39D0`) argument
   in the requester; PS4 slot = the `mErrorCode`/`mStatus` store index via `mpManager` in the handler and the
   `reserveNetworkErrorDialog` argument in the requester; the sender by its `WritePacket` constant key
   (PC) / single `Send_C2S_*` call (PS4). Keep every T005e refusal and gate. And: the PC codec walk skips
   callees with null `codec_distance` instead of counting them as coverage gaps.
4. Rerun `match.py` (twice, identical), the precision holdout and the negative control; report counts per
   rule against T005e (rules 1-3 should not lose pairs; explain any change).

Owns: `research/03040008/ida-transfer/{extract_ida.py,matcher/**,match.py,tests/**,README.md,manifest/**}`,
`dumps/ps4-ida.jsonl`, `dumps/MANIFEST.tsv`, `dumps/logs/*`. Never touch the PC dump, the work copy, the
original or accepted databases, ddon-hook, client/, packets/.
Libraries: IDAPython (`ida_ua`, `ida_frame`), stdlib, pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; counts and the precision/control
tables in the receipt; signed commits with `git commit -m <msg> -- <paths>`. Stop: budget 150 min of work time;
stop and ask if the control accepts any pair after one tightening.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
