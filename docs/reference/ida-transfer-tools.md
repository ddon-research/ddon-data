# IDA transfer tools

The scripts of `research/03040008/ida-transfer/`, for anyone who runs the PS4 02020005 -> PC 03040008 annotation transfer or reads its output: flags, the extractor's records, the manifest's columns, and the rules of the matcher, the transfer and the apply. [Transfer annotations from PS4 to PC](../how-to/transfer-annotations-ps4-to-pc.md) gives the order of the commands, and [IDA transfer method](../explanation/ida-transfer-method.md) the reasons. Counts are in [Status](status.md#annotated-database-pc-03040008).

## Published results

Addresses are VAs of the PC 03040008 executable, input SHA-256 `f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20`, image base `0x400000`. PS4 02020005 input SHA-256: `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`.

| Result | Under `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/` | `.i64` SHA-256 |
| --- | --- | --- |
| Annotated database, whole types and partial types (`private-copy.sh pc-handlers`) | `spec007-packet-handlers-20261103-wave2/` | `ee07f0b6870cf41fcc1e21ef2c8367c079574f26bfae46b14101faaad1c38c1d` |
| Snapshot before the partial types | `spec007-packet-handlers-20261103-wave1/` | `f7f3a2198cf511ba495d0305a7d7381d6a4cf0b4cbc9d905352fc28a7d3e3c25` |
| Work copy, and its rollback `...exe.before-W2.i64` (= the snapshot) | `ddon-data-007work/` | as the two rows above |
| Base the work started from (ddon-hook's accepted database) | `feature008-field-map-property-working-20261029T161123Z/` | `382e346e0b48b157e261119cf803c7b10d072b40ba3ae187a79291d640a58c0f` |

In the repository, under `research/03040008/ida-transfer/`: `manifest/` (pairs), `manifest/transfer/` (whole types, names, prototypes, comments), `manifest/transfer/wave2/` (partial types, locals). The dumps and logs in `dumps/` are gitignored; `dumps/MANIFEST.tsv` is committed. Reports are in `specs/007-pc-handler-annotation/research/`.

## Scripts

| Script | Runs in | Version | Input | Output |
| --- | --- | --- | --- | --- |
| `repair_functions.py` | `idat` batch | 3 | the database | JSONL log; the database, with `--apply` |
| `extract_ida.py` (with `extract/`) | `idat` batch, or `exec` in ida-mcp | 6 | the database | `dumps/pc-ida.jsonl`, `dumps/ps4-ida.jsonl` |
| `extract_dwarf.py` | `uv run` | 1 | the staged ELF, a PS4 dump | `dumps/ps4-dwarf.jsonl` |
| `manifest.py` | `uv run` | none | `dumps/*.jsonl` | `dumps/MANIFEST.tsv` |
| `match.py` (with `matcher/`) | `uv run` | `pairs.tsv` v2 | the three dumps | `manifest/*.tsv` |
| `transfer.py` (with `transfer/`) | `uv run` | none | the dumps, `manifest/` | `manifest/transfer/`, `manifest/transfer/wave2/` |
| `apply_transfer.py` | `idat` batch | 2 | a manifest directory | JSONL log; the database, with `--apply` or `--undo` |

Gates, from that directory: `uv run pytest`, `uv run ruff check --no-fix .`; `tools/check.sh` runs them as its `xfer` section. Tests are in `tests/`, one file per part (`test_extract_ida_v3.py` to `tests/test_extract_ida_v6.py`, `test_matcher.py`, `test_roles.py`, `test_transfer.py`, `test_wave2.py`, `test_apply_transfer.py`); the IDA adapters `_Ida` and `_ida_*` run only under IDA.

### Flags

| Script | Argument | Default | Meaning |
| --- | --- | --- | --- |
| `repair_functions.py` | `<OUT>` | required | the JSONL log |
| | `--apply` | dry run | write; a dry run writes nothing of its own but ends with `qexit(0)`, which re-saves |
| | `--extract-ida <path>` | beside the script | the `extract_ida.py` whose table reader to use |
| `extract_ida.py` | `<OUT> <pc\|ps4>` | required | the dump and the side; a trailing `--exit` is ignored |
| `extract_ida.py`, `exec` route | globals `OUT`, `SIDE`, `DEPTH` (3), `CODEC_DEPTH` (8), `ROOTS`, `ROOT_PATTERNS`, `PC_WRITE_ENTRY_OVERRIDE`, `SCRIPT_DIR` | | as named; `SCRIPT_DIR` is this script's folder, when the working directory is elsewhere |
| `extract_dwarf.py` | `--elf` | `binaries/PS4_02020005/elf-dumps/.staging/input/DDOORBIS.elf` | gated by the hash in `--chains` |
| | `--chains` | `binaries/PS4_02020005/elf-dumps/dwarf/inline-chains.orbis-addr2line.tsv` | its `elf_sha256` gates the ELF |
| | `--out` | `dumps/ps4-dwarf.jsonl` | |
| | `--ida-dump` | none | scope: every function VA of a PS4 dump. Without it: the ELF symbols `cSeed*Connection::{OnPacket_,Send_}*` and `CPacket_*::{ReadPacket,WritePacket}` plus callees to `--depth` |
| | `--depth` | 3 | |
| | `--type-depth` | none | member and base recursion limit |
| `manifest.py` | `[dumps_dir]` | `dumps` | |
| `match.py` | `--dumps`, `--out` | `dumps`, `manifest` | |
| | `--triage` | `specs/006-packet-pattern-coverage/research/T001-triage.tsv` | cross-check only |
| | `--prior` | `specs/007-pc-handler-annotation/research/T002-prior-annotations.tsv` | audit of the earlier annotations |
| `transfer.py` | `--dumps`, `--pairs`, `--out` | `dumps`, `manifest/pairs.tsv`, `manifest/transfer` | with `--wave2`, the default `--out` is `manifest/transfer/wave2` |
| | `--prior` | as for `match.py` | |
| | `--decisions` | `specs/007-pc-handler-annotation/research/T009-decisions.tsv` | settled conflicts |
| | `--no-holdout` | off | skip rule 6 |
| | `--wave2` | off | member links, partial types, locals |
| | `--wave1` | `manifest/transfer` | with `--wave2`: the types already in the work copy |
| | `--callsites` | `manifest/callsites.tsv` | |
| `apply_transfer.py` | `<manifest dir> <OUT>` | required | a directory with `locals.tsv` is a partial-type manifest |
| | none, `--apply`, `--verify`, `--undo <apply log>` | dry run | exclusive modes |
| | `--apply-log <apply log>` | | required with `--verify`, refused otherwise |
| | `--limit-types N`, `--limit-locals M` | none | first N partial types (retyped ones first, with what they embed) and M locals; recorded in the header, and `--verify` needs the same |

### Exit status

| Script | 0 | 1 | 2 |
| --- | --- | --- | --- |
| `match.py` | clean | a wrong holdout pair, an acceptance in the control, or a dump that fails its identity check (uncaught `DumpIdentityError`) | |
| `transfer.py` | clean | a dump that fails its identity check (as above) | `pairs.tsv` from other dumps or differing from the matcher's run, or a decision that does not fit |
| `repair_functions.py`, `extract_ida.py`, `apply_transfer.py` under `idat` | done; last log line `<script> summary: {...}` | exception: traceback, an error summary, `DBFL_KILL` | |

| `apply_transfer.py` mode | Ends with | The `.i64` |
| --- | --- | --- |
| dry run, `--verify` | `DBFL_KILL`, `qexit(0)` | unchanged |
| `--apply`, `--undo` | `qexit(0)` | saved |
| exception | `DBFL_KILL`, `qexit(1)` | unchanged; `OUT.tmp` keeps the records written before it |

## Function repair

`repair_functions.py` makes function starts of the PC handler-table callbacks and of the call targets in scope. Roots: the table callbacks, read with `extract_ida._ida_pc_table` (the run aborts unless the table matches the audit); then the `call rel32` targets of the functions in `extract_ida.pc_roots`' scope, depth 3, recomputed after the table phase, that are not function starts (`root: "call_target"`, `level`, `call_sites`); then the call targets inside each repaired body, up to level 3. The rest is written as `pending`.

Per root: decode linearly to the closing `ret` or `jmp`, and check that no other function overlaps; inside a function, check the gap before the root and that the enclosing function (one chunk) ends at the body end. Accepted in addition:

- gap bytes that are neither padding nor the tail of an instruction crossing the root, when no code or data xref targets any address in [enclosing start, root) and the enclosing start is not itself a table callback; the junk items become unexplored;
- a stray function (one instruction, one chunk, no xref) lying wholly inside the decoded body, such as a nullsub on the body's own `retn`: deleted before the repair;
- an indirect jump with IDA switch info (`ida_nalt.get_switch_info`) whose case targets all lie in the body and whose jump table lies outside it.

Refusals keep their `check`: `gap_referenced`, `gap_not_padding`, `runs_into_function`, `overlaps_function`, `branch_out_of_body`, `indirect_jump`, `switch_target_out_of_body`, `switch_table_in_body`, `enclosing_has_tails`.

Apply order: delete the enclosing function and any stray (`del_func`), undefine the conflicting items and junk gap items, create the decoded instructions, `add_func` at the root (IDA picks the end), wait for auto-analysis, read the bounds back. Deleting comes first because undefining a function's entry instruction deletes the function, and `set_func_start` then fails with `MOVE_FUNC_NOFUNC`. Names are not moved: a name left at a deleted enclosing start is in the undo record.

`OUT` holds a header, one `result` per root (`already-ok`, `would-repair`, `repaired`, `refused` + `check`, `failed` + `check`), an `undo` record flushed before each applied repair (items, the functions to delete with their chunks, names, comments of the range) and a `summary` (`by_status`, `by_check`, `call_targets`: `roots`, `by_status`, `by_check`, `by_level`, `scope_functions`, `pending_beyond_depth`). There is no undo mode.

## What the extractor emits

`extract_ida.py` reads the database only: no renames, types, comments, decompilation or saves. Every field below is present in a version 6 dump. A value it cannot prove is absent or null, never estimated. Register names play no part in decoding, so IDA renames cannot hide a register.

### Records

| `kind` | Side | Fields |
| --- | --- | --- |
| `header` (line 1) | both | `script`, `script_version`, `side`, `bitness`, `image_base`, `ida_version`, `idb_path`, `database_path`, `input_path`, `input_sha256`, `params` (`depth`, `codec_depth`, `extra_roots`, `reserve_dialog`; PC `group_table`, `groups`, `initializer_range`, `write_entry`) |
| `table` | PC | `group`, `id`, `sub`, `key`, `callback`, `record_va`, `assignment_va`, `initializer`, `bytes`, `literal`, `proved` |
| `missing_root` | both | a root that is not a function start: `va`, `missing` (`no-function`, `inside-function`), `enclosing`, `root` (reason). The enclosing function is never expanded in its place |
| `requester_site` | both | a call of the reserve dialog function outside any function: `va`, `target`, `missing` |
| `function` | both | below |
| `extern` | both | one per call target with no function record: `va`, `reason` (`import`, `extern_segment`, `not_function`, `inside_function`, `out_of_scope`), `name`, `import` (`ida_nalt` import, or the import a PLT `jmp [slot]` reaches), `segment`, `segment_class`, `function_start`, `sites`; `via: "mem"` records the import slots of `call [slot]` |
| `summary` (last) | both | `functions`, `roots`, `missing_roots`, `missing_roots_by_kind`, `depth0_expected` (= roots - missing), `depth0_functions`, `codec_functions`, `codec_path_functions`, `object_accesses`, `call_args_by_kind`, `externs`, `externs_by_reason`, `requesters`, `requester_sites`, `requester_sites_outside_functions`, `reserve_dialog`, `reserve_dialog_name`; PC also `table_ok`, `table_records`, `table_callbacks`, `unproved_records`, `initializers`, `expected`, `senders`, `onpacket_functions`, `onpacket_orphan_refs`, `onpacket_orphan_ref_count` |

### Scope

| Root or scope | Rule |
| --- | --- |
| Depth | callees to `DEPTH` (3) from the roots; each function has `depth` and `root` |
| Requester roots (`root: "requester"`) | every caller of `sNetworkExt::reserveNetworkErrorDialog`: PC `0xBB39D0` (`ret 4`), PS4 by its one symbol. The run fails when the VA is not that function's start, carries another name, or the PS4 symbol is not unique |
| Codec paths (`scope: "codec_path"`) | beyond the depth, every function on a call path of at most `CODEC_DEPTH` (8) levels from a root to a codec (the shape classifier, the four PC variable-length codecs, PS4 `nPacket::Read_*`/`Write_*`), plus the direct callees of each such function |

### Function records

Common: `va`, `name`, `demangled`, `default_name`, `prototype`, `prototype_user`, `size`, `instructions`, `chunks`, `calls`, `callers`, `callers_count`, `caller_sites`, `strings`, `constants`, `data_refs`, `ret_imm`, `depth`, `root`, `scope`, `codec`, `codec_distance`, `object_accesses`. PC only: `ecx_read_before_write`, `annotations`.

- `codec_distance`: least calls to a codec within `CODEC_DEPTH` levels; 0 = a codec, null = none, so a walk can skip callees that reach no codec instead of counting them as gaps.
- `codec`: `{"dir": "read"|"write", "width": 1|2|4|8, "evidence": {...}}` or null. One cursor advance (`add [base+d], N` or `inc`) and a bounds check with the same N (`lea r, [x+N]` = read, `cmp r, N` = write). PC also needs the cursor field (`+0x0C` read, `+0x10` write) and every `mov eax, <width>` = N. Load width and byte swap (`bswap`, `movbe`, shift, rotate, `call`) are evidence only. Variable-length codecs (`Read_MtString`, `Read_bytes`) are not classified.

### Call sites (`calls`)

Common: `site`, `target`, `tail`, `args`. Tail jumps carry no argument facts.

| Field | Side | Meaning |
| --- | --- | --- |
| `pushes`, `pushed_bytes`, `ecx_loaded` | PC | the pushes before the call and their bytes; `ecx` loaded for the call. Implicit register writes (string instructions, `loop`, one-operand `mul`/`div`, `cdq`, `cpuid`) count |
| `via_mem` | PC | the slot address of a `call [slot]` |
| `arg_regs` | PS4 | argument registers written before the call; implicit writes count |
| `arg_bytes` | PC | the callee's single `ret N`, else `add esp, N` right after the call, else 0 for a known callee with plain `retn`, else null |
| `const_stack` | PC | `[[slot, value], ...]`, slot 0 = `[esp]` at the call, from `push imm` and `mov [esp+N], imm` after the previous call in the same block, within `arg_bytes`, not overwritten or popped; an unmodelled `esp` change drops all |
| `const_ecx` | PC | `{"kind": "imm"\|"addr"\|"load", ...}` when the last `ecx` write is `mov ecx, imm`, `xor ecx, ecx`, `lea ecx, [abs]` or `mov ecx, [abs]` |
| `const_regs` | PS4 | `{rdi\|rsi\|rdx\|rcx\|r8\|r9: value}` when the register's last write in the block is `mov r32/r64, imm` or `xor r, r`; any later write, implicit ones included, leaves nothing |
| `args` | both | one record per argument slot whose value the code provably holds at the call. Slots: PC `"ecx"` and stack `0 .. arg_bytes/4 - 1` (the pushes and `mov [esp+N]` since the previous call in the block; none when `arg_bytes` is null); PS4 `rdi rsi rdx rcx r8 r9` |

Kinds of `args`, in `extract/callargs.py`:

| Kind | Fields | From |
| --- | --- | --- |
| `const` | `value` | `mov r, imm`, `xor r, r`, `push imm` |
| `obj` | `arg`, `arg_loc`, `disp`, `def` | function argument `arg` (PC `ecx` or `stack`, PS4 the register) + `disp`, from `lea r,[base+X]`, `mov r, base` + `add`/`sub r, imm` (`sub r, -0x80` = +0x80), or the base itself; `def` = the forming instruction, null for the argument or a plain copy |
| `stack` | `frame`, `def` | a stack slot address; `frame` relative to the entry stack pointer (return address at 0; PC stack argument k at `4 + 4k`; PS4 `rsp` and `rbp` are tracked from entry for this) |
| `element` | `from`, ..., `disp`, `def` | an array element + `disp`. `from: "result"` = the return of an allocator call (`site`, `callee`; PC `sub_8BC2E0`, PS4 `operator new`, or an indirect call on the result of `MtMemoryAllocator::getAllocator`, then `callee: "indirect"`, `getter`). `from: "index"` = `lea r,[data + i*scale]` or `add data, i` with `data = [arg+via]` (`arg`, `arg_loc`, `via`, `index`, `scale`, `index_def`). The allocator identities are inferred from the listing |

Arguments and their copies cross blocks through the must-analysis below; everything derived from them is proved within the block only. Anything else (a register loaded from memory, a `lea` of a non-argument base, a register overwritten after its `lea`) records nothing. MSVC padding nops `lea r,[r+0]` (pointer width, `extract/x86.py` `is_padding_nop`; one at PC `0x757ded`) are skipped as operations, also in `object_accesses`.

### `object_accesses`

One record per memory operand `[base + idx*scale + disp]` whose base provably holds an argument, in `extract/dataflow.py`:

| Field | Meaning |
| --- | --- |
| `va`, `op` | instruction, operand index |
| `arg_loc`, `arg` | `ecx` (arg 0), `stack` (slot k = entry `[esp+4+4k]`), or the PS4 register `rdi`..`r9` with its ABI index |
| `disp`, `width` | signed displacement, operand size |
| `access`, `rmw` | `load`, `store` or `lea`; `rmw` = a store that also reads |
| `value` | a store of an immediate, masked to the width |
| `via` | the displacement of the field the base pointer was loaded from: one dereference, such as PS4 `this->mpManager->mErrorCode[171]` |
| `indexed`, `index`, `scale` | an indexed operand |

Tracking rules:

- A must-analysis over IDA's flow chart (`ida_gdl.FlowChart`, `FC_NOEXT`) iterated to a fixed point: a register keeps a value into a block only if every predecessor agrees. Copies are pointer-width `mov r, r`; a 32-bit PS4 copy truncates and kills. Any other write kills, implicit writes included. A call kills the caller-saved registers (MSVC x86 `eax/ecx/edx`, SysV the argument registers and `rax/r10/r11`); callee-saved ones survive by the ABI.
- PC stack arguments: `esp` is tracked from entry through `push`, `pop`, `sub`/`add esp, imm` and calls whose callee has one `ret N`, else the stack picture ends; `ebp` by copy. A load of an argument slot after a store to it, a `lea` of the argument area, or a store at an unknown `esp`/`ebp` offset is not an argument.
- PC `ecx` accesses mean the function reads `ecx` at entry. Whether it is thiscall is the consumer's decision (`ecx_read_before_write`, the callers' `ecx_loaded`).
- Load and store come from `CF_CHGn` and `CF_USEn`, the displacement from the operand's `addr`.
- Base, index and scale come from the decoded operand, never from printed operand text (`print_operand`), since the PS4 database names argument registers (`[this+cArcLoaderBase.mNum]`). `decode_mem` and `_Db.mem_regs` follow the IDA SDK `intel.hpp` helpers `x86_base_reg`, `x86_index_reg` and `x86_scale` (inline C++, not exported to IDAPython 9.5; read from `D:/GitHub/HexRaysSA/ida-sdk`, commit `04c0a982c8`): `hasSIB` = `op_t.specflag1`, `sib` = `op_t.specflag2`, REX = `insn_t.insnpref` (REX.B and REX.X only in 64-bit mode, `auxpref & aux_use64`). Without SIB the base is `op_t.phrase`; an `o_mem` with SIB has an index and no base; SIB index `100b` without REX.X is no index. 16-bit addressing and VSIB (gather/scatter) give no registers. `reads_reg`, behind `ecx_read_before_write`, uses the same decoding.

Slot facts for consumers: the PC `callOnPacketFunc` `0x878860` slot is `const_stack` slot 0. PS4 `mErrorCode`/`mStatus` stores are `object_accesses` stores with `via` = `mpManager`'s offset (a constant index is a plain `disp`, a variable one `indexed`).

`extract_ida.py` stays the batch entry. Its pure helpers are in `extract/`: `x86.py` (register names, `signed`, the padding nop), `dataflow.py` (`object_accesses`, `block_in_states`), `callargs.py`. It puts its own folder on `sys.path` from `__file__`, which `idat -S` sets.

### `ps4-dwarf.jsonl`

| `kind` | Fields |
| --- | --- |
| `header` | `script`, `script_version`, `side`, `elf_path`, `elf_sha256`, `inline_chains`, `inline_chains_elf_sha256`, `scope_source`, `depth`, `type_depth`, `tool`, `python` |
| `function` | `va`, `name`, `symbol`, `linkage_name`, `prototype`, `return_type`, `params`, `locals` (with lexical block and DWARF location expression), `blocks`, `inlined`, `frame_base`, `ranges`, `cu`, `die`, `decl_die`, `decl_file_index`, `decl_line`, `scope_depth` |
| `type` | `name`, `tag`, `size`, `die`, `cu`, `members`, `bases`, `vtable`, `vtable_holder`, `enumerators`, `underlying`, `target`, `target_die`, `declaration`, `other_definitions` |
| `summary` | `functions`, `types`, `types_by_tag`, `params`, `locals`, `locals_named`, `locals_with_location`, `blocks`, `inlined`, `cus_parsed`, `roots`, `scope`, `scope_without_cu`, `scope_without_dwarf`, `missing_sample`, `seconds`, `scope_seconds` |

### `dumps/MANIFEST.tsv`

`file`, `sha256`, `bytes`, `lines`, `script`, `script_version`, `side`, `source_sha256` (the header's `input_sha256` or `elf_sha256`). The matcher needs `pc-ida.jsonl`, `ps4-ida.jsonl` and `ps4-dwarf.jsonl`: each file's hash and header source must equal it, the sides must match the names, and both PS4 dumps must come from one ELF.

## Matching rules

Offline over the three dumps. Code: `matcher/`.

### Tier 0, seeds and propagation

- **Tier 0** (`matcher/tier0.py`): a table callback with exactly one `cSeed*Connection::OnPacket_*` string that no other function and no orphan (non-function) reference uses takes that string as its name.
- **Seeds**: the PS4 `cSeed*Connection::OnPacket_{S2C,L2C}_<NAME>` where `<NAME>` is the string after 1..n of the group's common leading tokens. Candidates are searched in every `cSeed*` class; the one candidate must be of the string's own class, be claimed by no other string, and pass gate (c).
- **Propagation** (`matcher/propagate.py`): anchors are calls whose targets are an accepted pair. A gap with one unpaired call per side proposes the callees. A gap holding an anchor-capable call that did not align is blocked. Indirect calls count as calls. `extern` names are used only to name PS4 codec and element-reader call targets, not as anchors.

### Gates

In `matcher/gates.py`, gate (b) in `matcher/engine.py`, with a fixed point and a restart on a conflict with an accepted pair.

| Gate | Passes when | Constants |
| --- | --- | --- |
| (a) witnesses | two witnesses, or one witness plus a fingerprint: the same non-empty string set, or the same set of at least two constants | `MIN_CONSTANT` `0x10000` |
| (b) uniqueness | the pair conflicts with no proposal of either function | |
| (c) shape | PC `ecx` use equals a DWARF object parameter, and PC stack bytes equal the DWARF parameters' 32-bit bytes | |
| (d) not trivial | at least `MIN_INSTRUCTIONS` instructions and at most `MAX_CALLERS` callers on each side, and no PC code-identical function | 8, 64 |

Inputs to gate (c):

- PC `this`: `ecx_read_before_write`, except that a function no caller site loads `ecx` for (every caller site in the dump, `ecx_loaded` false) takes no object, since MSVC's `push ecx` stack reservation reads `ecx`.
- PC stack bytes: `ret N` when every `ret` agrees; else the callers' `arg_bytes` when every caller site is in the dump and all agree; else their pushed bytes likewise; else unknown.
- DWARF bytes: pointer and reference 4, 32-bit base types by table, enums 4, typedefs followed. A class by value is unknown.
- `MT_CTSTR` and `MT_STR` count as pointers: inferred from the MT naming.

Gate (d)'s folding is a code-identity proxy, since the dump holds no body bytes (`fold_key`): size, instructions, ordered call targets with each call site's immediate arguments, constants, strings, data refs, `ret` immediates, `ecx` use.

### Role anchors

`matcher/codecs.py`, `matcher/roles.py`. They run over the accepted seed handler pairs, after propagation. Every role pair carries its rule, its witnesses and the seeds it depends on.

- **Codec widths**: PC from the dump's `codec` field, plus the four variable-length codecs by VA (`S` MtString, `B` bytes, `C` C string; `specs/007-pc-handler-annotation/research/T005b-role-anchors.md`). PS4 from the DWARF-named `nPacket::Read_*`/`Write_*` symbols. The PS4 `codec` field is a cross-check only (`summary.tsv`: classified, disagreements).
- **Codec tree** (`codecs.flatten`): codec leaves in call-site order; a callee that holds codecs is a bracket. The PC walk enters every callee in the dump except `callOnPacketFunc`, the allocator, the 64-bit swap helper, `WritePacket`, `getAllocator`, the CRT `mem*`/`str*` routines and a callee whose `codec_distance` is null. The PS4 walk enters only `nPacket::Read_*` and `CPacket_*::ReadPacket` (`nPacket::Write_*` for senders). A callee the walk needs but the dump lacks makes the tree a coverage gap.
- **Rule 1, reader**: the PC handler's unique callee that reaches a codec within depth 2 pairs with the one `CPacket_<NAME>::ReadPacket` the PS4 handler calls. `<NAME>` must be the PS4 handler's packet and one of the names the PC `OnPacket_` string allows. An inlined PS4 reader gives no pair.
- **Rule 2, element reader**: header rule PC `44` <-> PS4 `24` (`2` when the second PS4 token is not 4). In an equal body, or a body whose PS4 sequence embeds into the PC one in exactly one way (flag `season3-extended`), each PS4 `nPacket::Read_CData*` bracket pairs with the outermost PC bracket that covers the same codec positions, applied recursively inside accepted element pairs. Accepted only when it is the same pair at every occurrence (a PS4 element reader without a PC partner at one occurrence counts as different), conflicts with no accepted pair, passes gates (c) and (d), and at least one occurrence is **identified by widths**: no other packet reader of either side whose widths fit the same partner pairs either function differently. For an equal body that is a reader with the same body; for an embedded one also any embedding reader.
- **Rule 3, codec positions**: `callsites.tsv` gives, for each PC codec call site in an equal-width pair, the PS4 overload at the same body position, with `ps4_site` and `ps4_owner` (space-separated, one owner per PS4 site in the same order; one PC element-reader site can align with several inlined PS4 copies). It names call sites only, never the shared PC codec bodies.
- **Rule 4, listener slot**: the PC requester (calls `reserveNetworkErrorDialog(slot)` with the slot the handler passes to `callOnPacketFunc`) and its single sender with `WritePacket` key `(g,id,1)` pair with the PS4 requester of the PS4 handler's slot and its single `Send_C2S_*`. Conditions: slots not shared, one requester and one sender per side, no second PC sender for the key, outside the login-manager range, equal payload write widths, and no PS4 -> PC slot-order inversion against **every** handler pair with a slot on both sides. Then gates (b) to (d) per pair.
  - PC slot: `const_stack` slot 0 of the handler's `callOnPacketFunc` `0x878860` call (one constant) and of the requester's `reserveNetworkErrorDialog` `0xBB39D0` call.
  - PS4 slot (`model.ps4_slot`): the index of the handler's stores `this->mpManager->mErrorCode[idx]` or `mStatus[idx]` (`rdi` arg 0, `via` = `mpManager`, not indexed, element width), with the offsets from DWARF (`cSeedGameSvConnection::mpManager` +280 -> `cNetGameServer`, `mStatus` +8, `mErrorCode` +2260, 563 x 4 bytes; refused unless each class has one record). Several indices or a register index give no slot. The requester's slot is the `esi` immediate of its `reserveNetworkErrorDialog` `0x7EDF80` call. Sender: the single `Send_C2S_*` within two calls.
  - PC reserve call sites outside functions (`requester_site`) are counted in `summary.tsv`, not paired.
- **Anchored gap rule** (`matcher/anchored.py`): after the role anchors, the gap rule runs again over every accepted pair with more anchors. A rule 3 PC codec site (`agree`, its PS4 site aligned with no other PC site) and its aligned PS4 site carry the same token; every other codec call is a blocker. Proposals pass gates (a) to (d); accepted pairs (rule `anchored-gap`) join the role pairs, so the precision check and the control cover them.
- **Rule 5, packet object** (constructor, vtable, `operator_new`): **Status:** planned.

### Controls

- **Holdout** (`precision.tsv`): 5 fixed RNG seeds (1 to 5) each withhold 20% of the seeds. Every role pair of the full run that depends on a withheld seed must be absent or come back with the same partner, and no pair of the holdout run may contradict the full run (`role_wrong`). Pairs that appear only in the holdout run are in `role_new`.
- **Shuffled partners** (`control.tsv`): the PS4 side of the seeds is deranged with the same 5 RNG seeds. Any role pair accepted there is a failure.

### Matcher output (`manifest/`)

Each file has a `#` line naming its inputs and their hashes, then the columns.

| File | Columns |
| --- | --- |
| `pairs.tsv` | `pc_va`, `ps4_va`, `ps4_symbol`, `pc_name`, `pc_name_source`, `rule` (`seed`, `propagation`, `reader`, `element-reader`, `listener-requester`, `listener-sender`, `anchored-gap`), `tier`, `iteration`, `witnesses`, `gate_results`, `flags`, `status` |
| `callsites.tsv` | `pc_site`, `pc_function`, `pc_codec_va`, `width`, `ps4_overload`, `contexts`, `status`, `ps4_site`, `ps4_owner` |
| `rejected.tsv` | `candidate`, `gate` (`tier0`, `seed`, a gate letter, `role-<rule>`, `role-b`), `detail` |
| `conflicts.tsv` | `stage`, `side`, `va`, `conflicting_pairs` |
| `precision.tsv` | `rng_seed`, `seeds`, `withheld`, `seeds_recovered`, `seeds_recovered_correctly`, `seeds_recovered_wrongly`, `role_pairs_full`, `role_dependent`, `role_dependent_absent`, `role_dependent_same_partner`, `role_wrong`, `role_new`, `role_pairs_holdout`, `seed_wrong`, `role_detail` |
| `control.tsv` | `rng_seed`, `seeds`, `shuffled_seeds_passing_c`, `contexts_equal`, `contexts_embedded`, `proposals`, `accepted`, `accepted_equal_to_real_run`, `accepted_not_in_real_run`, `detail` |
| `crosscheck.tsv` | `source` (`006-T001 matched`, `T002 holds`, `T002 wrong`, `T005b example`), `key`, `pc_va`, `expected`, `paired`, `result` |
| `summary.tsv` | `count`, `value`: counts per rule, contexts, refusal reasons, codec cross-check, precision and control totals |

## Transfer rules

`transfer.py` reads the three dumps, the accepted rows of `pairs.tsv` and the audit `specs/007-pc-handler-annotation/research/T002-prior-annotations.tsv`.

| Rule | Code | What it writes |
| --- | --- | --- |
| 1, names | `transfer/names.py` | A tier-0 callback takes its PC `OnPacket_` string, paired or not; any other accepted pair takes the PS4 function's IDA name (`ps4_symbol`, as in `nPacket::Read_CDataAbilityLevelParam_` for `nPacket::Read<CDataAbilityLevelParam>`; the DWARF qualified name and the mangled symbol go into the comment). Against the name in the database: default -> `set`; equal -> nothing; another non-default name -> `conflict`, except an audit `wrong` or name-source-not-code verdict, or the exact PS4-form spelling of the PC string (`OnPacket_S2C_<N>` for `OnPacket_<N>`), which become `correct` with the reason quoted. A name proposed for two PC functions -> `folded`, neither set. A name another PC function holds -> `conflict`. Three labels at former function starts -> `remove-label`, removed before the callback is named at its repaired start |
| 2, prototypes | `transfer/prototypes.py` | `__thiscall` when the matcher's `pc_has_this` holds, else `ret N` -> `__stdcall`, plain `ret` -> `__cdecl`. Written in IDA's printed form without a name (`int __thiscall(A *this, CPacket *pPacket)`). Types: base types and fixed-width typedefs by size and encoding; pointer or reference to a class -> pointer to that class (opaque `struct X;` unless rule 3 transfers it; template names verbatim); 4-byte enums by value -> the DWARF enum; anything else -> the width-sized integer, DWARF type in `notes`. Refused (`skipped.tsv`): IDA's prototype takes a register argument other than `ecx` (`__usercall`, `__userpurge` `@<edi>`), a class returned by value, a user-set prototype that differs (`conflict`). Tier-0 handlers without a PS4 pair: `int __thiscall(<class> *this, void *packet)` only with `ecx` `this`, every `ret` = `ret 4` and the string's class `cSeedGameSvConnection` or `cSeedLoginSvConnection` |
| 3, types | `transfer/layout.py`, `transfer/typecheck.py`, `transfer/render.py` | below |
| 4, comments | `transfer/comments.py` | One per function with a written name or prototype: `PC name from string at <ea>.` and/or `PS4 02020005: <qualified> (<mangled>); paired by <rule>.` plus `Season 3: <flags>.`. A comment already there is kept, ours appended below a `----` line, nothing when it is there |
| 5 | | `skipped.tsv`: every candidate not written, with rule and reason |
| 6, precision | `precision.tsv` | The holdout, the whole pipeline rerun and then the type check on its pairs. A type accepted in the full run and not in a holdout run is listed in `types.tsv` `holdout_lost_in_rng`; `new` lists types accepted only in a holdout run |

**Settled conflicts** (`transfer/decisions.py`): `--decisions` decides conflict rows by (`kind`, `pc_va`); its path and SHA-256 go into every output header. `ours` -> name `correct` or prototype `replace`, with the decision's reason and evidence VAs in `basis`; `theirs` -> `keep` (not written, in `skipped.tsv`); `merge` -> the decision's final value as `correct` or `replace`; `undecided` -> stays `conflict`. Exit status 2 for: a decision for a row that is not a conflict, whose recorded current or ours value differs from the row's, a duplicate, an unknown decision, or one without a row. Rule 4 comments every written function, the corrected ones included.

### Layout rules

Rule 3 computes the PC 32-bit layout from the DWARF members; offsets of the PS4 64-bit layout are not used. One test each in `tests/test_transfer.py`:

| Rule | Statement | Test |
| --- | --- | --- |
| L1 | Scalars by PC size: fixed-width typedefs (`u64`, `s64`, `uint64_t`) by name before the typedef chain; `long`, `wchar_t`, `long double` differ between the PS4 ABI and MSVC and are refused otherwise | `test_l1_scalars_fixed_typedef_and_abi_dependent_long` |
| L2 | Pointers, references, function pointers and pointer-sized typedefs (`size_t`, `uintptr_t`): 4 bytes; pointers to members refused, since MSVC's size depends on the class | `test_l2_pointers_are_four_bytes_and_member_pointers_refused` |
| L3 | Natural alignment capped at 8 (`/Zp8`: `double` and 64-bit integers align to 8); size rounded up | `test_l3_alignment_capped_at_eight_and_size_rounded` |
| L4 | A class that declares the vptr (DWARF artificial `_vptr$`) and has no dynamic base: 4-byte vptr at 0; a dynamic base's vptr is shared | `test_l4_vptr_own_and_shared_with_dynamic_base` |
| L5 | The base comes first; an empty base (no data, no vptr) takes no space; several bases are refused, since MSVC reorders dynamic bases first | `test_l5_empty_base_takes_no_space_and_multiple_bases_refused` |
| L6 | Members in declaration order at their aligned offsets; unions at 0; an empty class has size 1; MSVC never reuses a base's tail padding (Itanium may), which this gives by construction | `test_l6_no_tail_padding_reuse_and_union` |
| L7 | Refused: bitfields, virtual bases, declaration-only types, unresolvable member types, anywhere inside | `test_l7_bitfield_and_virtual_base_and_declaration_refused` |

### Access check

Candidates: the class of `this` and of each pointer-to-class argument of the accepted pairs (PC stack slot from gate (c)'s widths), the pointee class of a pointer member a `via` access goes through, and the embedded member and base types. Every `object_accesses` record of the paired PC function through such an argument must fit the layout (`transfer/layout.py` `land`):

| Access | Fits when | Contradicts |
| --- | --- | --- |
| load or store | it lands on the start of a **leaf** member (scalar, pointer, enum, vptr) with exactly the leaf's width, recursing through bases, embedded structs and array elements | a whole aggregate read at once (an 8-byte copy of a 2 x u16 element), no width, padding, a byte inside a member, another width, past the size |
| `lea` | it lands on the object start, on the start of one of the object's **own** members (bases included), or on an element start of such an array member | a `lea` inside an embedded struct |
| indexed | a SIB scale equal to the element size of an array member whose element start its displacement is, then the leaf rule at that element start | a field of `arr[i]` other than the first |

A pointer to a pointer (`MtObject **mpArray`) is not a pointer to a class: `via` accesses through it lay nothing on `MtObject`. There are no exceptions for narrow `test byte ptr` or 8- and 16-byte block copies: they count as contradictions.

A contradiction counts against the argument's class (the root), which is refused. An access counts for an embedded type or a `via` pointee only while its root is not refused. A type that embeds a refused type is refused (fixed point). Accepted: zero contradictions, at least one checked **width** access (a load or store on a leaf start), and the size equal to a known PC size where one exists. A `lea` may contradict a type but never accepts one: a type checked by `lea` records alone stays `unchecked` with reason `lea-only`, and so does an embedded type, which is then written as bytes inside its outer type; a prototype that names it keeps an opaque pointer.

The dumps link no allocation or constructor to a type, so the only size evidence is `typecheck.KNOWN_SIZES` (`cSeedGameSvConnection` `0x540`, `CPacket_S2C_GET_STAGE_LIST_RES` `0x30`, from the audit); other types say so in `size_evidence`.

Types left forward-only because `lea`s alone had checked them: `CDataClanSearchResult`, `CDataGPShopLineupElementBase`, `CDataGameTimeBaseInfo`, `CDataMailInfo`, `CDataOrbGainExtendParam`, `CDataWorldInfo`.

**Status:** planned: a typed `lea`. A `lea` whose address is passed as the argument of a paired callee whose PS4 parameter type is the member's type (`lea ecx, [esi+0x18]; call <paired CDataX::read>` with `this` of type `CDataX*`, and the member at +0x18 of type `CDataX`) ties the sub-object's type and could accept a `lea`-only type.

### `types.h`

Accepted types and the checked types embedded in them (`embedded`), each after its dependencies, inside `#pragma pack(push, 1)` with explicit `gap` members, so IDA places every member at the computed offset. The vptr is `void *__vftable`, a base `Base baseclass_<off>`. A member of a type not transferred is written as bytes with the DWARF type in the comment. A pointer to a class not transferred points to an opaque `struct X;`, which claims no layout. Enums used by transferred members or prototypes are written as in DWARF (4-byte ones); an enum whose enumerator names another written enum already uses is skipped. Names are the DWARF names, templates included (`MtTypedArray<CDataX>`); anonymous types are not written. IDA's built-in C parser may not take `<...>` in names; the tinfo API does.

### Partial types and locals (`transfer.py --wave2`)

Inputs: the dumps with `args`, `pairs.tsv`, `callsites.tsv` (must equal the matcher's run, exit status 2 otherwise) and the whole-type pass's `manifest/transfer/types.tsv` and `types.h`. Code: `transfer/wave2.py`, `transfer/locals.py`, `transfer/wave2_run.py`.

- **Member links**: a rule 3 codec site pair of an accepted owner pair whose destinations are `obj+X` (PC slot 1) and `obj+Y` (PS4 `rsi`) off the same object parameter links PC offset X of that parameter's class (PS4 DWARF) to the innermost leaf member at PS4 offset Y (bases and embedded structs entered), with the codec width.
- **Element-reader links**: a paired callee called once in each owner, its argument `obj+X`/`obj+Y` off the owners' object parameter, links X to the member starting at Y whose type is the callee parameter's pointee and has a whole-type PC layout; its size is the width. `args` slots are intersected with the callee's DWARF parameters.
- **Packet class witness**: a packet class (`CPacket_*`) needs a PC handler calling the owner whose tier-0 string names it (`tier0.candidate_names`).
- **Not derived**: array-element links (`element` does not fire), owners that are no accepted pair, variable-width codecs. `links.tsv` lists every site with its reason.
- **Partial type**: links and no conflict (offset -> two members, member -> two offsets, width != leaf width, overlapping links). Members at the linked offsets with the PS4 names (`a.b` -> `a__b`) and leaf types, gaps elsewhere. Size = a known size (`typecheck.KNOWN_SIZES`) or the end of the last member (`size: lower bound`). Whole types are unchanged (`status wave-1`). `types.h` carries one comment line per type (`// <type>: Partial: N members linked by codec position ...`) and repeats the whole types they embed verbatim.
- **Access check of a partial type**: every width access of the paired PC functions through that class. One overlapping a linked member must land on a leaf start of it with the leaf's width (`layout.land`), else the class is refused. Gap accesses are allowed and counted; indexed ones are counted as not placed. An access through the object (not through a loaded pointer) ending past a lower-bound size (`disp + width`; a `lea` at `disp` as `disp + 1`) extends the size to that end, the farthest one recorded as `size_evidence`, with `last_member_end`. Past a proved size it refuses the class. Shifts, PS4 offsets alone and `lea`s never make members.

**Locals** (`locals.tsv`):

| Rule | Statement |
| --- | --- |
| `R1` | a paired callee called once on each side, the slot a PC stack address and, on PS4, the register DWARF says holds a local's address at the call (`DW_OP_breg<N> 0` covering the site) |
| `R2` | the same at rule 3 codec site pairs (PC slot 1, `rsi`) |
| `R3` | the PC handler's stack object passed as `this` to the PC reader of a rule 1 pair <-> the PS4 handler's single DWARF local of the reader's class, when the PS4 handler passes a stack address as `rdi` to that reader or inlines it (DWARF inline record). Two stack objects passed refuse. `R3` retypes to the partial or whole type; without one: refused, since the size is unverifiable. An object reaching the return address: refused |

PC location: entry-relative frame < 0, never an incoming argument slot; `pc_def` the defining `lea`. Per function, a location with two names, a name at two locations, or a named local inside a retyped object refuse every row involved. The width, "no user name" and "not an argument" on the Hex-Rays side are checked by the apply.

**Controls**: the holdout reruns the matcher pipeline and this pass (links, types, locals: `lost`, `contradict`, `new` per RNG seed, `precision.tsv`). `control.tsv`: the PS4 side of the reader pairs deranged (5 RNG seeds), their rule 3 rows re-aligned by position to the partner's `nPacket::Read_*` calls; with the witness everything on the shuffled classes must vanish; the `variant` row runs without it.

The whole-type pass refuses dumps taken after its own apply (exit status 2): the decisions find no conflicts there. `manifest/transfer/` stays as written.

### Transfer output

| File, `manifest/transfer/` | Columns |
| --- | --- |
| `names.tsv` | `pc_va`, `action` (`set`, `correct`, `remove-label`), `name`, `current`, `source`, `basis`, `reason` |
| `prototypes.tsv` | `pc_va`, `action` (`set`, `replace`), `decl`, `current`, `basis`, `notes`, `types`, `enums` |
| `comments.tsv` | `pc_va`, `action` (`set`, `append`), `comment`, `existing` |
| `types.tsv` | `type`, `kind`, `status` (`accepted`, `embedded`, `declared`), `pc_size`, `ps4_size`, `checked_accesses`, `functions`, `members_checked`, `members_unchecked`, `evidence_vas` (up to 10), `size_evidence`, `holdout_lost_in_rng`, `basis`, `coverage` (bytes of leaves hit by fixed-offset loads and stores over the PC size; a `lea` or an indexed access checks no bytes) |
| `type_members.tsv` | `type`, `offset`, `size`, `member`, `decl`, `dwarf_type`, `checked_by` |
| `skipped.tsv` | `rule`, `item`, `candidate`, `action` (`equal`, `refused`, `skip`, `unchecked`, and where they arise `conflict`, `keep`, `folded`), `reason` |
| `precision.tsv` | `rng_seed`, `withheld_seeds`, `pairs`, `types_accepted`, `lost`, `new` |
| `summary.tsv` | `key`, `value` |
| `types.h` | the C header above |

| File, `manifest/transfer/wave2/` | Columns |
| --- | --- |
| `links.tsv` | `class`, `pc_offset`, `width`, `ps4_member`, `dwarf_type`, `ps4_offset`, `kind`, `pc_site`, `ps4_site`, `pc_owner`, `ps4_owner`, `outcome` |
| `types.tsv` | `type`, `kind`, `status` (`partial`), `pc_size`, `size_kind`, `last_member_end`, `size_evidence`, `members`, `links`, `width_checked`, `gap_accesses`, `indexed_unplaced`, `functions`, `evidence_vas`, `holdout_lost_in_rng`, `basis`, `comment` |
| `type_members.tsv` | `type`, `offset`, `size`, `ps4_member`, `decl`, `dwarf_type`, `links` |
| `locals.tsv` | `pc_va`, `ps4_va`, `rule`, `pc_call`, `ps4_call`, `callee`, `slot`, `name`, `dwarf_type`, `dwarf_die`, `ps4_bind`, `pc_frame`, `pc_def`, `size`, `retype`, `holdout_lost_in_rng`, `status` (`accepted`, `refused`, `duplicate`), `why` |
| `precision.tsv` | `rng_seed`, `withheld_seeds`, `pairs`, then `full`, `lost`, `contradict`, `new` for each of `links_`, `types_`, `locals_` |
| `control.tsv` | `rng_seed`, `variant`, `reader_pairs_shuffled`, `reader_class_links`, `links_equal_to_real`, `reader_classes`, `classes_conflicted`, `classes_accepted`, `accepted_equal_to_real`, `r3_locals`, `r3_equal_to_real` |
| `summary.tsv` | `key`, `value` |
| `types.h` | the C header above, with a comment line per type |

## Apply rules

`apply_transfer.py` is a pure decision layer over an adapter: `_Ida` in IDA, a fake in `tests/test_apply_transfer.py`.

- **Precheck** (every mode): input SHA-256 `f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20`; idb path under `ddon-data-007work` or `ddon-data-007smoke`; every manifest file's header names that PC dump source and the same run. The files' SHA-256 and the counts (user names, functions with a user type, local type ordinals) go into the log's header.
- **Order**: types (`types.h`), `remove-label` rows, names, prototypes, comments, locals. `conflict` rows of `skipped.tsv` are reported (`conflict-names`, `conflict-prototypes`), never written.
- **Every write**: `undo` record (before-state: name and user flag, printed type + serialized tinfo, comment, local type layout + serialized tinfo, or `null` for an absent type) flushed first, then the write, then the read-back. A mismatch is `failed` with both values, no retry. A second `--apply` finds every row `already`.

### Types

`types.h` is read with its own grammar (one member per line with `// +0x<off> <size>`, gaps `gapN[k]`; a non-contiguous layout or an unknown line fails) and declared through the `ida_typeinf` tinfo/udt API, not the C parser, so `MtTypedArray<CDataX>` stays verbatim: forward declarations first for every absent name, then each struct as a fixed-layout udt with explicit member offsets, named-type members as references (`create_typedef(..., BTF_STRUCT)`), `set_named_type(NTF_REPLACE)`.

| The type in the database | Result |
| --- | --- |
| absent | created |
| row is opaque | `already` |
| forward declaration | defined; a partial type's comment line becomes the type comment (`set_type_cmt`) |
| equal layout | `already` |
| different | `refused` with both layouts, unless its `types.tsv` status is `replace` |

A struct embedding a refused type and a prototype naming one are refused. Opaque rows (`struct X;`), the `lea`-only types among them, are written as forward declarations without members.

Equal layout (`same_layout`): same size and the same non-gap members by (offset, size), names equal, except IDA's conventions:

- the row's vptr (`__vftable`, udm vftable flag) equals a member at +0 with the vftable flag or named `__vftable`, `_vptr$*` or `vfptr`;
- a row base (`baseclass_<off>`, udm base-class flag) equals a base-class member, `baseclass_*`, unnamed or named after its class, whose type name is the row's base class;
- a row base whose class is not transferred (rendered as `unsigned __int8 baseclass_<off>[<size>]; // ... base X (not transferred)`; any other declarator with that comment fails) compares by its class `X`: a base of class `X` at the same offset and size is equal, the type stays `already` and the database's richer base is kept;
- a plain member's type must match too. The adapter's type is the member's type name, or its printed type when it has none (`MtObject **`, `char[16]`), and it must equal the row's base type with its pointer stars and array count after `norm_type` (no spaces, `struct`, `const`; one spelling per scalar, `uint32_t` = `_DWORD` = `unsigned int`). A record without a type compares by name only.

Anything else differing, a base of another type, offset or size included, refuses. The adapter reads members as `(name, offset, size, kind, type)`, with kind `vptr`, `base` or empty from the udm flags. Rendered types keep their pointer depth: `ctype` and `Layouts.resolve` strip one `*` or `&` level at a time, as `MtArray::mpArray` is `MtObject **`.

### Names, prototypes, comments

- **Names**: `remove-label` rows first, since a removed label's name is free for its callback; then `set` and `correct`. Refused when the address is not a function start (`not-function-start`), the current name is not the row's `current` (`current-changed`), or the name is held at another address (`name-used-elsewhere`).
- **Prototypes**: refused when the current prototype is user-set (`set` rows, `user-prototype`; a `replace` row is a settled conflict and overwrites one) or differs from the row's `current` (`current-changed`, both kinds). Type names the parser may refuse (`<...>`, `::`) are parsed as `void *` and patched to pointers to the local type through `func_type_data_t`; a parse failure (`parse`) is a refusal before any write. `apply_tinfo(TINFO_DEFINITE)`. The `already` check, the read-back and `--verify` compare types, not printed text, since IDA prints a `::` or template type as `struct X`: the row parsed into a `tinfo_t` against the function's `get_tinfo`, equal when the calling convention, the return type, the argument count and each argument's name and type (`tinfo_t.compare_with(.., TCMP_EQUAL)`, IDA 9.5 `python/ida_typeinf.py`) agree. The printed text stays in the logs (`db`, `row`, `before`).
- **Comments**: function comment; ours appended below a `----` line, `already` when present. An `append` row carries `existing + ---- + ours`; the loader keeps only `ours` (any other shape fails), so the database's comment is kept and ours appended once.

### Locals

A directory with `locals.tsv` is a partial-type manifest (`types.tsv`, `locals.tsv`, `types.h`; no names, prototypes or comments). The `locals` step: decompile, find the stack lvar whose IDA frame offset is `frame_off_retaddr + pc_frame` and equals the defining `lea`'s `calc_stkvar_struc_offset` (else `frame-mismatch`), exactly one (else `lvar-not-unique`). Refused when it is an argument (`argument`), has a user name (`user-name`) or, when retyping, a user type (`user-type`), its width differs from the row's size for `R1` and `R2` (`width`), or the retype's local type is missing (`type-missing`) or of another size (`type-size`). Written with `modify_user_lvar_info` by `lvar_locator_t` (stack offset + `defea`) with `MLI_NAME`, plus `MLI_TYPE` for `R3`; read back by re-decompiling (`mark_cfunc_dirty`). Undo drops the lvar's saved user settings.

### Verify and undo

- **Verify**: every row against the database (`ok`, `mismatch`; a retyped local also needs its lvar width equal to its type's size, else `mismatch` with `check: width`); the counts against the apply log's header plus what its applied rows account for (+1 name per `set` on a default name, -1 per removed label, +1 typed function per prototype set, +1 local type per type created); and a decompilation of each function whose prototype is the row's. The manifest hash must equal the apply log's.
- **Undo**: the undo records of an apply log in reverse order (absent type -> deleted, default name -> cleared, non-user type -> `del_tinfo`), each read back. A defined forward declaration is deleted and declared again, so the local type ordinal count grows by one per type.

## Libraries and own code

| Part | Libraries | Own code, and why |
| --- | --- | --- |
| Extractor | IDAPython (`ida_ua`, `ida_idp`, `ida_gdl`, `ida_funcs`, `idautils`, `idc`) | the register dataflow (no IDAPython or stdlib module tracks argument registers across blocks; `ida_regfinder` answers constant values only), the SIB/REX decoding, the memoized codec reachability |
| DWARF | pyelftools, capstone | |
| Matcher | stdlib (`csv`, `json`, `hashlib`, `random`, `re`, `dataclasses`) | the anchored alignment (`difflib.SequenceMatcher` picks one of several equal alignments when anchors repeat; here an alignment is used only when forced), the gate logic and the 32-bit parameter widths (no library models MSVC x86 stack bytes from DWARF) |
| Transfer | stdlib, the matcher's gates | the MSVC x86 layout from DWARF records and the access landing (no library computes an MSVC layout from Itanium DWARF), the TSV and C-header writers |
| Apply | IDAPython (`ida_typeinf`, `ida_name`, `ida_bytes`, `ida_funcs`, `ida_nalt`, `ida_hexrays`, `ida_loader`, `idc`, `idautils`), stdlib | the `types.h` reader (a generated format no parser covers), the prototype argument split (templates the IDA parser does not take) |
