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
| `Login.hexpat` | login-server CData (T002 §15): URL info, login setting, game server list info, error message, and the character list types (matching profile, Season 3 equip item info, character list info); includes Character, Context and GP | 4 |
| `GP.hexpat` | GP course info, effect param and the Season 3 GP course valid (T002 §10, §11) | 1, and 5.0.2 through Login |
| `Cert.hexpat` | `CDataServerCert`, the server certificate notice body: modulus[256], exponent[16], SHA-1 u32[5] (T003 §1, §15) | 1.1.16, 44.1.16 |
| `Server.hexpat` | game-server connection setup CData (T003 §18): cheat info (ping), game setting with its Season 3 changes and element types, weather forecast, game time base info, weather loop/schedule, moon schedule; includes Login | 0.0.1, 1.0.2, 1.1.2, 1.7.2, 1.8.2 |
| `Instance.hexpat` | group 13 INSTANCE CData (T004 §20): stage layout id, enemy set (enemy info with the Season 3 sixth bool, drop item set, named enemy param), layout item data, gathering item element (Season 3, 17 bytes), get request, the Season 3 gathering restriction and its item amount, OM data (Season 3 u64 key); includes Packet and Character | 25 group-13 patterns |

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
  Every login pattern (`C2L_`/`L2C_`) carries it: the game server reuses the login ids 0.0.x,
  0.2.x, 1.0.x and 3.0.x, and naming the packet keeps a later game-server capture out of the export.
  The game-server patterns of the shared ids carry it as well (0.0.1-0.2.2, 1.0.1, 1.0.2; T003b).
- `// packet-size: <bytes>`: only where two packets share both id and file name. `@` then keeps
  only files of that size. No pattern needs it now: `1.0.1 C2L_CLIENT_CHALLENGE_REQ` carried
  `// packet-size: 336` while the CLI filed the server's 304-byte certificate notice under the same
  `.1_0_1` name (T002c §3); since T002e the notice is `1.1.16 L2C_LOGIN_SERVER_CERT_NTC`, and the
  42 C2L JSON files came out byte-identical without the line. The feature and its test stay.

**JSON conventions.** The root key is `packet`. Header keys are lowercase (`group`, `id`, `subId`,
`source`, `packetcounter`). Lists export as `{count, entries}` and strings as `{length, value}`.
String values are UTF-8 JSON strings, written as is with the standard escapes (`\"`, `\\`, `\n`,
`\r`, `\t`, `\u00XX` for control characters); there is no percent encoding since spec 006 T001d
(the export before it wrote `"Rumi%20Amestris"`). A byte that is not valid UTF-8 comes out as
`\u00XX`, which reads the same as the code point U+00XX.

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

