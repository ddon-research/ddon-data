# 007 T001: the earlier PC packet-annotation work (ddon-hook specs 006-008)

Builds: PC **03040008** (fixed dump `2022_01_29_DDO_DUMP_FIX.exe`, SHA-256 `f1c974d0…`, IDA VA, base
`0x400000`, 32-bit) and seed PS4 **02020005** (`DDOORBIS.elf`, DWARF DIE/CU ids). Every PC VA below is
a 03040008 IDA VA; every DIE is from 02020005. Read-only survey, 2026-11-03, ddon-data base
`834c45de0e`, ddon-hook HEAD `36a61a6` (36 dirty paths, left as found). No IDA was opened. Paths
below are relative to `C:/Users/morph/CLionProjects/ddon-hook/` unless they say otherwise.
Marks: **V** = I checked it here (file read, count or hash). **I** = inferred. **R** = taken from
the prior agent's own receipt or document and not re-checked against the database.

## 0. Answer in brief

- The prior packet work (ddon-hook spec 006, hardened by 007) is strict about **PC identity** and
  loose about **PS4 identity**. A PC S2C handler was named only when two things held: an exact
  dispatch-table callback assignment, and a PC `.rdata` diagnostic string
  `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>` referenced from the body. The applied name is
  **that PC string**, not the PS4 symbol. The PS4 counterpart was found by name stem / alias search
  and is recorded only as "PC continuity inferred" (V, section 1).
- The output is small: **107 method views** (V: 22+13+2+9+12+12+30+2+1 contract rows, plus Send,
  the history sender and 2 destructors = 107, matching `coverage.json`). That includes **50 of the
  1,040 table callbacks** (V: every one equals its table callback) and **1 C2S sender**. There are
  2 new packet structs, 9 peer types and 11 neutral field renames. **No locals** were deliberately
  named. The whole handler table (1,041 records, 1,040 callbacks) exists in machine-readable form
  but was **not annotated** (V, section 2).
- Its own confidence contract rates source identity as **117 inferred / 79 unavailable / 0
  verified** over 196 methods (V, `specs/007-harden-recovery-confidence/contracts/recovery-confidence.json`).
  Overlap with ddon-data 006 T001-triage: **24 shared ids, 24 agree on PC VA and PS4 symbol, 0
  disagree** (V, section 5).

## 1. Method

