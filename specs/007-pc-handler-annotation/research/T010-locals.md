# 007 T010: local variable names, feasibility and rules

PC 03040008 <- PS4 02020005. Addresses are VAs (PC image base `0x400000`, 32-bit; PS4 base `0`, 64-bit).
Base `eb1cdda52ad`, 2026-11-03. Brief: `specs/007-pc-handler-annotation/briefs/T010-locals-feasibility.md`.
12-pair walk: `T010-locals-walk.tsv` (31 rows, sha256 `9d89ccd6...c669`).

**Outcome: the spec § 3 rule names 0 PC locals across the 898 pairs whose PC function exists in the
database it ran on, with 0 conflicts. Binding the PS4 DWARF locals to PS4 Hex-Rays lvars works (1,257 of
2,256 locals bind uniquely). The bottleneck is the operation link. 3,235 of the 3,321 PS4 defining
operations call callees that are not in `pairs.tsv`. The 86 that do call paired callees are refused by
binding (47), by size (24) or because the PC side passes no `&var` (15). The only rule that names anything
with every gate passing is the codec-anchor extension (R2 below): 3 `nRet` names. Feasible, but the yield
is very low unless the callee pairing grows.** (Measured on the accepted PC copy, not on the work copy: § 1.)

## 1. Inputs and identity

| Item | Identity |
| --- | --- |
| PS4 database | private copy `PS4_DDON_02020005_2016_12_21/ddon-data-t010/DDOORBIS.elf.i64` (`private-copy.sh ps4 t010`); `get_idb_path` confirmed, 64-bit, min EA `0x0` |
| PC database | private copy `PC_DDON_03040008/ddon-data-t010/2022_01_29_DDO_DUMP_FIX.exe.i64` of the **accepted** database (`private-copy.sh pc-accepted t010`, feature008, sha256 `382e346e...a58c0f`); `get_idb_path` confirmed, 32-bit, image base `0x400000` |
| DWARF | `research/03040008/ida-transfer/dumps/ps4-dwarf.jsonl` sha256 `352d86c7...8d69` (ELF `4236f598...63c0`) |
| Pairs | `manifest/pairs.tsv` sha256 `3e2d0d3c...5eb7` (972 accepted) |
| Anchors | `manifest/callsites.tsv` sha256 `f939fd39...be13` (926 rows, all `agree`) |
| PC sizes | `manifest/transfer/types.tsv` sha256 `878c53c6...c280` (90 accepted structs) |
| Work copy | `ddon-data-007work/...exe.i64` **not opened and not run**; sha256 `f7f3a219...3c25` at start and end (unchanged) |

**The work copy was not used.** Its read-only batch needs a batch script file. This role's write hook
(`guard_paths.py --allow 'specs/*/research/*'`) refuses every script path outside `specs/*/research/`, and
the brief owns only the report and the TSV. So all IDA work ran through ida-mcp on the two private copies.
The accepted PC copy lacks the 248 repairs: 74 of the 972 PC pair functions are not function starts there
(`no-function`), which leaves 898 pairs evaluated. It also lacks the wave-1 names and prototypes, so PC
callees show as `sub_...`. That does not change a ctree's call and argument structure, so the counts
should carry over to the work copy (**inferred**, not run there). Section 6 gives the work-copy rerun.

Scratch dumps (session scratchpad `t010/`, not committed): `ps4_lvars.jsonl` sha256 `b14d8c23...443e`
(972 functions, 0 errors, 19 s), `pc_lvars.jsonl` `6d8ba3b6...ccca` (972, 74 `no-function`, 9 s) and
`ps4_bind.jsonl` `fa4d2cd6...0b21`. Per function they hold the Hex-Rays lvars (name, width, arg/user flag,
type, register or stack offset converted with `mba.stkoff_vd2ida`, `defea`). They also hold every ctree
`cot_call` (call EA, `cot_obj` callee, the arguments with casts stripped: `&var`, `&var.m`, `&var[i]`,
`var`, number, other; and the result-assigned lvar when the call, through casts, is the right side of
a `cot_asg` to a `cot_var`). On PS4 they add every `lea reg, [stack]` with
`ida_frame.calc_stkvar_struc_offset`.

## 2. PS4 binding: DWARF local -> PS4 Hex-Rays lvar (step 1)

