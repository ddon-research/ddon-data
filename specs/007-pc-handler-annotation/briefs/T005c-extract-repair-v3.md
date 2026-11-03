007 T005c: extractor v3 (call-site constant arguments) and repair v3 (call-target roots)

Objective (PC 03040008, PS4 02020005): the role anchors proposed in
`specs/007-pc-handler-annotation/research/T005b-role-anchors.md` § 6 need facts the dumps lack, and
code the PC database leaves undefined. Read § 0, § 1.3, § 3, § 4, § 6 and "Not run / limits".

1. `extract_ida.py` v3:
   - Per call site, the constant arguments: PC: the values of `push imm` (and `mov [esp+N], imm`) that
     belong to that call's argument window, by stack slot, plus `ecx` if loaded from an immediate or an
     address; PS4: immediates moved into the SysV argument registers (`edi`/`esi`/`edx`/`ecx`/`r8d`/`r9d`
     and 64-bit forms) in the same basic block before the call. Record only what is provably that call's
     argument (same block, not overwritten); else nothing.
   - Per function, a `codec` field when its body is one of the read/write codec shapes of T005b § 2.1/2.2:
     width from the instructions (bounds check, cursor advance, load width, byte swap), never from a name.
     T005b's VA tables are the test oracle.
   - Call targets outside the dump: one `extern` record per target (va, name if IDA has one, import or PLT
     name, segment), so imports can anchor.
   Scope unchanged; bump the script version; tests for each new field (fakes) including the near-misses:
   a push that belongs to an earlier call, a register overwritten before the call, a codec look-alike with
   a different cursor advance.
2. `repair_functions.py` v3: besides the table callbacks, roots are the **direct call targets** (`call rel32`)
   from functions in scope that are not function starts (T005b: 34 element readers at `0x758000`-`0x77C000`
   with broken boundaries, the login code region `0x888000`-`0x88E000` largely undefined). Same checks,
   same undo log and refusals; a call target inside an existing function is refused unless the T004e
   inside-function rules accept it. Iterate: newly created functions' call targets become roots, up to
   depth 3, until no new root. Tests: a call target inside a real function (refused), a chain of two
   undefined callees (both repaired).

Owns: `research/03040008/ida-transfer/{extract_ida.py,repair_functions.py,tests/**,README.md}`. Never
touch matcher code (T005e), the dumps, the databases, ddon-hook, client/, packets/.
Libraries: IDAPython (ida_ua operand decoding, ida_bytes, ida_funcs, idautils, ida_nalt imports), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 120 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