The engine is plbatch (`research/imhex/plbatch`, built with its `build.sh`): PatternLanguage master
`300d7388` (UTF-8 strings), one process per shard. Without plbatch, the script runs one
`imhex --pl format` per packet; ImHex 1.38.1 still percent-encodes strings, so its JSON differs
from the committed export wherever a string holds a byte outside `[A-Za-z0-9-_.~]`. The summary line counts:

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
`fits` true (counted 2026-11-01 after commit cc7ebd0fb3, and for 11.15.2, 11.71.2, 11.89.16 and
13.44-13.47.16 again after the T001c re-export, and for the login ids of T002 after their first
export, and for the group 13 ids of T004 after their first export (2026-11-02, T004b); no type has a `.json.err`). `no capture`
means no raw file exists, so the pattern was checked on synthetic input at most. The Report column
gives the section the pattern header cites: P11a and P11b are
`specs/005-netmsg-patterns/research/P11*-old-patterns.md`, and P1, P4 and P5 are the reports of
those names. T001b is `specs/006-packet-pattern-coverage/research/T001b-save-blob.md`, the save
blob that 9.0.2 and 9.1.1 share through `include/CharacterData.hexpat`. T001c is
`specs/006-packet-pattern-coverage/research/T001c-parked-static-items.md` (spec 005's parked items).
T002 is `specs/006-packet-pattern-coverage/research/T002-login.md` (the login group).
T003 is `specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md` (groups 0
CONNECTION, 1 SERVER and 44 CERT of the game server; counts after their first export, T003b).
T004 is `specs/006-packet-pattern-coverage/research/T004-instance.md` (group 13 INSTANCE; counts
after their first export, T004b).

| Id | Pattern | Report | Status |
| --- | --- | --- | --- |
| 0.0.1 | `C2L_PING_REQ` | T002 §1 | 75/75 fit |
| 0.0.2 | `L2C_PING_RES` | T002 §1 | 75/75 fit |
| 0.0.1 | `C2S_CONNECTION_PING_REQ` | T003 §2 | 2134/2134 fit |
| 0.0.2 | `S2C_CONNECTION_PING_RES` | T003 §2 | 2133/2133 fit |
| 0.1.1 | `C2L_LOGIN_REQ` | P11b §2 | 42/42 fit |
| 0.1.2 | `L2C_LOGIN_RES` | P11b §3 | 42/42 fit |
| 0.1.1 | `C2S_CONNECTION_LOGIN_REQ` | T003 §3 | 42/42 fit |
| 0.1.2 | `S2C_CONNECTION_LOGIN_RES` | T003 §3 | 42/42 fit |
| 0.2.1 | `C2L_LOGOUT_REQ` | T002 §2 | 42/42 fit |
| 0.2.2 | `L2C_LOGOUT_RES` | T002 §2 | 42/42 fit |
| 0.2.1 | `C2S_CONNECTION_LOGOUT_REQ` | T003 §4 | 42/42 fit |
| 0.2.2 | `S2C_CONNECTION_LOGOUT_RES` | T003 §4 | 42/42 fit |
| 0.3.1 | `C2S_CONNECTION_GET_LOGIN_ANNOUNCEMENT_REQ` | T003 §5 | 41/41 fit |
| 0.3.2 | `S2C_CONNECTION_GET_LOGIN_ANNOUNCEMENT_RES` | T003 §5 | 41/41 fit |
| 0.5.1 | `C2S_CONNECTION_MOVE_IN_SERVER_REQ` | T003 §6 | 41/41 fit |
| 0.5.2 | `S2C_CONNECTION_MOVE_IN_SERVER_RES` | T003 §6 | 41/41 fit |
| 0.6.1 | `C2S_CONNECTION_MOVE_OUT_SERVER_REQ` | T003 §7 | 41/41 fit |
| 0.6.2 | `S2C_CONNECTION_MOVE_OUT_SERVER_RES` | T003 §7 | 41/41 fit |
| 0.7.1 | `C2S_CONNECTION_RESERVE_SERVER_REQ` | T003 §8 | 41/41 fit |
| 0.7.2 | `S2C_CONNECTION_RESERVE_SERVER_RES` | T003 §8 | 41/41 fit |
| 0.10.16 | `S2C_CONNECTION_0_10_16_NTC` | T003 §9 | 2/2 fit (code name SESSION_STATUS_NTC, V) |
| 1.0.1 | `C2L_CLIENT_CHALLENGE_REQ` | T002 §3, T002c | 42/42 fit (no header, body at offset 0) |
| 1.0.2 | `L2C_CLIENT_CHALLENGE_RES` | T002 §4 | 42/42 fit |
| 1.0.1 | `C2S_SERVER_GET_SERVER_LIST_REQ` | T003 §10 | 43/43 fit |
| 1.0.2 | `S2C_SERVER_GET_SERVER_LIST_RES` | T003 §10 | 43/43 fit |
| 1.1.1 | `C2S_SERVER_GET_GAME_SETTING_REQ` | T003 §11 | 42/42 fit |
| 1.1.2 | `S2C_SERVER_GET_GAME_SETTING_RES` | T003 §11 | 42/42 fit, slack 1 |
| 1.1.16 | `L2C_LOGIN_SERVER_CERT_NTC` | T003 §1, §15 | 42/42 fit, slack 12 (no header; layout by the game reader and the capture SHA-1 check) |
| 1.4.1 | `C2S_SERVER_GET_REAL_TIME_REQ` | T003 §12 | 87/87 fit |
| 1.4.2 | `S2C_SERVER_GET_REAL_TIME_RES` | T003 §12 | 87/87 fit |
| 1.7.1 | `C2S_SERVER_WEATHER_FORECAST_GET_REQ` | T003 §13 | 1/1 fit |
| 1.7.2 | `S2C_SERVER_WEATHER_FORECAST_GET_RES` | T003 §13 | 1/1 fit |
| 1.8.1 | `C2S_SERVER_GAME_TIME_GET_BASEINFO_REQ` | T003 §14 | 41/41 fit |
| 1.8.2 | `S2C_SERVER_GAME_TIME_GET_BASEINFO_RES` | T003 §14 | 41/41 fit |
| 2.1.1 | `C2L_GET_GAME_SESSION_KEY_REQ` | T002 §5 | 42/42 fit |
| 2.1.2 | `L2C_GET_GAME_SESSION_KEY_RES` | T002 §5 | 42/42 fit |
| 2.2.1 | `C2L_GET_LOGIN_SETTING_REQ` | T002 §6 | 41/41 fit |
| 2.2.2 | `L2C_GET_LOGIN_SETTING_RES` | T002 §6 | 41/41 fit |
| 2.3.16 | `L2C_NEXT_CONNECT_SERVER_NTC` | T002 §7 | 42/42 fit |
| 2.13.16 | `C2S_CHARACTER_CHARACTER_DOWN_NTC` | P4 §4 | 14/14 fit |
| 2.14.16 | `C2S_CHARACTER_CHARACTER_DOWN_CANCEL_NTC` | P4 §4 | no capture |
| 2.15.16 | `C2S_CHARACTER_CHARACTER_DEAD_NTC` | P4 §4 | 7/7 fit |
| 2.19.16 | `C2S_CHARACTER_PAWN_DOWN_NTC` | P4 §4 | 20/20 fit |
| 2.20.16 | `C2S_CHARACTER_PAWN_DOWN_CANCEL_NTC` | P4 §4 | 10/10 fit |
| 2.21.16 | `C2S_CHARACTER_PAWN_DEAD_NTC` | P4 §4 | no capture |
| 3.0.1 | `C2L_GET_ERROR_MESSAGE_LIST_REQ` | T002 §8 | 41/41 fit |
| 3.0.2 | `L2C_GET_ERROR_MESSAGE_LIST_RES` | T002 §8 | 41/41 fit |
| 3.0.16 | `L2C_GET_ERROR_MESSAGE_LIST_NTC` | T002 §9 | 410/410 fit |
| 3.3.16 | `C2S_LOBBY_LOBBY_DATA_MSG_REQ` | P1 §1.1 | 59881/59881 fit |
| 3.4.16 | `S2C_LOBBY_LOBBY_DATA_MSG_NTC` | P1 §1.1 | 21000/21000 fit |
| 4.0.1 | `C2L_GP_COURSE_GET_INFO_REQ` | T002 §10 | 41/41 fit |
| 4.0.2 | `L2C_GP_COURSE_GET_INFO_RES` | T002 §10 | 41/41 fit |
| 5.0.1 | `C2L_GET_CHARACTER_LIST_REQ` | T002 §11 | 42/42 fit |
| 5.0.2 | `L2C_GET_CHARACTER_LIST_RES` | T002 §11 | 42/42 fit |
| 5.1.1 | `C2L_DECIDE_CHARACTER_ID_REQ` | T002 §12 | 42/42 fit |
| 5.1.2 | `L2C_DECIDE_CHARACTER_ID_RES` | T002 §12 | 42/42 fit |
| 5.5.16 | `L2C_LOGIN_WAIT_NUM_NTC` | T002 §13 | 9/9 fit |
| 6.23.16 | `C2S_PARTY_SEND_BINARY_MSG_ALL_NTC` | P1 §1.1 | 8/8 fit |
| 6.24.16 | `S2C_PARTY_RECV_BINARY_MSG_ALL_NTC` | P1 §1.1 | no capture |
| 6.25.16 | `C2S_PARTY_SEND_BINARY_MSG_NTC` | P1 §1.1 | 29176/29176 fit |
| 6.26.16 | `S2C_PARTY_RECV_BINARY_MSG_NTC` | P1 §1.1 | no capture |
| 8.30.2 | `S2C_PAWN_GET_NORA_PAWN_LIST_RES` | P11b §14 | 41/41 fit |
| 9.0.2 | `S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES` | P4 §3, T001b §4 | no capture (synthetic: versions 0x19, 0x13, 0x0C) |
| 9.1.1 | `C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ` | P4 §3, T001b | 47/47 fit; 47/47 equal T001b's walk field by field |
| 10.9.2 | `S2C_ITEM_GET_ITEM_STORAGE_INFO_RES` | P11b §13 | 4/4 fit |
| 11.15.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES` | P11a §5 | 6/6 fit |
| 11.19.2 | `S2C_QUEST_GET_AREA_BONUS_LIST_RES` | P11a §9 | 182/182 fit |
| 11.37.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES` | P11a §12 | 41/41 fit |
| 11.56.2 | `S2C_QUEST_GET_AREA_INFO_LIST_RES` | P11a §11 | 1/1 fit |
| 11.71.2 | `S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES` | P11a §4 | 43/43 fit |
| 11.89.16 | `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC` | P11a §1 | 41/41 fit |
| 11.120.16 | `S2C_QUEST_PARTY_QUEST_PROGRESS_NTC` | P11a §3 | no capture |
| 12.0.2 | `S2C_STAGE_GET_STAGE_LIST_RES` | P11a §7 | 42/42 fit |
| 13.0.1 | `C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ` | T004 §2 | 563/563 fit |
| 13.0.2 | `S2C_INSTANCE_GET_ENEMY_SET_LIST_RES` | T004 §2 | 667/667 fit (NamedParamList never non-empty) |
| 13.1.16 | `C2S_INSTANCE_ENEMY_GROUP_ENTRY_NTC` | T004 §3 | 202/202 fit, slack 14 (PS4 ENEMY_GROUP_ENTRY_NOTICE, V by behaviour) |
| 13.2.16 | `C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC` | T004 §3 | 184/184 fit, slack 14 (PS4 ENEMY_GROUP_LEAVE_NOTICE, V by behaviour) |
| 13.3.1 | `C2S_INSTANCE_ENEMY_KILL_REQ` | T004 §4 | 391/391 fit, slack 12 |
| 13.3.2 | `S2C_INSTANCE_ENEMY_KILL_RES` | P11b §15 | 412/412 fit |
| 13.5.1 | `C2S_INSTANCE_GET_ITEM_SET_LIST_REQ` | T004 §5 | 118/118 fit, slack 14 |
| 13.5.2 | `S2C_INSTANCE_GET_ITEM_SET_LIST_RES` | T004 §5 | 258/258 fit |
| 13.6.1 | `C2S_INSTANCE_GET_GATHERING_ITEM_LIST_REQ` | T004 §6 | 155/155 fit |
| 13.6.2 | `S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES` | T004 §6 | 155/155 fit (restriction list never non-empty) |
| 13.8.1 | `C2S_INSTANCE_GET_GATHERING_ITEM_REQ` | T004 §7 | 51/51 fit |
| 13.8.2 | `S2C_INSTANCE_GET_GATHERING_ITEM_RES` | T004 §7 | 51/51 fit |
| 13.10.1 | `C2S_INSTANCE_GET_DROP_ITEM_LIST_REQ` | T004 §8 | 88/88 fit |
| 13.10.2 | `S2C_INSTANCE_GET_DROP_ITEM_LIST_RES` | T004 §8 | 88/88 fit |
| 13.11.1 | `C2S_INSTANCE_GET_DROP_ITEM_REQ` | T004 §9 | 44/44 fit |
| 13.11.2 | `S2C_INSTANCE_GET_DROP_ITEM_RES` | T004 §9 | 44/44 fit |
| 13.20.1 | `C2S_INSTANCE_SET_OM_INSTANT_KEY_VALUE_REQ` | T004 §11 | 542/542 fit |
| 13.20.2 | `S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_RES` | T004 §11 | 559/559 fit |
| 13.20.16 | `S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_NTC` | T004 §11 | 571/571 fit (PS4 SET_OM_INSTANT_KEY_VALUE_NOTICE, V by behaviour) |
| 13.22.1 | `C2S_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_REQ` | T004 §12 | 150/150 fit (no body) |
| 13.22.2 | `S2C_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_RES` | T004 §12 | 150/150 fit |
| 13.23.1 | `C2S_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ` | T004 §13 | 44/44 fit |
| 13.23.2 | `S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_RES` | T004 §13 | 46/46 fit |
| 13.31.16 | `S2C_INSTANCE_ENEMY_GROUP_DESTROY_NTC` | T004 §14 | 81/81 fit, slack 13 (V by behaviour) |
| 13.32.16 | `S2C_INSTANCE_ENEMY_GROUP_RESET_NTC` | T004 §15 | 130/130 fit, slack 14 (PS4 ENEMY_GROUP_RESET_NOTICE, V by behaviour) |
| 13.39.16 | `S2C_INSTANCE_POP_DROP_ITEM_NTC` | T004 §16 | 74/74 fit |
| 13.40.16 | `S2C_INSTANCE_ENEMY_REPOP_NTC` | T004 §17 | 41/41 fit |
| 13.42.16 | `S2C_INSTANCE_AREA_RESET_NTC` | T004 §18 | 120/120 fit (no body; V by behaviour) |
| 13.44.16 | `C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC` | P4 §4, T001c §3 | 19/19 fit |
| 13.45.16 | `C2S_INSTANCE_CHARACTER_END_BAD_STATUS_NTC` | P4 §4, T001c §3 | 19/19 fit |
| 13.46.16 | `C2S_INSTANCE_ENEMY_BAD_STATUS_START_NTC` | P4 §4, T001c §3 | 31/31 fit |
| 13.47.16 | `C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC` | P4 §4, T001c §3 | 30/30 fit |
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
| 35.12.16 | `S2C_CONTEXT_35_12_16_NTC` | P4 §2.3, T001c §1 | no capture (synthetic: one file built from T001c §1's field table, every value read back; a truncated copy fails) |
| 35.13.16 | `S2C_CONTEXT_SET_CONTEXT_NTC` | P4 §2.3 | 24/24 fit |
| 35.14.16 | `S2C_CONTEXT_MASTER_CHANGE_NTC` | P4 §2.3 | 948/948 fit |
| 35.15.16 | `S2C_CONTEXT_MASTER_INFO_NTC` | P4 §2.3 | 43/43 fit |
| 44.0.1 | `C2S_CERT_CLIENT_CHALLENGE_REQ` | T003 §15 | 83/83 fit, slack 12 (no header, body at offset 0) |
| 44.0.2 | `S2C_CERT_CLIENT_CHALLENGE_RES` | T003 §16 | 83/83 fit |
| 44.1.16 | `S2C_CERT_GAME_SERVER_CERT_NTC` | T003 §1, §15 | 83/83 fit, slack 12 (no header, body at offset 0) |
| 51.0.2 | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES` | P11a §6 | 1/1 fit |
| 52.1.2 | `S2C_MY_ROOM_FURNITURE_LIST_GET_RES` | P11a §10 | 20/20 fit |
| 57.0.2 | `S2C_BOX_GACHA_BOX_GACHA_LIST_RES` | P11a §8 | 3/3 fit |
| 60.0.1 | `C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ` | P11b §12 | 219/219 fit |
| 63.11.16 | `S2C_63_11_16_NTC` | P5 §7 | 1/1 fit |
| 64.0.2 | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES` | P11a §2 | 20/20 fit |

## Open items

- **0.10.16 name:** the raws and the pattern keep the CLI's name `S2C_CONNECTION_0_10_16_NTC`;
  the code-backed name is `SESSION_STATUS_NTC` (T003 §9, V by behaviour: the handler sets the
  SessionStatus byte of the lobby member with that CharacterID). Which of the PS4 lobby-member
  bytes Platform/ClientVersion Season 3 dropped is I.
- **Game setting names without code backing (T003 §11, §20):** the Season 3 tail of
  `CDataGameSetting` (`unk_bool`, `unk_u32_0..2`, `unk_u16`, and the element names of
  `CDataWalletLimit`, `CDataExpSetting`, `CDataExpRequirement`, all server leads, I), and the
  position of PawnPresentItemID/Num after Season 3 dropped the two CapLink strings (I: width
  alignment plus one value match).
- **Game-server RES error branch untested:** no captured RES of groups 0, 1 and 44 has
  Error != 0; `CDataMoonSchedule`, the ping CheatInfo list beyond one element and every list count
  above those seen are code-only (T003 §17).
- **1.1.16 login reader not decoded:** the login certificate notice reuses the game body
  (`include/Cert.hexpat`) on the strength of the captures (42/42 SHA-1 match, T002c §4) and the
  shared receive path (T003 §1); the reader behind handler `0x886b00` is not decoded (T003 §20).
- **Login RES error branch untested:** no captured login RES has Error != 0, so the
  `if (Error == 0)` guard of the ten login RES patterns is code-only (V code, not run on
  captures; T002 §14). The same holds for the 2.3.16 Error, which is read unconditionally.
- **Login names without code backing (T002 §17):** 2.3.16 `Error` (I), 3.0.16 `RemainingNum` (I),
  the CDataEquipItemInfo fields after ItemID (`unk_*`; ItemID, Color, PlusValue I) and the
  CDataGPCourseValid second MtString (`unk_MtString`). CDataGPCourseValid is not capture-tested:
  every captured list is empty.
- **Unnamed 35.12.16 and 13.44-13.47.16:** no PC string and no PS4 sender, so the client names
  are unresolved (T001c §1, §3); the pattern names are the names in the raws, which come from the
  server. Their roles are V: 35.12.16 is an enemy status snapshot (`CDataContextEnemyStatus`, name
  I); 13.44/13.45 are status start/end (`cOcdBase::init`/`final`) for the master player character,
  13.46/13.47 the same for an enemy the client is master of (P5 §7's actors are contradicted).
- **13.46/13.47 `unk_u32`:** the set-group record's +0x30 (server: PosId, lead); its getter
  `0x4d9e70` is a protected thunk (T001c §3).
- **Context variants without captures:** `include/Context.hexpat` holds the 35.0.2, 35.1.x, 35.2.x
  and 35.3.2/35.4.x bodies as types (`CDataLobbyContextPlayer`, `CDataPartyContextPlayer`,
  `CDataAllContextPlayer`, `CDataPartyContextPawn`; T001c §2), unvalidated; no pattern uses them.
- **Season 3 nNetMsg names (T001c §6):** the second catch triple of CatchRequest/CatchInfo is
  `cpCatchCtrl::mCaughtInfo` (V); SetCreateContext's triple carries the same names by shape only (I).
  Unresolved: CtrlAction 0x3C (the cContextInstEm u32[4] at cContext+0xC48, shared with
  SetAdditional `unk_u32[4]` and 35.12.16) and 0x3D (signed delta into its slot 0), GameNormal
  0x0F/0x10 (feed the sEnemyManager+0xDB0 block) and 0x11/0x12 (cContextInstPl+0x3A94/+0x3A90).
- **Season 3 field names:** fields new in Season 3 are `unk_*`. Where PC adds one field to a run of
  same-width fields, its position is inferred: BoxGacha u32, AreaBonus u16, MyRoomFurniture u32, and
  the CDataQuestOrderList u32s and u64s (R2 F5). QuestEnemyInfo is settled: {GroupId, Season 3
  `unk_u32`, Lv, IsPartyRecommend} (T001c §5, V; P11a §1.3 contradicted).
- **Season 3-exclusive, not patterned (T004):** 13.16.1/13.16.2 TREASURE_POINT_GET_CATEGORY_LIST
  and 13.17.1/13.17.2 TREASURE_POINT_GET_LIST (T004 §10: no PS4 counterpart, V by code; one capture
  each) and 13.23.16 S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC (T004 §13: no PS4 handler, V by
  code; 46 captures). Season 3-exclusive ids go to a later spec (Sam); T004 §10 and §13 hold their
  PC readers and wire layouts.
- **Group 13 widths that fit either way (T004 §19):** three Season 3 widths rest on the PC code
  alone, because the slack absorbs the difference: the 13.3.1 second bool (`unk_bool`), the
  13.40.16 sixth enemy-info bool (`EnemyInfo.unk_bool`, also V by the 13.0.2 counter-test) and the
  13.20.16 u64 Key (also V by the 13.20.2 counter-test). The 9-byte bodies of 13.1.16, 13.2.16,
  13.5.1 and 13.32.16, the 13.31.16 bool and the empty 13.22.1 and 13.42.16 rest on the code too.
- **Group 13 lists never non-empty in captures (T004 §19, §22):** the 13.0.2 `NamedParamList`
  (`CDataNamedEnemyParamClient`) and the 13.6.2 `unk_RestrictionList` (`CDataGatheringItemRestriction`
  with its wallet-point and item-amount lists): their elements are code-only.
- **Group 13 names without code backing (T004 §22):** the Season 3 fields are `unk_*` with the
  server name as lead: the 13.3.1 and 13.11.1 bools, the 13.6.2 `unk_bool` and restriction list, the
  13.8.1 bool and u32 (server: EquipToCharacter, RestrictionId), the enemy-info sixth bool (server:
  IsHighOrbEnemy), the `CDataGatheringItemElement` u32 and bool (server: Quality, IsHidden), the
  restriction element fields. Which 13.6.2 bool is the PS4 IsGatheringItemBreak, and that the first
  13.3.1 bool is the PS4 IsNoBattleReword, are I (position). The PC sOmManager callbacks are protected
  thunks; their identity rests on call shape. No captured group-13 RES has Error != 0: the guard is
  code-only. The 13.44-13.47.16 patterns keep their inline layout triplet (same fields and JSON as
  `CDataStageLayoutId`, unchanged).
- **u64 OM Key in JSON:** `CDataOmData.Key` carries the high bit (0x80000000_001415b3), so the JSON
  integer exceeds 2^53; a reader that parses numbers as doubles rounds it (Python `json` keeps it
  exact).
