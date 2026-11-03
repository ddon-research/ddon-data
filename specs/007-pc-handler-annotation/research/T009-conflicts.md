# 007 T009: the 61 conflicts with the earlier annotations (PC 03040008 <- PS4 02020005)

Base `085fcd7d1c`, 2026-11-03 13:44-14:00 (WEST). Addresses are IDA VAs. Marks: **V** verified here in IDA,
**I** inferred, **C** contradicted. Decisions per row: `T009-decisions.tsv` (61 rows: 7 names, 54
prototypes; columns kind, pc_va, current, ours, decision, final_value, evidence_vas, reason; sha256
`1f47a283...bc09`).

## 0. Answer

- **All 61 rows: `ours`.** None is `theirs`, `merge` or `undecided`.
- 7 names: the earlier names mix the two naming schemes.
  - PC handler strings are `OnPacket_<GROUP>_<PS4 packet name>`. Examples: PS4 `OnPacket_S2C_STAY_INN_RES`
    is PC `OnPacket_INN_STAY_INN_RES`, and PS4 `OnPacket_S2C_ENTRY_BOARD_ITEM_LIST_RES` is PC
    `OnPacket_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES` (V).
  - Five earlier names copy that PC group prefix into a PS4-style `Send_C2S_*` or `CPacket_S2C_*` name:
    `ACHIEVEMENT_ACHIEVEMENT_`, `GP_GP_`, `GP_GET_CAP`, `MY_ROOM_MY_ROOM_`. No PS4 symbol is spelled that
    way (C). One more (`Send_PAWN_GET_PAWN_HISTORY_LIST_REQ`) has no class and no PS4 spelling.
  - `0x7DA410` is the reverse case. Its current name is the PS4 symbol. Ours repeats the PC string the
    handler references, byte for byte (V).
- 54 prototypes:
  - **50** handler rows differ only in parameter names: `self`/`packet` against the DWARF `this`/`pPacket`.
    The types are identical. They are exactly T002's 50 audited handlers (ecx `this`, `ret 4`; V there).
  - **2** current prototypes are physically wrong (C): `0x8320B0` and `0x87B140` are declared
    `__fastcall`. Both read `this` from ecx, never read edx, and end with `retn 8`.
  - **2** current prototypes are only less specific: `0x7D3880` (`MtObject *this`, `BOOL`) and `0x833670`
    (`void *self`, `unknown_u32`).
- Step 0: the dry run matches expectation. **Verify did not run**: the script refused, because the
  manifest changed after `apply.jsonl` (section 1).

## 1. Step 0: read-only check of the work copy

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"
    "$IDAT" -A -L<scratch>/apply-dryrun-t009.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun-t009.jsonl" $DB   # 13:44, rc 0
    "$IDAT" -A -L<scratch>/apply-verify-t009.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-verify-t009.jsonl --verify --apply-log $T/dumps/apply.jsonl" $DB   # 13:44, rc 1

- `apply_transfer.py` sha256 `dd1d80e6...d7376` (head `733a4c77e6`).
- Work copy sha256 `be0cc624fdb38deaa646de2ecea04fbf8d5297d8d37cf164ca4a61310aee162f`, the same before,
  between and after both runs. Bytes 112,370,180; mtime 13:17 (V).
- The logs are in the session scratchpad, not in `dumps/logs/`.

**Dry run** `dumps/apply-dryrun-t009.jsonl`: sha256 `7925508a88e9239316029150ce4d623de597d8e4cf2ffc6214ff2e96f71684df`,
3,456 lines. Counts come from `jq -r 'select(.kind=="result")|[.step,.status]|@tsv' | sort | uniq -c`:

| step | status | count |
| --- | --- | ---: |
| types | already | 181 (`MtArray` included, now compared by member type) |
| names | already | 1,079 |
| remove-label | already | 3 |
| prototypes | already | 1,011 |
| comments | already | 1,119 |
| conflict-names | conflict | 7 |
| conflict-prototypes | conflict | 54 |

- Every row that would be written is `already`. There is no non-`already` row to report.
- The 61 conflict records equal those in `apply.jsonl`. I checked this with `diff` of the conflict rows
  with the timestamp removed: they are identical.

**Verify: not run (refused).** `run_verify` raised `ValueError: apply log was written from other manifest
files` and wrote no output. I removed the empty `apply-verify-t009.jsonl.tmp` that the run left.

- Cause (V): the `manifest_sha256` in the `apply.jsonl` header has `types.h` `39864eaf...`. The current
  `types.h` is `b70c311a...`, changed by `733a4c77e6` (T008 F1: `MtArray.mpArray` rendered as
  `MtObject **`). The other five manifest hashes are equal.
- The dry run already shows `types: already 181` against the new `types.h`, so the database content
  agrees.
