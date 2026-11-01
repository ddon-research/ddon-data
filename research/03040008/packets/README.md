# Packet patterns, client 03040008

ImHex patterns for the decrypted packets of the PC client 03040008 (Season 3) in
`packets/decrypted_raw/`, exported to `packets/decrypted_json/`. Spec 005
(`specs/005-netmsg-patterns/`) built them. Its reports in `specs/005-netmsg-patterns/research/` hold
the evidence each pattern cites (P1, P2, P4, P5, P11a, P11b) and the reviews (R1, R2).

## How the patterns are built

Each packet type has one file, `<packet name>-pattern.cpp`, named after the packet name the raws
carry now. Every pattern starts with `#pragma endian big` and includes what it needs from `include/`:

| Include | Holds | Patterns |
| --- | --- | --- |
| `Packet.hexpat` | the raw framing `CPacket` (u8 group, u16 id, u8 sub, u8 source, u32 counter; body at 0x09), `MtTypedArray<T>` (u32 count + entries), `MtString` (u16 length + bytes), `CDataCommonU32`/`CDataCommonU8`, the fit-flag rules and the RES convention | every pattern without nNetMsg |
| `nNetMsg.hexpat` | the nNetMsg (cNetMsg RPC) payload of the lobby and party binary packets: ids, DTI enum, message structures (P1, P2, P3) | 3.3.16, 3.4.16, 6.23-6.26.16 |
| `Context.hexpat` | group 35 CONTEXT structures (P4) | 11 group-35 patterns |
| `Quest.hexpat` | group 11 QUEST CData and the enums ORDER_CONDITION_TYPE, CYCLE_CONTENTS_CATEGORY, CYCLE_CONTENTS_SUB_CATEGORY, COMMAND_CHECK_LIST (P11a) | 5 |
| `Area.hexpat` | group 23 AREA CData (P11a, P11b) | 4 |
| `Character.hexpat` | E_WALLET_POINT_TYPE, CDataWalletPoint, job base info, character name and list element | 2 |
| `Clan.hexpat`, `Item.hexpat`, `Pawn.hexpat`, `Skill.hexpat` | the CData of those groups (P11b) | 1-2 each |

Each structure comment names the PC reader or writer VA (PC 03040008 database, image base 0x400000)
and the PS4 02020005 DWARF type, and carries a mark: V means read in IDA, I means inferred. A name
that is not proven stays `unk_*`. A Season 3 field with no PS4 counterpart is labelled that way.

**Header comment.** It gives the packet id and name, the evidence (report section, PC VAs), a body
summary, and two lines the export script reads:

- `// packet-id: <group>.<id>.<sub>`: the id that `imhex-export.sh @` selects by.
- `// packet-select: <name>`: only where another server uses the same id. With it, `@` keeps only
  the files of that id whose name holds `_<name>_`. `C2L_LOGIN_REQ` (0.1.1) and `L2C_LOGIN_RES`
  (0.1.2) carry it, because the game server's `C2S_CONNECTION_LOGIN_REQ` and
  `S2C_CONNECTION_LOGIN_RES` use the same ids (R2 F2).

**JSON conventions.** The root key is `packet`. Header keys are lowercase (`group`, `id`, `subId`,
`source`, `packetcounter`). Lists export as `{count, entries}` and strings as `{length, value}`.

**RES error guard.** The PC reads `s32 Error`, and reads Result and the body only when Error is 0
(P11a G1). PS4 reads a u16 Error; the captures back the PC's s32 (R2). Every RES pattern writes the
guard inline, `s32 Error; if (Error == 0) { s32 Result; ... }`, so every RES JSON holds
`packet.Error` and, on success, `packet.Result` (R2 F3). There is no `ResHeader` struct.

There is one exception. On 18.0.2 the server writes Result and an empty list after a non-zero
Error, although the client stops reading after Error. The pattern decodes those 8 bytes as
`unk_serverResult` and `unk_serverListCount`, and only when more than 15 bytes remain.

**Exported checks.**

- `sourceOk`: the header source byte matches the direction in the name (0x00 client for C2S/C2L,
  0x34 server for S2C/L2C). 63.11.16 has source 0x00 although its name says S2C (P10).
