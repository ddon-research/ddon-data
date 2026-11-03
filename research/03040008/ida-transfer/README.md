# ddon-ida-transfer (spec 007)

Fact extractors for the PC 03040008 and PS4 02020005 IDA databases and the PS4 DWARF, plus the PC
handler function repair. Spec: `specs/007-pc-handler-annotation/`. Gates: `uv run pytest`,
`uv run ruff check --no-fix .`.

## Read path and write path

- **Reads** (`extract_ida.py`, inspection): ida-mcp on a private copy
  (`bash research/ida/private-copy.sh <pc|ps4> <name>`), or a read-only headless batch:

      idat -A -L<log> -S"extract_ida.py <OUT> <pc|ps4>" <private copy .i64>

  The batch waits for auto-analysis, writes `OUT`, prints `extract_ida summary: {...}` to the log,
  discards the session (`DBFL_KILL`: the packed `.i64` is not rewritten) and exits (`idc.qexit`,
  1 after an error).
- **Writes** (`repair_functions.py --apply`): only as a headless batch job on the work copy, never
  through an ida-mcp worker:

      idat -A -L<log> -S"repair_functions.py <OUT> --apply" <work copy .i64>

  The script ends with `idc.qexit(0)`, which saves and packs the database; it prints
  `repair_functions summary: {...}` as the last line of the log. After an exception it prints the
  traceback and an error summary, marks the database not to be saved (`DBFL_KILL`) and exits with
  code 1; the partial `OUT.tmp` keeps the undo records written so far.
- **A killed worker's writes are lost.** ida-mcp's `close_database` and `save_database` are denied
  here, so an ida-mcp worker cannot save; when it is killed, the next open finds the unpacked files
  and offers "Restore packed base (DISCARD unpacked)" (T004d: 0 of 116 repairs survived). Check the
  `.i64` sha256 and mtime after every batch write.

## Function repair (`repair_functions.py`, script version 2)

`extract_ida.py` (script version 2) writes a `missing_root` record for each root that is not a
function start (`missing`: `no-function` or `inside-function`, `enclosing`, `root` reason) and never
expands the enclosing function in its place; the summary gives `missing_roots`,
`missing_roots_by_kind`, `depth0_expected` (= roots - missing), `depth0_functions` and
`onpacket_orphan_ref_count` beside the `onpacket_orphan_refs` list.

`repair_functions.py` repairs the PC handler-table callbacks that are not function starts. Dry run
first (no `--apply`; also possible in ida-mcp as
`exec(open(path).read(), {"OUT": ".../repair-dryrun.jsonl", "APPLY": False})`).

The callbacks come from the handler table (`extract_ida._ida_pc_table`; the run aborts unless the
table matches the T002 audit). Per callback it decodes the body linearly to its closing `ret`/`jmp`
and checks that no other function overlaps it and, inside a function, the gap before the callback
and that the enclosing function (one chunk) ends at the body end. Accepted since T004e:

- gap bytes that are neither padding nor the tail of an instruction crossing the callback, when no
  code or data xref targets any address in [enclosing start, callback) and the enclosing start is
  not itself a table callback (the junk items become unexplored);
- a stray function (one instruction, one chunk, no xref) lying wholly inside the decoded body, such
  as a nullsub on the body's own `retn`: deleted before the repair;
- an indirect jump with IDA switch info (`ida_nalt.get_switch_info`) whose case targets all lie in
  the body and whose jump table lies outside it.

The near misses stay refused (`gap_referenced`, `gap_not_padding`, `runs_into_function`,
`indirect_jump`, `switch_target_out_of_body`, `switch_table_in_body`, `enclosing_has_tails`).

`OUT` holds a header, one `result` per callback (`already-ok`, `would-repair`, `repaired`,
`refused` + `check`, `failed` + `check`), an `undo` record written and flushed before each applied
repair (items, the functions to delete with their chunks, names, comments of the range), and a
`summary`. Apply order: delete the enclosing function and any stray (`del_func`), then undefine the
conflicting items (and junk gap items), create the decoded instructions, `add_func` at the callback
(IDA picks the end), wait for auto-analysis and read the bounds back. Deleting first matters:
undefining a function's entry instruction deletes the function, which made the T004d
`set_func_start` repairs fail with `MOVE_FUNC_NOFUNC`. Names are not moved: a name left at a
deleted enclosing start is in the undo record.

## Version 3 (T005c): constant arguments, codecs, externs, call-target roots

`extract_ida.py` script version 3 adds, for the role anchors of
`specs/007-pc-handler-annotation/research/T005b-role-anchors.md` § 6:

- **Per call site** (not tail jumps), only what is provably that call's argument:
  - PC: `arg_bytes` (the callee's single `ret N`, else `add esp, N` right after the call, else 0 for a
    known callee with plain `retn`, else null); `const_stack` `[[slot, value], ...]` (slot 0 = `[esp]`
    at the call) from `push imm` and `mov [esp+N], imm` after the previous call in the same block,
    within `arg_bytes`, not overwritten or popped (an unmodelled `esp` change drops all);
    `const_ecx` `{"kind": "imm"|"addr"|"load", ...}` when the last ecx write is `mov ecx, imm`,
    `xor ecx, ecx`, `lea ecx, [abs]` or `mov ecx, [abs]`.
  - PS4: `const_regs` `{rdi|rsi|rdx|rcx|r8|r9: value}` when the register's last write in the block
    is `mov r32/r64, imm` or `xor r, r`; any later write (implicit ones included) leaves nothing.
- **Per function** `codec`: `{"dir": "read"|"write", "width": 1|2|4|8, "evidence": {...}}` or null.
  One cursor advance (`add [base+d], N` / `inc`), a bounds check with the same N (`lea r, [x+N]` =
  read, `cmp r, N` = write); PC also needs the cursor field (`+0x0C` read, `+0x10` write) and every
  `mov eax, <width>` = N. Load width and byte swap (`bswap`, `movbe`, shift, rotate, `call`) are
  evidence only. Variable-length codecs (`Read_MtString`, `Read_bytes`) are not classified.
- **`extern` records**: one per call target without a function record (`reason`: `import`,
  `extern_segment`, `not_function`, `inside_function`, `out_of_scope`), with `name`, `import`
  (`ida_nalt` import, or the import a PLT `jmp [slot]` reaches), `segment`, `segment_class`,
  `function_start` and `sites`; `via: "mem"` records the import slots of `call [slot]`.
- Implicit register writes (string instructions, `loop`, one-operand `mul`/`div`, `cdq`, `cpuid`, ...)
  now count in `arg_regs` and `ecx_loaded` as well.

`repair_functions.py` script version 3: after the table callbacks, the `call rel32` targets of the
functions in scope (roots of `extract_ida.pc_roots`, depth 3, recomputed after the table phase) that
are not function starts are roots too (`root: "call_target"`, `level`, `call_sites`), then the call
targets inside each repaired (dry run: would-repair) body, up to level 3; the rest is written as
`pending`. Same checks, undo records and refusals; a target inside a function passes only by the
T004e inside-function rules. The summary gains `call_targets` (`roots`, `by_status`, `by_check`,
`by_level`, `scope_functions`, `pending_beyond_depth`).

## Matcher (`match.py`, `matcher/`, T005)

    uv run python match.py        # rewrites manifest/*.tsv; identical on rerun; exit 1 on a wrong holdout recovery

Offline over the three dumps; each file's sha256 and header source sha256 must equal `dumps/MANIFEST.tsv`
(fail closed). Libraries: stdlib only (`csv`, `json`, `hashlib`, `random`, `re`, `dataclasses`); pytest, ruff.
Own code: the anchored alignment (`matcher/propagate.py`; `difflib.SequenceMatcher` picks one of several
equal alignments when anchors repeat, here an alignment is used only when forced), the gate logic and the
32-bit parameter widths (no library models MSVC x86 stack bytes from DWARF).

- Tier 0 (`matcher/tier0.py`): a table callback with exactly one `cSeed*Connection::OnPacket_*` string that no
  other function and no orphan (non-function) reference uses takes that string as its name.
- Seeds: the PS4 `cSeed*Connection::OnPacket_{S2C,L2C}_<NAME>` where `<NAME>` is the string after 1..n of the
  group's common leading tokens; candidates are searched in every `cSeed*` class, the one candidate must be
  of the string's own class, be claimed by no other string, and pass gate (c).
- Propagation: anchors are calls whose targets are an accepted pair; a gap with one unpaired call per side
  proposes the callees; a gap holding an anchor-capable call that did not align is blocked; indirect calls
  count as calls. Import/extern anchors: since v3 both dumps carry `extern` records with names; the matcher
  uses them only to name PS4 codec and element-reader call targets (T005e), not as propagation anchors.
- Gates in `matcher/gates.py` (a, c, d) and `matcher/engine.py` (b, fixed point, restart on a conflict with
  an accepted pair). Folding (d) is a code-identity proxy (size, instructions, ordered call targets,
  constants, strings, data refs, ret immediates, ecx use): the dump has no body bytes.
- Gate (c) inputs since T005e: a PC function that no caller site loads `ecx` for (every caller site in the
  dump, v3 `ecx_loaded` false) takes no object even when the extractor saw an `ecx` read (MSVC `push ecx`
  stack reservation); without `ret N` the stack bytes come from the callers' v3 `arg_bytes` before their
  pushed bytes.

### Role anchors (T005e, `matcher/codecs.py`, `matcher/roles.py`)

