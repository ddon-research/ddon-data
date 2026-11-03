# 007 T007b: apply run (PC 03040008) - first run stopped after the dry run; rerun stopped after the apply (restored)

Build PC 03040008, work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
(input sha256 `f1c974d0...fa20`, header `idb_path` confirmed under `ddon-data-007work`). First run base
`59bf8e3e9b3`, 2026-11-03 12:28-12:40 (WET); rerun base `4f9926d22e`, 2026-11-03 12:34-12:38 (WEST). IDA work by
`C:/Program Files/IDA Professional 9.5/idat.exe` batch only; ida-mcp was not used. Addresses are VAs (image base
`0x400000`).

**Rerun outcome (after T007c `c91df1e373`): stopped at step 3, work copy restored.** The dry run is clean
(0 refusals in every kind). The apply writes every row, but 171 prototype read-backs come back `failed`. In
every one of them, IDA prints `struct ` in front of a type name that contains `::` or `<...>`, and the row's
text does not have it. The diagnostic batch shows the types resolve to the intended local types. The brief says
to restore on any `failed` row, so the rollback copy was copied back (sha256 `65120b34...8b9111` again). Steps
4-7 were not run. Section "Rerun".

**First-run outcome: stopped at step 2.** The dry run refuses 105 of 189 type rows (55.6%), above the brief's 10% stop
threshold. Steps 3-7 (apply, second apply, verify, re-extract, spot checks) were **not run**. The work copy was
not written; its sha256 is unchanged.

## First run (base 59bf8e3e9b3)

### 1. Rollback point

    sha256sum ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    cp -p ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64 ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64

| File | sha256 | bytes |
| --- | --- | --- |
| work copy `.i64` (before) | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 |
| `...exe.before-T007b.i64` | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 |

Equal: verified. The rollback copy stays in place for the rerun.

### 2. Dry run

    T=D:/ddon-data/research/03040008/ida-transfer
    idat -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # rc 0, 11 s

- Output `dumps/apply-dryrun.jsonl` (the rerun renamed it `dumps/apply-dryrun.run1.jsonl` and its log
  `logs/apply-dryrun.run1.log`): sha256 `bd500eb50458f63ad44ad6edb2bf09451a795890a968f8dc1735cf483f92fea7`,
  3,464 lines (header, 3,462 results, summary); row added to `dumps/MANIFEST.tsv` (`uv run python manifest.py`;
  the three dump rows unchanged).
- Manifest inputs (header `manifest_sha256`): names `7f4e8c21...`, prototypes `b2909484...`, comments `596891df...`,
  types.tsv `fdcf08f7...`, types.h `ddad9dfb...`, skipped `c17db87b...`. No parse failure.
- Work copy after: sha256 `65120b34...8b9111` (unchanged), mtime 10:03 (unchanged); log has no
  "unpacked"/"restore" prompt; no unpacked files beside the `.i64`.
- Counts before (header) = counts after (dry run): local types 788, user names 51,074, typed functions 453.

| Kind | Would write | Already | Refused | Refused % | Other |
| --- | ---: | ---: | ---: | ---: | --- |
| types | 80 (declare) | 4 | **105** | **55.6%** | |
| remove-label | 3 | | 0 | 0% | |
| names | 1,079 | | 0 | 0% | |
| prototypes | 912 | | 99 | 9.8% | |
| comments | 1,119 | | 0 | 0% | |
| conflict-names | | | | | 7 reported, not written |
| conflict-prototypes | | | | | 54 reported, not written |

`already` types: `CPacket`, `MtString`, `MtString::STRING`, `cSeedGameSvConnection`.

#### 2.1 Refusal reasons (verified from the dump)

| Step | check | count |
| --- | --- | ---: |
| types | `different-local-type` | 3 |
| types | `embeds-refused-type` | 102 |
| prototypes | `uses-refused-type` | 99 |

The three root refusals are local types that already exist in the work copy with the **same size and the same
member offsets and sizes**; only member names differ (`existing` vs `row`, from the dump):

