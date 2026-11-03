# 007 W2 T013d: apply wave 2 (partial layouts, locals) to the work copy (PC 03040008): done, published

Build PC 03040008. Work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
(header `input_sha256` `f1c974d0...fa20`, `idb_path` under `ddon-data-007work`). Base `a1fc7ed612b`,
2026-11-03 19:07-19:34 (WEST). Every IDA run was a `C:/Program Files/IDA Professional 9.5/idat.exe` batch job.
ida-mcp was not used, and neither the original, the accepted database nor the wave-1 snapshot was opened. The
spot-check batch confirms the database: `get_idb_path` is the work copy, `inf_is_64bit` false, image base
`0x400000`. Addresses are VAs. `apply_transfer.py` sha256 `3e1188e1...19b0` (`script_version` 2, c2bbfd18a7).

**Outcome (verified): the apply defined the 48 partial types (formerly forward declarations, each with its
type comment) and named and retyped 23 `packet` locals (R3). 21 wave-1 types were `already`. 1 locals row was
refused: `sendFeedbackList` at `0x87caa0`, `user-name`, the refusal T013c's smoke test reported. There were 0
`current-changed` and 0 `failed`. The second apply finds every row `already` (the same refusal) and writes 0
undo records. Verify gives 69 types `ok`, 23 locals `ok` and `counts_ok: true`. The work copy is published as
`spec007-packet-handlers-20261103-wave2/` (sha256 equal).**

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"

Manifest `manifest/transfer/wave2/` (header `manifest_sha256`, the same in all four dumps): types.tsv
`f694129d...2cce8`, locals.tsv `ac24e03f...228ab`, types.h `3e60a9dc...89d18`. The header names inputs pc-ida
`f1c974d0...fa20`, ps4-dwarf/ps4-ida `4236f598...63c0` and wave-1 types.tsv `878c53c6...c280`. `filter` null:
the run used no `--limit-*`.

## 1. Rollback copy (verified)

    sha256sum ...exe.i64                 # f7f3a2198cf511ba495d0305a7d7381d6a4cf0b4cbc9d905352fc28a7d3e3c25 (= brief)
    cp -p ...exe.i64 ...exe.before-W2.i64
    sha256sum ...exe.before-W2.i64       # f7f3a219...3c25, 112,373,500 bytes, mtime 14:00:18

After the hashes matched, `...exe.before-T009c.i64` was deleted. The folder now holds only `...exe.i64` and
`...exe.before-W2.i64`. The rollback copy was opened once more by a read-only batch (`DBFL_KILL`, § 4.4). Its
sha256 afterwards is still `f7f3a219...3c25`.

## 2. Commands, counts and hashes

    "$IDAT" -A -L$T/dumps/logs/apply-dryrun-w2.log  "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-dryrun-w2.jsonl" $DB            # 19:07, rc 0, 6 s
    "$IDAT" -A -L$T/dumps/logs/apply-w2.log         "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-w2.jsonl --apply" $DB          # 19:08, rc 0, 8 s
    "$IDAT" -A -L$T/dumps/logs/apply-w2-2.log       "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-w2-2.jsonl --apply" $DB        # 19:08, rc 0
    "$IDAT" -A -L$T/dumps/logs/apply-verify-w2.log  "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-verify-w2.jsonl --verify --apply-log $T/dumps/apply-w2.jsonl" $DB  # rc 0

The counts come from `jq -c 'select(.kind=="result")|[.step,.status]' <dump> | sort | uniq -c`:

| Kind | dry run | apply | second apply | verify |
| --- | --- | --- | --- | --- |
| types: 48 partial | 48 would-define | 48 defined | 48 already | 48 ok |
| types: 21 embedded wave-1 (`MtArray`, 20 `MtTypedArray<...>`) | 21 already | 21 already | 21 already | 21 ok |
| locals: 24 accepted rows (23 R3, 1 R1) | 23 would-set, 1 refused | 23 set, 1 refused | 23 already, 1 refused | 23 ok |
| current-changed / failed / mismatch | 0 | 0 | 0 | 0 |
| undo records | | 71 (48 types + 23 locals) | 0 | |

### 2.1 Dry-run check (verified with jq)