| Decision | Rule (quoted or condensed) | Source |
| --- | --- | --- |
| Overall | "use original PS4 DWARF and PC native evidence together … Alternative rejected: transfer names by matching call order, sizes or addresses" | `specs/006-recover-pc-packets/research.md:9-11` |
| Rejections | "Matching call order, byte width, name substring, source slots or identical bodies does not authorize a match." | `specs/006-recover-pc-packets/spec.md:111-112` |
| Identity chain | "Trace source declaration → PC identifier/registration → owning connection or factory → vptr/dispatch → native parser/writer and callers. Reject matches based only on constants, consecutive functions, current names or identical bodies." | `docs/investigations/13-packet-recovery.md:87-89`; family recipe `docs/investigations/16-recovery-method-and-lessons.md:212-215` |
| Handler table anchor | 74 `{ptr,count}` pairs at `0x1BC0110`, 24-byte records, command u16 at +16, subtype byte at +18. Callback = last literal `mov [esp],imm` → `movq xmm` → `movq [record],xmm` in the 73 initializers, proved with no overwrite inside an 8-instruction window | `13-packet-recovery.md:94-100`; code `scripts/ida_packet_dispatch.py:14-16,37,63-89`; `research.md:107,111` |
| Handler acceptance gate | "PC diagnostic strings, native dispatch and ECX/one-stack-word/ret4/EAX0..1 behavior authorize13existing game handler names/physical prototypes." Code: the name must equal the diagnostic bytes + NUL exactly; body range hash, extent and live/fixed/installed PE mapping must match | `research.md:159`; `scripts/ida_packet_handlers.py:57-84`; per-row `confidence` block in `contracts/batch008-handler-annotations.json` (`identity: "verified PC diagnostic plus exact dispatch identifier/callback assignment"`) |
| PS4 counterpart | Exact-name search first, then a shorter role alias ("Search shorter role aliases after an exact-name miss"). The suffix search also hit lost-pawn handlers, which were excluded. Status always "PC continuity inferred" | `13-packet-recovery.md:114-123`; `research.md:137-139,159` |
| Prototypes | Physical PC view only: `int __thiscall(cSeedGameSvConnection *self, CPacket *packet)` for handlers. PS4 `BOOL` recorded separately ("int is physical32bit return lens; PS4 BOOL declaration is separate") | `scripts/ida_packet_batch008_handlers.py:78-81`; `13-packet-recovery.md:108-112,276-279` |
| Types / layouts | From PC allocation, accesses and DTI sizes. PS4 64-bit layouts were explicitly **not** transplanted: "PS4 has wider pointers and different offsets. No PS4 virtual-slot number was transferred". Unknown storage stays opaque, unknown flags get neutral names | `13-packet-recovery.md:133-137,142-144`; `spec.md:61-62`; `16-…:412-417` |
| Signedness | Identical codec bodies cannot set signedness: "Preserve neutral physical widths until native consumers distinguish alternatives" | `16-…:401`; `specs/007-harden-recovery-confidence/scalar-native-audit.md:9-11` |
| Locals | No PS4-driven local naming. Rule: match each local by stored location and definition token and type only that lifetime | `16-…:322-327` |
| Writing and saving | Fixed hash-pinned manifest, before-capture, labelled native undo, apply, fresh decompilation (`NO_CACHE`), exact undo plus replay, independent review, unique backup, then save of the actual PC GUI IDB | `13-packet-recovery.md:192-221,350-365`; `scripts/packet_transaction.py`; `ida_packet_batch008_handlers.py:139-170` |
| Later relaxation (resources, 008) | "A plausible match may be annotated as a hypothesis. Do not count it as verified"; the full capture/replay is needed only when the operation presents that risk | `16-…:21-60` (2026-10-30). Not applied to packets: no packet annotation after 2026-10-15 (`specs/006-recover-pc-packets/progress.md:147-160`) |

Batches were at most 25 logical packets in catalog order (`13-packet-recovery.md:161-165`). The C2S
side used the 658 header-writer call sites. A request was annotated only when a direct caller and
the whole sender were proved; the history request is the one example (`13-packet-recovery.md:563-603`).

## 2. Outputs

### What is in the database (R, per contracts; database state not re-checked)

| Kind | Count | Where (all under `specs/006-recover-pc-packets/contracts/`) |
| --- | --- | --- |
| Codec, framework and stage method views (`nPacket::Read_u8` … `Read_CDataStageAttribute_`, `CPacketBase::ReadBytes`, `sub_8BC2E0` allocator, stage handler `0x7FD9E0`, parser `0x81CC40`) | 22 | `annotations.json` (`methods[]`: `ea`, `name`, `prototype`, `source.die`) |
| S2C handler name, prototype and function comment | 13 + 2 + 9 + 12 + 12 = 48, plus stage `0x7FD9E0` and server list `0x7F9740` = **50** | `connection-handler-annotations.json`, `source-handler-annotations.json`, `batch005-/batch007-/batch008-handler-annotations.json`, `server-list-method.json` |
| Peer wrapper methods (`nNetwork::PacketReader/Writer/Coder/Decoder`, `MtMemoryStream`) | 30 | `peer-annotations.json` (`source_die`, `source_cu`) |
| String writers `0x8BC790` `Write_MtString`, `0x8BCA30` `Write_cstr` | 2 | `string-writers.json` |
| `cSeedServerConnection::Send` `0x9D6A20` (prototype plus 4 SP points) | 1 | `send027-annotations-v3.json` |
| C2S sender `0x833670` `Send_PAWN_GET_PAWN_HISTORY_LIST_REQ` (boundary repair) | 1 | `history029-annotations.json`, `history029-method-evidence.json` |
| Deleting destructors `0x7B6B20`, `0x7B6B60` (boundary repair, one-slot table views) | 2 | `scripts/ida_packet_destructors.py`; `research.md:73` |
| New structs | `cSeedGameSvConnection` (1,344 B, opaque except `vft`, `mpManager`@316) and `nUserSession::CPacket_S2C_GET_STAGE_LIST_RES` (48 B) | `annotations.json` `new_types`; layout in `scripts/ida_packet_annotations.py:169-176` |
| Peer types | 9 (`MtMemoryStream`, `nNetwork::Coder`, `Decoder`, `PacketBase`/`Reader`/`Writer` plus their 3 `_vtbl`) | `peer-annotations.json` `new_types` |
| Field changes | 11 neutral renames `mFlag00..mFlag10` each in `CDataStageAttribute` and `CStageAttribute`; `CDataStageInfo` field 5 retyped | `annotations.json` `field_renames`, `field_type_change` |
| Enums | none found in the packet contracts (V, not exhaustive) | n/a |
| Locals | **0 deliberate**; 3 generated-local renames and 629 propagated caller prototypes from the Send retype; 156 generated `packet`/`str` argument labels | `13-packet-recovery.md:450-455,505-511` |
| Comments | Function comment on every annotated method. Spec 007 later removed 193 provenance comments, replaced 4 call-site and 3 vtable notes and added 13 function comments; 570 stored pseudocode notes remain | `docs/investigations/14-recovery-confidence.md:83-89` |

