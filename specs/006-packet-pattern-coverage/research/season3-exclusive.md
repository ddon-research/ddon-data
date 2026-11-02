# Season 3-exclusive and unresolved packet ids (spec 006 deliverable, client 03040008)

`season3-exclusive.tsv` lists every packet id of the T001 triage that spec 006 left without a
pattern: the Season 3-exclusive ids (by code or by inference) and the ids whose PS4 counterpart and
role stay open. They go to a later spec (Sam). Built 2026-11-02 (TC1) from the tree at `2ae4d5d0a76`.

## Counts

| status | ids | captured packets | meaning |
| --- | ---: | ---: | --- |
| exclusive V | 37 | 1,666 | the batch report confirmed by code that PS4 02020005 has no counterpart (mark `X`, `X (confirmed)`, `X (S3-exclusive)`, `none (exclusive, V)`, `none (S3, V by reader callers)`) |
| exclusive I | 75 | 3,067 | no counterpart found, inferred: report mark `X(I)`, `none (S3, I)`, `X (candidate C)` (11.7.16: the triage's PS4 candidate contradicted), group 63 `rejected` (no PS4 `CHAIN_DUNGEON` code at all, T013 § 13), and the 60 triage-only rows |
| unresolved | 3 | 63 | 11.88.16 (no-op handler), 11.118.16 (handler discards the u8), 29.23.16 (handler reads nothing; PS4 candidate rejected) |
| **total** | **115** | **4,796** | |

Check against the triage: `T001-triage.tsv` (sha256 `4459eea8ecbf1615…`) has 526 uncovered ids; 411
of them are declared by a pattern (`// packet-id:` of `research/03040008/packets/*-pattern.cpp`, login
patterns as `L:g.i.s`), so 526 - 411 = 115 rows, all listed. Of the triage's 94 `exclusive` rows, 93
are here; 31.40.1 `C2S_CLAN_CLAN_PARTNER_PAWN_DATA_GET_REQ` was patterned (T010, the PS4 DWARF type
`CPacket_C2S_CLAN_PARTNER_PAWN_DATA_GET_REQ` backs it). The 22 triage `unresolved` rows that remain were
decided by their batch: 19 exclusive (4 V, 15 I), 3 still unresolved.

Sources: 55 rows come from a batch report (T004 5, T005 12, T006 3, T008 5, T009 5, T010 7, T011 1,
T012 3, T013 14); 60 rows are triage-only, the whole groups no batch covered: 62 SEASON_DUNGEON (35),
59 INFINITY_DELIVERY (8), 72 DAILY_MISSION (7), 61 PAWN_TRAINING (2), 65 EQUIP_ENHANCED (2), 70
ACTION (2), 71 BATTLE_CONTENT (2), 60.0.2 NPC_GET_NPC_EXTENDED_FACILITY_RES and 64.0.1
MANDRAGORA_GET_MY_MANDRAGORA_REQ (their partners 60.0.1 and 64.0.2 are patterned). Their exclusivity
is the triage's rule (a PC string names the packet, no PS4 symbol carries the name and no PS4 body
has a unique matching shape; groups 62 and 72 unnamed NTCs by group, T001 § Method 6), so I.

## Columns

- `id`, `raw_name`, `group`, `captured`, `pc_va`, `triage_mark`: from `T001-triage.tsv` (`pc_va` is
  the PC 03040008 handler (S2C) or writer (C2S), image base 0x400000).
- `status`: exclusive V / exclusive I / unresolved, as above.
- `report_ps4_mark`: the PS4 column of the batch report's summary table (`-` for triage-only rows).
- `report`: the report and section that decides the id (`T001 (triage)` when no batch read it).
- `pc_layout`: what the PC code shows of the body: the body bytes of the report's summary table
  (RES bodies after `Error == 0`; `+kn` = list of k-byte elements; `var` = nested lists or strings),
  for group 63 the order and widths of the T013 § 13 table. The wire layouts in field detail are in
  the cited sections (for example T004 § 10 and § 13, T005 § 7-8 and § 40-42, T012 § 12: 27.10.2 is
  `MtTypedArray<CDataAchievementProgress>` of `include/Achievement.hexpat`). Triage-only rows were not
  read in spec 006.

## Method and limits

Generated with stdlib Python (`csv`, `re`): the triage rows minus the pattern ids; for each, the batch
report row starting `| <id> |` with at least six cells, its section the first `## ` heading naming the
id or its `g.i.x`/`g.x` form, else the first section after § 0 that mentions the id outside the
summary. Status from the mark text as listed above. Not checked: the PS4 side of the 60 triage-only
rows beyond the triage's symbol and shape search; the generator is not committed (the table is the
artifact; rerun by the rule above).