- The set of `would-define` keys equals the set of the 48 `partial` rows in `types.tsv`: `comm -3` prints 0
  lines. Every `already` type is a wave-1 type that the partial types embed. No type would be created from
  nothing, and nothing other than types and locals would be written. A wave-2 manifest has no name, prototype
  or comment rows. The comment of each type is written as its type comment in the define step: each `defined`
  record carries `comment` and `comment_error: null`.
- The 23 `would-set` locals are exactly the 23 accepted R3 rows of `locals.tsv`. Each names the local `packet`
  and retypes it to its `nUserSession::CPacket_S2C_*_RES`. None of the previous lvars has a user name or a user
  type.
- The one refusal: `0x87caa0@-20` (`cNetGameServer::returnRentedPawn`), rule R1, name `sendFeedbackList`,
  check `user-name`. The lvar there is `in_PawnFeedbackList`, `struct MtTypedArray<CDataPawnFeedback>`, width 20,
  `user_name: true`, `user_type: false`. This is the refusal T013c's smoke test reported (README § Apply script),
  so it is the expected `user-name` case. There is no other refusal.

### 2.2 Counts record (verify)

before = after = expected = 965 local types / 52,148 user names / 1,464 typed functions. The applied delta is
0/0/0 and `ok: true`. Defining a forward declaration reuses its ordinal, and lvar settings are not function
types, so no count changes.

### 2.3 Work copy sha256 at each step

| Step | sha256 | bytes | mtime |
| --- | --- | ---: | --- |
| start (= `.before-W2.i64`) | `f7f3a2198cf511ba495d0305a7d7381d6a4cf0b4cbc9d905352fc28a7d3e3c25` | 112,373,500 | 14:00:18 |
| after the dry run (`DBFL_KILL`) | `f7f3a219...3c25` (hashed again at 19:08:16, before the apply) | | |
| after the apply | `6f927dc3b66c0750e8ba2e99d00dbe2dbce5f5a6793c6ec2127ba43ea4f4e2bb` | 112,457,493 | 19:08:24 |
| after the second apply (re-saved by `qexit(0)`, 0 writes) | `80b0908695012e5d5dffc5bc5608ef102a4aaa697473c8f823dc51da63622bc7` | 112,432,870 | 19:08:40 |
| after verify and the spot-check batches (each `DBFL_KILL`) | `80b09086...2bc7` | 112,432,870 | 19:08:40 |

As in T007e and T009c, the second apply changes the hash although it writes nothing. Inferred: `qexit(0)`
re-saves and repacks the database.

| Dump (`$T/dumps/`) | sha256 | lines |
| --- | --- | ---: |
| `apply-dryrun-w2.jsonl` | `02ea9499f39d6f083dde2cc550c562feb93274963beb12d4e9267d85c9a983e6` | 95 |
| `apply-w2.jsonl` | `221eed3e45b13e0f1a37abd2a29e402e5882437771d4ee6c73e77b24a444c4fd` | 166 |
| `apply-w2-2.jsonl` | `f71c5bb1e283aa091da0a483a719d3f8fff226d9d8a53e6b86aeca56732d54f9` | 95 |
| `apply-verify-w2.jsonl` | `b44ea9d04f3b3d25cc12c80aa6dcb91aa706485dc80486f707dc4fb7c40bd852` | 95 |

Logs: `dumps/logs/{apply-dryrun-w2,apply-w2,apply-w2-2,apply-verify-w2}.log`. `rg -ci
"unpacked|restore|traceback"` finds 0 matches in each. `dumps/MANIFEST.tsv` was regenerated with
`uv run python manifest.py` (rc 0). The diff adds exactly the 4 rows above and changes no other row.

## 3. Decompilation of every typed function (verified, with one gap explained)

A wave-2 manifest has no prototype rows, so `--verify` decompiles only the 23 locals functions, through its
read-back. To cover "every typed function decompiles", a read-only batch
(`<scratchpad>/spot_w2.py`, `DBFL_KILL`, rc 0, 19:09-19:33) decompiled every function for which
`ida_nalt.get_tinfo` returns a type. That is 141,608 functions, guessed types included, so it is a superset of
the 1,464 user-typed functions. 141,589 decompile. 19 fail: `0x407a00`, `0xac1550`, `0xac15b0`, `0xb1d0f0`,
`0xd37080`, `0x10432a0`, `0x15ce8d0`, `0x16874e0`, `0x19a8728`, `0x19a87e0`, `0x19a89c8`, `0x19a8b08`,
`0x19a8cc8`, `0x19a8e18`, `0x19a8ecd`, `0x19a8f70`, `0x19ba310`, `0x19bb319`, `0x36cad4b`. All are unnamed
`sub_*` functions without a wave-1 or wave-2 row.