Totals: 107 saved method views, 200 offline wire schemas (163 reader, 37 writer), 1,590 records
pending (V, `specs/006-recover-pc-packets/coverage.json`). Last packet save: 2026-10-15 to the
*root* PC IDB, SHA-256 `fc1fa220…` (`progress.md:29-33`).

### Machine-readable PC VA <-> PS4 lists

- `contracts/packet-catalog.json` (2.3 MB, 1,790 records keyed `game:S2C:<group>:<command>:<subtype>`).
  It holds **1,041 `pc_registration`** records: `record_ea`, `initializer`, `assignment_ea`, and
  `literal_candidates[-1].ea` = callback VA. That is 1,040 callbacks, all distinct, plus the null
  key `15:65535:255`. There are 38 `pc_method` rows (VA, name, physical prototype) and 44 `source_hints` (V).
  **This is the full handler-table list; it carries no PS4 symbol.**
- The handler-annotation contracts above: `ea`, `packet_key`, `diagnostic.ea/reference`,
  `ps4_source.qualified_name`, declaration/definition DIE, CU, PS4 range. 48 rows (V).
- `contracts/batch007-writer-method-map.json`: 12 C2S senders (`0x832600` … `0x834480`) ↔ PS4
  `Send_C2S_*` declaration DIEs. `annotation_authority: false`, so they were not applied (V).
