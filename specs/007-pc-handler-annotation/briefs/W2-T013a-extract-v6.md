007 W2 T013a: extractor v6 (call argument values) and matcher exports for member links

Objective (PC 03040008, PS4 02020005): the facts wave 2 needs to link packet members and locals by operation
(`specs/007-pc-handler-annotation/research/W2-T012-evidence.md` § Q1-Q3; read it first, esp. "Q2").

1. `extract_ida.py` v6, per call site, the **argument values**: for each argument slot (PC pushes in the call's
   window, ecx; PS4 rdi/rsi/rdx/rcx/r8/r9), the value it provably holds at the call within the block: a
   constant (exists), or `obj+X` where `obj` is a function argument (or a copy) and X comes from `lea reg,[base+X]`,
   `mov reg,base; add reg,X` / `sub`, or the base unchanged (X = 0); or a stack local address
   (`lea reg,[esp/ebp/rsp/rbp+N]` -> frame offset); else nothing. Skip the MSVC padding nop
   (`lea ecx,[ecx+0]`, `lea esi,[esi+0]`, ...) as an operation. Also: in array readers, the allocated element
   (the return of the allocator/`new` call, or the element pointer computed from `[arr+0x10]+i*size`) as a
   base kind `element`, when provable within the block. Tests with fakes incl. near-misses (a register
   overwritten between lea and push, a push of a register loaded from memory, a lea of a non-argument base).
2. Matcher: `callsites.tsv` gains `ps4_site` and `ps4_owner` (rule 3 computes them, T012 § Q2). And the anchored
   gap rule (T012 § Q3): aligned codec call sites count as anchors in `propagate.py`; keep every gate (a)-(d)
   and the control/holdout; report the new pairs (expected about 1-5, e.g.
   `sNetworkExt::cancelReserveNetworkErrorDialog`).
Bump versions; dump format additive. Do not run against a database (T013b runs the extractor).

Owns: `research/03040008/ida-transfer/{extract_ida.py,matcher/**,match.py,tests/**,README.md,manifest/*.tsv}`.
Never touch `transfer/`, `apply_transfer.py`, dumps, databases, ddon-hook, client/, packets/.
Libraries: IDAPython (`ida_ua`, `ida_gdl`), stdlib, pytest, ruff. If `extract_ida.py` grows past ~1,800 lines, first
split it into a package (`extract/`), keeping `extract_ida.py` as the batch entry (the T011 retro: its edits
returned ~19k tokens each).
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; `match.py` twice identical; signed commits
with `git commit -m <msg> -- <paths>`; receipt. Stop: budget 150 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