A second read-only batch (`fail19.py`) decompiled these 19 on the work copy and on `.before-W2.i64`. The output is
identical on both. 16 fail with `call analysis failed`, and 3 decompile when run alone (`0xb1d0f0`, `0x15ce8d0`,
`0x36cad4b`). Verified: wave 2 introduced none of these failures. Inferred: the 3 that fail only in the sweep
fail because of the sweep's order.

The same batch found 48 functions whose prototype has a pointer argument to a partial type: 6 element readers
`nPacket::Read_CData*_` (`d`) and 42 `CPacket_S2C_*_RES::ReadPacket` (`this`). Each of the 48 partial types
exists as a fixed-layout udt; their sizes match `types.tsv` `pc_size` (for example CHANGE_JOB_RES `0xc4`,
GET_GP_RES `0x32`).

## 4. Spot checks (read-only batch, pseudocode excerpts)

### 4.1 Handlers with a renamed and retyped `packet` local (verified)

**`0x7d0d30`** `cSeedGameSvConnection::OnPacket_CRAFT_RECIPE_GET_CRAFT_GRADEUP_RECIPE_RES`: the lvar is
`packet : struct nUserSession::CPacket_S2C_GET_CRAFT_GRADEUP_RECIPE_RES`, user name and type, stkoff 24. Its
only linked member is not touched in the handler, so all accesses are `gap0`:

    struct nUserSession::CPacket_S2C_GET_CRAFT_GRADEUP_RECIPE_RES packet; // [esp+4h] [ebp-48h] BYREF
    if ( nUserSession::CPacket_S2C_GET_CRAFT_GRADEUP_RECIPE_RES::ReadPacket(this: &packet, pPacket) != 0 )
      v4 = *(_DWORD *)&packet.gap0[20];
        *(_DWORD *)(sub_B38670(this: sGamePointer_1, n4: 1, a3: packet.gap0[24]) + 8) = 3;

**`0x7d73b0`** `cSeedGameSvConnection::OnPacket_GP_GET_GP_RES`: the members appear by name.

    struct nUserSession::CPacket_S2C_GET_GP_RES packet; // [esp+4h] [ebp-38h] BYREF
    char v6; // [esp+36h] [ebp-6h]
    memset(&packet.m_llUseLimit, 0, 18);
        *((_DWORD *)this->mpManager + 10169) = packet.m_unGP;
        sub_B9F1A0(this: (int)sItemManagerPointer, a2: packet.m_llUseLimit, a3: SHIDWORD(packet.m_llUseLimit));
        sub_BB3E90(this: (int)::this, a2: packet.m_ullRealTime, a3: SHIDWORD(packet.m_ullRealTime), a4: packet.m_usMilliseconds);

**`0x7f8f30`** `cSeedGameSvConnection::OnPacket_SERVER_GAME_TIME_GET_BASEINFO_RES`: the arrays and the scalar
appear by name.

    struct nUserSession::CPacket_S2C_GAME_TIME_GET_BASEINFO_RES packet; // [esp+8h] [ebp-98h] BYREF
      if ( v4 + 14 != (unsigned int *)&packet.m_WeatherLoop )
        if ( v4[16] < packet.m_WeatherLoop.mLength )
      if ( v4 + 19 != (unsigned int *)&packet.m_WeatherSchedule )
      v4[24] = packet.m_unMoonAgeLoopSec;
      if ( v4[27] < packet.m_MoonSchedule.mLength )

### 4.2 Readers whose object argument now has a partial type (verified)

**`0x769030`** `nPacket::Read_CDataGameTimeBaseInfo_(CPacket *packet, CDataGameTimeBaseInfo *d)`: all 10
codec reads land on named members.

    return nPacket::Read_u32(packet, value: &d->m_unGameTimeOneDayMin) != 0
        && nPacket::Read_u32(packet, value: &d->m_unGameTimeYearMonth) != 0
        ...
        && nPacket::Read_s64(packet, value: (unsigned __int64 *)&d->m_llOriginalRealTimeSec) != 0
        && nPacket::Read_u32(packet, value: &d->m_unOriginalMoonAge) != 0;