- `paddingSize`: the bytes left after the decode (the slack).
- `fits`: `paddingSize <= 15`. The raws store no body length and are padded to 16-byte blocks, so a
  decode fits when it ends inside the cipher padding. Reading past the end fails the decode.
- `msgFits` (nNetMsg patterns only): the message ended exactly at its `len` field.

A fit proves that the decode did not overrun the packet and left less than one cipher block. It
does not prove field widths or field order. When the slack is larger than a field, a body that is
that field shorter or longer fits as well (a 16-byte packet fits any body of 0-7 bytes). Two
same-width fields in swapped order fit identically (R1 F3, R2 F1). Widths and order rest on the PC
readers and writers.

## How to export

```
packets/imhex-export.sh [--force] [--json-nonfinite=keep|null] <filter> <pattern-name> [jobs]
packets/imhex-export.sh --force @ S2C_CONTEXT_GET_SET_CONTEXT_RES
```

The filter selects raw files three ways:

- `@` takes the pattern's `// packet-id:` and, if present, its `// packet-select:`.
- `g.id.sub` takes the files whose names end in `.g_id_sub`.
- Anything else is a substring of the file names.

`@` refuses an id that login-server (`C2L_`/`L2C_`) and game-server (`C2S_`/`S2C_`) files share,
unless the pattern names its packet with `// packet-select:` (test: `tests/imhex-export-select.sh`).

The engine is plbatch (`research/imhex/plbatch`, built with its `build.sh`): PatternLanguage at the
commit ImHex 1.38.1 embeds, one process per shard. Without plbatch, the script runs one
`imhex --pl format` per packet. The summary line counts:

- `exported`, `skipped` and `failed` packets;
- `nonfinite`: outputs holding a bare `nan` or `inf`, which is not valid JSON unless you pass
  `--json-nonfinite=null`;
- `badjson`: invalid output, counted as a failure.

A failed packet leaves `<file>.json.err` and removes its old JSON. Output paths must stay under 260
characters. For details, see `packets/README-decrypt-annotate-streams.adoc`, section "Exporting
packet structures with ImHex".

## Evidence rules

- PC code comes first: the PC 03040008 reader (S2C) or writer (C2S) decides the layout. Captures
  confirm a layout; they do not prove it.
- PS4 02020005 is matched to PC by code (handler and reader structure, strings), never by packet
  number: PS4 packet numbers do not identify PC packets.
- The PS4 recompilation C++ is the baseline wherever it has a ReadPacket or WritePacket body. For
  the 36 older patterns it has none (stubs or no body, R2), so only its class layouts were compared.
- The server's C# (Arrowgene) is a lead only. Its names appear as `server: <name> (lead)`.
- Enums come from PS4 DWARF only. A value with no DWARF name is `UNK_<value>`.
- Every inferred position or name is marked (I) or stays `unk_*`.

## Patterns

Status `n/m fit` means that n of the m JSON files of that type in `packets/decrypted_json` have
`fits` true (counted 2026-11-01 after commit cc7ebd0fb3; no type has a `.json.err`). `no capture`
means no raw file exists, so the pattern was checked on synthetic input at most. The Report column
gives the section the pattern header cites: P11a and P11b are
`specs/005-netmsg-patterns/research/P11*-old-patterns.md`, and P1, P4 and P5 are the reports of
those names.