The PS4 DWARF frame base is `DW_OP_reg6` (rbp), but the compiler emits almost no `fbreg` locals: 1 plain
expression among the 2,256 locals. Locals carry location lists of `DW_OP_regN` (register value), `DW_OP_bregN 0`
(the register holds the local's **address**: stack objects at the point they are passed) and
`DW_OP_constu` (a constant, no storage). DWARF register numbers: 0 rax, 1 rdx, 2 rcx, 3 rbx, 4 rsi,
5 rdi, 6 rbp, 7 rsp, 8-15 r8-r15.

Binding rules (verified on `0x2de4d0` `OnPacket_S2C_LOBBY_JOIN_RES` by disassembly):

- **B-reg-def**: a list entry `[lo, hi) DW_OP_regN` binds a non-argument register lvar of the same
  register family (`get_mreg_name`, so `esi`/`si` count as `rsi`) when its `defea` lies in the def window.
  The window runs from the first of up to 4 consecutive instructions before `lo` that write that register
  (e.g. `movzx esi, cx; cmovz esi, eax` before `tmpErr` at `0x2de5bf`) to `lo`. Hex-Rays' `defea` is not
  always the last writer (`v8` has `defea 0x2de5ba`).
- **B-stack-lea**: an entry `[lo, hi) DW_OP_bregN 0` binds the stack lvar whose start equals the frame
  offset of a `lea N, [rbp/rsp+off]` that ends exactly at `lo`. Example: `lea rsi, [rbp+packet]` at
  `0x2de621`, length 4, before `packet` `breg4 0` at `0x2de625` binds lvar `packet` at stack offset 0. A
  `lea` into the middle of a stack lvar is refused (`lea-interior`).
- **B-reg-use** (weaker): when no def-window match exists, a register lvar of the same family with a
  ctree use (`cot_var` EA) inside `[lo, hi)`. Loop counters such as `i` bind only this way.
- A local binds when exactly one lvar matches over all its entries, and that lvar is bound by no other
  local (`shared-lvar`: 0 cases).

Counts over all 972 PS4 pair functions (2,256 DWARF locals, all named):

| Result | Locals |
| --- | ---: |
| bound uniquely | **1,257** (def 906, use 351) |
| ambiguous (2+ lvars) | 54 |
| unbindable: no location (optimized out) | 884 |
| unbindable: no register or `lea` match | 23 |
| unbindable: `breg` off frame or offset != 0 (`breg6 -56` and others) | 31 |
| unbindable: constant only (`DW_OP_constu`) | 4 |
| unbindable: `lea` interior / `breg` without `lea` / other expression | 1 / 1 / 1 |

Sanity check, **verified as a count**: PS4 lvar width against the DWARF 64-bit size gives def 889 equal,
8 different, 9 unknown; use 328 equal, 22 different, 1 unknown. The differences are narrow types held in
wider registers. Hex-Rays' own lvar names agree where they carry meaning (stack `packet` = DWARF `packet`
29 times). Others are plausible auto-names: DWARF `sendPacket` = Hex-Rays `packet` 234 times (an IDA frame
name), `dwSize` = `v` 89 times (from the callee prototype), `tmpErr` = `m_nResult`/`m_usError`.

## 3. Operation link (step 2) and type check (step 3)

Rule, as the spec and brief state it: for a bound PS4 lvar defined by a ctree call to a callee that has a
pair (the result is assigned to it, or `&lvar` is argument k), that callee must be called exactly once in
the PS4 function and its PC counterpart exactly once in the PC function. The PC lvar is the one assigned
from that PC call, or `&lvar` at the same argument k, with equal argument counts. It must not be an
argument and not user-named. Its width must equal the DWARF type's 32-bit size: pointers 4, base types by
name, enums from DWARF, classes only from `types.tsv` `accepted` `pc_size`.

All 972 pairs (898 evaluated):

| Stage | Count |
| --- | ---: |
| PS4 defining operations (result-assigned or `&var` argument) | 3,321 |
| callee not in `pairs.tsv` | 3,235 (with a bound lvar 1,195: callee once 364, several times 831) |
| callee paired | **86** |
| refused: PS4 lvar not bound | 47 (39 `ar`: a member of a packet object Hex-Rays split off, which DWARF gives no location; 8 results with no DWARF local) |
| refused: size unverifiable (class without a PC layout) | 23 (all `packet`, `&v` passed to the paired `CPacket_S2C_*::ReadPacket`) |
| refused: PC argument is a stack array (`var`, decays to an address) | 15 (all `packet`) |
| refused: size mismatch | 1 (`cNetGameServer::returnRentedPawn` `0x87caa0`: `sendFeedbackList` `PawnFeedbackVec`, 20 bytes on PC, against PC `v17`, 4 bytes) |
| refused: callee not called exactly once on either side | 0 |
| **PC lvars named** | **0** |
| PC lvars that two rules would name differently | 0 |
| one name on two PC lvars of one function | 0 |

Variants (measured, **not proposed**): with the 15 stack arrays counted as `&var` (relaxed variant 1),
the size refusals become 38. With "size unverifiable passes for address-of" added (relaxed variant 2),
38 PC lvars would be named `packet`, all in `seed` handlers, with 0 conflicts. But the PC lvars are
Hex-Rays pieces of the split packet object: `int` (15), `_BYTE[16]` (10), the vptr
`int (__stdcall **)(char)` (7), `char[16]` (2) and others. The type gate is right to stop them.
`T010-locals-walk.tsv` column `outcome_relaxed` shows it for CLAN_GET_MY_INFO `0x7cb2b0` (`v6`, vptr-typed)
and CLAN_CREATE `0x7cace0` (`v6`, `char[16]`).

## 4. Codec-anchor extension (R2, brief "call sites already aligned by the matcher's anchors")