| Type (types.tsv status) | Existing in DB | Row (types.h) | Difference |
| --- | --- | --- | --- |
| `MtObject` (accepted) | size 4: `_vptr$MtObject` +0 4 | size 4: `__vftable` +0 4 | vptr member name |
| `CPacketDataBase` (embedded) | size 4: `""` +0 4 | size 4: `baseclass_0` +0 4 | base member unnamed in DB |
| `MtArray` (embedded) | size 20: `""` +0 4, `mLength` +4 4, `mBufsiz` +8 4, `mAutoDelete` +12 1, `mpArray` +16 4 | size 20: `baseclass_0` +0 4, same four, gap `gapD` +13 3 | base member unnamed in DB (gap not compared) |

The cascade (`embeds-refused-type` names the refused type each struct embeds; a struct can name several):
`MtArray` 92, `CPacketDataBase` 10, `CDataCharacterName` 2, five `MtTypedArray<...>` and
`CDataCommunityCharacterBaseInfo`, `CDataCharacterJobData` 1 each. All 99 prototype refusals name a refused
type (mostly `MtTypedArray<CDataX>` element readers, e.g. `0x758100` `MtTypedArray<CDataAbilityLevelParam>`,
plus `nUserSession::CPacket_S2C_CHANGE_JOB_RES`). So all 204 refusals trace back to these three name-only
differences (verified: every `embeds`/`uses` record lists only types in the refused set).

The apply script behaves as README § "Apply script" specifies (equal layout = size and non-gap members'
name/offset/size; different -> refused unless `types.tsv` status is `replace`); none of the three rows is
`replace`. This is not a script fault.

### 3. Not run

Apply, second apply (idempotence), verify, PC re-extract and comparison, spot checks: **not run** (stop
condition). No `apply.jsonl`, `apply-2.jsonl`, `apply-verify.jsonl`, `pc-ida-applied.jsonl` exist. The `_Ida`
adapter's write path (udt build, `create_typedef`, tinfo serialize) is therefore still untested on a real
database; the read path (precheck, counts, type/name/prototype lookups) ran without error.

### 4. Options for the coordinator (inferred, not decided here)

1. In T006, treat the three as equal-layout types: mark them `replace`, or emit the existing member names
   (`_vptr$MtObject`, unnamed base) so the comparison finds `already`. With `already` the cascade disappears;
   expected dry run then about 185 types written/already and 1,011 prototypes (inferred: the 102 embedding
   structs and 99 prototypes were refused only for these types, but their own checks have not run).
2. Or change `apply_transfer.py`'s layout equality to ignore member names for a vptr at +0 and an unnamed or
   `baseclass_<off>` base member, keeping offsets and sizes strict.
3. `replace` would overwrite the DB's existing `MtObject`/`MtArray`/`CPacketDataBase`, whose origin
   (earlier annotation or IDA) was not checked here; option 1 with the existing names or option 2 leaves them.

Rerun T007b from step 2 after the fix; the rollback copy `...exe.before-T007b.i64` (sha256 above) is in place.

## Rerun (base 4f9926d22e, after T007c c91df1e373)

Same work copy, same `idat.exe`, batch only; ida-mcp not used. `apply_transfer.py` script version 1 as of
`4f9926d22e` (with T007c's `same_layout`). Manifest inputs unchanged: the header `manifest_sha256` values equal
the first run's (names `7f4e8c21...`, prototypes `b2909484...`, comments `596891df...`, types.tsv `fdcf08f7...`,
types.h `ddad9dfb...`, skipped `c17db87b...`).

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"