| Id | Pattern | Report | Status |
| --- | --- | --- | --- |
| 0.1.1 | `C2L_LOGIN_REQ` | P11b §2 | 42/42 fit |
| 0.1.2 | `L2C_LOGIN_RES` | P11b §3 | 42/42 fit |
| 2.13.16 | `C2S_CHARACTER_CHARACTER_DOWN_NTC` | P4 §4 | 14/14 fit |
| 2.14.16 | `C2S_CHARACTER_CHARACTER_DOWN_CANCEL_NTC` | P4 §4 | no capture |
| 2.15.16 | `C2S_CHARACTER_CHARACTER_DEAD_NTC` | P4 §4 | 7/7 fit |
| 2.19.16 | `C2S_CHARACTER_PAWN_DOWN_NTC` | P4 §4 | 20/20 fit |
| 2.20.16 | `C2S_CHARACTER_PAWN_DOWN_CANCEL_NTC` | P4 §4 | 10/10 fit |
| 2.21.16 | `C2S_CHARACTER_PAWN_DEAD_NTC` | P4 §4 | no capture |
| 3.3.16 | `C2S_LOBBY_LOBBY_DATA_MSG_REQ` | P1 §1.1 | 59881/59881 fit |
| 3.4.16 | `S2C_LOBBY_LOBBY_DATA_MSG_NTC` | P1 §1.1 | 21000/21000 fit |
| 6.23.16 | `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC` | P1 §1.1 | 8/8 fit |
| 6.24.16 | `S2C_PARTY_RECV_BINARY_MSG_ALL_NTC` | P1 §1.1 | no capture |
| 6.25.16 | `C2S_PARTY_SEND_BINARY_MSG_NTC` | P1 §1.1 | 29176/29176 fit |
| 6.26.16 | `S2C_PARTY_RECV_BINARY_MSG_NTC` | P1 §1.1 | no capture |
| 8.30.2 | `S2C_PAWN_GET_NORA_PAWN_LIST_RES` | P11b §14 | 41/41 fit |
| 9.0.2 | `S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES` | P4 §3 | no capture |
| 9.1.1 | `C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ` | P4 §3 | 47/47 fit |
| 10.9.2 | `S2C_ITEM_GET_ITEM_STORAGE_INFO_RES` | P11b §13 | 4/4 fit |
| 11.15.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES` | P11a §5 | 6/6 fit |
| 11.19.2 | `S2C_QUEST_GET_AREA_BONUS_LIST_RES` | P11a §9 | 182/182 fit |
| 11.37.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES` | P11a §12 | 41/41 fit |
| 11.56.2 | `S2C_QUEST_GET_AREA_INFO_LIST_RES` | P11a §11 | 1/1 fit |
| 11.71.2 | `S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES` | P11a §4 | 43/43 fit |
| 11.89.16 | `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC` | P11a §1 | 41/41 fit |
| 11.120.16 | `S2C_QUEST_PARTY_QUEST_PROGRESS_NTC` | P11a §3 | no capture |
| 12.0.2 | `S2C_STAGE_GET_STAGE_LIST_RES` | P11a §7 | 42/42 fit |
| 13.3.2 | `S2C_INSTANCE_ENEMY_KILL_RES` | P11b §15 | 412/412 fit |
| 13.44.16 | `C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC` | P4 §4, P5 §7 | 19/19 fit |
| 13.45.16 | `C2S_INSTANCE_CHARACTER_END_BAD_STATUS_NTC` | P4 §4, P5 §7 | 19/19 fit |
| 13.46.16 | `C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC` | P4 §4, P5 §7 | 31/31 fit |
| 13.47.16 | `C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC` | P4 §4, P5 §7 | 30/30 fit |
| 18.0.2 | `S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES` | P11b §18 | 41/41 fit |
| 19.1.2 | `S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES` | P11b §16 | 4/4 fit |
| 19.2.2 | `S2C_SKILL_GET_ACQUIRABLE_ABILITY_LIST_RES` | P11b §17 | 16/16 fit |
| 23.0.1 | `C2S_AREA_GET_AREA_MASTER_INFO_REQ` | P11a §18 | 42/42 fit |
| 23.0.2 | `S2C_AREA_GET_AREA_MASTER_INFO_RES` | P11a §17 | 42/42 fit |
| 23.3.2 | `S2C_AREA_GET_AREA_SUPPLY_INFO_RES` | P11b §10 | 13/13 fit |
| 23.4.1 | `C2S_AREA_GET_AREA_SUPPLY_REQ` | P11b §9 | 12/12 fit |
| 23.8.2 | `S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES` | P11a §15 | 131/131 fit |
| 23.9.1 | `C2S_AREA_GET_AREA_QUEST_HINT_LIST_REQ` | P11a §14 | 183/183 fit |
| 23.9.2 | `S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES` | P11a §13 | 183/183 fit |
| 23.11.1 | `C2S_AREA_GET_SPOT_INFO_LIST_REQ` | P11b §8 | 29/29 fit |
| 23.11.2 | `S2C_AREA_GET_SPOT_INFO_LIST_RES` | P11b §11 | 29/29 fit |
| 23.12.2 | `S2C_AREA_GET_AREA_BASE_INFO_LIST_RES` | P11a §16 | 72/72 fit |
| 23.13.16 | `S2C_AREA_POINT_UP_NTC` | P11b §7 | 29/29 fit |
| 31.4.2 | `S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES` | P11b §6 | 41/41 fit |
| 31.17.2 | `S2C_CLAN_CLAN_SETTING_UPDATE_RES` | P11b §5 | 42/42 fit |
| 31.29.1 | `C2S_CLAN_CLAN_GET_MY_INFO_REQ` | P11b §1 | 41/41 fit |
| 31.29.2 | `S2C_CLAN_CLAN_GET_MY_INFO_RES` | P11b §4 | 41/41 fit |
| 35.0.16 | `S2C_CONTEXT_GET_LOBBY_PLAYER_CONTEXT_NTC` | P4 §2.3 | 264/264 fit |
| 35.3.16 | `S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC` | P4 §2.2 | 9/9 fit |
| 35.5.16 | `C2S_CONTEXT_35_5_16_NTC` | P4 §2.3 | 2/2 fit |
| 35.7.1 | `C2S_CONTEXT_GET_SET_CONTEXT_REQ` | P4 §2.3 | 223/223 fit |
| 35.7.2 | `S2C_CONTEXT_GET_SET_CONTEXT_RES` | P4 §2.3 | 608/608 fit |
| 35.8.16 | `C2S_CONTEXT_SET_CONTEXT_BASE_NTC` | P4 §2.3 | no capture |
| 35.9.16 | `C2S_CONTEXT_SET_CONTEXT_NTC` | P4 §2.3 | 763/763 fit |
| 35.11.16 | `S2C_CONTEXT_SET_CONTEXT_BASE_NTC` | P4 §2.3 | 526/526 fit |
| 35.12.16 | `S2C_CONTEXT_35_12_16_NTC` | P4 §2.3, P5 §7 | no capture |
| 35.13.16 | `S2C_CONTEXT_SET_CONTEXT_NTC` | P4 §2.3 | 24/24 fit |
| 35.14.16 | `S2C_CONTEXT_MASTER_CHANGE_NTC` | P4 §2.3 | 948/948 fit |
| 35.15.16 | `S2C_CONTEXT_MASTER_INFO_NTC` | P4 §2.3 | 43/43 fit |
| 51.0.2 | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES` | P11a §6 | 1/1 fit |
| 52.1.2 | `S2C_MY_ROOM_FURNITURE_LIST_GET_RES` | P11a §10 | 20/20 fit |
| 57.0.2 | `S2C_BOX_GACHA_BOX_GACHA_LIST_RES` | P11a §8 | 3/3 fit |
| 60.0.1 | `C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ` | P11b §12 | 219/219 fit |
| 63.11.16 | `S2C_63_11_16_NTC` | P5 §7 | 1/1 fit |
| 64.0.2 | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES` | P11a §2 | 20/20 fit |

