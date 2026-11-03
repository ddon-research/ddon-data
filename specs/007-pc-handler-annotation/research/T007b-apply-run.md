# 007 T007b: apply run (PC 03040008) - stopped after the dry run

Build PC 03040008, work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
(input sha256 `f1c974d0...fa20`, header `idb_path` confirmed under `ddon-data-007work`). Base `59bf8e3e9b3`.
2026-11-03 12:28-12:40 (WET). IDA work by `C:/Program Files/IDA Professional 9.5/idat.exe` batch only; ida-mcp
was not used. Addresses are VAs (image base `0x400000`).

**Outcome: stopped at step 2.** The dry run refuses 105 of 189 type rows (55.6%), above the brief's 10% stop
threshold. Steps 3-7 (apply, second apply, verify, re-extract, spot checks) were **not run**. The work copy was
not written; its sha256 is unchanged.

## 1. Rollback point

    sha256sum ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    cp -p ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64 ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.before-T007b.i64

| File | sha256 | bytes |
| --- | --- | --- |
| work copy `.i64` (before) | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 |
| `...exe.before-T007b.i64` | `65120b3498dc5ec40872f7e8748611e7d75e52a3b0bf9387afa6cb408c8b9111` | 111,886,983 |

Equal: verified. The rollback copy stays in place for the rerun.

## 2. Dry run

    T=D:/ddon-data/research/03040008/ida-transfer
    idat -A -L$T/dumps/logs/apply-dryrun.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun.jsonl" $DB
    # rc 0, 11 s

- Output `dumps/apply-dryrun.jsonl`: sha256 `bd500eb50458f63ad44ad6edb2bf09451a795890a968f8dc1735cf483f92fea7`,
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

### 2.1 Refusal reasons (verified from the dump)

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

## 3. Not run

Apply, second apply (idempotence), verify, PC re-extract and comparison, spot checks: **not run** (stop
condition). No `apply.jsonl`, `apply-2.jsonl`, `apply-verify.jsonl`, `pc-ida-applied.jsonl` exist. The `_Ida`
adapter's write path (udt build, `create_typedef`, tinfo serialize) is therefore still untested on a real
database; the read path (precheck, counts, type/name/prototype lookups) ran without error.

## 4. Options for the coordinator (inferred, not decided here)

1. In T006, treat the three as equal-layout types: mark them `replace`, or emit the existing member names
   (`_vptr$MtObject`, unnamed base) so the comparison finds `already`. With `already` the cascade disappears;
   expected dry run then about 185 types written/already and 1,011 prototypes (inferred: the 102 embedding
   structs and 99 prototypes were refused only for these types, but their own checks have not run).
2. Or change `apply_transfer.py`'s layout equality to ignore member names for a vptr at +0 and an unnamed or
   `baseclass_<off>` base member, keeping offsets and sizes strict.
3. `replace` would overwrite the DB's existing `MtObject`/`MtArray`/`CPacketDataBase`, whose origin
   (earlier annotation or IDA) was not checked here; option 1 with the existing names or option 2 leaves them.

Rerun T007b from step 2 after the fix; the rollback copy `...exe.before-T007b.i64` (sha256 above) is in place.
