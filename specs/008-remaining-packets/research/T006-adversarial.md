# 008 T006: adversarial review of the 008 layouts, marks and names

Client 03040008. Reviewer `adversarial-reviewer`, base `73d8c52478`. Canaries `.agent-ledger/canaries/008-T006/`
(`widthwalk.py`, `padcheck.py`, `corr.py`, `itemdistinct.py`, `smallenum.py`, `renames.py`, `ida_out.txt`,
`ida.log`). Filed by the coordinator from the reviewer's final message; the coordinator reproduced `itemdistinct.py`
and `smallenum.py` (output as below). IDA: one headless batch on a `cp` of the wave-2 database (sha256 unchanged,
deleted).

## Verdict

No layout defect. Three findings, all marks claiming more than their evidence.

## F1: "value is an item id" cannot tell item ids from chance

`client/03040008/.../itemlist.ipa.json` holds 21,505 ids in 1..25768 (density 0.83 overall, 0.92-1.00 in the ranges
the captures use; even the placeholder 999 passes). The `I (value)` counts repeat few distinct values: 10.14.16
ItemId 1 distinct; 62.9.2 ItemId 1 (18659); 62.18.2 TrialCost 1; 62.33.2 ItemRewards 3; 71.22.2
RareItemAppraisalList 3; 72.0.2 MissionList ItemList 1; chance that every distinct value is an item id by luck
0.07-0.62 for 59.9.2, 65.3.2, 31.53.2. Stage ids likewise (550, 560, 655 one value each; density about 0.86 in
500-700); claims that also match a stage name (559) stand. Fix: state distinct counts in every value basis; 3 or
fewer distinct -> `G (lead; value consistent)`. 10.14.16 ItemId has a code basis instead: handler `0x7DE260` passes
element +8 to the sItemManager lookup `sub_B98C80` and posts chat message 0x85 (V candidate,
`S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC-pattern.cpp:22`).

## F2: `I (value)` on constant or small-enum fields named only by the server

71.22.2 GameMode (value 2 in all 84; meaning from Arrowgene `GameMode.cs`), 72.2.1 StorageType (19 x6, 20, 13; only
`Storages.cs` maps them), DailyMission WalletPointList.Type (4, 12; server names). Fix: `G (lead)`; wallet type: the
PS4 DWARF enum `E_WALLET_POINT_TYPE` in `Character.hexpat` (4 = `WALLET_POINT_TYPE_TICKET`, 12 = `UNK_12`).

## F3: headline counts repeat identical captures

71.22.2: all 42 captures carry one identical list ("294/294" = 7 comparisons x 42); 72.0.2: 3,393 missions are 29
MissionIds and 187 distinct tuples (none breaks the State rule); 62.39.16 "148/148" includes 121 empty lists (27
non-empty, 3 CharacterIds). Conclusions hold; report distinct counts in the reports and pattern comments.

Unconfirmed: the 12 slack bytes of the only 10.14.16 capture look structured, but slack is non-zero in 82% of 4,000
reference raws; the PC reader reads only a u16 and the list.

## Checked and found right

- Layouts, all 115 ids: `widthwalk.py` decodes every raw from the T001 `width_seq` alone (T002's for 70.0.1) and
  matches 4,885/4,887 JSON leaf by leaf; the other 2 are 29.23.16 (no reader, G as stated).
- IDA re-read: 10.14.16, 72.2.1 (T004 correction right), 34.0.1 (T005 correction right), 63.2.16, 12.5.1, 11.7.16,
  13.16.1, 13.17.1, 63.5.16, 62.33.2, 61.2.2, 62.39.16, 72.1.16, 72.0.2 element `0x762530`, 62.16.16 `0x779090`,
  28.34.2, 2.5.16, 62.27.16, 29.23.16 (`return 1`): code matches the patterns.
- Every response pattern reads Result only when Error == 0, as the PC readers.
- Renames: 11.7.16 (notice class pushed in `0x7F2DB0`), 72.1.16 (80 ids 1 -> 2, 33 1 -> none), 62.39.16, 63.2.16 /
  63.5.16 `G (lead)` as stated. Ids whose layout differs from the server: 10.14.16, 34.0.1, 14.11.16 agree with code.
- Not run: the consumer checks behind role-only `V` marks of 28.34.2 and 11.68.16, the 13.23.16 ValueOld check, ImHex.
