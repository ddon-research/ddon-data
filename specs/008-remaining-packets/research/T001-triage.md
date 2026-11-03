# 008 T001: triage of the captured packet ids without a pattern (client 03040008)

Date 2026-11-03, base `91c9bdf3f5`. Per-id table: `T001-triage.tsv` (115 rows); scripts and
intermediate output in `t001/`. Addresses are PC 03040008 VAs (image base `0x400000`).

## 1. Answer

- **115 uncovered ids, 4,887 captured files** (70 S2C, 45 C2S; 41 REQ, 41 RES, 33 NTC; all game server, no
  login id). They are the 115 ids of `season3-exclusive.tsv`, none added or gone. TC3 raised the counts of four:
  62.26.16 354 → 428, 27.10.1 5 → 19, 27.10.2 17 → 19, 63.10.16 11 → 12 (+91 files over 006's 4,796).
- **Every id has a PC root**: S2C the handler-table callback, C2S a `WritePacket` sender with the constant key; 114
  from the v6 dump, 45.4.1 from IDA (§ 4).
- **The PC codec trees fit 4,885 of 4,887 files**: 89 ids in plain form from the dump, 5 C2S ids when one writer callee
  is read as a list (I), 17 ids that read nothing and have empty bodies, and 3 ids read in IDA. The 2 misfits are
  both files of 29.23.16, whose handler ignores its 87-byte body (V, § 4). No RES capture carries an Error ≠ 0.
- **Arrowgene (fork `88d82caf07`)** names all 115 ids in `PacketId.cs` and has a structure class for 87 of them.
  The parser turns 84 of those into token sequences. All 84 fit every capture, and **81 match the PC shape
  exactly**; the other 3 lay out the same bytes in another form (§ 3). 28 ids have a name only: all of groups 72
  and 59 (15), group 28 (5), 11.7.16, 11.88.16, 11.118.16, 29.23.16, 62.27.16, 63.3.16, 63.5.16 and 63.6.16.
- **IDA reading still needed** is small. The layouts are known (V from the dump or IDA); what remains is mainly
  the field meanings, from captures, extractor data and leads. See § 5 for the per-batch IDA list.

## 2. Method

1. **Inventory** (`t001/inventory.py`, stdlib `os.scandir`): every file in `packets/decrypted_raw/*/`, named
   `<n>_<NAME>_<time>.<g>_<id>_<sub>` (160,615 files in 125 streams, 0 unparsed). The side is login for the
   `C2L`/`L2C` name prefixes and game otherwise (006 T001 § Method 1). From these ids it removes the
   `// packet-id:` lines of the 480 `research/03040008/packets/*-pattern.cpp` (480 ids; the pattern file prefix
   gives the side). This leaves 587 distinct captured ids, 472 covered and 115 uncovered. Eight pattern ids have no
   capture (2.14.16, 2.21.16, 6.24.16, 6.26.16, 9.0.2, 11.120.16, 35.8.16, 35.12.16). Body bytes = file size − 9
   (header) and include ≤ 15 bytes of cipher padding. A `body_max` of 7 means the 16-byte minimum file.
   Output: `t001/inventory.json` (files per id, per stream, raw names, body range).
2. **PC facts** (`t001/triage.py`, stdlib) over `research/03040008/ida-transfer/dumps/pc-ida.jsonl`. This is the
   v6 dump (sha256 `79827380…26abb` = `MANIFEST.tsv`, input sha256 `f1c974d0…fa20`, taken from the 007 work copy).
   - S2C: the `table` record's `callback` for (g,id,sub). C2S: the functions calling `WritePacket` `0x8BCBB0` with
     constant stack slots 1, 2, 3 = g, id, sub (`const_stack`). 642 such sites are in the dump.
   - The `OnPacket_` name is the `strings` record of the handler; the dump also gives the 007 annotation names
     (`Send_C2S_…`, `OnPacket_…`).
   - The codec tree takes codec leaves in call-site order. Widths come from the dump's `codec` field, and the four
     variable-length codecs from their VAs, as in `matcher/codecs.py`. The walk enters every dumped callee except
     `callOnPacketFunc`, the allocator, `WritePacket`, the CRT and callees whose `codec_distance` is null. Indirect
     calls are counted, never entered (the `indirect` column).
   - **List shape (I, own heuristic)**: a read-4 is taken as a count when the allocator `0x8BC2E0` follows within
     two calls, or when the next call is a helper that is called again later in the same function (the
     `MtTypedArray` resize; inline-element lists allocate nothing, e.g. `0x757F20`). The element is everything up
     to the helper's next call. Writers carry no allocator, so a C2S tree that fails plain is retried with the
     first write-4 of chosen callees as counts. All subsets of up to 6 candidates are tried and the best is kept,
     reported as `writer-lists <va>`.
   - Rendering in `width_seq` (full trees: `t001/width-trees.txt`): `1 2 4 8` widths, `S` MtString, `C`
     `Write_cstr`, `<va>{…}` a callee, `L[…]` a counted list.
3. **Fit**: the body starts at file offset 9 and the decode must end within the last 15 bytes without overrunning
   (006 rule). Lists are expanded from their u32 counts. `S`/`C` are a u16 length plus bytes; `C` is inferred from
   the 12.5.1 captures, where the length 0x2A covers exactly the UTF-8 text with no terminator. A RES whose s32 Error
   ≠ 0 counts as `fit_err` (none occur). Every RES reader reads s32 Error and s32 Result itself, so they are the
   tree's first two 4s.
4. **Leads**: Arrowgene `PacketId.cs` (name, line, trailing comment) and the class whose `Id` is that PacketId, under
   `Entity/PacketStructure` or `Entity/Structure`. Its `Write(...)` statements are mapped to tokens (`WriteServerResponse`
   = 4 4, `WriteEntityList` = `L[...]`, entities expanded recursively). A statement the parser does not know
   leaves `ag_fit` empty. `ag_vs_pc` compares the shapes without VAs. Fork `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline`
   `88d82caf07` (2026-03-30). Against the `.Upstream` clone (`e2411fe8f9`, 2026-09-06) only 5 rows differ:
   11.5.1/11.5.2 name `Unk0` as `StageNo`, 63.7.16 uses `CDataStageLayoutInfo`, and 63.5.16/63.6.16 have names
   (`C2S_CHAIN_DUNGEON_END_CHAIN_NTC`, `S2C_CHAIN_DUNGEON_REWARD_CHEST_APPEAR_NTC`, which agree with the raw
   names) and a structure for 63.6.16.
5. **006 notes**: `status`, `report` and `pc_layout` from `season3-exclusive.tsv`.

Commands (from `D:/ddon-data`):

    python -X utf8 -I specs/008-remaining-packets/research/t001/inventory.py specs/008-remaining-packets/research/t001/inventory.json
    python -X utf8 -I specs/008-remaining-packets/research/t001/triage.py specs/008-remaining-packets/research/t001/inventory.json \
        specs/008-remaining-packets/research/T001-triage.tsv specs/008-remaining-packets/research/t001/width-trees.txt

## 3. Findings worth a batch's attention

- **Shapes inferred, not proved (I)**: 70.0.1 (`0x77D1E0` = list of {u8,u32}), 62.24.1, 62.10.1 and 12.5.1 (`0x77FD30`
  = list of {MtString,u32}, empty in every capture), and 62.34.1 (`0x77F9D0` = list of {u32,u32}). Writer loops need
  one look in IDA to become V. Arrowgene agrees with all five.
- **Same bytes, another form (lead vs PC)**: 10.14.16 (PC u16 + list `0x76CC70` {u8,u32}; AG writes one fixed element,
  2 4 1 4), 34.0.1 (PC `0x77DFF0` {4 8} plain, AG `L[8]`: the same bytes when the list holds one entry), and 14.11.16
  (PC sender writes one u32; AG empty; every body is ≤ 7 bytes).
- **Weak fits**: 22 ids have only 16-byte files (`body_max` 7) and read ≤ 7 bytes, so padding alone cannot confirm
  their width (TSV rows with `body_max` = 7 and `leaves` > 0). The PC tree is still V for them.
- **Shared structures across ids**: `0x766790` {4 1 4 4 1} (62.26.16, 62.15.16); `0x779090` list {1 1 4 4 S} (62.14.16,
  62.16.16); C2S {4 1 4 4} (62.12.16, 62.18.1, 62.33.1, 62.8.1, 62.40.16, and inside 62.34.1/62.35.1); `0x762460`
  daily-mission list (72.0.2, 72.3.2); `0x769FE0`/`0x769DE0` (59.0.2, 59.4.2, 59.9.2); `0x762C50` list {4 1 4 4}
  (63.6.16, 63.7.16); `0x77C5A0` list {1 4} wallet (11.122.2, 41.8.2, 65.3.2); `0x75E8E0` CDataCommonU32 list.
- **Names**: the 41 RES handlers all carry their `OnPacket_` string (V). Their REQ partners take the name by pairing
  (I). The 007 work copy already names 10 senders `Send_C2S_…`. NTCs have no PC string; their names are leads (G)
  or from context. 11.123.2's string is `QUEST_GET_ADVENTURE_GUIDE_QUEST_NOTICE_RES`; the raw and AG name is
  `…_NTC_RES`.

## 4. IDA reads (private copy of the accepted PC database)

Copy: `bash research/ida/private-copy.sh pc-accepted t001` →
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t001/2022_01_29_DDO_DUMP_FIX.exe.i64`. Confirmed 32-bit,
image base `0x400000`, `get_idb_path` = that copy. The copy was read only: no rename, retype, comment or save.

| id | finding | mark |
| --- | --- | --- |
| 45.4.1 | Sender `0x83F5A0`, which is no function in the database (junk bytes `90 0D 31 2B` at `0x83F59C`; called from `0x87869B` in `sub_878650`). It does `push 1; push 4; push 2Dh` then `WritePacket` at `0x83F613`, followed directly by `cSeedServerConnection::Send`, so the body is empty. | V (the start at 0x83F5A0 is I, from the call target) |
| 63.2.16 | Handler `0x7D1BE0` is no function in the dump. It calls reader `0x806610`: `Read_bool, Read_u8, Read_u32 ×4`, then list `0x762B40` {`Read_u8, Read_u32, Read_MtString`}. This equals 006 T013 § 13 and fits 21/21. | V |
| 50.0.16 | `0x75E6E0` `Read_CDataItemSort_`: a u32 count; each element is `Read_u8`, then a `while (Read_u8(...)) if (++i >= 0x400) …` loop over a 0x400-byte array (memset 0x400). So the element is u8 + u8[1024], matching 006's 4+1025n. It fits 48/48. | V |
| 29.23.16 | Handler `0x7D5730` is `return 1` (8 bytes): the 87-byte body is ignored. The layout can only come from captures or a lead, and Arrowgene has no structure. | V (no reader) |
| 11.122.2 | `0x775420` reads u16 ×3, then `0x7754A0` (list {u32, s32 ×4}), `0x757F20` (a list of `0x7738F0` lists with no allocation, which led to the list rule above) and `0x7738F0` (list {u16, s32 ×4}). With that rule the dump tree fits 45/45, up from 19/45. | V |

The worker could not be closed (`close_database` is withheld). `rm -rf` of `ddon-data-t001/` removed the `.i64`, but
the open worker holds `.id0`, `.id1` and `.nam` ("Device or resource busy"). **The coordinator should delete
`D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t001/` once the worker is gone.**

## 5. Batches (by group and shared structures; ordered by captured files)

| batch | ids | files | content | IDA reading needed |
| --- | ---: | ---: | --- | --- |
| B5 | 18 | 1,375 | 70 ACTION, 60.0.2 NPC extended facility, 28 GP (5), 24.6.16 job master marks, 45 STAMP (4), 31.53 clan furniture, 61.2 pawn training, 64.0.1 mandragora | 70.0.1 writer loop `0x77D1E0` (I → V); group 28 has no AG structure |
| B2 | 15 | 1,302 | 11 QUEST (11.5, 11.7, 11.68, 11.88, 11.118, 11.121-123), 14 WARP (14.11.16, 14.14) | none for widths; 11.88.16 (no-op handler) and 11.118.16 (u8 discarded) stay meaning-open (006); 11.122.2's deep tree (23 functions) wants a field-naming pass |
| B1 | 20 | 1,215 | 62 SEASON_DUNGEON soul ordeal: 62.12/14/15/16/22/23/26/40 NTCs, 62.18, 62.20, 62.24, 62.33-35 | 62.24.1 and 62.34.1 writer loops (`0x77FD30`, `0x77F9D0`) |
| B4 | 17 | 416 | 72 DAILY_MISSION (7), 59 INFINITY_DELIVERY (8), 71.22 battle content | none for widths (all fit V); no AG structure for groups 72 and 59, so names come from the PC strings and context (59.x RES have only 1-2 captures) |
| B3 | 18 | 376 | 62 SEASON_DUNGEON info/blockade/EX/area: 62.0, 62.1, 62.7-10, 62.27/38/39.16; 12.5 (unison recruitment), 12.9.16 dungeon start | 62.10.1 and 12.5.1 writer loop `0x77FD30`, and 12.5.1's `Write_cstr` wire form (`0x8BCA30`, read from captures only) |
| B7 | 14 | 107 | 50.0.16 item sort, 27.10 achievement category, 41.5/41.8 character edit, 65.3 equip-enhanced packs, 2.5.16, 29.23.16, 34.0 entry board, 10.14.16 | done (§ 4); 29.23.16 has no reader: captures only (8+18n per 006), mark G |
| B6 | 13 | 96 | 63 CHAIN_DUNGEON (8), 13 INSTANCE (13.16, 13.17, 13.23.16) | done (63.2.16, § 4) |

## 6. Limits

- The list rule is a heuristic over call order, not a CFG. It is checked only by the fits (4,885/4,887) and by the
  three IDA reads. Fixed-count inline arrays (50.0.16) are invisible to it.
- Call-site order is the order of the code, not of execution. A branch that reads alternatives would look like a
  sequence; none was found among the fitting ids, but where only weak fits exist that is not tested.
- The dump is from the 007 work copy (`ddon-data-007work`); the IDA reads used the accepted database. Both
  are the same input binary (`f1c974d0…`).
- Captures prove shapes, not semantics. Signedness and float/int are not given by the widths (T005b § 0).

## 7. Identities

- `T001-triage.tsv` (columns: id, batch, raw_name, dir, files, streams, body_min/max, pc_role, pc_va, pc_func,
  pc_onpacket, readers, width_seq, leaves, lists, indirect, fit_ok/err/bad, fit_variant, ida_note, s006_*,
  ag_name, ag_packetid_line, ag_struct, ag_fields, ag_fit, ag_vs_pc). Its hash changes on each regeneration;
  run the command in § 2 and `sha256sum` it.
- `t001/inventory.json` sha256 `a3d54d2984b231143280521b828464c7d9af8a73b58063aefd24aea6bd6e1736`.
- `pc-ida.jsonl` sha256 `79827380b171fa8838ce81a98b28ac37e060675fb4c8bc3af815f51d43d26abb` (v6, `extract_ida` 6).
