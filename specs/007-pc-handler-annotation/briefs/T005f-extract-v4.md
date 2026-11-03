007 T005f: extractor v4 (object-relative accesses, slot displacements, requester roots, reader depth)

Objective (PC 03040008, PS4 02020005): the facts still missing for (1) the listener-slot anchor (T005e
rule 4: 0 pairs because the dumps lack the slot and the requesters) and (2) the structure-layout check
of spec 007 § 3 (every member access of a paired function lands on a predicted member). Read
`research/T005b-role-anchors.md` § 1.3, § 4, § 5 and the T005e receipt notes in `tasks.md`.

`extract_ida.py` v4, both sides, all tested with fakes incl. near-misses:
1. **Object-relative memory accesses** per function: for each instruction with a memory operand
   `[base + disp]` (load or store, width from the operand), where `base` provably holds an argument at that
   point: PC `ecx` at entry (thiscall `this`) or a stack argument loaded into a register (`mov r, [esp+N]`
   / `[ebp+N]` in the prologue), and copies of those registers until overwritten, within the function's
   basic blocks in order (no cross-block guessing: a register is tracked into a block only if every
   predecessor agrees); PS4: `rdi`/`rsi`/`rdx`/`rcx`/`r8`/`r9` at entry and copies. Record (insn va,
   argument index, disp, width, load|store, and for a store of an immediate its value). Indexed forms
   `[base + idx*scale + disp]`: record with `indexed: true` and the scale.
2. **Slot facts**: the immediate argument of calls to `callOnPacketFunc` `0x878860` and, on PS4, the
   displacement/index of the `mErrorCode`/`mStatus` stores (from 1., stores into `cNetGameServer`): make
   sure the indexed store form is captured (`mErrorCode[idx]` with a constant idx is a plain displacement).
3. **Requester roots**: every caller of the PC `reserveNetworkErrorDialog` counterpart (find its VA from
   T005b § 1.3/§ 5: the function the requesters call with the slot; give the VA in the receipt with its
   evidence) and of the PS4 `reserveNetworkErrorDialog` symbol; plus their callees to depth 2.
4. **Reader depth**: callees of functions that reach a codec are followed to depth 8 (until no codec is
   reached), so sub-element readers (e.g. PC `0x771FD0`) are in the dump.
Bump the script version. Keep the dump format additive (new record fields / kinds only) so `matcher/`
keeps working; run the matcher's tests.

Owns: `research/03040008/ida-transfer/{extract_ida.py,tests/**,README.md}`. Never touch `matcher/`, the
dumps, the databases, ddon-hook, client/, packets/.
Libraries: IDAPython (ida_ua operands, ida_gdl flow chart for blocks, ida_funcs, idautils), pytest, ruff.
Done: tests; `uv run pytest`, ruff, `bash tools/check.sh --since <base>`; signed commits with
`git commit -m <msg> -- <paths>`; receipt. Stop: budget 120 min of work time.
Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
