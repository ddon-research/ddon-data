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
| `Packet.hexpat` | the raw framing `CPacket` (u8 group, u16 id, u8 sub, u8 source, u32 counter; body at 0x09), `MtTypedArray<T>` (u32 count + entries), `MtString` (u16 length + bytes), `CDataCommonU32`/`CDataCommonU8`, the fit-flag rules and the RES convention | every pattern without nNetMsg, except the four header-less ones (1.0.1, 1.1.16, 44.0.1, 44.1.16), which read the body at offset 0 without `CPacket` |
| `nNetMsg.hexpat` | the nNetMsg (cNetMsg RPC) payload of the lobby and party binary packets: ids, DTI enum, message structures (P1, P2, P3) | 3.3.16, 3.4.16, 6.23-6.26.16 |
| `Context.hexpat` | group 35 CONTEXT structures (P4) | 11 group-35 patterns |
| `Quest.hexpat` | group 11 QUEST CData and the enums ORDER_CONDITION_TYPE, CYCLE_CONTENTS_CATEGORY, CYCLE_CONTENTS_SUB_CATEGORY, COMMAND_CHECK_LIST (P11a); since T005b also the Season 3 `CDataQuestList` (PC `0x774530`, beside `CDataQuestOrderList`) and the list, detail, play start/end, priority, reward box and fort defense types of T005 §44 | 72 |
| `Area.hexpat` | group 23 AREA CData (P11a, P11b) | 4 |
| `Character.hexpat` | E_WALLET_POINT_TYPE, CDataWalletPoint, job base info, character name and list element; since T006b `CDataCharacterLevelParam` (PC `0x75cb00`) and the Season 3 `CDataLobbyMemberInfo` (PC `0x76d7f0`, 3 u8); since T007b `CDataPartyMember` (PC `0x771580`) | 2, and 3.0.2, 3.2.16, 33.12/13/16/17.16, 8.37.16 |
| `Clan.hexpat`, `Skill.hexpat` | the CData of those groups (P11b) | 1-2 each |
| `Item.hexpat` | item storage types (P11b §13); since T008b the Season 3 `CDataItemList` (PC `0x76aca0`), `CDataItemUpdateResult`, `CDataUpdateWalletPoint`, `CDataSwitchStorage` (Season 3 u16), `CDataMoveItemUIDFromTo` and `CDataItemSort` (T008 §1, §6); includes Packet, Character and Context | 10.9.2, 10.3.2, 10.6.2, 10.7.1, 10.9.1, 10.12.16, 10.13.16, 50.0.2, 50.1.1 |
| `Pawn.hexpat` | group 8 PAWN CData (P11b §14); since T007b the Season 3 `CDataPawnInfo` (PC `0x772180`) with its job, equip, craft and orb-extend types, the pawn list, rented, lost and history elements, profile, total score, orb status, and `CDataPartnerPawnData`/`CDataPartnerPawnReward`, shared with group 53 (T007 §1, §6); includes Login | 8.30.2, 10 group-8 and 3 group-53 patterns |
| `PawnExpedition.hexpat` | group 58 PAWN_EXPEDITION CData (T007 §4, §6): `CDataAreaSpotSet`, `CDataPawnExpeditionClanSallySpotInfo`, `CDataBattleResultInfo`; includes Packet only (group 58 also uses Packet's common types and Instance's gathering-item element and get request) | 58.0.2, 58.5.2 |
| `Login.hexpat` | login-server CData (T002 §15): URL info, login setting, game server list info, error message, and the character list types (matching profile, Season 3 equip item info, character list info); includes Character, Context and GP | 4 |
| `GP.hexpat` | GP course info, effect param and the Season 3 GP course valid (T002 §10, §11) | 1, and 5.0.2 through Login |
| `Cert.hexpat` | `CDataServerCert`, the server certificate notice body: modulus[256], exponent[16], SHA-1 u32[5] (T003 §1, §15) | 1.1.16, 44.1.16 |
| `Server.hexpat` | game-server connection setup CData (T003 §18): cheat info (ping), game setting with its Season 3 changes and element types, weather forecast, game time base info, weather loop/schedule, moon schedule; includes Login | 0.0.1, 1.0.2, 1.1.2, 1.7.2, 1.8.2 |
| `Instance.hexpat` | group 13 INSTANCE CData (T004 §20): stage layout id, enemy set (enemy info with the Season 3 sixth bool, drop item set, named enemy param), layout item data, gathering item element (Season 3, 17 bytes), get request, the Season 3 gathering restriction and its item amount, OM data (Season 3 u64 key); includes Packet and Character | 25 group-13 patterns |
| `Job.hexpat` | group 33 JOB CData (T006 §1.1, §6): job change info (with Login's Season 3 `CDataEquipItemInfo`), pawn job change info, play point data and job play point; includes Login | 33.0.2 |
| `Stage.hexpat` | group 12 STAGE CData (T006 §3.2, §6): the two Season 3 element types of 12.1.2 (`CDataAreaChangeUnk0/1`, names unk) | 12.1.2 |
| `Warp.hexpat` | group 14 WARP CData (T008 §1.2, §6): `CDataWarpPoint`, `CDataFavoriteWarpPoint`, `CDataAreaWarpPoint`, `CDataJumpLocation`; includes Packet only | 14.2.2, 14.4.2, 14.8.2, 14.12.2 |

Each structure comment names the PC reader or writer VA (PC 03040008 database, image base 0x400000)
and the PS4 02020005 DWARF type, and carries a mark: V means read in IDA, I means inferred. A field
name is code-backed (V), inferred and marked (I) with its basis, or `unk_*`; a server name alone
never becomes a field name (it goes in a `server: <name> (lead)` comment). A Season 3 field with no
PS4 counterpart is labelled that way.

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
after their first export, T004b). T005 is `specs/006-packet-pattern-coverage/research/T005-quest.md`
(group 11 QUEST; counts after their first export, 2026-11-02, T005b). T006 is
`specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md` (groups 33 JOB, 3 LOBBY,
23 AREA and 12 STAGE; counts after their first export, 2026-11-02, T006b). T007 is
`specs/006-packet-pattern-coverage/research/T007-pawn-partner.md` (groups 8 PAWN, 53 PARTNER_PAWN and
58 PAWN_EXPEDITION; counts after their first export, 2026-11-02, T007b). T008 is
`specs/006-packet-pattern-coverage/research/T008-warp-item.md` (groups 14 WARP, 10 ITEM and 50
ITEM_SORT; counts after their first export, 2026-11-02, T008b).