`callsites.tsv` anchors PC codec call sites to their PS4 overload (`nPacket::Read_u32`, ...). Rule: a PS4
call to overload O with a bound lvar, where O is called once in the PS4 function and the PC function has
exactly one `agree` row for O. The PC call at that `pc_site` then supplies the counterpart, with the same
gates as § 3.

| Result | Count |
| --- | ---: |
| PS4 codec operations with an unbound lvar | 681 |
| overload called more than once in the PS4 function | 801 |
| no PC anchor row for the overload / several rows | 141 / 1 |
| PC lvar is an argument or user-named | 21 (`dwSize`: MSVC reuses the dead argument slot, e.g. `0x758100` `nPacket::Read_u32(packet, &value)`) |
| **linked, all gates passed** | **3** (`nRet`, `int`, element readers `0x75e9b0`, `0x775310`, `0x777920`, PC `v3`) |
| conflicts | 0 |

Repeated overloads (801) would need the anchor's PS4 site. Rule 3 in `matcher/roles.py` computes it, as
the tuple `(pc site, owner, codec, token, PS4 overload, PS4 site)`, but `callsites.tsv` does not export
it. Exporting `ps4_site` turns those into anchored sites; most of them pass `&this->member` or
`&packet.member` (`refmem` 130, `refidx` 65 over all calls), so few would name locals.

## 5. Proposal for the implementer

**Recommendation: implement R1 + R2 as a separate read-only batch (`locals.py`, writing
`manifest/transfer/locals.tsv`), expecting single-digit names on today's pairs.** Do not relax the
size gate for address-of objects. The cheaper gains are listed under near-misses.

1. **PS4 binding** (§ 2): B-reg-def, B-stack-lea, then B-reg-use. Unique both ways. Record the method,
   the DWARF DIE, the location entry used and the PS4 lvar (index, location).
2. **R1, paired callee**: as in § 3, both sides once, equal argument counts, `&var` exactly (offset 0,
   no member, no index) or a result assigned through casts to a `cot_var`.
3. **R2, codec anchor**: as in § 4, keyed by `callsites.tsv` (better: export `ps4_site`).
4. **Gates**: the PC lvar is not an argument, has no user name (`lvar.has_user_name`), and its width
   equals the DWARF 32-bit size; an unknown size refuses. 0 conflicts and 0 duplicate names per
   function, else refuse every row involved.
5. **`locals.tsv` columns**: `pc_va ps4_va rule(R1|R2) pc_call ps4_call callee op(arg k|res)
   dwarf_name dwarf_type dwarf_die ps4_bind_method ps4_lvar pc_lvar_index pc_lvar_defea pc_lvar_location
   pc_width size32 status why`.
6. **Apply**: identify the PC lvar by location plus `defea` (`lvar_locator_t`), never by index or name.
   Rename with `ida_hexrays.rename_lvar(func_ea, old, new)`, or with `modify_user_lvar_info` and
   `MLI_NAME` through `lvar_saved_info_t`. Keep the before-state in the undo log. Rerun the binding after
   the wave-1 prototypes, because a prototype change can renumber lvars.

Near-misses, each a separate decision for Sam:

- **Callee pairing for library getters**: 364 operations have an unpaired callee called once and a bound
  lvar. They are mostly `sendPacket`/`packet` passed to `nPacket::Write_*`/`Read_*` (on PC, a shared
  `CPacket::WritePacket` header call with a different structure). There are also result-assigned
  `pContext`/`pInfo`/`pPlInfo` (about 50) from `sContextManager::getContextMyPlayer`,
  `cContextInterface::getContextPlayerInfo_0` and similar. Pairing those getters would name these.
- **Packet object locals**: 38 `packet` links (§ 3) need the PC 32-bit layout of each
  `CPacket_S2C_*` class first. `types.tsv` has them `opaque`/`declared`, and refuses several for
  contradictions. Only then can the lvar be retyped to the whole object and named.
- **`dwSize` in element readers**: 21 anchored links land on the reused argument slot. Naming an argument
  after a local would be wrong; leave them.
- **Not used, by the spec**: declaration order, position, and "only stack object of type T" (the
  `sendPacket` in 234 senders would bind that way: PC `CPacket v4`).

## 6. Not run, and how to rerun on the work copy

- Not run: the batch on `ddon-data-007work` (`f7f3a219...3c25`), refused by the role's write hook (§ 1);
  the counts on the work copy are inferred. To rerun: put the dump of § 1 (the ida-mcp code of this run)
  into the implementer's script, then
  `idat -A -L<log> -S"locals.py <OUT>" <work copy>`, ending with `DBFL_KILL` and `qexit`. Check the
  sha256 before and after.
- Not run: a type gate for classes without a PC layout (none exists); ImHex and the gates (`tools/check.sh`)
  are not relevant (no code changed).
- Cleanup: the private copies are deleted except the unpacked `.id0`/`.id1`/`.nam` files the two ida-mcp
  workers still hold open (`close_database` is withheld) in `PC_DDON_03040008/ddon-data-t010/` and
  `PS4_DDON_02020005_2016_12_21/ddon-data-t010/`; delete both folders once the workers exit.
