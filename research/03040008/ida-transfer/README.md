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

## Version 4 (T005f): object-relative accesses, requester roots, codec-path depth

`extract_ida.py` script version 4, additive (new fields and one new record kind; v3 readers keep working):

- **Per function `object_accesses`**: one record per memory operand `[base + idx*scale + disp]` whose base
  provably holds an argument: `va`, `op` (operand index), `arg_loc` (`ecx`, `stack`, or the PS4 register
  `rdi`..`r9`), `arg` (0 for `ecx`; stack slot k = entry `[esp+4+4k]`; PS4 ABI index), `disp` (signed),
  `width` (operand size), `access` (`load` / `store` / `lea`), `rmw` (a store that also reads), `value`
  (store of an immediate, masked to the width), `via` (the disp of the field the base pointer was loaded
  from: one dereference, e.g. PS4 `this->mpManager->mErrorCode[171]`), `indexed` + `index` + `scale`.
  - The tracking is a must-analysis over IDA's flow chart (`ida_gdl.FlowChart`, `FC_NOEXT`) iterated to a
    fixed point: a register keeps a value into a block only if every predecessor agrees. Copies are
    pointer-width `mov r, r` (a 32-bit PS4 copy truncates and kills); any other write kills (implicit
    writes included); a call kills the caller-saved registers (MSVC x86 `eax/ecx/edx`, SysV the argument
    registers and `rax/r10/r11`), callee-saved ones survive by the ABI.
  - PC stack arguments: `esp` is tracked from entry through `push`/`pop`/`sub`/`add esp, imm` and calls whose
    callee has one `ret N` (else the stack picture ends); `ebp` by copy. A load of an argument slot after a
    store to it, a `lea` of the argument area, or a store at an unknown `esp`/`ebp` offset is not an
    argument. PC `ecx` accesses mean the function reads `ecx` at entry; whether it is thiscall is the
    consumer's decision (`ecx_read_before_write`, the callers' `ecx_loaded`).
  - Base, index and scale come from the decoded operand since v5 (below), the displacement from the
    operand's `addr`, load/store from `CF_CHGn`/`CF_USEn`.
- **Slot facts**: the PC `callOnPacketFunc` `0x878860` slot is v3's `const_stack` slot 0 (675 sites in the
  v3 PC dump); PS4 `mErrorCode`/`mStatus` stores are `object_accesses` stores with `via` = `mpManager`'s
  offset (a constant index is a plain `disp`, a variable one `indexed`).
- **Requester roots** (`root: "requester"`): every function that calls `sNetworkExt::reserveNetworkErrorDialog`,
  PC `0xBB39D0` (named so in the work copy, 581 caller sites = T005b § 5, `ret 4`), PS4 by its one symbol.
  The run fails closed when the VA is not that function's start, carries another name, or the PS4 symbol is
  not unique. A call site outside any function is a `requester_site` record. Callees follow the normal
  depth (3).
- **Codec-path depth** (`CODEC_DEPTH` = 8): beyond the depth-3 scope, every function on a call path of at
  most 8 levels from a root to a codec (v3 shape classifier, the four PC variable-length codecs, PS4
  `nPacket::Read_*`/`Write_*`) is dumped with `scope: "codec_path"`, plus the direct callees of each such
  function. Every function record carries `codec_distance` (least calls to a codec within 8 levels, 0 = a
  codec, null = none), so a walk can skip callees that reach no codec instead of counting them as gaps.
- Header `params` gain `reserve_dialog` and `codec_depth`; the summary gains `reserve_dialog`,
  `reserve_dialog_name`, `requester_sites`, `requesters`, `requester_sites_outside_functions`,
  `codec_path_functions` and `object_accesses`.

Libraries: IDAPython (`ida_ua`, `ida_idp`, `ida_gdl`, `ida_funcs`, `idautils`, `idc`). Own code: the
register dataflow (no IDAPython or stdlib module tracks argument registers across blocks; `ida_regfinder`
answers constant values only), the SIB/REX decoding (v5, below), and the memoised codec reachability.

## Version 5 (T005h): memory operands from `op_t`, not from operand text

v4 parsed base/index/scale from `print_operand` text. The PS4 database names argument registers (register
variables: `[this+cArcLoaderBase.mNum]`), so that text holds no register and v4 dropped almost every PS4
access (722 records instead of 30,587; T005g § 4). v5 (`decode_mem`, `_Db.mem_regs`) reads the decoded
operand instead, following the IDA SDK `intel.hpp` helpers `x86_base_reg` / `x86_index_reg` / `x86_scale`
(inline C++, not exported to IDAPython 9.5; read from `D:/GitHub/HexRaysSA/ida-sdk`, commit 04c0a982c8):
`hasSIB` = `op_t.specflag1`, `sib` = `op_t.specflag2`, REX = `insn_t.insnpref` (REX.B/REX.X only in
64-bit mode, `auxpref & aux_use64`); without SIB the base is `op_t.phrase`; an `o_mem` with SIB has an
index and no base; SIB index `100b` without REX.X is no index. 16-bit addressing and VSIB (gather/scatter)
give no registers (fail closed). `reads_reg` (`ecx_read_before_write`) uses the same decoding. Register
names play no part, so IDA renames cannot hide a register.

PS4 v5 run (T005h): 30,587 records in 2,839 functions, 1,772 indexed, 7,345 via a pointer load, 2,685
stores via `mpManager` (`+280`): equal to T005g's register-variable what-if. The PC dump stays v4 (PC has no
register-variable operands, T005g § 4; the v5 decoding gives the v4 records on the `sub_4169B0` fixture).

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
  constants, strings, data refs, ret immediates, ecx use; since T005h also each call site's v3 immediate
  arguments, which are body bytes): the dump has no body bytes. Without the call-site immediates about 200
  PC senders, which differ only in their `WritePacket` key, counted as one folded group.
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
  needs but the dump lacks makes the tree a coverage gap (T005e on v3: 83 reader contexts, mostly PC
  sub-element readers beyond depth 3; T005h on v4: 3). Since T005h the PC walk also skips a callee whose v4
  `codec_distance` is null (it reaches no codec within 8 levels) instead of entering it, so that callee's
  own missing callees are no gap.
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
  equal payload write widths, and no PS4 -> PC slot-order inversion against **every** handler pair with a
  slot on both sides (T005h: checking the candidates alone let one deranged pair of the negative control
  through). Then gates (b)-(d) per pair.
  - PC slot: `const_stack` slot 0 of the handler's `callOnPacketFunc` `0x878860` call (one constant) and of
    the requester's `reserveNetworkErrorDialog` `0xBB39D0` call.
  - PS4 slot (`model.ps4_slot`, T005h): the index of the handler's stores `this->mpManager->mErrorCode[idx]`
    / `mStatus[idx]` (v5 `object_accesses`: `rdi` arg 0, `via` = `mpManager`, not indexed, element width),
    with the offsets from DWARF (`cSeedGameSvConnection::mpManager` +280 -> `cNetGameServer`, `mStatus` +8,
    `mErrorCode` +2260, 563 x 4 bytes; fail closed unless each class has one record). Several indices or a
    register index give no slot. The requester's slot is the `esi` immediate of its
    `reserveNetworkErrorDialog` `0x7EDF80` call. Sender: the single `Send_C2S_*` within two calls.
  - T005h run (v5 PS4 dump): 497 PS4 functions with a slot, 245 candidates, 107 requester and 234 sender
    pairs accepted (138 requesters fail gate (c) on unknown PC stack bytes); the 33 PC reserve call sites
    outside functions (`requester_site`) are counted in `summary.tsv`, not paired.
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
