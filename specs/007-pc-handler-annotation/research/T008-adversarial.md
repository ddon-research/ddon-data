# 007 T008: adversarial review of the applied wave-1 rows

PC 03040008 <- PS4 02020005. Reviewer: `adversarial-reviewer`, base `d74ad80dc2`, sample seed 8008. IDA only as
`idat -A` batches with `DBFL_KILL` on private copies `pc-accepted t008` / `ps4 t008` (deleted); the work copy was
not opened. Manifest `types.h` sha256 `39864eaf...`. Canaries and raw dumps: `.agent-ledger/canaries/007-T008/`
(`sample.py`, `sample.tsv`, `dump_funcs.py`, `pc.out`, `ps4.out`, `side.py`, the two tests). Written by the
coordinator from the reviewer's final message (the role's write hook allows only the canary folder); the
coordinator reproduced both canaries (rc 1 each, output as below).

## Findings (both route; the work copy is right)

### F1: `ctype` drops pointer depth

`transfer/prototypes.py:73` strips every trailing `*` (`s.rstrip("&").rstrip("*").rstrip("&")`), so the `T**`
branch (lines 79-83) never runs; `transfer/layout.py:110` does the same for `pointee`. Result: `types.h:103`
declares `MtObject *mpArray`, while `type_members.tsv` (`dwarf_type` `MtObject**`), the PS4 code (`0x1a03ab0`
assigns `(MtObject **)`) and the PC code (5 readers store the element pointer at `[[arr+0x10] + 4*i]`:
`0x776e50`, `0x7738f0`, `0x776f20`, `0x7776e0`, `0x7732e0`) say `MtObject **`. Canary `test_pointer_depth.py`:
`ctype('MtObject**') = 'MtObject *'` (also `char**`, `unsigned int**`). Only `T**`/`T*&` member in the manifest;
no prototype row has one. The database is right only because T007e kept its existing `MtArray`. Fix: strip one
level (`strip(s[:-1])`), same at `layout.py:110`; regenerate the manifest.

### F2: `member_equal` ignores a plain member's type

`apply_transfer.py:186` (`member_equal`, 167-186) matches a plain member on offset, size and name only, so
`MtArray` was `already` and verify `ok` although the database has `MtObject **` and the row `MtObject *`; a same-size
`unsigned int` or `float` would pass too. Canary `test_member_type_ignored.py`: 3 of 3 cases return True. Fix:
require `ex["type"] is None or norm(ex["type"]) == norm(row.type + "*" * row.ptr)` (`norm` drops spaces, `struct`,
`const`).

## Checked and found right (seed 8008)

| Stratum | Checked | Wrong |
| --- | ---: | ---: |
| Seeds (handlers) | 8 | 0 |
| Rule 1 readers | 8 | 0 |
| Rule 2 element readers | 8 | 0 |
| Rule 4 requesters | 8 | 0 |
| Rule 4 senders | 8 | 0 |
| Gate (a) one-witness pairs (pool 55) | 10 | 0 |
| Prototypes | 10 | 0 |
| `MtTypedArray<X>` layouts | 5 | 0 offsets or widths |
| Tier-0 handlers without a PS4 pair | 5 | 0 |

- Seeds: the PC string equals the PS4 symbol after the group prefix. Readers/element readers: codec width
  sequences and nested-reader pairs consistent. Requesters: one sender each; senders one caller each on both
  sides; `WritePacket` group/id agree with Arrowgene `PacketId.cs` for 12 senders (lead only, corroboration).
- Prototypes: 3 `__cdecl` (callers clean 8 bytes), 3 with `__int64` (`ret 8`), 3 handlers (`ret 4`), 1 sender with
  no arguments. The manifest has no float/double and no `__stdcall` rows.
- Layouts: byte at +0xC, dwords at +4 and +8, dword at +0x10 indexed by 4; all 101 prototype rows with an
  `MtTypedArray<X>*` argument: every function touching it shows the +0xC store; 12 senders only pass it on.
- Tier 0: each string occurs in exactly one function.
- Not proved: `MtArray` size 0x14; PS4 prototypes were taken from the PS4 database's types, not re-derived
  from raw DWARF.

## Notes (not defects)

- `0x76dee0` `Read_CDataMDataCraftMaterial_` reads an extra bool on PC (Season 3); same function, element type
  opaque, no row wrong.
- `0x758823` lies in no function in the accepted database (the dumps come from the repaired work copy).
- `0x804790` calls `0x75e2a0`, inside another item in the accepted database (`loc_75E29C+4`): an unrepaired
  boundary there (check in the work copy).