## Open items

- **Save blob bit walk (9.1.1):** `C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ` decodes the two
  version fields. The rest of the `cCharacterData::serialize` bit stream stays `undecoded` bytes
  until someone reads the BitWriter bit order (P4 §3.1).
- **35.12.16 tail:** `S2C_CONTEXT_35_12_16_NTC` decodes up to its second list. The list element that
  PC 0x76fc20 reads and the count that 0x757e60 reads are not decoded (P4 §5), so `decoded` is
  false. There is no capture.
- **Unnamed 13.44-13.47.16:** the client names are unresolved (P5 §7). The pattern names are the
  names in the raws, which come from the server.
- **QuestEnemyInfo u32 position:** PC reads {u32, u32, u16, bool}; PS4 has {u32 GroupId, u16, bool}.
  P11a §1.3 puts the Season 3 u32 first, while the earlier include put it second, so both are now
  `unk_u32_0` and `unk_u32_1` (R2 F1). The committed JSON of 11.89.16, 11.71.2 and 11.15.2 (67 files)
  keeps the old keys `GroupId` and `unk_u32` until those types are re-exported. A scratch re-export
  showed the rename as the only change.
- **Season 3 field names:** fields new in Season 3 are `unk_*`. Where PC adds one field to a run of
  same-width fields, its position is inferred: BoxGacha u32, AreaBonus u16, MyRoomFurniture u32, and
  the CDataQuestOrderList u32s and u64s (R2 F5).
