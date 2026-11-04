# 009 T004: where each section of the packet docs went

Sources at base `715f8f2305d`: `README` = `packets/patterns/03040008/README.md` (`research/03040008/packets/README.md` when T001 classified it), `adoc` = `packets/README-decrypt-annotate-streams.adoc`. Written by `T004-moves.py` from `T001-sections.tsv`. Spot-check: `T004-spotcheck.py`.

The explanation pages T001 named for some rows (`wire-protocol`, `packet-decoding-method`, `evidence-model`) belong to the next package. Until they exist, the rule or fact stands on the reference page this table names, so nothing waits on them.

| Source | Section | Lines | Went to | Note |
| --- | --- | --- | --- | --- |
| README | Packet patterns, client 03040008 | 1-7 | packets/patterns/03040008/README.md | short README; spec history lines 4-6 cut, spec 005 keeps them |
| README | How the patterns are built | 8-139 | see the [sub] rows |  |
| README | How to export | 140-170 | docs/how-to/export-packets-to-json.md, docs/reference/imhex-export-cli.md |  |
| README | Evidence rules | 171-182 | docs/reference/packet-marks.md § Evidence rules | the rules whole; the why is for the explanation page of the next package |
| README | Patterns | 183-845 | see the [sub] rows |  |
| README | Open items | 846-1215 | see the [sub] rows |  |
| adoc | Parallel CLI Runner README | 1-7 | packets/README.md | stale title dropped |
| adoc | Purpose | 8-12 | docs/how-to/reannotate-streams.md |  |
| adoc | Requirements | 13-21 | docs/how-to/reannotate-streams.md | stale: `flock` and `grep`, which the script does not use, are cut; gawk's `match` added |
| adoc | Configuration | 22-35 | docs/how-to/reannotate-streams.md § Variables |  |
| adoc | Usage | 36-48 | docs/how-to/reannotate-streams.md | stale `./run-parallel-packet.sh` corrected to `decrypt-annotate-streams.sh`; the script does not cd, so the page says run it from packets/ |
| adoc | Concurrency tuning | 49-55 | docs/how-to/reannotate-streams.md § Variables |  |
| adoc | Required Arrowgene CLI patches | 56-186 | docs/how-to/patch-the-arrowgene-cli.md, docs/reference/arrowgene-cli-patches.md | reasons on the reference page; the why is for the explanation page of the next package; export comparisons cut, see below |
| adoc | Splitting large dumps | 187-200 | docs/how-to/reannotate-streams.md § Split large dumps |  |
| adoc | Exporting raw packets | 201-247 | docs/how-to/reannotate-streams.md § Export raw packets, docs/reference/packet-pattern-format.md § Raw file names | export history cut, see below |
| adoc | Exporting packet structures with ImHex | 248-316 | docs/how-to/export-packets-to-json.md, docs/reference/imhex-export-cli.md, docs/reference/packet-pattern-format.md | measurements to docs/reference/status.md |
| adoc | Packet statistics | 317-328 | docs/how-to/refresh-packet-statistics.md | `unknown` file, `-k`, `-f` and `ANNOTATED_DIR` added from the script |
| README | [sub] Include table | 13-49 | docs/reference/packet-includes.md | history wording cut; `CharacterData.hexpat` row added |
| README | [sub] Structure comment and marks | 51-56 | docs/reference/packet-marks.md |  |
| README | [sub] Naming unknown fields by inference | 58-84 | docs/how-to/name-an-unknown-field.md, docs/reference/packet-marks.md § Comment forms | the count of T014c's application is in 006 tasks |
| README | [sub] Header comment | 86-103 | docs/reference/packet-pattern-format.md § Header comment | reason history in 005 R2 F2, 006 T002c |
| README | [sub] JSON conventions | 105-114 | docs/reference/packet-pattern-format.md § JSON conventions |  |
| README | [sub] RES error guard | 116-123 | docs/reference/packet-pattern-format.md § RES error guard | rule and 18.0.2 exception; the why is for the explanation page of the next package |
| README | [sub] Exported checks | 125-132 | docs/reference/packet-pattern-format.md § Exported checks |  |
| README | [sub] What a fit proves | 134-138 | docs/reference/packet-pattern-format.md § Exported checks | the rule; the why is for the explanation page of the next package |
| README | [sub] Patterns: status meaning and report key | 185-234 | docs/reference/packet-ids.md § Report labels, § Reading the table; docs/reference/packet-marks.md | dated recount prose reduces to one date |
| README | [sub] Patterns: how value bases are counted | 235-246 | docs/reference/packet-marks.md § Value bases | rule, density formula and item density; the why is for the explanation page of the next package |
| README | [sub] Patterns: the per-id table | 248-844 | docs/reference/packet-ids.md § The table | 595 rows intact; 31 counts corrected in their own commit |
| README | [sub] Open item: Code-backed renames (spec 006 TC2): | 848-857 | cut (history) | docs/reference/arrowgene-cli-patches.md § Names from code holds the eight renames; the `(was ...)` notes stay on packet-ids.md |
| README | [sub] Open item: 0.10.16 lobby member: | 858-859 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Game setting names without code backing (T003 §11, §20): | 860-866 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Game-server RES error branch untested: | 867-869 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: 1.1.16 login reader not decoded: | 870-872 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Login RES error branch untested: | 873-875 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Login names without code backing (T002 §17): | 876-879 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Unnamed 35.12.16 and 13.44-13.47.16: | 880-884 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: 13.46/13.47 `unk_u32`: | 885-886 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Context variants without captures: | 887-889 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Season 3 nNetMsg names (T001c §6): | 890-894 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Season 3 field names: | 895-898 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Season 3-exclusive, not patterned (T004): | 899-903 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Season 3-exclusive, not patterned (T005): | 904-909 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Group 11 unresolved, not patterned (T005): | 910-912 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Group 11 names without code backing (T005 §46): | 913-924 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: `CDataTimeGainQuestList` bool order (R2b): | 925-927 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Group 11 code-only (T005 §43, §46): | 928-931 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Shared quest types moved (T005b): | 932-935 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: Season 3-exclusive, not patterned (T006): | 936-940 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Groups 3, 12, 23, 33 names without code backing (T006 §8): | 941-947 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 3, 12, 23, 33 code-only (T006 §5, §8): | 948-954 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: No existing pattern changed (T006b): | 955-957 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Group 13 widths that fit either way (T004 §19): | 958-962 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Group 13 lists never non-empty in captures (T004 §19, §22): | 963-965 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Group 13 names without code backing (T004 §22): | 966-974 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 8, 53, 58 names without code backing (T007 §8): | 975-981 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 8, 53, 58 code-only (T007 §5, §8): | 982-988 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: 53.9.16 message index: | 989-990 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Pawn types added, no existing pattern changed (T007b): | 991-996 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: 14.10.16 name: | 997-1000 | cut (history) | docs/reference/arrowgene-cli-patches.md § Names from code holds the call-site evidence (`0x840160`) |
| README | [sub] Open item: Season 3-exclusive, not patterned (T008): | 1001-1008 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Groups 10, 14, 50 names without code backing (T008 §8): | 1009-1014 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 10, 14, 50 code-only (T008 §5, §8): | 1015-1021 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Item and warp types added, no existing pattern changed (T008b): | 1022-1026 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: Season 3-exclusive and unmatched, not patterned (T009): | 1027-1033 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Groups 2, 37, 45 names without code backing (T009 §24): | 1034-1050 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: 2.29.16/2.30.16 identity (T009 §11): | 1051-1052 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 2, 37, 45 code-only (T009 §24): | 1053-1057 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: CDataCharacterListElement users already Season 3 (T009b): | 1058-1064 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: Season 3-exclusive, not patterned (T010): | 1065-1071 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Groups 28, 31 names without code backing (T010 §27): | 1072-1079 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 28, 31 code-only (T010 §27): | 1080-1087 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: GP and clan types added; one existing pattern changed (T010b): | 1088-1096 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: Season 3-exclusive, not patterned (T011): | 1097-1102 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Groups 5, 6, 16, 17, 26 names without code backing (T011 §20): | 1103-1108 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 5, 6, 16, 17, 26 code-only (T011 §20): | 1109-1113 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Character types added (T011b): | 1114-1119 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: StatusInfo MaxHp (T010 §23): | 1120-1122 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: u64 OM Key in JSON: | 1123-1125 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Season 3-exclusive, not patterned (T012): | 1126-1130 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Group 29 unresolved, not patterned (T012): | 1131-1134 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: Groups 19, 20, 25, 27, 29, 39, 43 names without code backing (T012 §21): | 1135-1142 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 19, 20, 25, 27, 29, 39, 43 code-only (T012 §21): | 1143-1149 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Types added (T012b): | 1150-1158 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: Season 3-exclusive or without PS4 counterpart, not patterned (T013): | 1159-1166 | cut (stale) | every id listed has a pattern; spec 006 reports keep the PC readers |
| README | [sub] Open item: 15.0.16/15.1.16 and 34.6.16 identity (T013 §7, §12): | 1167-1171 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 30, 34, 41, 51, 54 names without code backing (T013 §18): | 1172-1181 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Groups 30, 34, 41, 51, 54 code-only (T013 §18): | 1182-1188 | docs/reference/packet-open-questions.md | history wording cut; re-checked by `T004-names.py` |
| README | [sub] Open item: Craft, entry-board and dispel types added; no existing pattern changed (T013b): | 1189-1195 | cut (history) | the named report and spec 006 tasks hold it |
| README | [sub] Open item: Naming sweep (TC1, 2026-11-02): | 1196-1215 | cut (history) | the named report and spec 006 tasks hold it |

