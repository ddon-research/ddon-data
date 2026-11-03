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
  count as calls. Import/extern anchors are not possible: neither dump names call targets outside it.
- Gates in `matcher/gates.py` (a, c, d) and `matcher/engine.py` (b, fixed point, restart on a conflict with
  an accepted pair). Folding (d) is a code-identity proxy (size, instructions, ordered call targets,
  constants, strings, data refs, ret immediates, ecx use): the dump has no body bytes.
- Outputs (`manifest/`): `pairs.tsv`, `rejected.tsv`, `conflicts.tsv`, `precision.tsv` (5 fixed RNG seeds,
  20% of seeds withheld), `crosscheck.tsv` (006 T001 `matched`, T002 `holds`/`wrong`), `summary.tsv` (counts,
  gap shapes, PS4-inline-only uneven gaps).