**`0x808f70`** `nUserSession::CPacket_S2C_GET_GP_RES::ReadPacket`:

    || nPacket::Read_u32(packet: pPacket, value: &this->m_unGP) == 0
    || nPacket::Read_s64(packet: pPacket, value: (unsigned __int64 *)&this->m_llUseLimit) == 0
    || nPacket::Read_u64(packet: pPacket, value: &this->m_ullRealTime) == 0
    || nPacket::Read_u16(packet: pPacket, value: &this->m_usMilliseconds) == 0 )
    *((_BYTE *)this + 50) = 1;

### 4.3 `0x80cf80` CHANGE_JOB_RES (verified: partial, as the manifest says)

`types.tsv` line 12: `nUserSession::CPacket_S2C_CHANGE_JOB_RES`, partial, `0xc4` lower bound, 1 member
(`m_EquipJobItemList` at `0xb0`, `MtTypedArray<CDataEquipJobItem>`, link anchor `0x80d034`). The locals row of
its handler `0x7de910` is refused in the manifest ("PC argument value not recorded"), so the handler's local
was not touched. Pseudocode of the reader:

    int __thiscall nUserSession::CPacket_S2C_CHANGE_JOB_RES::ReadPacket(
            struct nUserSession::CPacket_S2C_CHANGE_JOB_RES *this, CPacket *pPacket)
        || nPacket::Read_CDataS2CCharacterEquipInfo_(packet: pPacket, ar: (struct MtTypedArray<CDataS2CCharacterEquipInfo> *)&this->gap0[96]) == 0
        || nPacket::Read_CDataEquipJobItem_(packet: pPacket, ar: &this->m_EquipJobItemList) == 0
        || sub_7732A0(CPacket: pPacket, a2: (int)(this + 1)) == 0
        || sub_765F70(packet: pPacket, a2: (int)this + 208) == 0 )
      *((_BYTE *)this + 236) = 1;

### 4.4 R1/R2 locals: only one in the manifest, and it is refused (verified)

`locals.tsv` has 24 accepted rows: 23 R3 and 1 R1. It has no accepted R2 row. So the brief's "2 R1/R2 locals"
cannot be met, and the one R1 row is the expected refusal. **`0x87caa0`** `cNetGameServer::returnRentedPawn`
is unchanged. Its local keeps the earlier user name, with no user type:

    struct MtTypedArray<CDataPawnFeedback> in_PawnFeedbackList; // [esp+Ch] [ebp-14h] BYREF
    in_PawnFeedbackList._vptr$MtObject = (int (**)())&off_1BC1464;
    in_PawnFeedbackList.mLength = 0;

## 5. Observations for review (not stops)

- **Lower-bound sizes are visibly short.** Observed: the readers of CHANGE_JOB_RES (`0x80cf80`) and GET_GP_RES
  (`0x808f70`) write past the declared size. `this + 1` is `+0xc4`; `+208`, `+236` and `+50` lie beyond
  `0xc4`/`0x32`. In the GET_GP handler, the byte after `packet` shows as a separate lvar `v6` at `ebp-6h`
  (`packet` at `ebp-38h` + `0x32`). This is consistent with `size_kind: lower bound` (end of the last linked
  member). Inferred: a size taken from the ReadPacket's highest write (for example `+0xed` for CHANGE_JOB_RES,
  `+0x33` for GET_GP_RES) or from the constructor would remove the `this + 1` and split-lvar artefacts. That is a
  manifest decision for a later task, not an apply failure.
- The 19 decompile failures in § 3 come before wave 2 and are not related to it.

## 6. Published copy (verified)

    mkdir PC_DDON_03040008/spec007-packet-handlers-20261103-wave2
    cp -p ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64 spec007-packet-handlers-20261103-wave2/

Published copy sha256 `80b0908695012e5d5dffc5bc5608ef102a4aaa697473c8f823dc51da63622bc7`, 112,432,870 bytes,
mtime 19:08:40. This equals the work copy. The wave-1 snapshot `spec007-packet-handlers-20261103-wave1/` was not
touched.