- `contracts/batch003-method-map.json`: 19 S2C VAs. Only 6 have a PS4 declaration ("no source
  name fabricated" for the rest). It records one rejected candidate, `0x841B60` (V).
- `annotations.json` (codecs ↔ `nPacket::Read/Write` overload DIEs) and `peer-annotations.json`.
- `specs/007-harden-recovery-confidence/contracts/recovery-confidence.json`: 196 methods with
  per-dimension status (identity inferred 117 / unavailable 79; code identity verified 196) (V).
- Raw local receipt: `specs/006-recover-pc-packets/receipts/game-dispatch-native-final.json` (exists, V; not opened).

**Handler-table coverage:** all 1,041 entries are catalogued. 50 callbacks are annotated in the
IDB, and I matched each of the 50 to its table callback (V). The other 990 callbacks carry no
prior annotation.

## 3. Weak points, contradictions, open items

1. **Byte-identical codecs got distinct signed or unsigned names.** `0x8BC480` `Read_s32` and
   `0x8BC4D0` `Read_u32` are byte-identical 74-byte bodies. So are `0x8BC410` `Read_u8` and
   `0x8BC6E0` `Read_bool` (35 B), and `0x8BC660` `Read_s64` and `0x8BC6A0` `Read_u64` (60 B)
   (`scalar-native-audit.md:9-11`). Which body bears which name is not fixed by code. It was taken
   from DIE pairing in `annotations.json`, and no consumer audit separated them (the audit covers
   one consumer, `scalar-native-audit.md:43-47`). `Read_s64` is even typed `unsigned __int64*`.
   Spec 007 must not reuse these names as identity (I).
2. **The PS4 counterpart rests on name similarity.** The handler identity is PC-verified, but the
   PS4 symbol was found by stem or alias search (`13-…:114-123`; `research.md:139`). No body-shape
   comparison was recorded for the 48 handlers. They mark this "inferred" themselves.
3. **The connection type's size has no located evidence.** I found no source for
   `cSeedGameSvConnection` = 1,344 B or `mpManager`@316 (`ida_packet_annotations.py:169-171`;
   `offline-layout.cpp:9`) in `evidence.json` or `receipts/pc-framework-stage-before.json` (V,
   negative search; the evidence may sit elsewhere). Treat it as unverified.
4. **Propagated metadata sits in the IDB without review.** 629 caller prototypes, 3 local renames
   and 156 argument labels came from IDA propagation (`13-…:450-455,505-511`). One `GUESSED`
   prototype in `sub_824750` needed special restoration (`13-…:458-463`).
5. **Unresolved control flow was left in place on purpose.** Noreturn on `0x407AC0` (23 call sites
   in 20 functions) and callee `0x35D3CB5` truncates 5 notification pseudocode bodies. Party
   notification `0x7EBEB0` has a state-dependent no-read path (`progress.md:70-79`;
   `13-…:306-322`). Send helper `0x9D78C0` has an unresolved indirect return. Stale disassembly at
   callback `0x88D300` contradicts the decoded `ret 20` (`13-…:469-473`).
6. **Database lineage is contradictory.** Spec 006 saved its packet work into the root
   `…/PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64` (`progress.md:29-31`, hash `fc1fa220…`).
   `CURRENT-RECOVERY.json` now names that path `original_PC` (`717e862d…`, V by `sha256sum`) and
   says "Original databases intentionally preserved and not overwritten". 008 records that the
   root's hash changed and that the cause is unattributed (`specs/008-recover-pc-resources/ability-research.md:237-240`).
   The accepted copy (`feature008-…/…i64`, `382e346e…`, V) descends from a copy chain whose link
   to `fc1fa220` I did not trace (I). Whether the accepted IDB holds all 107 packet views is
   **not checked**; a later IDA package must check it.
7. **The docs contradict each other.** `13-packet-recovery.md:9-14` still says "70 annotated
   methods / Eighty structural reader documents", and `:371` says 120/12. `coverage.json` says
   107/200. Heading `13-…:517` "# Pawn packet batch 008" sits over batch009 text. The catalog
   still gives `game:S2C:1:0:2` the disposition `…handler_boundary_pending`, though
   `research.md:129,139` record the repair (V). The catalog has `pc_method` for 38 records, while
   50 handlers are annotated; batch008's 12 are absent (V). Contract `comment` texts predate
   spec 007's comment cleanup, so they no longer equal the IDB comments (I, from
   `14-…:87-89`).
8. **Open tasks remain.** T021-T025 (global coverage, framing, source, runtime), T029
   (`0x407AC0` and party), T030 (nora-data 8:32:1 sender not found in 658 header-call windows)
   and T031 (runtime-offset provenance audit) are unchecked (`specs/006-recover-pc-packets/tasks.md:72-89,316,324,390`;
   `progress.md:81-84,123-126`). Batch010 review caught two wrong runtime-offset maps before they
   reached IDA (`13-…:618-623`). Maps in earlier batches were never audited against access sites.
9. **Some review limits were never closed.** No independent reopen of the saved packed IDB
   (`progress.md:34`). "Live operations were receipt-reviewed by workers, not re-executed"
   (`progress.md:54`). Only the pawn graph got a full native audit; "Other131schemas retain
   integrity/association checks" (`specs/007-harden-recovery-confidence/convergence.md:31-32`).
10. **Shared helpers have provisional resource views.** Spec 008 annotated 139 resource views,
    89 of them explicitly provisional (`specs/008-recover-pc-resources/checkpoint.md:28-31`).
    `MtArray` grow `0x40BFA0` has 1,031 references, likely including packet array readers (I),
    and its old `MtTypedArray::MtTypedArray` name is called unsupported
    (`specs/008-recover-pc-resources/array-research.md:26-37`). `MtPropertyList` insertion has
    9,177 references (`checkpoint.md:62-67`).
