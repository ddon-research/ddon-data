# 007 W2 T013e: partial-type sizes cover every access; wave 2 re-applied (PC 03040008): done, republished

Build PC 03040008 <- PS4 02020005. Base `d62639750e`, 2026-11-03 19:40-19:50 (WEST). Fix commit `af9a3f29a3`.
Every IDA run was a `C:/Program Files/IDA Professional 9.5/idat.exe` batch job on the work copy
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64`. ida-mcp
was not used. The original database, the accepted database and the wave-1 snapshot were not opened.

**Outcome (verified): after the fix, all 48 partial-type sizes cover every access through their object. 42 sizes
grew. The T015 canary passes (rc 0, "0 of 48"). On the restored work copy, the apply defined 48 types and set 23
`packet` locals. The second apply found every row `already`. Verify found every row `ok`, including the new width
check, with `counts_ok: true`. In each of the 23 retyped handlers, `packet` spans its whole type, no other stack
lvar overlaps it, and no line contains `OVERLAPPED`. The work copy is republished as
`spec007-packet-handlers-20261103-wave2/` (sha256 `ee07f0b6...8c1d`, equal to the work copy).**

## 1. Fix (`transfer/wave2.py` `_access_check`, tests in `tests/test_wave2.py`)

- An access through the class's parameter (not through a loaded pointer, not indexed) can end past the size: a
  width access at `disp + width`, or a `lea` at `disp` as `disp + 1`. Such an access extends a lower-bound size to
  its end, and the farthest access becomes `size_evidence`. Against a proved size (`KNOWN_SIZES`) it is a
  contradiction, and the class is refused. A `lea` only bounds the size; it is never placed on a member.
- `types.tsv` gains the columns `last_member_end` (the old lower bound, when an access extended it) and
  `size_evidence`. `summary.tsv` gains `types partial with size extended by an access 42`.
- `apply_transfer.py --verify`: each retyped local's lvar width must equal its type's size. Otherwise the row is
  `mismatch` with `check: width`.
- Tests (`tests/test_wave2.py`):
  - `test_access_past_a_lower_bound_size_extends_it`: the canary, made synthetic. It fails on the old code (size
    `0x1c`, not `0x31`).
  - `test_lea_past_a_lower_bound_size_counts_as_one_byte`.
  - `test_access_past_a_proved_size_refuses_the_class`: refused with "past the proved size". It fails on the old
    code, which accepted the class.
  - `test_real_partial_types_cover_every_access_of_their_link_owners`: the T015 canary, run on the committed
    manifest and `dumps/pc-ida.jsonl`. It failed on the old manifest (112 accesses past the size) and passes now.
  - `test_verify_checks_the_retyped_local_spans_its_type`: the verify width check.
- `uv run pytest`: 473 passed. `uv run ruff check --no-fix .`: clean.

**Handler accesses to the stack object (brief item 1, second half): the v6 dump does not record them relative to
the local.** `object_accesses` covers only memory operands whose base holds an argument (`extract/dataflow.py`).
So direct stack stores are absent, among them the inline constructor's word store. Call arguments are recorded,
as `kind: stack` with an entry-relative `frame`. Measured on the 23 retyped handlers:

- 70 such call arguments fall in `[frame, frame + new size)`. These include `0x7e3c10`'s member-array constructor
  and destructor calls at `packet+0x20` (`0x7e3c5a`, `0x7e3c7e`, `0x7e3ccf`), which now lie inside the object.
- 8 fall past the object, all in two handlers: `0x7fbb70` at `packet+0x28` (size `0x25`, 5 calls) and `0x7fbe60`
  at `packet+0x2c` (size `0x29`, 3 calls).

Nothing in the dump ties these 8 to the packet object rather than to a separate local. So they do not extend the
size, and the code does not use handler call arguments. Inferred: they belong to a separate local. The
decompilation agrees (§ 4: no lvar overlaps `packet`).

## 2. Manifest (`uv run python transfer.py --wave2`, deterministic)

Two runs gave identical sha256 for all 8 files: types.tsv `c3e41a48...ae11f`, locals.tsv `ad867e9b...0433`,
types.h `d1a39e54...cc1cb`.

- Counts are unchanged except for the sizes: 48 partial types, 23 R3 and 1 R1 accepted locals.
- `control.tsv` changed by one cell (rng 5, without witness): `accepted_equal_to_real` went from 1 to 0. That
  control type no longer equals the real one, because the real one's size grew.
- The 6 `CData*` types keep their sizes.
- The 23 `packet` rows of `locals.tsv` carry the new sizes.

The table lists the size changes (old -> new). The evidence is the farthest access in the reader: function,
instruction, displacement and width. For all 42 it is a 1-byte store, the trailing read-ok byte T015 identified.

| `CPacket_S2C_*` | old | new | reader | evidence |
| --- | --- | --- | --- | --- |
| `AREA_CHANGE_RES` | `0x34` | `0x5d` | `0x81ca00` | store `0x81ca31` `+0x5c` w1 |
| `AREA_RANK_UP_RES` | `0x28` | `0x51` | `0x7ffaf0` | store `0x7ffb21` `+0x50` w1 |
| `CHANGE_CAP_TO_GP_RES` | `0x24` | `0x25` | `0x808c50` | store `0x808c81` `+0x24` w1 |
| `CHANGE_JOB_RES` | `0xc4` | `0xed` | `0x80cf80` | store `0x80cfb1` `+0xec` w1 |
| `CHANGE_PAWN_JOB_RES` | `0xc8` | `0x13d` | `0x80d170` | store `0x80d1a1` `+0x13c` w1 |
| `CLAN_SHOP_GET_BUFF_ITEM_LIST_RES` | `0x30` | `0x61` | `0x8046f0` | store `0x804721` `+0x60` w1 |
| `CLAN_SHOP_GET_FUNCTION_ITEM_LIST_RES` | `0x30` | `0x61` | `0x804790` | store `0x8047c1` `+0x60` w1 |
| `GAME_TIME_GET_BASEINFO_RES` | `0x90` | `0x91` | `0x81a620` | store `0x81a651` `+0x90` w1 |
| `GET_AREA_MASTER_INFO_RES` | `0x70` | `0x71` | `0x7ffcc0` | store `0x7ffcf1` `+0x70` w1 |
| `GET_CHARACTER_EQUIP_LIST_RES` | `0x54` | `0x55` | `0x808020` | store `0x808051` `+0x54` w1 |
| `GET_CRAFT_GRADEUP_RECIPE_RES` | `0x44` | `0x46` | `0x805c60` | store `0x805c91` `+0x45` w1 |
| `GET_CRAFT_PROGRESS_LIST_RES` | `0x54` | `0x55` | `0x805b40` | store `0x805b71` `+0x54` w1 |
| `GET_CRAFT_RECIPE_DESIGNATE_RES` | `0x44` | `0x45` | `0x805d10` | store `0x805d41` `+0x44` w1 |
| `GET_CURRENT_SET_SKILL_LIST_RES` | `0x2c` | `0x55` | `0x81b3b0` | store `0x81b3e1` `+0x54` w1 |
| `GET_CYCLE_CONTENTS_REWARD_RES` | `0x31` | `0x32` | `0x815ee0` | store `0x815f11` `+0x31` w1 |
| `GET_GP_RES` | `0x32` | `0x33` | `0x808f70` | store `0x808fa1` `+0x32` w1 |
| `GET_MATCHING_PROFILE_RES` | `0x48` | `0x49` | `0x814500` | store `0x814531` `+0x48` w1 |
| `GET_PAWN_EQUIP_LIST_RES` | `0x44` | `0x45` | `0x8081c0` | store `0x8081f1` `+0x44` w1 |
| `GET_PAWN_TOTAL_SCORE_RES` | `0x1c` | `0x41` | `0x812920` | store `0x812951` `+0x40` w1 |
| `GP_SHOP_DISPLAY_BUY_RES` | `0x34` | `0x39` | `0x8098d0` | store `0x809901` `+0x38` w1 |
| `JOB_VALUE_SHOP_GET_LINEUP_RES` | `0x30` | `0x31` | `0x80db80` | store `0x80dbb1` `+0x30` w1 |
| `LEADER_QUEST_PROGRESS_REQUEST_RES` | `0x22` | `0x23` | `0x817530` | store `0x817561` `+0x22` w1 |
| `LEARN_NORMAL_SKILL_RES` | `0x24` | `0x25` | `0x81bc60` | store `0x81bc91` `+0x24` w1 |
| `LEARN_PAWN_NORMAL_SKILL_RES` | `0x28` | `0x29` | `0x81bdc0` | store `0x81bdf1` `+0x28` w1 |
| `NG_WORD_GET_LIST_RES` | `0x48` | `0x49` | `0x80fef0` | store `0x80ff21` `+0x48` w1 |
| `PARTY_INVITE_RES` | `0x20` | `0x21` | `0x811080` | store `0x8110b1` `+0x20` w1 |
| `PARTY_JOIN_RES` | `0x2c` | `0x2d` | `0x8111a0` | store `0x8111d1` `+0x2c` w1 |
| `PAWN_EXPEDITION_GET_MY_SALLY_INFO_RES` | `0x27` | `0x28` | `0x811a00` | store `0x811a31` `+0x27` w1 |
| `PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_RES` | `0x31` | `0x32` | `0x811b40` | store `0x811b71` `+0x31` w1 |
| `PAWN_EXPEDITION_GET_REWARD_DROP_RES` | `0x44` | `0x45` | `0x811be0` | store `0x811c11` `+0x44` w1 |
| `PAWN_EXPEDITION_GET_SALLY_INFO_RES` | `0x6c` | `0x6d` | `0x811c80` | store `0x811cb1` `+0x6c` w1 |
| `PAWN_LOST_RES` | `0x21` | `0x22` | `0x8130a0` | store `0x8130d1` `+0x21` w1 |
| `QUEST_PROGRESS_RES` | `0x34` | `0x35` | `0x818490` | store `0x8184c1` `+0x34` w1 |
| `RELEASE_PAWN_ORB_ELEMENT_RES` | `0x28` | `0x29` | `0x810350` | store `0x810381` `+0x28` w1 |
| `RENTAL_PAWN_LOST_RES` | `0x21` | `0x22` | `0x8131c0` | store `0x8131f1` `+0x21` w1 |
| `REPORT_JOB_ORDER_PROGRESS_RES` | `0x44` | `0x45` | `0x80ddd0` | store `0x80de01` `+0x44` w1 |
| `RESET_CRAFTPOINT_RES` | `0x34` | `0x35` | `0x805ed0` | store `0x805f01` `+0x34` w1 |
| `SET_PAWN_ABILITY_RES` | `0x25` | `0x26` | `0x81c550` | store `0x81c581` `+0x25` w1 |
| `SET_PAWN_SKILL_RES` | `0x25` | `0x26` | `0x81c690` | store `0x81c6c1` `+0x25` w1 |
| `START_EQUIP_GRADE_UP_RES` | `0x34` | `0x85` | `0x8061d0` | store `0x806201` `+0x84` w1 |
| `SYSTEM_MAIL_GET_ALL_ITEM_RES` | `0x20` | `0x75` | `0x80eee0` | store `0x80ef11` `+0x74` w1 |
| `WEATHER_FORECAST_GET_RES` | `0x20` | `0x35` | `0x81ac30` | store `0x81ac61` `+0x34` w1 |

## 3. Re-apply (headless batch)

    T=D:/ddon-data/research/03040008/ida-transfer
    DB=.../ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64
    mv $DB ...exe.w2-undersized.i64          # 80b09086...2bc7 (the T013d state)
    cp -p ...exe.before-W2.i64 $DB           # f7f3a2198cf511ba495d0305a7d7381d6a4cf0b4cbc9d905352fc28a7d3e3c25 (= brief)
    "$IDAT" -A -L$T/dumps/logs/apply-dryrun-w2e.log  "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-dryrun-w2e.jsonl" $DB              # rc 0
    "$IDAT" -A -L$T/dumps/logs/apply-w2e.log         "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-w2e.jsonl --apply" $DB            # rc 0
    "$IDAT" -A -L$T/dumps/logs/apply-w2e-2.log       "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-w2e-2.jsonl --apply" $DB          # rc 0
    "$IDAT" -A -L$T/dumps/logs/apply-verify-w2e.log  "-S$T/apply_transfer.py $T/manifest/transfer/wave2 $T/dumps/apply-verify-w2e.jsonl --verify --apply-log $T/dumps/apply-w2e.jsonl" $DB  # rc 0
    "$IDAT" -A -L$T/dumps/logs/spot-w2e.log          "-S<scratchpad>/spot_w2e.py" $DB                                                                     # rc 0, DBFL_KILL

`apply_transfer.py` sha256 `7bb7976e...a49` (`script_version` 2). The header's `manifest_sha256` matches the three
files above. `filter` is null.

| Kind | dry run | apply | second apply | verify |
| --- | --- | --- | --- | --- |
| types: 48 partial | 48 would-define | 48 defined | 48 already | 48 ok |
| types: 21 embedded wave-1 | 21 already | 21 already | 21 already | 21 ok |
| locals: 23 R3 + 1 R1 | 23 would-set, 1 refused `user-name` | 23 set, 1 refused | 23 already, 1 refused | 23 ok |
| failed / mismatch | 0 | 0 | 0 | 0 |
| undo records | | 71 (48 types + 23 locals) | 0 | |

- The `user-name` refusal is `0x87caa0@-20` `sendFeedbackList`, the same expected refusal as in T013c and T013d.
- Verify counts: before = after = expected = 965 local types, 52,148 user names and 1,464 typed functions, with
  `ok: true`.
- In the apply log, each `set` local has an `after.width` equal to the row's new size (e.g. `0x7e3c10` 117,
  `0x7d73b0` 51).
- `rg -ci "unpacked|restore|traceback"` finds 0 matches in each of the four logs.

| Step | work copy sha256 |
| --- | --- |
| restored (= `.before-W2.i64`), and after the dry run | `f7f3a2198cf511ba495d0305a7d7381d6a4cf0b4cbc9d905352fc28a7d3e3c25` |
| after the apply | `f715fc2a9f2bc37d59a055aa91833c1c9528ee533fd4f57550d49a5a8ca0cc81` |
| after the second apply (re-saved, 0 writes), verify and spot check | `ee07f0b6870cf41fcc1e21ef2c8367c079574f26bfae46b14101faaad1c38c1d` |

| Dump (`$T/dumps/`) | sha256 | lines |
| --- | --- | ---: |
| `apply-dryrun-w2e.jsonl` | `e52cf85d8350c92406718986ddcef5bebcfd6c09aaa4e934953d86b2823a3b07` | 95 |
| `apply-w2e.jsonl` | `173f73fa2e9fca1ed50955d20a28548e669c28d51307afd48dc9cde229a22d85` | 166 |
| `apply-w2e-2.jsonl` | `d35682d20a5455164b9558ee2cdaa08b52f97905512392e0790d325a4b44143b` | 95 |
| `apply-verify-w2e.jsonl` | `acdd4d43bf7b97e6c27699b3f7b12920b10289340eb147e61009b0d37a992f23` | 95 |
| `spot-w2e.txt` | `89e8b956343b7beb757ea06077ee635d5c850a59adde42a8d271100c2cc28af6` | |

`dumps/MANIFEST.tsv` was regenerated with `uv run python manifest.py`. The diff adds the 4 jsonl rows and changes
no other row. The T013d dumps (`*-w2.jsonl`) stay as the record of the undersized run.

## 4. Checks against the new state (verified)

- Canary: `python -X utf8 -I .agent-ledger/canaries/007-W2/test_lower_bound.py` gives "0 of 48 partial types
  have accesses past their declared size", rc 0. Before the fix it gave 42 of 48, rc 1.
- Database types: `spot_w2e.py` ran with `DBFL_KILL`; its `idb` is the work copy and its input sha256
  `f1c974d0...fa20`. All 48 partial types have their `types.tsv` size in the database (0 mismatches).
- All 23 retyped handlers:
  - The `packet` lvar width equals the type size and the row size.
  - 0 other stack lvars overlap `[packet, packet + width)`.
  - 0 pseudocode lines contain `OVERLAPPED`.

  Before the fix, T015 found splits in 15 handlers and `OVERLAPPED` in 4.
- Spot checks (pseudocode in `dumps/spot-w2e.txt`):
  - `0x7e3c10` SYSTEM_MAIL_GET_ALL_ITEM_RES (width 117):
    - The member array is `packet.gap20`: `sub_57F990(this: packet.gap20)`, `sub_57FD70(this: packet.gap20)`.
    - The flag is `packet.gap20[84] = 0`.
    - The `v6 : _DWORD[21]` and `v7` lvars are gone.
  - `0x7fae10` GET_CURRENT_SET_SKILL_LIST_RES (width 85):
    - The arrays read as `packet.gap2C[4]`/`[16]`/`[24]`/`[36]` and `packet.m_NormalSkillList.mLength`.
    - The `v12`-`v15` lvars are gone.
  - `0x7d73b0` GET_GP_RES (width 51):
    - `memset(&packet.m_llUseLimit, 0, 19)` now includes the read-ok byte.
    - The `char v6` at `ebp-6h` is gone.
  - `0x7e9ef0` PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_RES (width 50):
    - The inline constructor's word store reads `*(_WORD *)&packet.m_ucPawnExpeditionStatus = 0`.
    - The lvar is not `OVERLAPPED`.

## 5. Rollback point and published copy (verified)

- After all checks passed, `...exe.w2-undersized.i64` (`80b09086...2bc7`) was deleted. `ddon-data-007work/`
  now holds `...exe.i64` (`ee07f0b6...8c1d`) and `...exe.before-W2.i64` (`f7f3a219...3c25`, unchanged).
- The work copy was copied (`cp -p`) over
  `PC_DDON_03040008/spec007-packet-handlers-20261103-wave2/2022_01_29_DDO_DUMP_FIX.exe.i64`:
  - sha256 `ee07f0b6870cf41fcc1e21ef2c8367c079574f26bfae46b14101faaad1c38c1d`, 112,433,230 bytes, the same as the
    work copy.
  - `spec007-packet-handlers-20261103-wave1/` was not touched (14:03, 112,373,500 bytes).