## Cut facts

History and stale facts on no page, with where they stay. The adoc and the README stay readable in Git at the base commit.

| Fact | Why cut | Stays in |
| --- | --- | --- |
| `0x758810`, `0x7ff650`, `0x81dc90`: 27.10.x list reader, RES reader, REQ writer | "not patterned" bullet, stale | 006 `T012-achievement-equip-skill.md`, 008 `T005-batches-B3-B7-B6.md` |
| `0x76abe0`: `CDataSwitchStorage` reader | history bullet (T008b) | 006 `T008-warp-item.md` |
| `0x76c5f0`, `0x7e0b70`: 24.6.16 element reader and handler | "not patterned" bullet, stale | 006 `T011-party-profile-friend.md`, 008 `T003-batches-B5-B2.md` |
| `d75b26ef7fcce075205e3a830e660781622687420dafad21447355dd4c6a32b1`: `Arrowgene.Ddon.Cli.dll` of the fixed-key build, 2026-11-01 | a superseded build | the adoc at the base commit only |
| `d311f08d2278e65dc6fdb1e02797899a2bbcd180d12ded268e51bb5446da03d0`: `Arrowgene.Ddon.Cli.dll` of the relabel and rename builds, 2026-11-01 and 2026-11-02 | a superseded build | the adoc at the base commit only |
| Export comparisons: 146,891 files byte-identical, 125 renamed certificate notices, 244 renamed files by id, 13,724 recovered packets in 41 streams (13,492 in stream85 tcp-stream-11; 3.3.16 6,394, 6.25.16 5,431, 35.7.1 560), 13,633 of 13,633 fit | a run's counts, history | 006 `tasks.md` (TC2, TC3), the adoc at the base commit |
| The 2024-05-13 export: 51 ids renamed (1,958 files), millisecond timestamps, 43 `1.0.1` files without the header | history of the raw tree; the resulting format is on `packet-pattern-format.md` | the adoc at the base commit |
| `T014c applied the 478 TSV rows (251 struct.field pairs)` | a run's count | 006 `tasks.md` |
| 91 packets with no pattern at the raw export (62.26.16: 74, 27.10.1: 14, 27.10.2: 2, 63.10.16: 1) | stale: all have patterns | 008 `tasks.md` |
| `T003`, `T004`, `T005` batch prose: "counts after their first export" per group | the recount replaces them; groups stay in the key | 006 and 008 `tasks.md` |
| P3's export of 110,065 nNetMsg packets at about 6 packets/s | a run's count; `plbatch-design.md` keeps the order of magnitude | 005 `tasks.md` |
| Server misplacement, lead only: Arrowgene's `CDataNormalSkillParam` swaps SkillNo and Index, and its 27.8.16 element lacks the u8 | history bullet (T012b) | 006 `T012-achievement-equip-skill.md` § 20 |
| Include changes and their `cmp` results (T005b, T007b, T008b, T009b, T010b, T011b, T012b, T013b), the naming sweep's key and type renames (TC1) | history bullets | 006 `tasks.md`; the include facts themselves are on `packet-includes.md` |
| 3,028-file comparison by way of the adoc, plbatch then at `fb6ea061` | moved, not cut | `docs/reference/status.md` |