- To run verify, someone has to supply an apply log that carries the current manifest hashes, for
  example a fresh `--apply` on this copy (its rows would all be `already`), or relax the check. I did
  neither. This is the coordinator's decision.

## 2. Databases for the conflict research

- **PC 03040008**: `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t009/2022_01_29_DDO_DUMP_FIX.exe.i64`,
  made with `bash research/ida/private-copy.sh pc-accepted t009`.
  - `.i64` sha256 `382e346e...a58c0f`, equal to `accepted_PC.sha256` in `CURRENT-RECOVERY.json` (V).
  - 32-bit, image base `0x400000`. ida-mcp instance `1ff1ca044d2a`.
- **PS4 02020005**: `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t009/DDOORBIS.elf.i64`,
  made with `private-copy.sh ps4 t009`.
  - 64-bit, image base `0`. Instance `6b162142a927`.
  - The PS4 types quoted below are the IDA types that the DWARF import set.
- Read-only: no rename, retype, comment, patch or reanalysis, and no save. The `ddon-data-007work` copy was
  never opened in ida-mcp.
- Pair and key cross-checks: `manifest/pairs.tsv` (all 10 distinct VAs are `accepted`) and
  `manifest/crosscheck.tsv` (6 `agree`).

## 3. Names (7)

The sender keys come from the `nUserSession::CPacket::WritePacket` pushes: group, id, sub, then -1 (V).

| PC VA | current | ours (final) | PC evidence (V) | PS4 (V) |
| --- | --- | --- | --- | --- |
| `0x7DA410` | `cSeedGameSvConnection::OnPacket_S2C_STAY_INN_RES` | `cSeedGameSvConnection::OnPacket_INN_STAY_INN_RES` | It references `"cSeedGameSvConnection::OnPacket_INN_STAY_INN_RES"` (`0x1BCD3CC`, xref `0x7DA492`) | The current name is PS4 `0x3020A0`'s symbol. PS4 also has `cNetGameServer::OnPacket_S2C_STAY_INN_RES` `0x370A20` |
| `0x8098D0` | `nUserSession::CPacket_S2C_GP_GP_SHOP_DISPLAY_BUY_RES::ReadPacket` | `nUserSession::CPacket_S2C_GP_SHOP_DISPLAY_BUY_RES::ReadPacket` | Its only caller is the handler `0x7D8590` (`0x7D85DB`), whose string is `OnPacket_GP_GP_SHOP_DISPLAY_BUY_RES`. The PC has no class-name string for the packet | `0x19D7ED0`, called only by `OnPacket_S2C_GP_SHOP_DISPLAY_BUY_RES`. No `GP_GP` symbol |
| `0x81DD70` | `...Send_C2S_ACHIEVEMENT_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_REQ` | `cSeedGameSvConnection::Send_C2S_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_REQ` | Key 27.2.1. Its response string `OnPacket_ACHIEVEMENT_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_RES` (`0x1BD2B08`) is group + name | `0x19CB350`, caller `cNetGameServer::getFurnitureReward` |
| `0x81DE30` | `...Send_C2S_ACHIEVEMENT_ACHIEVEMENT_GET_PROGRESS_LIST_REQ` | `cSeedGameSvConnection::Send_C2S_ACHIEVEMENT_GET_PROGRESS_LIST_REQ` | Key 27.0.1. Its response string is at `0x1BD0F08` | `0x19CB0F0`, caller `getAchievementProgress` |
| `0x829310` | `...Send_C2S_GP_GET_CAP_REQ` | `cSeedGameSvConnection::Send_C2S_GET_CAP_REQ` | Key 28.3.1. 28.3.2 is `OnPacket_GP_GET_CAP_RES` (`0x1BCA36C`). The PC caller `0x8691EB` is in `cNetGameServer::getCAP` | `0x19BC2E0`, called only by `cNetGameServer::getCAP` `0x353090` |
| `0x8308B0` | `...Send_C2S_MY_ROOM_MY_ROOM_RELEASE_REQ` | `cSeedGameSvConnection::Send_C2S_MY_ROOM_RELEASE_REQ` | Key 52.0.1. The response string `OnPacket_MY_ROOM_MY_ROOM_RELEASE_RES` (`0x1BD2424`) is group + name; compare `OnPacket_MY_ROOM_FURNITURE_LIST_GET_RES`. The PC caller `0x87B10B` is `cNetGameServer::reqMyRoomRelease` | `0x19CE030`, called only by `reqMyRoomRelease` `0x36A980` |
| `0x833670` | `Send_PAWN_GET_PAWN_HISTORY_LIST_REQ` | `cSeedGameSvConnection::Send_C2S_GET_PAWN_HISTORY_LIST_REQ` | Key 8.28.1, one u32 payload. 8.28.2 is `OnPacket_PAWN_GET_PAWN_HISTORY_LIST_RES` (`0x1BC7830`) | `0x19B6090`, unique, caller `getPawnHistoryList` |