Evidence: `specs/007-pc-handler-annotation/research/T005b-role-anchors.md` § 6. They run over the accepted
seed handler pairs, after propagation. Every role pair carries its rule, its witnesses (the handler or
element pairs it was read from) and the seeds it depends on.

- **Codec widths**: PC from the dump's `codec` field (20 functions), plus the four variable-length codecs by
  their T005b § 2.1 VA (`S` MtString, `B` bytes, `C` C string). PS4 from the DWARF-named
  `nPacket::Read_*`/`Write_*` symbols, because the v3 classifier knows only 4 of 22 PS4 codecs. The PS4
  `codec` field is a cross-check only (`summary.tsv`: classified, disagreements).
- **Codec tree** (`codecs.flatten`): codec leaves in call-site order. A callee that holds codecs is a
  bracket. The PC walk enters every callee in the dump except `callOnPacketFunc`, the allocator, the
  64-bit swap helper, `WritePacket`, `getAllocator` and the CRT `mem*`/`str*` routines. The PS4 walk enters
  only `nPacket::Read_*` and `CPacket_*::ReadPacket` (`nPacket::Write_*` for senders). A callee the walk
  needs but the dump lacks makes the tree a coverage gap (83 reader pairs, mostly PC sub-element readers
  beyond the dump's depth 3).
- **Rule 1, reader**: the PC handler's unique callee that reaches a codec within depth 2 pairs with the one
  `CPacket_<NAME>::ReadPacket` the PS4 handler calls. `<NAME>` must be the PS4 handler's packet and one of the
  names the PC `OnPacket_` string allows. An inlined PS4 reader gives no pair ("inlined on PS4").
- **Rule 2, element reader**: header rule PC `44` <-> PS4 `24` (`2` when the second PS4 token is not 4).
  In an equal body, or a body whose PS4 sequence embeds into the PC one in exactly one way
  (`season3-extended`), each PS4 `nPacket::Read_CData*` bracket pairs with the outermost PC bracket that
  covers the same codec positions. The rule is applied recursively inside accepted element pairs. A pair
  is accepted only when:
  - it is the same pair at every occurrence (a PS4 element reader without a PC partner at one occurrence
    counts as different);
  - it conflicts with no accepted pair;
  - gates (c) and (d) hold;
  - at least one occurrence is **identified by widths**: no other packet reader of either side whose
    widths fit the same partner pairs either function differently. For an equal body that is a reader with
    the same body; for an embedded one also any embedding reader.

  Without the identification gate the negative control accepted wrong pairs from short equal bodies.
- **Rule 3, codec positions**: `callsites.tsv` gives, for each PC codec call site in an equal-width pair,
  the PS4 overload at the same body position. It names call sites only, never the shared PC codec bodies
  (T002 s32/u32/f32 caveat).
- **Rule 4, listener slot**: the PC requester (calls `reserveNetworkErrorDialog(slot)` with the slot the
  handler passes to `callOnPacketFunc`) and its single sender with `WritePacket` key `(g,id,1)` pair with the
  PS4 requester of the PS4 handler's slot and its single `Send_C2S_*`. Conditions: slots not shared, one
  requester and one sender per side, no second PC sender for the key, outside the login-manager range,
  equal payload write widths, and no PS4 -> PC slot-order inversion. **Not effective on the v3 dumps.** The
  PS4 handler's slot (`mErrorCode[idx]`, a memory displacement) is not recorded, and the requesters (callers
  of the senders) are outside both dumps' scope: 11 of 581 PC and 9 of 478 PS4 reserve call sites are in
  the dumps. All 467 handler pairs are listed as a coverage gap. The rule is tested on synthetic facts.
- **Rule 5, packet object** (ctor/vtable/`operator_new`, T005b § 6.5): not implemented; a later rule.
- **Precision** (`precision.tsv`): 5 fixed RNG seeds each withhold 20% of the seeds. Every role pair of
  the full run that depends on a withheld seed must be absent or come back with the same partner, and no
  pair of the holdout run may contradict the full run (`role_wrong`). Pairs that are new in the holdout
  run are listed (`role_new`).
- **Negative control** (`control.tsv`): the PS4 side of the seeds is deranged with the same 5 RNG seeds.
  Any role pair accepted there is a failure.
- `match.py` exits 1 on a wrong holdout pair or on any control acceptance.
- Outputs (`manifest/`): `pairs.tsv` v2 (`rule`: seed / propagation / reader / element-reader /
  listener-requester / listener-sender; `flags`), `callsites.tsv`, `rejected.tsv` (role refusals as
  `role-<rule>` and `role-b`), `conflicts.tsv` (`stage`), `precision.tsv`, `control.tsv`, `crosscheck.tsv`
  (006 T001 `matched`, T002 `holds`/`wrong`, T005b examples), `summary.tsv` (counts per rule, contexts,
  refusal reasons, codec cross-check, precision and control totals).