11. **Things that are *not* weak:** no community-server name was used as a name authority (Arrowgene
    is "corroboration, never PC protocol authority", `research.md:44-47`); there was no packet-number
    matching and no 64-bit layout transplant (`13-…:142-144`).

## 4. Scripts (`scripts/`)

"Need" says whether a clean method needs the script: **pattern** = reuse the idea, not the code;
**no** = one-shot, pinned to old states.

| Script | What it does | Need | Defect or note |
| --- | --- | --- | --- |
| `ida_packets.py` | Read-only capture: identity, catalog, functions with fresh pseudocode | pattern | `capture_functions(fresh=True)` default (`13-…:361-365`) |
| `ida_packet_dispatch.py` | Reads the handler table and proves the literal callback per record | **yes (logic)** | Literal VA window `0x401000-0x1AE0000` hard-coded (`:70`); 8-instruction window; records without data xrefs get no candidate |
| `ida_packet_annotations.py` | The 22-method codec/stage transaction, creates 2 structs | no | Struct sizes inline with no evidence link (`:169-176`) |
| `ida_packet_handlers.py` | 13-handler transaction; diagnostic-equals-name gate | pattern | Hard-coded type sizes 1344/28/28 (`:57-59`) and input paths (`:52-54`) |
| `ida_packet_source_handlers.py`, `_batch005_`, `_batch007_`, `_batch008_handlers.py` | 2/9/12/12 handler transactions | no | Pinned `MANIFEST_HASH`, target tuples and before digests (`_batch008_:16-18,47-56`): refuse on the current IDB |
| `ida_packet_server_list.py` | Boundary repair of `0x7F9740..0x7F9812` | no | Done |
| `ida_packet_destructors.py` | Repairs 2 deleting destructors | no | Done |
| `ida_packet_peer.py` | 30 peer views plus 9 types | no | Done |
| `ida_packet_send.py` | Send ABI and 4 SP points; restores `sub_824750` | no | Done; propagation side effects (`13-…:450-463`) |
| `ida_packet_strings.py` | 2 string-writer views; shared capture used by batch008 | no | Done |
| `ida_packet_history.py` | Repairs and annotates sender `0x833670` | no | Done |
| `packet_transaction.py` | Guarded apply / partial-failure rollback | pattern | Needs the native undo label; session-bound |
| `packet_catalog.py` | Imports the DDON_RE GamePackets table ("addresses and names are never match authority") | no | Community table only |
| `packet_evidence.py` | PE32 section map, VA→file range hash | **yes** | f1c9 has 122 checksum stubs absent in installed `DDO.exe` (`docs/investigations/06-evidence-workflow.md:15`) |
| `packet_wire.py` | Strict offline schema interpreter | no (pattern-file side) | Partial-failure `decode` vs `decode_strict` (`14-…:120-130`) |
| `packet_schema_batch001-010.py`, `_batch007_writers.py`, `_character.py` | Hand byte recipes → `*.wire.json` | no | Earlier batches' runtime offsets were not audited (T031) |
| `recovery_bindings.py` | Catalog/schema/native-root binding gate | no | Pinned hashes; input paths `:20-24`. Both hashes still match (V: `DDO.exe` `f2a80229…`, IDA9.3 and IDA9.5 dump `f1c974d0…`) |
| `verify_packets.py`, `verify_packet_checkpoint.py`, `verify_packet_batch008/009/010.py`, `verify_packet_history.py` | Re-verify receipts per batch | no | Checkpoint verifier keeps historical counts (`13-…:555-558`); batch008 must run without `--saved` (`progress.md:66-68`) |

Not run: none of these scripts were executed in this survey.

## 5. Reusable for spec 007