### R1. Rollback point (not copied again)

    sha256sum ddon-data-007work/*.i64

`2022_01_29_DDO_DUMP_FIX.exe.i64` and `...exe.before-T007b.i64`: both
`65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111`, 111,886,983 bytes, mtime 10:03. Verified.

### R2. Dry run (clean)

    mv dumps/apply-dryrun.jsonl dumps/apply-dryrun.run1.jsonl; mv dumps/logs/apply-dryrun.log dumps/logs/apply-dryrun.run1.log
    "$IDAT" -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # rc 0, 10 s

- `dumps/apply-dryrun.jsonl`: sha256 `5d25d04d14304d7f170f203c03c6ec1badf78adbed9a0b7572eb071357332523`, 3,464
  lines (header, 3,462 results, summary). No parse failure. The log has no error or traceback and no
  "unpacked"/"restore" prompt.
- Work copy after: sha256 `65120b34...8b9111`, mtime 10:03 (unchanged). Counts before = after: local types 788,
  user names 51,074, typed functions 453.

| Kind | Would write | Already | Refused | Other |
| --- | ---: | ---: | ---: | --- |
| types | 182 (80 declare, 102 define) | 7 | 0 | |
| remove-label | 3 | | 0 | |
| names | 1,079 (1,077 `set`, 2 `correct`) | | 0 | |
| prototypes | 1,011 | | 0 | |
| comments | 1,119 | | 0 | |
| conflict-names / conflict-prototypes | | | | 7 / 54 reported, not written |

`already` types: `CPacket`, `MtString`, `MtString::STRING` and `cSeedGameSvConnection`, as in the first run,
plus `MtObject`, `CPacketDataBase` and `MtArray`. Under T007c's rule the three first-run refusals now count as
equal. The 2 `correct` names are `0x7c61f0` (DB
`cSeedGameSvConnection::OnPacket_S2C_BAZAAR_GET_EXHIBIT_POSSIBLE_NUM_RES`) and `0x7c6510` (DB
`...::OnPacket_S2C_BAZAAR_GET_ITEM_PRICE_LIMIT_RES`). The first run's inferred expectation (about 185 types,
1,011 prototypes) is now verified as 189 types and 1,011 prototypes.

### R3. Apply: 171 prototype read-back failures, work copy restored

    "$IDAT" -A -L$T/dumps/logs/apply.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply.jsonl --apply" $DB
    # rc 0, 14 s

- `dumps/apply.jsonl`: sha256 `1addfb6c5fd8c1431aaebdc78706cb9a9389b3fc4e27d0d4c1dcb0393697eb99`, 6,858 lines
  (header, 3,462 results, 3,394 undo records, summary). No `.tmp` file is left. The log has no error or
  traceback and no "unpacked"/"restore" prompt; it ends with "Flushing buffers, please wait...ok" (saved).
- Work copy after: sha256 `7d92c177c7a7d844c1eee11b0c77453559e791dbc912af841b74a02d533c9dfe`, 112,332,011 bytes,
  mtime 12:35; no unpacked files beside it.
- Counts before -> after (header / summary): local types 788 -> 970, +182 (80 declared plus 102 defined). Names
  51,074 -> 52,148, +1,074 (1,077 `set` on default names minus 3 removed labels). Typed functions 453 -> 1,464,
  +1,011 (every prototype was applied, the failed rows included).

| Kind | written | already | refused | failed |
| --- | ---: | ---: | ---: | ---: |
| types | 182 (80 declared, 102 defined) | 7 | 0 | 0 |
| remove-label | 3 | | 0 | 0 |
| names | 1,079 | | 0 | 0 |
| prototypes | 840 | | 0 | **171** |
| comments | 1,119 | | 0 | 0 |

**The failing calls.** All 171 records have `check: read-back` and `applied: true`. So
`apply_tinfo(ea, tif, TINFO_DEFINITE)` returned true, and then `idc.get_type(ea)` differed from the row under
`norm`, which only collapses whitespace (`apply_transfer.py` line 271 and lines 548-553). No exception and no
other error text. Examples from the dump:

| VA | `db` (`idc.get_type` read-back) | `row` (`prototypes.tsv` `decl`) |
| --- | --- | --- |
| `0x758100` | `int __cdecl(CPacket *packet, struct MtTypedArray<CDataAbilityLevelParam> *ar)` | `int __cdecl(CPacket *packet, MtTypedArray<CDataAbilityLevelParam> *ar)` |
| `0x7ffaf0` | `int __thiscall(struct nUserSession::CPacket_S2C_AREA_RANK_UP_RES *this, CPacket *pPacket)` | the same without `struct ` |
| `0x87caa0` | `bool __thiscall(cNetGameServer *this, int slotNo, struct nNet::stPawnFeedback *feedback)` | the same without `struct ` |

Full list: `jq -c 'select(.status=="failed")' dumps/apply.jsonl` (from `0x758100` to `0x87caa0`).

Classification (verified with jq over `dumps/apply.jsonl` and `manifest/transfer/prototypes.tsv`):

- In all 171 records, `db` with `struct ` deleted and whitespace collapsed equals `row` exactly. Each `db`
  contains `struct ` exactly once. The names it precedes: 101 `MtTypedArray<...>`, 69
  `nUserSession::CPacket_S2C_*_RES`, 1 `nNet::stPawnFeedback`.
- `prototypes.tsv` has 171 rows whose `decl` contains `::` or `<`, and they are exactly the failed rows. None
  of the 840 `set` rows contains either.
- `parse_prototype` patches these rows through `_ref`: `create_typedef(til, name, BTF_STRUCT, True)`, then
  `create_ptr`. When the name is not a plain C identifier, IDA prints the reference with a `struct ` keyword.
  Plain names print without it: `cNetGameServer *`, for example, is a forward declaration (ordinal 799) and has
  no `struct `. (Inferred from these read-backs; the IDA printer source was not read.)

Before the restore, a read-only diagnostic batch ran on the applied copy (`diag.py` in the scratchpad
`C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/`; it
ends with `DBFL_KILL` and `qexit(0)`). The copy's sha256 afterwards was still `7d92c177...9dfe`, mtime 12:35.
Results for 4 failed VAs:

| VA | argument | pointed type resolves to | local type |
| --- | --- | --- | --- |
| `0x758100` | `ar` | `MtTypedArray<CDataAbilityLevelParam>`, udt, size 20 | ordinal 878, size 20 |
| `0x7ffaf0` | `this` | `nUserSession::CPacket_S2C_AREA_RANK_UP_RES`, forward decl | ordinal 802 |
| `0x80d170` | `this` | `nUserSession::CPacket_S2C_CHANGE_PAWN_JOB_RES`, forward decl | ordinal 804 |
| `0x87caa0` | `feedback` | `nNet::stPawnFeedback`, forward decl | ordinal 800 |

All four decompiled without error, with the transferred name, the argument names and the PS4 comment, for
example:

    // PS4 02020005: nPacket::Read<CDataAbilityLevelParam> (_ZN7nPacket4ReadI22CDataAbilityLevelParamEEiR7CPacketR12MtTypedArrayIT_E); paired by element-reader.
    int __cdecl nPacket::Read_CDataAbilityLevelParam_(CPacket *packet, struct MtTypedArray<CDataAbilityLevelParam> *ar)

The writes are the intended types: verified for these 4, and inferred for the other 167 because they follow the
same pattern. What fails is the read-back comparison, which does not accept IDA's `struct ` keyword as equal.
The brief says: "if any write `failed` ... restore ... do not edit the script". So:

    cp -p ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64 ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    sha256sum ddon-data-007work/*.i64     # 12:37

Both files: `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111`, 111,886,983 bytes, mtime 10:03.
Restore verified. `dumps/apply.jsonl` therefore records a database state that no longer exists. Its undo
records were not used, because copying the file back was the rollback.

### R4. Not run

Steps 4-7 were **not run** because the stop condition fired: second apply, verify, PC re-extract with
comparison, spot checks. No `apply-2.jsonl`, `apply-verify.jsonl` or `pc-ida-applied.jsonl` exists.

The `_Ida` write path did run on a real database for the first time. The udt build, `create_forward_decl`,
`create_typedef`, `set_named_type`, the name and comment writes and the tinfo serialize for undo raised no
errors. Their read-backs matched: types 182, names 1,082 (including the 3 removed labels), comments 1,119,
prototypes 840.

`dumps/MANIFEST.tsv` was regenerated (`uv run python manifest.py`). It has rows for `apply-dryrun.jsonl`
(rerun), `apply-dryrun.run1.jsonl` (first run, `bd500eb5...`) and `apply.jsonl`; the other rows are unchanged.

### R5. Options for the coordinator (inferred, not decided here)

1. Fix the prototype comparison in `apply_transfer.py`: drop a `struct `/`union `/`enum ` keyword before a type
   name before comparing, or compare the applied tinfo with the parsed one (`tinfo_t.compare_with`, or
   serialized equality) instead of the printed text. The fix has to reach three places that use the same
   `norm` text comparison (read from the code; not run):
   - the read-back (line 550);
   - the second `--apply`'s `already` check (line 518), where these 171 rows would be user-typed but unequal
     and therefore `refused` as `user-prototype` (line 528);
   - `--verify` (line 678), which would report them as `mismatch`.
2. Or have T006 write `struct ` into `decl` for `::`/`<...>` names. That changes the manifest and its hashes.
3. Then rerun T007b from step 3; the dry run does not depend on this comparison. The rollback copy is in place
   and equals the work copy.