Rule behind the decisions:

- Handlers take the PC string they reference, which is T002's verified rule.
- Requests and packet classes have no PC string, so they take the declared PS4 symbol. The match is unique
  by role, and where the caller is named, the PC caller and the PS4 caller agree.
- The earlier sender names are neither of these. They are the PC response string's group-prefixed form
  with `C2S_` spliced in.
- For `0x7DA410` the current name is a valid PS4 identity, not an error. It is replaced only for the
  scheme.

## 4. Prototypes (54)

### 4.1 The 50 handlers: ours (spelling only)

- Current: `int __thiscall(cSeedGameSvConnection *self, CPacket *packet)`.
- Ours: `int __thiscall(cSeedGameSvConnection *this, CPacket *pPacket)`.
- The 50 VAs are exactly the 50 that T002 3.1 audited. I checked the sets with `comm`: the difference is 0.
- T002 found ecx read before any write and `ret 4` in 50/50 (V there; not re-run here).
- The PS4 DWARF names are `this` and `pPacket`; for example `0x32E5E0`
  `BOOL (cSeedGameSvConnection *this, CPacket *pPacket)`.
- Neither prototype is wrong. Ours aligns the names with the other transferred handlers.

### 4.2 The 4 others

- **`0x7D3880`** (handler 34.1.2). Current: `BOOL __thiscall(MtObject *this, CPacket *packet)`. **Ours**
  (V):
  - `mov edi, ecx` at `0x7D3882`, then uses `+0x41C` (the packet slot) and `+0x13C`. The other handlers
    read `+0x13C` too (46, T002).
  - `retn 4` on both exits (`0x7D38F2`, `0x7D3923`).
  - `MtObject*` is only a base type of the connection. `BOOL` and `int` have the same width; `int`
    follows the T001 convention for handlers.
  - PS4 `0x321F30` is `BOOL (cSeedGameSvConnection *this, CPacket *pPacket)`.
- **`0x8320B0`** `Send_C2S_PARTY_MEMBER_SET_VALUE_REQ`. Current:
  `int __fastcall(MtObject *MtObject, char in_Index, char in_Value)`. **Ours, current contradicted**
  (V):
  - `mov esi, ecx` (`0x8320B4`), and esi is passed to `cSeedServerConnection::Send`.
  - edx is never read.
  - Two stack arguments, each passed to `nPacket::Write_u8` (`0x832138`, `0x83214D`), then `retn 8`.
  - The only caller, `0x87B140`, pushes two values.
  - Under `__fastcall`, IDA would take `in_Index` from edx, which is wrong.
  - PS4 `0x19B2160` is `s32 (cSeedGameSvConnection *this, u8 in_Index, u8 in_Value)`.
- **`0x833670`**. Current: `int __thiscall(void *self, unsigned int unknown_u32)`. **Ours** (more
  specific):
  - The physical shape is the same as T002 found: ecx is `this`, `retn 4`, and its caller `0x86F4B0`
    pushes one u32 with `ecx = [esi+0x29CC]`.
  - PS4 DWARF `0x19B6090` gives `cSeedGameSvConnection *this` and `u32 in_PawnID`.
  - The `this` class is **I**: PC code only shows an object passed to `cSeedServerConnection::Send`.
    The same `[cNetGameServer+0x29CC]` load feeds the other `cSeedGameSvConnection` senders (`0x87B105`,
    `0x8691E5`, `0x86B9B5`), and the ctor of the 0x540-byte object is outside this check.
- **`0x87B140`** `cNetGameServer::reqPartyMemberSetValue`. Current:
  `bool __fastcall(MtObject *this, s32 index, bool flag)`. **Ours, current contradicted** (V):
  - `mov esi, ecx`, then reads `+0x7C`, `+0x29CC` and `+0xC14`.
  - edx is never read.
  - `retn 8` on both exits (`0x87B1BF`, `0x87B1C5`).
  - `arg_4` is tested against 0 (bool) and `arg_0` is forwarded as the index. It returns al.
  - PS4 `0x345E30` is `bool (cNetGameServer *this, s32 index, bool flag)`. `s32` is the same type as
    `int`.

## 5. Gaps and cleanup

- Verify was not run (section 1).
- Not re-run here: T002's per-handler ecx and `ret 4` check of the 50.
- Not traced: where `[cNetGameServer+0x29CC]` is stored. A scan for `mov [reg+29CCh], reg` found only
  zero stores and unrelated functions.
- Cleanup (14:00): `rm -rf` of both `ddon-data-t009` folders removed the `.i64`, `.id2` and `.til` files. The open ida-mcp workers (`1ff1ca044d2a`, `6b162142a927`) still lock the unpacked `.id0`, `.id1` and `.nam` files, and `close_database` is withheld from this role. Delete the two folders once the workers exit.