| Fact or table | Quality |
| --- | --- |
| Table format at `0x1BC0110` (74 groups, 24-B stride, cmd +16 u16, sub +18 u8) | V twice: ddon-hook `ida_packet_dispatch.py:14-37` and ddon-data `specs/006-packet-pattern-coverage/research/T001-triage.md:36-42` agree |
| 1,040 callback VAs keyed by group:cmd:sub (`packet-catalog.json` `pc_registration`) | R; literal-copy proof per record. Strong discovery source, no PS4 data |
| Extra registrations 73:0:16, 73:1:16 (absent from DDON_RE); null 15:65535:255 | R (`13-…:59-65`) |
| 50 handlers with PC diagnostic + callback + ABI (ECX, 1 stack arg, `ret 4`, EAX 0/1) | R for ABI; V for callback equality. Usable as positive controls |
| PS4 qualified names and DIEs for those 48 handlers | R (DIEs verified by them); PC↔PS4 mapping inferred |
| Codec VAs `0x8BC410-0x8BCB80`, ABI cdecl vs `CPacketBase::ReadBytes` thiscall `ret 8`, return conventions (`0x8BC710` returns count; `0x8BC5B0` returns 2 on empty) | R (native), names only partly reliable (weak point 1) |
| Send `0x9D6A20` `void __thiscall(self, char*, unsigned)`, `ret 8`, 640 callers | R |
| PC request header: 9 bytes, group u8, cmd BE u16, sub u8, 0 u8, 0 u32 | R (`13-…:394-397`) |
| PS4 class dossier: `cSeedGameSvConnection` class DIE `0x09c0f5cf`, CU `0x09c04fff`, 1,401 members (781 S2C, 569 C2S) | R (`13-…:268-274`) |
| 12 C2S sender VAs ↔ PS4 `Send_C2S_*` (`batch007-writer-method-map.json`) | R structural match; not annotated |

**Overlap with ddon-data `specs/006-packet-pattern-coverage/research/T001-triage.tsv`** (526 rows:
355 matched, 94 exclusive, 77 unresolved; V). The triage covers only captured, uncovered ids, so
the overlap is small:

- 17 annotated handlers share an id. All 17 match the triage PC VA, and the PS4 symbols agree
  (all marked `matched`): `0x7C75E0`, `0x7C76A0`, `0x7C7A40`, `0x7C7AF0`, `0x7C9910`, `0x7F8F30`,
  `0x7F95C0`, `0x7C9CB0`, `0x7E2CE0`, `0x7E8B20`, `0x7E8F30`, `0x7EA9D0`, `0x7EAB80`, `0x7EB9F0`,
  `0x7EBB00`, `0x7EBD40`, `0x7EA870` (V, stdin script over both files).
- Server list 1.0.2 `0x7F9740`: the same VA and PS4 `OnPacket_S2C_GET_SERVER_LIST_RES` (V).
- 6 C2S writers (8.2.1, 8.3.1, 8.8.1, 8.9.1, 8.12.1, 8.28.1 history) share the same VA and PS4 `Send_C2S_*` (V).
- Total: 24 agreements, 0 conflicts. The 31 other annotated handlers and 6 other writers are
  outside the triage's id set. The 005/006 batch reports (`T002`-`T013`) were not cross-read
  per id (not run).

The two methods complement each other. ddon-hook supplies PC-side identity: callback plus
diagnostic plus ABI. ddon-data T001 supplies a PS4-side shape ratio (`T001-triage.md:51-68`),
which ddon-hook never recorded. A no-false-positive method can require both, plus a code-level
check. Neither source alone settles a PS4 identity.

## 6. Missing checks (not run)

- No IDA check that the accepted IDB (`382e346e…`) contains the 107 packet views, the 2 structs or
  the comments described here.
- The lineage `fc1fa220` (006 save) → `717e862d` (root now) → accepted copy is not traced.
- No consumer audit telling `Read_s32` from `Read_u32`, `Read_u8` from `Read_bool`, or `Read_s64`
  from `Read_u64`.
- The evidence for `cSeedGameSvConnection` 1,344 B and `mpManager`@316 was not located.
- I sampled ~10 of the 1,034 / 405 / 11,820 receipt files of specs 006 / 007 / 008. I opened only
  `pc-framework-stage-before.json` and searched a handful by name.
- `08-ida-mcp-runbook.md`, `11-`, `12-` and `32-` were read by heading only.
