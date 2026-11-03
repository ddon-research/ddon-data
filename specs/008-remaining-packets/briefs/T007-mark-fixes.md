008 T007: fix the overstated marks, distinct counts, and the Instance.hexpat renaming

Objective (client 03040008): apply `specs/008-remaining-packets/research/T006-adversarial.md` F1-F3 (read it; canaries in
`.agent-ledger/canaries/008-T006/`, `itemdistinct.py`/`smallenum.py`/`corr.py` give the numbers) and T005's proposal.

1. F1: every `I (value: ...)` basis states the distinct-value count; a basis with 3 or fewer distinct values, or whose
   chance level (`itemdistinct.py` "p(all by chance)") exceeds 0.05, becomes `G (lead; value consistent: n distinct)`
   (or `G (context; ...)`). Stage-id claims that also match the stage name stay I. 10.14.16 ItemId: `V (consumer)`
   from handler `0x7DE260` -> `sub_B98C80` (sItemManager lookup) and chat message 0x85, cited.
2. F2: 71.22.2 GameMode, 72.2.1 StorageType -> `G (lead)`; DailyMission `WalletPointList.Type` uses the PS4 DWARF enum
   `E_WALLET_POINT_TYPE` from `include/Character.hexpat` with its mark.
3. F3: the T003-T005 report tables and the pattern comments that give counts state distinct counts beside the totals
   (append an "Errata (T006, 2026-11-03)" note in each report; do not rewrite their original text).
4. T005 proposal: in `include/Instance.hexpat`, `GatheringItemListRes_unk_1`'s u32 is an ItemId in 38/38 (state the
   distinct count; mark by the F1 rule); rename the field (and others the 006/008 decodings settle there), keeping
   the structure; re-export every pattern that includes it and check that only renamed keys change in a 2-file
   sample per pattern.
Re-export every pattern whose JSON keys or enum values change (`packets/imhex-export.sh --force @ <name> </dev/null`);
all files still fit. README: the mark legend says how value bases are counted (distinct values, chance level).

Owns: the 008 patterns, `include/Instance.hexpat`, `include/DailyMission.hexpat`, the README, the re-exported JSON, the
T003-T005 report errata. Never touch raws, client/, 006 patterns other than re-exports of `Instance.hexpat` users,
ddon-hook.
Libraries: plbatch via `imhex-export.sh`, stdlib Python.
Done: fit counts per re-exported id; `bash tools/check.sh --since <base>`; signed commits with `git commit -m <msg> -- <paths>`
(stage directories explicitly); receipt with "For Sam's inspection" (old -> new mark/name/key). Stop: budget 90 min
of work time. Base: the head when you start. Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
