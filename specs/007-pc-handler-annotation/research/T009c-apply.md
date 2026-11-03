# 007 T009c: apply the T009 conflict corrections to the work copy (PC 03040008): done, every check passes

Build PC 03040008, work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`
(header `input_sha256` `f1c974d0...fa20`, `idb_path` under `ddon-data-007work`). Base `c39e1b0aea4`,
2026-11-03 13:58-14:02 (WEST). All IDA work ran as `C:/Program Files/IDA Professional 9.5/idat.exe` batch jobs.
ida-mcp was not used, and neither the original nor the accepted database was opened. The spot-check batch confirms
the database: `get_idb_path` is the work copy, 32-bit exactly (`inf_is_64bit` false), image base `0x400000`.
Addresses are VAs. `apply_transfer.py` sha256 `f1ad707ce0f5a60028e2a6125ee7604dc8c048184875504a73a7cb7070cacca0`
(T009b; `script_version` 1).

**Outcome: the apply wrote exactly the T009 correction rows: 7 `correct` names, 54 `replace` prototypes and 55
comments. Every other row was `already`, with 0 refusals, 0 `current-changed` and 0 `failed`. The second apply
finds all rows `already` and writes 0 undo records. Verify passes: every row `ok`, `counts_ok: true`, and 1,065 of
1,065 typed functions decompile. `dumps/apply-t009c.jsonl` is the new `--apply-log` base for `--verify`.**

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    IDAT="C:/Program Files/IDA Professional 9.5/idat.exe"

Manifest inputs (header `manifest_sha256`, the same in all four dumps): names.tsv `48f152c5...109a`,
prototypes.tsv `f7577c6a...0584`, comments.tsv `3cae170f...f004`, types.tsv `878c53c6...c280`, types.h
`fca66a82...e590`, skipped.tsv `16ac7161...8606`.

## 1. Rollback copy (verified)

    sha256sum *.i64                     # work copy be0cc624fdb38deaa646de2ecea04fbf8d5297d8d37cf164ca4a61310aee162f (= brief)
    cp -p ...exe.i64 ...exe.before-T009c.i64
    sha256sum ...exe.before-T009c.i64   # be0cc624...162f, 112,370,180 bytes, mtime 13:17

After the hashes matched, the older rollback copy `...exe.before-T007b.i64` (`65120b34...8b9111`) was deleted,
as the brief allows. The folder now holds only `...exe.i64` and `...exe.before-T009c.i64`.

## 2. Commands, counts and hashes

    "$IDAT" -A -L$T/dumps/logs/apply-dryrun-t009c.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-dryrun-t009c.jsonl" $DB                 # 13:59, rc 0, 13 s
    "$IDAT" -A -L$T/dumps/logs/apply-t009c.log        "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-t009c.jsonl --apply" $DB                 # 13:59, rc 0, 11 s
    "$IDAT" -A -L$T/dumps/logs/apply-t009c-2.log      "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-t009c-2.jsonl --apply" $DB               # 14:00, rc 0
    "$IDAT" -A -L$T/dumps/logs/apply-verify-t009c.log "-S$T/apply_transfer.py $T/manifest/transfer $T/dumps/apply-verify-t009c.jsonl --verify --apply-log $T/dumps/apply-t009c.jsonl" $DB  # 14:00, rc 0

The counts come from `jq -c 'select(.kind=="result")|[.step,.status]' <dump> | sort | uniq -c`:

| Kind | dry run | apply | second apply | verify |
| --- | --- | --- | --- | --- |
| types (181) | 181 already | 181 already | 181 already | 181 ok |
| remove-label (3) | 3 already | 3 already | 3 already | 3 ok |
| names (1,086) | 7 would-set (`correct`), 1,079 already | 7 set, 1,079 already | 1,086 already | 1,086 ok |
| prototypes (1,065) | 54 would-set (`replace`), 1,011 already | 54 set, 1,011 already | 1,065 already | 1,065 ok |
| comments (1,174) | 55 would-set, 1,119 already | 55 set, 1,119 already | 1,174 already | 1,174 ok |
| decompile | | | | 1,065 ok |
| refused / failed / mismatch | 0 | 0 | 0 | 0 |
| undo records | | 116 (7 + 54 + 55) | 0 | |

The dry-run summary lists no conflict steps, consistent with T009b's 0 conflicts left.

### 2.1 Dry-run check (verified with jq)

- Every `would-set` name row has action `correct`, and every `would-set` prototype row has action `replace`.
  There is no other `would-set` row, no refusal and no `current-changed`.
- The would-set names and prototypes cover 60 distinct VAs. The 7 names and 54 prototypes overlap only at
  `0x833670`. All 55 comment would-sets fall on those VAs: the 54 prototype VAs plus `0x7da410`, whose name
  is corrected and which has no prototype row.
- The other 5 name corrections (`0x8098d0`, `0x81dd70`, `0x81de30`, `0x829310`, `0x8308b0`) have their prototypes
  and comments `already`: T007e wrote them. Their comments.tsv rows name the PS4 symbol, not the PC name, so the
  name correction does not change the comment text.

### 2.2 Verify counts record

before = after = expected = 965 local types / 52,148 user names / 1,464 typed functions, applied delta 0/0/0,
`ok: true`. A name correction renames a user name, and a prototype replacement retypes a function that already
had a type, so no count changes.

### 2.3 Work copy sha256 at each step

| Step | sha256 | bytes | mtime |
| --- | --- | ---: | --- |
| start (= `.before-T009c.i64`) | `be0cc624fdb38deaa646de2ecea04fbf8d5297d8d37cf164ca4a61310aee162f` | 112,370,180 | 13:17 |
| after the dry run (`DBFL_KILL`) | not hashed separately; the apply started from `be0cc624...162f` (hashed at 13:59:51) | | |
| after the apply | `70cb264eab716b65e562be83e16d2c6514c2a813b9e7d5382220b61045168f0d` | 112,370,579 | 14:00 |
| after the second apply (re-saved by `qexit(0)`, 0 writes) | `f7f3a2198cf511ba495d0305a7d7381d6a4cf0b4cbc9d905352fc28a7d3e3c25` | 112,373,500 | 14:00:18 |
| after verify and both spot-check runs (each `DBFL_KILL`) | `f7f3a219...3c25` | 112,373,500 | 14:00:18 |

As in T007e, the second apply changes the hash although it writes nothing. Inferred: `qexit(0)` re-saves and
repacks the database. The read-only runs leave the hash unchanged.

| Dump (`$T/dumps/`) | sha256 | lines |
| --- | --- | ---: |
| `apply-dryrun-t009c.jsonl` | `114c54b1383c9678e4e894530e6a8515198a646168743080bc465f7e3b3cf9b7` | 3,511 |
| `apply-t009c.jsonl` | `feaa34371a02ec45afa80541173483769f26714e23ca9ce78af407164b2df19d` | 3,627 |
| `apply-t009c-2.jsonl` | `57ca4b6b860db55e6d967fa05f15d8ae8bae1ea4ecae409e33c62ff1996e4dd1` | 3,511 |
| `apply-verify-t009c.jsonl` | `2b34971172637ae8873843a3e8a41677e37923f3716cd8a00d0fe587613cd9c0` | 4,577 |

Logs: `dumps/logs/{apply-dryrun-t009c,apply-t009c,apply-t009c-2,apply-verify-t009c}.log`. `rg -ci
"unpacked|restore|traceback"` finds 0 matches in each. After every run, only the two `.i64` files are in the
work folder.

`dumps/MANIFEST.tsv` was regenerated (`uv run python manifest.py`, rc 0). The diff adds 5 rows: the 4 dumps above
and `apply-dryrun-t009.jsonl` (`7925508a...84df`, 3,456 lines). That T009 dry-run file was already in `dumps/` but
had no MANIFEST row. No other row changed.

## 3. Spot checks (verified)

The checks ran as a read-only batch: `idat -A -S<scratchpad>/spot_t009c.py $DB`, rc 0, ending with
`DBFL_KILL`. The script reads `get_name`, `get_type`, `get_func_cmt` and `ida_hexrays.decompile`. All 7
functions decompile without error. The excerpts below are the leading pseudocode lines (blank lines dropped).

**`0x7da410`**: name corrected to the PC string. The prototype is not a T009 row: `skipped.tsv` line 101 says
"register argument(s) edi; convention not provable", so the `__userpurge` stays, as expected. The comment is new.

    // PC name from string at 0x1bcd3cc. PS4 02020005: cSeedGameSvConnection::OnPacket_S2C_STAY_INN_RES (_ZN21cSeedGameSvConnection25OnPacket_S2C_STAY_INN_RESEP7CPacket); paired by seed.
    int __userpurge cSeedGameSvConnection::OnPacket_INN_STAY_INN_RES@<eax>(
            _DWORD **this@<ecx>,
            int a2@<edi>,
            CPacket *packet)

**`0x833670`**: name corrected (before `Send_PAWN_GET_PAWN_HISTORY_LIST_REQ`) and prototype replaced (before
`int __thiscall(void *self, unsigned int unknown_u32)`). The earlier comment is kept above `----`.

    // Writes request 8:28:1 with one four-byte value. Returns 0 if header or payload writing fails and 1 after calling Send; this does not confirm delivery. Receiver class and argument meaning remain unverified.
    // ----
    // PS4 02020005: cSeedGameSvConnection::Send_C2S_GET_PAWN_HISTORY_LIST_REQ (_ZN21cSeedGameSvConnection34Send_C2S_GET_PAWN_HISTORY_LIST_REQEj); paired by listener-sender.
    int __thiscall cSeedGameSvConnection::Send_C2S_GET_PAWN_HISTORY_LIST_REQ(
            cSeedGameSvConnection *this,
            unsigned int in_PawnID)
      ...
      if ( nUserSession::CPacket::WritePacket(&packet, groupId: 8u, id: 28, subId: 1u, a5: -1)
        && nPacket::Write_u32(&packet, value: in_PawnID) != 0 )
      {
        cSeedServerConnection::Send(
          self: (cSeedServerConnection *)this,

**`0x8320b0`**: prototype replaced (before `int __fastcall(MtObject *MtObject, char in_Index, char in_Value)`).
There was no earlier comment.

    int __thiscall cSeedGameSvConnection::Send_C2S_PARTY_MEMBER_SET_VALUE_REQ(
            cSeedGameSvConnection *this,
            unsigned __int8 in_Index,
            unsigned __int8 in_Value)
      ...
      if ( nUserSession::CPacket::WritePacket(&packet, groupId: 6u, id: 15, subId: 1u, a5: -1)
        && nPacket::Write_u8(&packet, value: in_Index) != 0
        && nPacket::Write_u8(&packet, value: in_Value) != 0 )

**`0x87b140`**: prototype replaced (before `bool __fastcall(MtObject *this, s32 index, bool flag)`). The caller
now passes `index`/`flag` into the typed sender `0x8320b0`:

    // PS4 02020005: cNetGameServer::reqPartyMemberSetValue (_ZN14cNetGameServer22reqPartyMemberSetValueEib); paired by listener-requester.
    bool __thiscall cNetGameServer::reqPartyMemberSetValue(cNetGameServer *this, int index, bool flag)
    {
      *((_DWORD *)this + 31) = 4;
      sNetworkExt::reserveNetworkErrorDialog(this: (MtObject *)::this, comId: 30);
      v4 = *((_DWORD *)this + 2675);
      ...
        || cSeedGameSvConnection::Send_C2S_PARTY_MEMBER_SET_VALUE_REQ(
             this: *((cSeedGameSvConnection **)this + 2675),
             in_Index: index,
             in_Value: flag) == 0 )

The `::this` passed to `reserveNetworkErrorDialog` is a pre-existing global name in the database, not a T009c
write (inferred: T009c wrote only the 60 function VAs of § 2.1).

**`0x7d3880`**: prototype replaced (before `BOOL __thiscall(MtObject *this, CPacket *packet)`).

    int __thiscall cSeedGameSvConnection::OnPacket_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES(
            cSeedGameSvConnection *this,
            CPacket *pPacket)
      ...
      v3 = *(void (__thiscall ****)(_DWORD, int))&this->opaque140[732];
      ...
      if ( nUserSession::CPacket_S2C_ENTRY_BOARD_ITEM_LIST_RES::ReadPacket(
             this: (int)EntryBoardItemListPacket,
             packet: pPacket) == 0 )

**Two of the 50 earlier handlers** (T002; prototype before `int __thiscall(cSeedGameSvConnection *self, CPacket
*packet)`, user-set):

- `0x7e99e0` has an earlier comment. That comment is kept above the separator, and the arguments are now
  `this`/`pPacket`. The undo record's before-comment equals the text above `----`.

      // Reads Error first; nonzero Error ends parsing before Result and payload. Parsing success does not establish a successful operation.
      // ----
      // PC name from string at 0x1bc7298. PS4 02020005: cSeedGameSvConnection::OnPacket_S2C_DELETE_FAVORITE_PAWN_RES (_ZN21cSeedGameSvConnection37OnPacket_S2C_DELETE_FAVORITE_PAWN_RESEP7CPacket); paired by seed.
      int __thiscall cSeedGameSvConnection::OnPacket_PAWN_DELETE_FAVORITE_PAWN_RES(
              cSeedGameSvConnection *this,
              CPacket *pPacket)
        ...
        result = sub_811730(this: (int)&v5, packet: pPacket);

- `0x7c7500` (`OnPacket_CHARACTER_CHARACTER_GOLDEN_REVIVE_RES`) had no earlier comment, so it now carries ours
  alone. Its arguments are `this`/`pPacket`, and it calls `sub_801BB0(this: (int)&v6, packet: pPacket)`.

The comment undo records show an earlier comment on 13 of the 55 commented functions: 12 handlers and `0x833670` (`jq` over `apply-t009c.jsonl`).

## 4. Files written

- Work copy `...exe.i64` (`f7f3a219...3c25`) and rollback copy `...exe.before-T009c.i64` (`be0cc624...162f`).
  `...exe.before-T007b.i64` was deleted.
- `research/03040008/ida-transfer/dumps/`: the four dumps of § 2, their four logs in `dumps/logs/`, and
  `MANIFEST.tsv`.
- This report. Scratchpad (not committed): `spot_t009c.py`, `spot_t009c.json`, `spot.log`.