| Id | Pattern | Report | Status |
| --- | --- | --- | --- |
| 0.0.1 | `C2L_PING_REQ` | T002 §1 | 75/75 fit |
| 0.0.1 | `C2S_CONNECTION_PING_REQ` | T003 §2 | 2134/2134 fit |
| 0.0.2 | `L2C_PING_RES` | T002 §1 | 75/75 fit |
| 0.0.2 | `S2C_CONNECTION_PING_RES` | T003 §2 | 2133/2133 fit |
| 0.1.1 | `C2L_LOGIN_REQ` | P11b §2 | 42/42 fit |
| 0.1.1 | `C2S_CONNECTION_LOGIN_REQ` | T003 §3 | 42/42 fit |
| 0.1.2 | `L2C_LOGIN_RES` | P11b §3 | 42/42 fit |
| 0.1.2 | `S2C_CONNECTION_LOGIN_RES` | T003 §3 | 42/42 fit |
| 0.2.1 | `C2L_LOGOUT_REQ` | T002 §2 | 42/42 fit |
| 0.2.1 | `C2S_CONNECTION_LOGOUT_REQ` | T003 §4 | 42/42 fit |
| 0.2.2 | `L2C_LOGOUT_RES` | T002 §2 | 42/42 fit |
| 0.2.2 | `S2C_CONNECTION_LOGOUT_RES` | T003 §4 | 42/42 fit |
| 0.3.1 | `C2S_CONNECTION_GET_LOGIN_ANNOUNCEMENT_REQ` | T003 §5 | 41/41 fit |
| 0.3.2 | `S2C_CONNECTION_GET_LOGIN_ANNOUNCEMENT_RES` | T003 §5 | 41/41 fit |
| 0.5.1 | `C2S_CONNECTION_MOVE_IN_SERVER_REQ` | T003 §6 | 41/41 fit |
| 0.5.2 | `S2C_CONNECTION_MOVE_IN_SERVER_RES` | T003 §6 | 41/41 fit |
| 0.6.1 | `C2S_CONNECTION_MOVE_OUT_SERVER_REQ` | T003 §7 | 41/41 fit |
| 0.6.2 | `S2C_CONNECTION_MOVE_OUT_SERVER_RES` | T003 §7 | 41/41 fit |
| 0.7.1 | `C2S_CONNECTION_RESERVE_SERVER_REQ` | T003 §8 | 41/41 fit |
| 0.7.2 | `S2C_CONNECTION_RESERVE_SERVER_RES` | T003 §8 | 41/41 fit |
| 0.10.16 | `S2C_CONNECTION_0_10_16_NTC` | T003 §9 | 2/2 fit (code name SESSION_STATUS_NTC, V by behaviour) |
| 1.0.1 | `C2L_CLIENT_CHALLENGE_REQ` | T002 §3, T002c | 42/42 fit (no header, body at offset 0) |
| 1.0.1 | `C2S_SERVER_GET_SERVER_LIST_REQ` | T003 §10 | 43/43 fit |
| 1.0.2 | `L2C_CLIENT_CHALLENGE_RES` | T002 §4 | 42/42 fit |
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
| 3.0.1 | `C2S_LOBBY_LOBBY_JOIN_REQ` | T006 §2.1 | 41/41 fit, slack 15 (packet-select: the login id 3.0.1 shares the suffix) |
| 3.0.2 | `S2C_LOBBY_LOBBY_JOIN_RES` | T006 §2.1 | 41/41 fit (packet-select; the 3-u8 member rests on the PC reader: PS4's 4 u8 fit too) |
| 3.0.2 | `L2C_GET_ERROR_MESSAGE_LIST_RES` | T002 §8 | 41/41 fit |
| 3.0.16 | `L2C_GET_ERROR_MESSAGE_LIST_NTC` | T002 §9 | 410/410 fit |
| 3.1.1 | `C2S_LOBBY_LOBBY_LEAVE_REQ` | T006 §2.2 | 41/41 fit (no body) |
| 3.1.2 | `S2C_LOBBY_LOBBY_LEAVE_RES` | T006 §2.2 | 41/41 fit, slack 15 |
| 3.2.1 | `C2S_LOBBY_LOBBY_CHAT_MSG_REQ` | T006 §2.3 | 328/328 fit |
| 3.2.2 | `S2C_LOBBY_LOBBY_CHAT_MSG_RES` | T006 §2.3 | 382/382 fit, slack 15 |
| 3.2.16 | `S2C_LOBBY_LOBBY_CHAT_MSG_NTC` | T006 §2.4 | 463/463 fit |
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
| 8.2.1 | `C2S_PAWN_GET_MYPAWN_LIST_REQ` | T007 §2.1 | 119/119 fit (no body) |
| 8.2.2 | `S2C_PAWN_GET_MYPAWN_LIST_RES` | T007 §2.1 | 119/119 fit (Season 3: three u32 per pawn, V; the PS4 element fails 119/119) |
| 8.3.1 | `C2S_PAWN_GET_MYPAWN_DATA_REQ` | T007 §2.2 | 72/72 fit |
| 8.3.2 | `S2C_PAWN_GET_MYPAWN_DATA_RES` | T007 §2.2 | 72/72 fit (Season 3 `CDataPawnInfo`; the PS4 body fails 72/72) |
| 8.8.1 | `C2S_PAWN_GET_RENTED_PAWN_LIST_REQ` | T007 §2.3 | 54/54 fit (no body) |
| 8.8.2 | `S2C_PAWN_GET_RENTED_PAWN_LIST_RES` | T007 §2.3 | 54/54 fit |
| 8.9.1 | `C2S_PAWN_GET_RENTED_PAWN_DATA_REQ` | T007 §2.2 | 2/2 fit |
| 8.9.2 | `S2C_PAWN_GET_RENTED_PAWN_DATA_RES` | T007 §2.2 | 2/2 fit (Season 3 `CDataPawnInfo`; the PS4 body fails 2/2) |
| 8.12.1 | `C2S_PAWN_JOIN_PARTY_MYPAWN_REQ` | T007 §2.4 | 7/7 fit |
| 8.12.2 | `S2C_PAWN_JOIN_PARTY_MYPAWN_RES` | T007 §2.4 | 9/9 fit, slack 15 |
| 8.20.1 | `C2S_PAWN_GET_LOST_PAWN_LIST_REQ` | T007 §2.5 | 20/20 fit (no body) |
| 8.20.2 | `S2C_PAWN_GET_LOST_PAWN_LIST_RES` | T007 §2.5 | 20/20 fit (list never non-empty) |
| 8.28.1 | `C2S_PAWN_GET_PAWN_HISTORY_LIST_REQ` | T007 §2.6 | 20/20 fit |
| 8.28.2 | `S2C_PAWN_GET_PAWN_HISTORY_LIST_RES` | T007 §2.6 | 20/20 fit |
| 8.30.1 | `C2S_PAWN_GET_NORA_PAWN_LIST_REQ` | T007 §2.7 | 41/41 fit (no body) |
| 8.30.2 | `S2C_PAWN_GET_NORA_PAWN_LIST_RES` | P11b §14 | 41/41 fit |
| 8.33.16 | `S2C_PAWN_GET_PAWN_PROFILE_NTC` | T007 §2.8 | 74/74 fit |
| 8.34.16 | `S2C_PAWN_GET_PAWN_HISTORY_INFO_NTC` | T007 §2.9 | 74/74 fit |
| 8.35.16 | `S2C_PAWN_GET_PAWN_TOTAL_SCORE_INFO_NTC` | T007 §2.10 | 74/74 fit |
| 8.36.16 | `S2C_PAWN_GET_PAWN_ORB_DEVOTE_INFO_NTC` | T007 §2.11 | 74/74 fit (Season 3: second job orb list, V; the PS4 body fails 72/74) |
| 8.37.16 | `S2C_PAWN_JOIN_PARTY_PAWN_NTC` | T007 §2.12 | 9/9 fit (code name JOIN_PARTY_PAWN_NOTICE, V: unique PS4 reader + guard) |
| 9.0.2 | `S2C_BINARY_SAVE_GET_CHARACTER_BIN_SAVEDATA_RES` | P4 §3, T001b §4 | no capture (synthetic: versions 0x19, 0x13, 0x0C) |
| 9.1.1 | `C2S_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_REQ` | P4 §3, T001b | 47/47 fit; 47/47 equal T001b's walk field by field |
| 10.0.1 | `C2S_ITEM_USE_BAG_ITEM_REQ` | T008 §3.1 | 18/18 fit |
| 10.0.2 | `S2C_ITEM_USE_BAG_ITEM_RES` | T008 §3.1 | 21/21 fit, slack 15 |
| 10.0.16 | `S2C_ITEM_USE_BAG_ITEM_NTC` | T008 §3.2 | 18/18 fit (code name USE_BAG_ITEM_NOTICE, V by behaviour; the PS4 framing fits too) |
| 10.3.1 | `C2S_ITEM_GET_STORAGE_ITEM_LIST_REQ` | T008 §3.3 | 136/136 fit |
| 10.3.2 | `S2C_ITEM_GET_STORAGE_ITEM_LIST_RES` | T008 §3.3 | 136/136 fit (Season 3 `CDataItemList`; the PS4 element fails 130/136) |
| 10.6.1 | `C2S_ITEM_GET_POST_ITEM_LIST_REQ` | T008 §3.4 | 3/3 fit (no body) |
| 10.6.2 | `S2C_ITEM_GET_POST_ITEM_LIST_RES` | T008 §3.4 | 3/3 fit (Season 3 `CDataItemList`; the PS4 element fails 3/3) |
| 10.7.1 | `C2S_ITEM_MOVE_ITEM_REQ` | T008 §3.5 | 6/6 fit |
| 10.7.2 | `S2C_ITEM_MOVE_ITEM_RES` | T008 §3.5 | 6/6 fit, slack 15 |
| 10.9.1 | `C2S_ITEM_GET_ITEM_STORAGE_INFO_REQ` | T008 §3.6 | 4/4 fit |
| 10.9.2 | `S2C_ITEM_GET_ITEM_STORAGE_INFO_RES` | P11b §13 | 4/4 fit |
| 10.10.16 | `S2C_ITEM_EXTEND_ITEM_SLOT_NTC` | T008 §3.7 | 43/43 fit (code name EXTEND_ITEM_SLOT_NTC, V by behaviour and unique shape; the PS4 framing fits too) |
| 10.12.16 | `S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC` | T008 §3.8 | 390/390 fit (Season 3 `CDataItemList`; the PS4 element fails 245/390) |
| 10.13.16 | `S2C_SWITCH_STORAGE_NTC` | T008 §3.9 | 2/2 fit (Season 3 u16 element field: code-only, the PS4 u8 fits too) |
| 11.0.1 | `C2S_QUEST_GET_LIGHT_QUEST_LIST_REQ` | T005 §2 | 1/1 fit |
| 11.0.2 | `S2C_QUEST_GET_LIGHT_QUEST_LIST_RES` | T005 §2 | 1/1 fit |
| 11.1.1 | `C2S_QUEST_GET_SET_QUEST_LIST_REQ` | T005 §3 | 179/179 fit |
| 11.1.2 | `S2C_QUEST_GET_SET_QUEST_LIST_RES` | T005 §3 | 179/179 fit |
| 11.2.1 | `C2S_QUEST_GET_MAIN_QUEST_LIST_REQ` | T005 §4 | 44/44 fit (no body) |
| 11.2.2 | `S2C_QUEST_GET_MAIN_QUEST_LIST_RES` | T005 §4 | 44/44 fit |
| 11.3.1 | `C2S_QUEST_GET_TUTORIAL_QUEST_LIST_REQ` | T005 §5 | 146/146 fit |
| 11.3.2 | `S2C_QUEST_GET_TUTORIAL_QUEST_LIST_RES` | T005 §5 | 146/146 fit |
| 11.4.1 | `C2S_QUEST_GET_LOT_QUEST_LIST_REQ` | T005 §6 | 20/20 fit |
| 11.4.2 | `S2C_QUEST_GET_LOT_QUEST_LIST_RES` | T005 §6 | 20/20 fit |
| 11.9.1 | `C2S_QUEST_GET_WORLD_MANAGE_QUEST_LIST_REQ` | T005 §9 | 42/42 fit (no body) |
| 11.9.2 | `S2C_QUEST_GET_WORLD_MANAGE_QUEST_LIST_RES` | T005 §9 | 42/42 fit (list never non-empty) |
| 11.10.1 | `C2S_QUEST_GET_END_CONTENTS_GROUP_REQ` | T005 §10 | 3/3 fit |
| 11.10.2 | `S2C_QUEST_GET_END_CONTENTS_GROUP_RES` | T005 §10 | 3/3 fit |
| 11.14.1 | `C2S_QUEST_GET_SET_QUEST_INFO_LIST_REQ` | T005 §11 | 2/2 fit |
| 11.14.2 | `S2C_QUEST_GET_SET_QUEST_INFO_LIST_RES` | T005 §11 | 2/2 fit |
| 11.15.1 | `C2S_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_REQ` | T005 §12 | 6/6 fit (no body) |
| 11.15.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_NEWS_LIST_RES` | P11a §5 | 6/6 fit |
| 11.19.1 | `C2S_QUEST_GET_AREA_BONUS_LIST_REQ` | T005 §12 | 182/182 fit (no body) |
| 11.19.2 | `S2C_QUEST_GET_AREA_BONUS_LIST_RES` | P11a §9 | 182/182 fit |
| 11.20.1 | `C2S_QUEST_QUEST_ORDER_REQ` | T005 §12 | 1/1 fit |
| 11.20.2 | `S2C_QUEST_QUEST_ORDER_RES` | T005 §13 | 1/1 fit |
| 11.21.1 | `C2S_QUEST_QUEST_PROGRESS_REQ` | T005 §14 | 705/705 fit |
| 11.21.2 | `S2C_QUEST_QUEST_PROGRESS_RES` | T005 §14 | 705/705 fit |
| 11.23.1 | `C2S_QUEST_LIGHT_QUEST_GP_COMPLETE_REQ` | T005 §12 | 1/1 fit |
| 11.23.2 | `S2C_QUEST_LIGHT_QUEST_GP_COMPLETE_RES` | T005 §15 | 1/1 fit, slack 15 |
| 11.31.1 | `C2S_QUEST_GET_QUEST_COMPLETE_LIST_REQ` | T005 §12 | 86/86 fit |
| 11.31.2 | `S2C_QUEST_GET_QUEST_COMPLETE_LIST_RES` | T005 §16 | 86/86 fit |
| 11.32.1 | `C2S_QUEST_SET_PRIORITY_QUEST_REQ` | T005 §12 | 3/3 fit |
| 11.32.2 | `S2C_QUEST_SET_PRIORITY_QUEST_RES` | T005 §17 | 3/3 fit |
| 11.32.16 | `S2C_QUEST_SET_PRIORITY_QUEST_NTC` | T005 §18 | 5/5 fit |
| 11.33.2 | `S2C_QUEST_CANCEL_PRIORITY_QUEST_RES` | T005 §17 | 2/2 fit |
| 11.34.1 | `C2S_QUEST_GET_PRIORITY_QUEST_REQ` | T005 §12 | 45/45 fit (no body) |
| 11.34.2 | `S2C_QUEST_GET_PRIORITY_QUEST_RES` | T005 §19 | 45/45 fit |
| 11.37.1 | `C2S_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_REQ` | T005 §12 | 41/41 fit (no body) |
| 11.37.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_STATE_LIST_RES` | P11a §12 | 41/41 fit |
| 11.38.1 | `C2S_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_REQ` | T005 §12 | 2/2 fit |
| 11.38.2 | `S2C_QUEST_GET_CYCLE_CONTENTS_SITUATION_INFO_LIST_RES` | T005 §20 | 2/2 fit |
| 11.39.1 | `C2S_QUEST_PLAY_ENTRY_REQ` | T005 §12 | 1/1 fit (no body) |
| 11.39.2 | `S2C_QUEST_PLAY_ENTRY_RES` | T005 §21 | 1/1 fit, slack 15 |
| 11.39.16 | `S2C_QUEST_PLAY_ENTRY_NTC` | T005 §22 | 1/1 fit (PS4 PLAY_ENTRY_NOTICE, V by behaviour) |
| 11.41.1 | `C2S_QUEST_PLAY_START_REQ` | T005 §12 | 1/1 fit |
| 11.41.2 | `S2C_QUEST_PLAY_START_RES` | T005 §21 | 1/1 fit, slack 15 |
| 11.42.1 | `C2S_QUEST_PLAY_START_TIMER_REQ` | T005 §12 | 1/1 fit (no body) |
| 11.42.2 | `S2C_QUEST_PLAY_START_TIMER_RES` | T005 §21 | 1/1 fit, slack 15 |
| 11.45.1 | `C2S_QUEST_PLAY_END_REQ` | T005 §12 | 1/1 fit (no body) |
| 11.45.2 | `S2C_QUEST_PLAY_END_RES` | T005 §21 | 1/1 fit, slack 15 |
| 11.45.16 | `S2C_QUEST_PLAY_END_NTC` | T005 §23 | 1/1 fit, slack 12 |
| 11.56.1 | `C2S_QUEST_GET_AREA_INFO_LIST_REQ` | T005 §12 | 1/1 fit (no body) |
| 11.56.2 | `S2C_QUEST_GET_AREA_INFO_LIST_RES` | P11a §11 | 1/1 fit |
| 11.57.1 | `C2S_QUEST_GET_QUEST_PARTY_BONUS_LIST_REQ` | T005 §12 | 84/84 fit (no body) |
| 11.57.2 | `S2C_QUEST_GET_QUEST_PARTY_BONUS_LIST_RES` | T005 §24 | 84/84 fit |
| 11.60.16 | `C2S_QUEST_11_60_16_NTC` | T005 §25 | 7/7 fit (client to server; code name PRT_READY_SET_RETURN_SESSION, V by behaviour) |
| 11.62.1 | `C2S_QUEST_GET_REWARD_BOX_LIST_REQ` | T005 §12 | 8/8 fit (no body) |
| 11.62.2 | `S2C_QUEST_GET_REWARD_BOX_LIST_RES` | T005 §26 | 8/8 fit |
| 11.64.1 | `C2S_QUEST_GET_REWARD_BOX_ITEM_REQ` | T005 §27 | 6/6 fit |
| 11.64.2 | `S2C_QUEST_GET_REWARD_BOX_ITEM_RES` | T005 §27 | 6/6 fit, slack 15 |
| 11.69.1 | `C2S_QUEST_DELIVER_ITEM_REQ` | T005 §29 | 1/1 fit, slack 15 |
| 11.69.2 | `S2C_QUEST_DELIVER_ITEM_RES` | T005 §29 | 1/1 fit |
| 11.69.16 | `S2C_QUEST_DELIVER_ITEM_NTC` | T005 §29 | 1/1 fit |
| 11.70.1 | `C2S_QUEST_DECIDE_DELIVERY_ITEM_REQ` | T005 §30 | 1/1 fit |
| 11.70.2 | `S2C_QUEST_DECIDE_DELIVERY_ITEM_RES` | T005 §30 | 1/1 fit |
| 11.70.16 | `S2C_QUEST_DECIDE_DELIVERY_ITEM_NTC` | T005 §30 | 1/1 fit, slack 15 (PS4 DECIDE_DELIVERY_ITEM_NOTICE, V by notice class) |
| 11.71.1 | `C2S_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_REQ` | T005 §12 | 43/43 fit (no body) |
| 11.71.2 | `S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES` | P11a §4 | 43/43 fit |
| 11.83.16 | `S2C_QUEST_11_83_16_NTC` | T005 §31 | 20/20 fit, slack 15 (code name SET_QUEST_UNRELEASED_AREA_NOTICE, V by notice class) |
| 11.89.16 | `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC` | P11a §1 | 41/41 fit |
| 11.90.16 | `S2C_QUEST_PROGRESS_WORK_SAVE_NTC` | T005 §33 | 11/11 fit |
| 11.91.16 | `S2C_QUEST_QUEST_COMPLETE_NTC` | T005 §34 | 4/4 fit, slack 12 |
| 11.95.16 | `S2C_QUEST_11_95_16_NTC` | T005 §35 | 48/48 fit (code name FORT_DEFENSE_NOTICE, V by notice class) |
| 11.101.16 | `S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC` | T005 §36 | 1/1 fit |
| 11.103.16 | `S2C_QUEST_11_103_16_NTC` | T005 §37 | 1/1 fit (code name PLAY_STOP_TIMER_NOTICE, V by notice class; no body) |
| 11.117.16 | `S2C_QUEST_11_117_16_NTC` | T005 §38 | 47/47 fit (code name REWARD_BOX_LIST_NUM_NOTICE, V by behaviour; the PS4 u8-only body fits too) |
| 11.120.16 | `S2C_QUEST_PARTY_QUEST_PROGRESS_NTC` | P11a §3 | no capture |
| 12.0.1 | `C2S_STAGE_GET_STAGE_LIST_REQ` | T006 §3.1 | 42/42 fit (no body) |
| 12.0.2 | `S2C_STAGE_GET_STAGE_LIST_RES` | P11a §7 | 42/42 fit |
| 12.1.1 | `C2S_STAGE_AREA_CHANGE_REQ` | T006 §3.2 | 150/150 fit, slack 15 |
| 12.1.2 | `S2C_STAGE_AREA_CHANGE_RES` | T006 §3.2 | 150/150 fit |
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
| 14.1.1 | `C2S_WARP_GET_RELEASE_WARP_POINT_LIST_REQ` | T008 §2.1 | 41/41 fit (no body) |
| 14.1.2 | `S2C_WARP_GET_RELEASE_WARP_POINT_LIST_RES` | T008 §2.1 | 41/41 fit |
| 14.2.1 | `C2S_WARP_GET_WARP_POINT_LIST_REQ` | T008 §2.2 | 178/178 fit |
| 14.2.2 | `S2C_WARP_GET_WARP_POINT_LIST_RES` | T008 §2.2 | 178/178 fit |
| 14.3.1 | `C2S_WARP_WARP_REQ` | T008 §2.3 | 44/44 fit |
| 14.3.2 | `S2C_WARP_WARP_RES` | T008 §2.3 | 44/44 fit |
| 14.4.1 | `C2S_WARP_GET_FAVORITE_WARP_POINT_LIST_REQ` | T008 §2.4 | 104/104 fit |
| 14.4.2 | `S2C_WARP_GET_FAVORITE_WARP_POINT_LIST_RES` | T008 §2.4 | 104/104 fit |
| 14.8.1 | `C2S_WARP_GET_AREA_WARP_POINT_LIST_REQ` | T008 §2.5 | 1/1 fit |
| 14.8.2 | `S2C_WARP_GET_AREA_WARP_POINT_LIST_RES` | T008 §2.5 | 1/1 fit, slack 15 |
| 14.9.1 | `C2S_WARP_AREA_WARP_REQ` | T008 §2.6 | 18/18 fit |
| 14.9.2 | `S2C_WARP_AREA_WARP_RES` | T008 §2.6 | 18/18 fit |
| 14.10.16 | `C2S_WARP_WARP_START_NTC` | T008 §2.7 | 62/62 fit (no body; code name C2S_WARP_END_NTC, V by call site: the raw name WARP_START is contradicted) |
| 14.12.1 | `C2S_WARP_GET_RETURN_LOCATION_REQ` | T008 §2.9 | 9/9 fit (no body) |
| 14.12.2 | `S2C_WARP_GET_RETURN_LOCATION_RES` | T008 §2.9 | 9/9 fit |
| 18.0.2 | `S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES` | P11b §18 | 41/41 fit |
| 19.1.2 | `S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES` | P11b §16 | 4/4 fit |
| 19.2.2 | `S2C_SKILL_GET_ACQUIRABLE_ABILITY_LIST_RES` | P11b §17 | 16/16 fit |
| 23.0.1 | `C2S_AREA_GET_AREA_MASTER_INFO_REQ` | P11a §18 | 42/42 fit |
| 23.0.2 | `S2C_AREA_GET_AREA_MASTER_INFO_RES` | P11a §17 | 42/42 fit |
| 23.3.1 | `C2S_AREA_GET_AREA_SUPPLY_INFO_REQ` | T006 §4 | 13/13 fit |
| 23.3.2 | `S2C_AREA_GET_AREA_SUPPLY_INFO_RES` | P11b §10 | 13/13 fit |
| 23.4.1 | `C2S_AREA_GET_AREA_SUPPLY_REQ` | P11b §9 | 12/12 fit |
| 23.4.2 | `S2C_AREA_GET_AREA_SUPPLY_RES` | T006 §4 | 12/12 fit, slack 15 |
| 23.8.1 | `C2S_AREA_GET_LEADER_AREA_RELEASE_LIST_REQ` | T006 §4 | 131/131 fit (no body) |
| 23.8.2 | `S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES` | P11a §15 | 131/131 fit |
| 23.9.1 | `C2S_AREA_GET_AREA_QUEST_HINT_LIST_REQ` | P11a §14 | 183/183 fit |
| 23.9.2 | `S2C_AREA_GET_AREA_QUEST_HINT_LIST_RES` | P11a §13 | 183/183 fit |
| 23.11.1 | `C2S_AREA_GET_SPOT_INFO_LIST_REQ` | P11b §8 | 29/29 fit |
| 23.11.2 | `S2C_AREA_GET_SPOT_INFO_LIST_RES` | P11b §11 | 29/29 fit |
| 23.12.1 | `C2S_AREA_GET_AREA_BASE_INFO_LIST_REQ` | T006 §4 | 72/72 fit (no body) |
| 23.12.2 | `S2C_AREA_GET_AREA_BASE_INFO_LIST_RES` | P11a §16 | 72/72 fit |
| 23.13.16 | `S2C_AREA_POINT_UP_NTC` | P11b §7 | 29/29 fit |
| 31.4.2 | `S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES` | P11b §6 | 41/41 fit |
| 31.17.2 | `S2C_CLAN_CLAN_SETTING_UPDATE_RES` | P11b §5 | 42/42 fit |
| 31.29.1 | `C2S_CLAN_CLAN_GET_MY_INFO_REQ` | P11b §1 | 41/41 fit |
| 31.29.2 | `S2C_CLAN_CLAN_GET_MY_INFO_RES` | P11b §4 | 41/41 fit |
| 33.0.1 | `C2S_JOB_GET_JOB_CHANGE_LIST_REQ` | T006 §1.1 | 42/42 fit (no body) |
| 33.0.2 | `S2C_JOB_GET_JOB_CHANGE_LIST_RES` | T006 §1.1 | 42/42 fit |
| 33.11.16 | `S2C_JOB_CHARACTER_JOB_EXP_UP_NTC` | T006 §1.2 | 417/417 fit |
| 33.12.16 | `S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC` | T006 §1.3 | 1/1 fit |
| 33.13.16 | `S2C_JOB_CHARACTER_JOB_LEVEL_UP_MEMBER_NTC` | T006 §1.4 | 1/1 fit |
| 33.15.16 | `S2C_JOB_PAWN_JOB_EXP_UP_NTC` | T006 §1.5 | 1245/1245 fit |
| 33.16.16 | `S2C_JOB_PAWN_JOB_LEVEL_UP_NTC` | T006 §1.6 | 3/3 fit, slack 2 |
| 33.17.16 | `S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC` | T006 §1.7 | 3/3 fit |
| 33.20.16 | `S2C_JOB_PLAY_POINT_NTC` | T006 §1.8 | 14/14 fit (code name UPDATE_PLAY_POINT_NOTICE, V by behaviour) |
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
| 50.0.1 | `C2S_ITEM_SORT_GET_ITEM_SORTDATA_BIN_REQ` | T008 §4.1 | 46/46 fit |
| 50.0.2 | `S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_RES` | T008 §4.1 | 46/46 fit (list never non-empty) |
| 50.1.1 | `C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ` | T008 §4.3 | 59/59 fit (Season 3 trailing bool: code-only, the PS4 body fits too) |
| 50.1.2 | `S2C_ITEM_SORT_SET_ITEM_SORTDATA_BIN_RES` | T008 §4.3 | 59/59 fit, slack 15 |
| 51.0.2 | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES` | P11a §6 | 1/1 fit |
| 52.1.2 | `S2C_MY_ROOM_FURNITURE_LIST_GET_RES` | P11a §10 | 20/20 fit |
| 53.4.1 | `C2S_PARTNER_PAWN_PAWN_LIKABILITY_REWARD_LIST_GET_REQ` | T007 §3.1 | 40/40 fit (no body) |
| 53.4.2 | `S2C_PARTNER_PAWN_PAWN_LIKABILITY_REWARD_LIST_GET_RES` | T007 §3.1 | 40/40 fit (list never non-empty) |
| 53.6.1 | `C2S_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_REQ` | T007 §3.1 | 41/41 fit (no body) |
| 53.6.2 | `S2C_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES` | T007 §3.1 | 41/41 fit |
| 53.7.1 | `C2S_PARTNER_PAWN_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_REQ` | T007 §3.2 | 20/20 fit (no body) |
| 53.7.2 | `S2C_PARTNER_PAWN_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_RES` | T007 §3.2 | 20/20 fit |
| 53.8.1 | `C2S_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_REQ` | T007 §3.3 | 20/20 fit |
| 53.8.2 | `S2C_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_RES` | T007 §3.3 | 20/20 fit |
| 53.9.16 | `S2C_PARTNER_PAWN_LIKABILITY_UP_NTC` | T007 §3.4 | 23/23 fit (code name PAWN_LIKABILITY_UP_NTC, V by behaviour; the PS4 framing fits too) |
| 57.0.2 | `S2C_BOX_GACHA_BOX_GACHA_LIST_RES` | P11a §8 | 3/3 fit |
| 58.0.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_INFO_REQ` | T007 §4.1 | 30/30 fit (no body) |
| 58.0.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_INFO_RES` | T007 §4.1 | 30/30 fit (ActiveBuffLineup and ClanSallySpot lists never non-empty) |
| 58.3.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_SALLY_REQ` | T007 §4.2 | 25/25 fit, slack 15 |
| 58.3.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_SALLY_RES` | T007 §4.2 | 25/25 fit, slack 15 |
| 58.4.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_CHANGE_GOLDEN_SALLY_REQ` | T007 §4.3 | 4/4 fit |
| 58.4.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_CHANGE_GOLDEN_SALLY_RES` | T007 §4.3 | 4/4 fit, slack 15 |
| 58.5.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_REQ` | T007 §4.4 | 25/25 fit (no body) |
| 58.5.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES` | T007 §4.4 | 25/25 fit (Season 3 list + bool, V by code; every list holds 1 element, so the PS4 body fits too) |
| 58.7.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_REQ` | T007 §4.5 | 25/25 fit (no body) |
| 58.7.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_RES` | T007 §4.5 | 25/25 fit |
| 58.8.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_REQ` | T007 §4.6 | 50/50 fit |
| 58.8.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_RES` | T007 §4.6 | 50/50 fit (Season 3 17-byte element; the PS4 element fails 10/50) |
| 58.9.1 | `C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_REQ` | T007 §4.7 | 25/25 fit |
| 58.9.2 | `S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_RES` | T007 §4.7 | 25/25 fit (list never non-empty) |
| 60.0.1 | `C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ` | P11b §12 | 219/219 fit |
| 63.11.16 | `S2C_63_11_16_NTC` | P5 §7 | 1/1 fit |
| 64.0.2 | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES` | P11a §2 | 20/20 fit |

## Open items

- **0.10.16 name:** the raws and the pattern keep the CLI's name `S2C_CONNECTION_0_10_16_NTC`;
  the code-backed name is `SESSION_STATUS_NTC` (T003 §9, V by behaviour: the handler sets the
  SessionStatus byte of the lobby member with that CharacterID). Which of the PS4 lobby-member
  bytes Platform/ClientVersion Season 3 dropped is I.
- **Game setting names without code backing (T003 §11, §20):** the Season 3 tail of
  `CDataGameSetting` (`unk_bool`, `unk_u32_0..2`, `unk_u16`, and the elements of
  `CDataWalletLimit`, `CDataExpSetting`, `CDataExpRequirement`: struct names I by server lead, fields
  `unk_*` with the server names as `server: <name> (lead)` comments since R1b), and the
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
- **Season 3-exclusive, not patterned (T005):** 11.5.1/11.5.2 GET_PACKAGE_QUEST_LIST (T005 §7),
  11.7.16 `S2C_QUEST_11_7_16_NTC` (MobHuntQuestListNum, §8; the triage's PS4 candidate is
  contradicted), 11.68.16 QUEST_BOARD_RELOAD_NTC (§28, exclusive by absence, I), 11.121.x
  GET_LEVEL_BONUS_LIST (§40), 11.122.x GET_ADVENTURE_GUIDE_QUEST_LIST (§41) and 11.123.x
  GET_ADVENTURE_GUIDE_QUEST_NTC (§42). Their PC readers and wire layouts are in those sections; they
  go to a later spec with the other exclusive ids.
- **Group 11 unresolved, not patterned (T005):** 11.88.16 (§32: the PC handler is `return 1`, empty
  body) and 11.118.16 (§39: the PC handler discards one u8). With no-op PC handlers neither shape nor
  behaviour selects a PS4 counterpart.
- **Group 11 names without code backing (T005 §46):** in `CDataQuestList`, which u64 is new
  (`unk_u64`, then `EndDistributionDate` by position; in every capture checked the first is 0 and
  the second a date), the `unk_u32_list`, and `BaseWalletPoint`/`BaseExp` (I: the lists sit where
  PS4 has BaseGold/BaseExp/BaseRim) with OrderNpcId/NameMsgId/DetailMsgId (I, position);
  `CDataLightQuestDetail` stays `unk_u32_0..6` and `CDataSetQuestDetail` keeps `unk_u16_0/1` and its
  two unnamed lists (as 11.89.16 had them; the captured lists hold 100 per entry, ratio-like); the
  `CDataTimeGainQuestList` bool order (PS4 names on the first four, I) and its two Season 3
  members; the 11.14.2 extra u64 and trailing condition list; the 11.45.16 lead `unk_s32` and middle
  u32s (PlayTimeMillSec on the 7th u32 is I by capture timestamps); the 11.95.16 extra u64 and
  {u32, u32} list; the 11.101.16 bools and u8 list; the 11.117.16 u16 roles (count/capacity, I).
- **Group 11 code-only (T005 §43, §46):** the 11.9.2 list is never non-empty; the 11.117.16 u16 pair
  and the empty 11.103.16 body fit within the slack, so they rest on the PC code; no captured group-11
  RES has Error != 0. The PC handlers of 11.0.2, 11.2.2, 11.4.2, 11.21.2, 11.31.2, 11.33.2, 11.34.2
  and 11.45.16 lie in undefined code (read by linear decoding only). 11.120.16 still has no capture.
- **Shared quest types moved (T005b):** `CDataLightQuestDetail`, `CDataSetQuestDetail`,
  `CDataQuestId` and `CDataPriorityQuest` moved unchanged from the 11.89.16 pattern into
  `include/Quest.hexpat`; its 41 JSON files came out byte-identical. No existing quest pattern had a
  layout error in T005, so none changed its layout.
- **Season 3-exclusive, not patterned (T006):** 12.5.1/12.5.2 STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT
  (T006 §3.3: no PS4 symbol, type or string, V by code; 3 captures each) and 12.9.16
  `S2C_STAGE_DUNGEON_START_NTC` (§3.4: no PS4 reader with its member sequence, exclusive by absence,
  X(I); 3 captures; the packet name has no PC string). Their PC readers and wire layouts are in those
  sections; they go to a later spec with the other exclusive ids.
- **Groups 3, 12, 23, 33 names without code backing (T006 §8):** the three Season 3 fields of 3.2.1 and
  3.2.16 (`unk_u8`, `unk_u32_0/1`; server: MessageFlavor, PhrasesCategory, PhrasesIndex), the first
  `CDataLobbyMemberInfo` u8 (which PS4 byte, Platform or ClientVersion, Season 3 dropped is open) and
  `OnlineStatus` on the third (I, position; `SessionStatus` on the second is V by 0.10.16, T003 §9),
  the 3.0.2 list name `LobbyMemberInfoList` (I, element type), and the two 12.1.2 lists (`unk_List0/1`,
  element types `CDataAreaChangeUnk0/1` in `include/Stage.hexpat`).
- **Groups 3, 12, 23, 33 code-only (T006 §5, §8):** the 3.0.2 member u8 count (the PS4 4-u8 body also
  fits 41/41); the no-header framing of the 33.x NTCs (PS4 framing also fits them); the empty bodies of
  3.1.1, 12.0.1, 23.8.1, 23.12.1 and 33.0.1. No captured RES of these groups has Error != 0. PC code
  read linearly only: `0x82ede0` (3.0.1 writer), `0x7e2e00` (3.1.2 handler), `0x7e29b0` (3.2.16
  handler), `0x76d6f0` and `0x77246d` (list readers). The T001 `recompiled_body yes` of 3.2.1, 33.0.2,
  33.12.16, 33.16.16 and 33.17.16 is a `DDON_STUB` (T006 §5). The 3.0.1/3.0.2 suffixes also match 41 +
  41 login-server files: the LOBBY patterns select by name (`// packet-select:`).
- **No existing pattern changed (T006b):** T006 shows no layout error in an existing pattern;
  `CDataStageInfo` stays local to 12.0.2 (one user), and the new types are new names in the includes
  (no include cycle: Job includes Login, Login includes Character, Context and GP).
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
- **Groups 8, 53, 58 names without code backing (T007 §8):** the three `CDataPawnList` tail u32
  (`unk_u32_0..2`; server: Unk0, TrainingExp, Unk2), the `CDataPawnInfo` Season 3 members (`unk_List`
  {u8, u16}, server: CharacterItemSlotInfoList; `unk_u8[64]`, server: TrainingStatus;
  `unk_TrainingProfile` u32 x5, type name I by server lead; `unk_SpSkillList`), the second 8.36.16 list
  (`unk_JobOrbStatusList`; server: JobOrbHiBOStatusList) and the 58.5.2 second bool (`unk_bool`;
  `IsGoldenSally` on the first is I by position).
- **Groups 8, 53, 58 code-only (T007 §5, §8):** never non-empty in the captures: the 8.20.2 list
  (`CDataLostPawnList`), the 53.4.2 list (its element is exercised by 53.6.2), the 58.0.2
  ActiveBuffLineup and ClanSallySpot lists and the 58.9.2 list (element exercised by 58.9.1); the
  58.5.2 list always holds one element, so its count prefix and second bool rest on the PC reader; the
  8.37.16 `CharacterListElement.unk_u8` and the no-header framing of 53.9.16 fit either way. No
  captured RES of these groups has Error != 0. PC code read linearly only: `0x7ea0a0` (58.0.2
  handler), `0x7ebeb0` (8.37.16 handler), `0x759f80` (58.5.2 list reader).
- **53.9.16 message index:** the PC handler announces message 0x1CC, PS4 0x1CE; the message tables
  were not compared (I: shifted table).
- **Pawn types added, no existing pattern changed (T007b):** T007 shows no layout error in an
  existing pattern (no existing pattern used a PS4 `CDataPawnInfo`). `Pawn.hexpat` now includes
  `Login.hexpat`; the 41 JSON files of 8.30.2 (the only earlier user of `Pawn.hexpat`) came out
  byte-identical after re-export. `CDataPartyMember` joined `Character.hexpat` and the group 58 types
  the new `PawnExpedition.hexpat`; no include cycle (Pawn -> Login -> Character, Context, GP;
  PawnExpedition -> Packet).
- **14.10.16 name:** the raws and the pattern keep the CLI name `C2S_WARP_WARP_START_NTC`; the
  code-backed name is `C2S_WARP_END_NTC` (T008 §2.7, V by call site: the PC writer `0x840160` and PS4
  `Send_C2S_WARP_END_NTC` are both called once, from `aStage::move_menu_warp`, after the same store,
  with the same empty body). PS4 has no WARP_START symbol, so the raw name is contradicted (C).
- **Season 3-exclusive, not patterned (T008):** 14.14.1/14.14.2 GET_START_POINT_LIST (T008 §2.10:
  no PS4 symbol or type, V; 42 captures each), 14.11.16 `C2S_WARP_WARP_END_NTC` (§2.8: the PC writes
  a u32, no PS4 counterpart, I by absence; 57 captures), 10.14.16
  `S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC` (§3.10: u16 + list {u8, u32}, I by absence; 1 capture) and
  50.0.16 `S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC` (§4.2: list CDataItemSort, V by the reader's only
  PS4 caller; 48 captures). Their PC readers and wire layouts are in those sections; they go to a later
  spec with the other exclusive ids. The 10.14.16 element type (`CDataItemRewardEntry`, T008 §6) is not
  in `include/Item.hexpat` yet: no pattern in scope uses it.
- **Groups 10, 14, 50 names without code backing (T008 §8):** the `CDataItemList` fields after
  `ItemUId` (ItemId, ItemNum, StorageType, SlotNo, Color, PlusValue, Bind are I with the basis in the
  include; the three Equip u32 carry PS4 names in the server's order, I; the Season 3 u8 and three
  lists are `unk_*`), the `CDataSwitchStorage` second field (`ChangeStorageType`, I by position; the
  same PC list reader `0x75c570` serves `Server.hexpat`'s `CDataCharacterItemSlotInfo` {u8, u16}) and
  the 50.1.1 trailing `unk_bool`.
- **Groups 10, 14, 50 code-only (T008 §5, §8):** the 10.13.16 u16 element field and the 50.1.1
  trailing bool fit either way (the PS4 bodies fit too); the no-header framing of 10.0.16 and 10.10.16
  fits either way; the 50.0.2 list is never non-empty (its element is exercised by the unpatterned
  50.0.16); the three `CDataItemList` element lists are always empty in 10.6.2. No captured RES of these
  groups has Error != 0. PC code read linearly only: `0x7ddb80` (50.0.2 handler), `0x80ca00` (its
  reader), `0x75e6e0` (CDataItemSort list), `0x766af0` (CDataFavoriteWarpPoint list), `0x83f910` (14.8.1
  writer). The 10.10.16 GUI message index differs (PC `0x1BA`, PS4 `0x1BC`); the tables were not compared.
- **Item and warp types added, no existing pattern changed (T008b):** no existing pattern used a PS4
  `CDataItemList` or `CDataSwitchStorage` layout (searched: neither type nor their PC readers `0x76aca0`
  / `0x76abe0` appear in any earlier pattern), so none was wrong for Season 3. `include/Item.hexpat`
  now includes Character and Context; the 4 JSON files of 10.9.2 (its only earlier user) came out
  byte-identical after re-export (4/4, `cmp`). No include cycle (Item -> Packet, Character, Context; Warp -> Packet).
- **u64 OM Key in JSON:** `CDataOmData.Key` carries the high bit (0x80000000_001415b3), so the JSON
  integer exceeds 2^53; a reader that parses numbers as doubles rounds it (Python `json` keeps it
  exact).
