# 007 W2 T015: adversarial review of the wave-2 partial types and locals

PC 03040008 <- PS4 02020005. Reviewer `adversarial-reviewer`, base `ee769b0d8f`, against the published wave-2
database (`spec007-packet-handlers-20261103-wave2`, sha256 `80b09086...2bc7`) through `DBFL_KILL` batches on a
private `cp` (deleted). Sample: all 48 types (42 `CPacket_S2C_*_RES`, 6 `CData*`) instead of a seeded 16, and the
locals. Canaries and outputs: `.agent-ledger/canaries/007-W2/` (`test_lower_bound.py`, `extent.py`,
`handlers.py`, `show.py`, `extent.jsonl`, `handlers.txt`, `show.txt`). Filed by the coordinator from the reviewer's
final message (the role writes only canaries); the coordinator reproduced the canary (rc 1, "42 of 48 partial
types have accesses past their declared size").

## Finding 1 (block): 42 of 48 lower-bound sizes are wrong

Every one of the 42 `CPacket_S2C_*_RES` readers writes past the declared `pc_size` through `this`: a trailing
read-ok byte `mov byte [ecx+N], 1` with `N >= pc_size`; 13 also read whole codec members past it, e.g.
`GET_GP_RES` size `0x32`, store `0x808fa1` -> `+0x32`; `CHANGE_JOB_RES` size `0xc4`, store `0x80cfb1` -> `+0xec`,
leas to `+0xc4`/`+0xd0`; `SYSTEM_MAIL_GET_ALL_ITEM_RES` size `0x20`, store `0x80ef11` -> `+0x74`, array lea `+0x20`;
`START_EQUIP_GRADE_UP_RES` size `0x34`, 11 accesses to `+0x84`; `GET_CURRENT_SET_SKILL_LIST_RES` size `0x2c`, arrays
at `+0x2c`/`+0x40`, flag `+0x54`. The 6 `CData*` readers stay within bounds.

Cause: `transfer/wave2.py:628-631` (`_access_check`) counts any access that hits no linked member as a gap, also
at or past `p.size` (`types.tsv`: `gap_accesses 4`, `width_checked 0` for every CPacket type).

Effect in the database: each retyped `packet` local is exactly `pc_size` wide; in 15 handlers Hex-Rays splits the
rest of the object into separate lvars (e.g. `0x7e3c10`: `v6 : _DWORD[21]` at `packet+0x20` is the object's
MtTypedArray, `v7` at `+0x74` the flag; `0x7fae10`: `v12`-`v15` are its two arrays' `mLength`/`mpArray`; 13 others: a
`char vN = 0` at `packet + pc_size`, e.g. `0x7d73b0` `v6` at `ebp-6h`); in 4 handlers (`0x7e9ef0`, `0x7ec490`,
`0x7fcb90`, `0x7fcd60`) `packet` is `OVERLAPPED` because the inline constructor writes a word at the last u8 member.

Fix (proposed): in `_access_check`, an access ending past `p.size` extends a lower-bound size to that end (with the
access as `size_evidence`) and contradicts a proved size; regression test from the canary; apply `--verify`
checks each retyped local's width covers the type's size; re-apply.

## Checked and found right

- Attack (1): all 132 codec links come from `callsites.tsv` rows with status `agree`; where the PC-PS4 offset delta
  changes within a type (20 types) the shifts fit 64-bit PS4 vs 32-bit PC (MtTypedArray 32 vs 20 bytes, 8-byte
  padding). Per-member derivation from PS4 disassembly: not run.
- Members: in the readers/handlers decompiled (`GET_GP_RES`, `SET_PAWN_ABILITY_RES`, `SET_PAWN_SKILL_RES`,
  `REWARD_DROP_ITEM_RES`, `PAWN_LOST_RES`) the linked members sit where the codec reads them, with the linked width.
- Locals: every applied `packet` local is the object passed as `this` to its `ReadPacket`.
