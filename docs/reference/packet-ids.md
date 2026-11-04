# Packet ids, client 03040008

Every packet pattern of the PC client 03040008, by packet id, for a reader who wants to know whether a packet is decoded, how often it was captured and which report holds its evidence. Read [Packet evidence marks](packet-marks.md) for the marks and the [glossary](glossary.md) for fit and slack. `tools/docs_check.py` compares this table with the patterns: the rows are edited by script, never by hand over the whole table.

## Report labels

The Report column of the table, and the labels in code spans on the other packet pages, name a report and a section of it (`T003 §9` is section 9 of `T003`). A bare label `T003` is the report of spec 006, and `008 T003` the report of spec 008.

| Label | Report | Covers |
| --- | --- | --- |
| `P1` | `specs/005-netmsg-patterns/research/P1-ps4-wire-format.md` | PS4 wire format, nNetMsg |
| `P2` | `specs/005-netmsg-patterns/research/P2-pc-deltas.md` | PC differences from PS4, nNetMsg |
| `P3` | `specs/005-netmsg-patterns/tasks.md` | the first nNetMsg patterns and export |
| `P4` | `specs/005-netmsg-patterns/research/P4-context-binary-character.md` | group 35 CONTEXT |
| `P5` | `specs/005-netmsg-patterns/research/P5-pc-send-side.md` | PC send side, 13.44-13.47.16, 63.11.16 |
| `P7` | `specs/005-netmsg-patterns/research/P7-imhex-as-library.md` | ImHex as a library, the plbatch design |
| `P9`, `P10` | `specs/005-netmsg-patterns/tasks.md` | 6.24.16 and 6.26.16; the fit flag and slack |
| `P11a`, `P11b` | `specs/005-netmsg-patterns/research/P11a-old-patterns.md`, `specs/005-netmsg-patterns/research/P11b-old-patterns.md` | the older patterns |
| `R1`, `R2` | `specs/005-netmsg-patterns/research/R1-pattern-review.md`, `specs/005-netmsg-patterns/research/R2-old-patterns-review.md` | reviews of those patterns |
| `T001b` | `specs/006-packet-pattern-coverage/research/T001b-save-blob.md` | the save blob of 9.0.2 and 9.1.1, `include/CharacterData.hexpat` |
| `T001c` | `specs/006-packet-pattern-coverage/research/T001c-parked-static-items.md` | items parked before these reports |
| `T002`, `T002c` | `specs/006-packet-pattern-coverage/research/T002-login.md`, `specs/006-packet-pattern-coverage/research/T002c-challenge-decrypt.md` | the login group; first-packet decryption |
| `T003` | `specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md` | groups 0 CONNECTION, 1 SERVER and 44 CERT of the game server |
| `T004` | `specs/006-packet-pattern-coverage/research/T004-instance.md` | group 13 INSTANCE |
| `T005` | `specs/006-packet-pattern-coverage/research/T005-quest.md` | group 11 QUEST |
| `T006` | `specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md` | groups 33 JOB, 3 LOBBY, 23 AREA and 12 STAGE |
| `T007` | `specs/006-packet-pattern-coverage/research/T007-pawn-partner.md` | groups 8 PAWN, 53 PARTNER_PAWN and 58 PAWN_EXPEDITION |
| `T008` | `specs/006-packet-pattern-coverage/research/T008-warp-item.md` | groups 14 WARP, 10 ITEM and 50 ITEM_SORT |
| `T009` | `specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md` | groups 2 CHARACTER, 37 MAIL and 45 STAMP |
| `T010` | `specs/006-packet-pattern-coverage/research/T010-gp-clan.md` | groups 28 GP and 31 CLAN |
| `T011` | `specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md` | groups 5 (user list), 6 PARTY, 16 FRIEND, 17 BLACK_LIST and 26 PROFILE |
| `T012` | `specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md` | groups 19 SKILL, 20 SHOP, 25 ORB_DEVOTE, 27 ACHIEVEMENT, 29 EQUIP, 39 GACHA and 43 LOADING_INFO |
| `T013` | `specs/006-packet-pattern-coverage/research/T013-small-groups.md` | groups 9 (save response), 15 (event notices), 18 (group chat request), 30 CRAFT, 34 ENTRY_BOARD, 41 CHARACTER_EDIT, 51 DISPEL, 52 (furniture request), 54 CRAFT_RECIPE and 57 (box gacha request) |
| `T014a`, `T014b` | `specs/006-packet-pattern-coverage/research/T014a-value-correlation.md`, `specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.md` | value correlation of `unk_*` fields; consumer and property names |
| `R4` | `specs/006-packet-pattern-coverage/research/R4-adversarial-marks.md` | review of the marks |
| `T003b ... T013b`, `T005b`, `TC1`, `TC2`, `R1b`, `R2b` | `specs/006-packet-pattern-coverage/tasks.md` | the patterns and re-export of a report (`b`), the naming sweep (`TC1`), the code-backed renames (`TC2`), the reviews |
| `008 T003` | `specs/008-remaining-packets/research/T003-batches-B5-B2.md` | 33 ids of groups 11, 14, 24, 28, 31, 45, 60, 61, 64 and 70 |
| `008 T004` | `specs/008-remaining-packets/research/T004-batches-B1-B4.md` | 37 ids of groups 59 INFINITY_DELIVERY, 62 SEASON_DUNGEON, 71 BATTLE_CONTENT and 72 DAILY_MISSION |
| `008 T005` | `specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md` | 45 ids of groups 2, 10, 12, 13, 27, 29, 34, 41, 50, 62, 63 and 65 |
| `008 T006`, `008 T007` | `specs/008-remaining-packets/research/T006-adversarial.md`, `specs/008-remaining-packets/research/t007/` | review of those marks; the rewrite of the value bases (`marks.py`, `mark-changes.tsv`) |

## Reading the table

- **Status `n/m fit`:** n of the m JSON files of that packet in `packets/decrypted_json/` have `fits` true. No packet has a `.json.err`.
- **Status `no capture`:** no raw file exists, so the pattern was checked on synthetic input at most.
- **Pattern name:** the file `<name>-pattern.cpp`. A pattern file may carry a better name than its raw files, because the export selects by `// packet-id:`: the rows say so (62.39.16, 63.2.16 among them). `(was ...)` gives the name the raw files had before the code-backed rename.
- **`marks:`** the row counts the marks in the pattern file; the structures of an include carry their own.

## The table

Fit counts not recounted: run `tools/docs_check.py --packet-counts --write`.

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
| 0.10.16 | `S2C_CONNECTION_SESSION_STATUS_NTC` | T003 §9 | 2/2 fit (renamed in TC2 from `S2C_CONNECTION_0_10_16_NTC`; code name SESSION_STATUS_NTC, V by behaviour) |
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
| 2.0.1 | `C2S_CHARACTER_DECIDE_CHARACTER_ID_REQ` | T009 §2 | 42/42 fit |
| 2.0.2 | `S2C_CHARACTER_DECIDE_CHARACTER_ID_RES` | T009 §1.3, §2 | 42/42 fit (Season 3 `CDataCharacterInfo` list and trailing u8; the PS4 body fails 22/42) |
| 2.1.1 | `C2L_GET_GAME_SESSION_KEY_REQ` | T002 §5 | 42/42 fit |
| 2.1.2 | `L2C_GET_GAME_SESSION_KEY_RES` | T002 §5 | 42/42 fit |
| 2.2.1 | `C2L_GET_LOGIN_SETTING_REQ` | T002 §6 | 41/41 fit |
| 2.2.2 | `L2C_GET_LOGIN_SETTING_RES` | T002 §6 | 41/41 fit |
| 2.3.16 | `L2C_NEXT_CONNECT_SERVER_NTC` | T002 §7 | 42/42 fit |
| 2.5.16 | `S2C_CHARACTER_2_5_16_NTC` | 008 T005 | 2/2 fit (T005 marks: open 1) |
| 2.6.16 | `S2C_CHARACTER_CONTENTS_RELEASE_ELEMENT_NTC` | T009 §4 | 41/41 fit (code name V by behaviour; the PS4 framing fails 41/41) |
| 2.7.16 | `S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_UPDATE_NTC` | T009 §5 | 111/111 fit (Season 3 list element u8; the PS4 element fails 107/111) |
| 2.12.1 | `C2S_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_REQ` | T009 §6 | 45/45 fit |
| 2.12.2 | `S2C_CHARACTER_COMMUNITY_CHARACTER_STATUS_GET_RES` | T009 §6 | 45/45 fit, slack 15 |
| 2.13.16 | `C2S_CHARACTER_CHARACTER_DOWN_NTC` | P4 §4 | 14/14 fit |
| 2.14.16 | `C2S_CHARACTER_CHARACTER_DOWN_CANCEL_NTC` | P4 §4 | no capture |
| 2.15.16 | `C2S_CHARACTER_CHARACTER_DEAD_NTC` | P4 §4 | 7/7 fit |
| 2.16.1 | `C2S_CHARACTER_CHARACTER_POINT_REVIVE_REQ` | T009 §7 | 5/5 fit |
| 2.16.2 | `S2C_CHARACTER_CHARACTER_POINT_REVIVE_RES` | T009 §7 | 5/5 fit |
| 2.18.1 | `C2S_CHARACTER_CHARACTER_PENALTY_REVIVE_REQ` | T009 §8 | 2/2 fit (Season 3 +u32; the PS4 body fails 2/2) |
| 2.18.2 | `S2C_CHARACTER_CHARACTER_PENALTY_REVIVE_RES` | T009 §8 | 2/2 fit, slack 15 |
| 2.19.16 | `C2S_CHARACTER_PAWN_DOWN_NTC` | P4 §4 | 20/20 fit |
| 2.20.16 | `C2S_CHARACTER_PAWN_DOWN_CANCEL_NTC` | P4 §4 | 10/10 fit |
| 2.21.16 | `C2S_CHARACTER_PAWN_DEAD_NTC` | P4 §4 | no capture |
| 2.24.1 | `C2S_CHARACTER_GET_REVIVE_CHARGEABLE_TIME_REQ` | T009 §9 | 3/3 fit (no body) |
| 2.24.2 | `S2C_CHARACTER_GET_REVIVE_CHARGEABLE_TIME_RES` | T009 §9 | 3/3 fit |
| 2.25.1 | `C2S_CHARACTER_CHARGE_REVIVE_POINT_REQ` | T009 §10 | 2/2 fit (no body) |
| 2.25.2 | `S2C_CHARACTER_CHARGE_REVIVE_POINT_RES` | T009 §10 | 2/2 fit |
| 2.27.16 | `S2C_CHARACTER_START_LANTERN_NTC` | T009 §11 | 25/25 fit (code name V by behaviour; the PS4 framing fits too) |
| 2.28.16 | `S2C_CHARACTER_FINISH_LANTERN_NTC` | T009 §11 | 9/9 fit (no body; code name V by behaviour) |
| 2.29.16 | `S2C_CHARACTER_START_LANTERN_OTHER_NTC` | T009 §11 | 3/3 fit (layout V; which OTHER notice is I, by ordering) |
| 2.30.16 | `S2C_CHARACTER_FINISH_LANTERN_OTHER_NTC` | T009 §11 | 1/1 fit (layout V; which OTHER notice is I, by ordering) |
| 2.31.16 | `S2C_CHARACTER_START_DEATH_PENALTY_NTC` | T009 §11 | 2/2 fit (code name V by behaviour) |
| 2.32.16 | `S2C_CHARACTER_FINISH_DEATH_PENALTY_NTC` | T009 §11 | 1/1 fit (no body; code name V by behaviour) |
| 2.38.1 | `C2S_CHARACTER_SET_ONLINE_STATUS_REQ` | T009 §12 | 2/2 fit |
| 2.38.2 | `S2C_CHARACTER_SET_ONLINE_STATUS_RES` | T009 §12 | 2/2 fit |
| 3.0.1 | `C2L_GET_ERROR_MESSAGE_LIST_REQ` | T002 §8 | 41/41 fit |
| 3.0.1 | `C2S_LOBBY_LOBBY_JOIN_REQ` | T006 §2.1 | 41/41 fit, slack 15 (packet-select: the login id 3.0.1 shares the suffix) |
| 3.0.2 | `S2C_LOBBY_LOBBY_JOIN_RES` | T006 §2.1 | 41/41 fit (packet-select; PS4's 4-u8 member fits these too: the 3 u8 rest on the PC reader and the 5.2.16 captures, T011 §2) |
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
| 5.2.16 | `S2C_USER_LIST_JOIN_NTC` | T011 §2 | 148/148 fit (code name V by behaviour; Season 3 3-u8 member: the PS4 element fails 50/148, the PS4 framing 148/148) |
| 5.3.16 | `S2C_USER_LIST_LEAVE_NTC` | T011 §3 | 162/162 fit (code name V by behaviour; the PS4 framing fails 162/162) |
| 5.5.16 | `L2C_LOGIN_WAIT_NUM_NTC` | T002 §13 | 9/9 fit |
| 6.0.1 | `C2S_PARTY_PARTY_CREATE_REQ` | T011 §4 | 42/42 fit (no body) |
| 6.0.2 | `S2C_PARTY_PARTY_CREATE_RES` | T011 §4 | 42/42 fit |
| 6.8.1 | `C2S_PARTY_PARTY_JOIN_REQ` | T011 §5 | 1/1 fit |
| 6.8.2 | `S2C_PARTY_PARTY_JOIN_RES` | T011 §5 | 1/1 fit |
| 6.8.16 | `S2C_PARTY_PARTY_JOIN_NTC` | T011 §6 | 43/43 fit (code name V by behaviour; Season 3 through the list element's u8, which the PS4 element fits too; the PS4 framing fails 43/43) |
| 6.10.1 | `C2S_PARTY_PARTY_LEAVE_REQ` | T011 §7 | 43/43 fit (no body) |
| 6.10.2 | `S2C_PARTY_PARTY_LEAVE_RES` | T011 §7 | 43/43 fit, slack 15 |
| 6.10.16 | `S2C_PARTY_PARTY_LEAVE_NTC` | T011 §7 | 43/43 fit (code name V by behaviour; the PS4 framing fits too) |
| 6.15.1 | `C2S_PARTY_PARTY_MEMBER_SET_VALUE_REQ` | T011 §8 | 6/6 fit |
| 6.15.2 | `S2C_PARTY_PARTY_MEMBER_SET_VALUE_RES` | T011 §8 | 6/6 fit, slack 15 |
| 6.18.16 | `S2C_PARTY_PARTY_INVITE_ACCEPT_NTC` | T011 §9 | 1/1 fit (code name V by code shape and capture flow; the PS4 framing fits too) |
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
| 9.1.2 | `S2C_BINARY_SAVE_SET_CHARACTER_BIN_SAVEDATA_RES` | T013 §11 | 47/47 fit, slack 15 (header only) |
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
| 10.14.16 | `S2C_ITEM_ACHIEVEMENT_REWARD_RECEIVE_NTC` | 008 T005 | 1/1 fit (T005 marks: V 1, open 3) |
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
| 11.5.1 | `C2S_QUEST_GET_PACKAGE_QUEST_LIST_REQ` | 008 T003 | 146/146 fit (T003 marks: open 1) |
| 11.5.2 | `S2C_QUEST_GET_PACKAGE_QUEST_LIST_RES` | 008 T003 | 146/146 fit (list never non-empty; T003 marks: I 2, G 2, open 6) |
| 11.7.16 | `S2C_QUEST_MOB_HUNT_QUEST_LIST_NUM_NTC` | 008 T003 | 43/43 fit (renamed from the raw name `S2C_QUEST_11_7_16_NTC`: notice class cQuestSvNotQuestMobHuntQuestListNum, I (consumer); T003 marks: I 1, G 1, open 1) |
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
| 11.60.16 | `C2S_QUEST_PRT_READY_SET_RETURN_SESSION_NTC` (was `C2S_QUEST_11_60_16_NTC`) | T005 §25 | 7/7 fit (client to server; code name PRT_READY_SET_RETURN_SESSION, V by behaviour) |
| 11.62.1 | `C2S_QUEST_GET_REWARD_BOX_LIST_REQ` | T005 §12 | 8/8 fit (no body) |
| 11.62.2 | `S2C_QUEST_GET_REWARD_BOX_LIST_RES` | T005 §26 | 8/8 fit |
| 11.64.1 | `C2S_QUEST_GET_REWARD_BOX_ITEM_REQ` | T005 §27 | 6/6 fit |
| 11.64.2 | `S2C_QUEST_GET_REWARD_BOX_ITEM_RES` | T005 §27 | 6/6 fit, slack 15 |
| 11.68.16 | `S2C_QUEST_QUEST_BOARD_RELOAD_NTC` | 008 T003 | 1/1 fit (T003 marks: V 3) |
| 11.69.1 | `C2S_QUEST_DELIVER_ITEM_REQ` | T005 §29 | 1/1 fit, slack 15 |
| 11.69.2 | `S2C_QUEST_DELIVER_ITEM_RES` | T005 §29 | 1/1 fit |
| 11.69.16 | `S2C_QUEST_DELIVER_ITEM_NTC` | T005 §29 | 1/1 fit |
| 11.70.1 | `C2S_QUEST_DECIDE_DELIVERY_ITEM_REQ` | T005 §30 | 1/1 fit |
| 11.70.2 | `S2C_QUEST_DECIDE_DELIVERY_ITEM_RES` | T005 §30 | 1/1 fit |
| 11.70.16 | `S2C_QUEST_DECIDE_DELIVERY_ITEM_NTC` | T005 §30 | 1/1 fit, slack 15 (PS4 DECIDE_DELIVERY_ITEM_NOTICE, V by notice class) |
| 11.71.1 | `C2S_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_REQ` | T005 §12 | 43/43 fit (no body) |
| 11.71.2 | `S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES` | P11a §4 | 43/43 fit |
| 11.83.16 | `S2C_QUEST_SET_QUEST_UNRELEASED_AREA_NTC` (was `S2C_QUEST_11_83_16_NTC`) | T005 §31 | 20/20 fit, slack 15 (code name SET_QUEST_UNRELEASED_AREA_NOTICE, V by notice class) |
| 11.88.16 | `S2C_QUEST_11_88_16_NTC` | 008 T003 | 20/20 fit (no body; PC handler reads nothing, meaning open; T003 marks: none (no fields)) |
| 11.89.16 | `S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC` | P11a §1 | 41/41 fit |
| 11.90.16 | `S2C_QUEST_PROGRESS_WORK_SAVE_NTC` | T005 §33 | 11/11 fit |
| 11.91.16 | `S2C_QUEST_QUEST_COMPLETE_NTC` | T005 §34 | 4/4 fit, slack 12 |
| 11.95.16 | `S2C_QUEST_FORT_DEFENSE_NTC` (was `S2C_QUEST_11_95_16_NTC`) | T005 §35 | 48/48 fit (code name FORT_DEFENSE_NOTICE, V by notice class) |
| 11.101.16 | `S2C_QUEST_TIME_GAIN_QUEST_PLAY_START_NTC` | T005 §36 | 1/1 fit |
| 11.103.16 | `S2C_QUEST_PLAY_STOP_TIMER_NTC` (was `S2C_QUEST_11_103_16_NTC`) | T005 §37 | 1/1 fit (code name PLAY_STOP_TIMER_NOTICE, V by notice class; no body) |
| 11.117.16 | `S2C_QUEST_REWARD_BOX_LIST_NUM_NTC` (was `S2C_QUEST_11_117_16_NTC`) | T005 §38 | 47/47 fit (code name REWARD_BOX_LIST_NUM_NOTICE, V by behaviour; the PS4 u8-only body fits too) |
| 11.118.16 | `S2C_QUEST_11_118_16_NTC` | 008 T003 | 41/41 fit (u8 read and discarded by the PC handler, meaning open; T003 marks: V 1) |
| 11.120.16 | `S2C_QUEST_PARTY_QUEST_PROGRESS_NTC` | P11a §3 | no capture |
| 11.121.1 | `C2S_QUEST_GET_LEVEL_BONUS_LIST_REQ` | 008 T003 | 182/182 fit (no body; T003 marks: none (no fields)) |
| 11.121.2 | `S2C_QUEST_GET_LEVEL_BONUS_LIST_RES` | 008 T003 | 182/182 fit (T003 marks: G 8, open 1) |
| 11.122.1 | `C2S_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_REQ` | 008 T003 | 45/45 fit (no body; T003 marks: none (no fields)) |
| 11.122.2 | `S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_LIST_RES` | 008 T003 | 45/45 fit, slack 15 (T003 marks: I 1, G 4, open 1) |
| 11.123.1 | `C2S_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_REQ` | 008 T003 | 155/155 fit (no body; T003 marks: none (no fields)) |
| 11.123.2 | `S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_RES` | 008 T003 | 155/155 fit (T003 marks: G 1) |
| 12.0.1 | `C2S_STAGE_GET_STAGE_LIST_REQ` | T006 §3.1 | 42/42 fit (no body) |
| 12.0.2 | `S2C_STAGE_GET_STAGE_LIST_RES` | P11a §7 | 42/42 fit |
| 12.1.1 | `C2S_STAGE_AREA_CHANGE_REQ` | T006 §3.2 | 150/150 fit, slack 15 |
| 12.1.2 | `S2C_STAGE_AREA_CHANGE_RES` | T006 §3.2 | 150/150 fit |
| 12.5.1 | `C2S_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_REQ` | 008 T005 | 3/3 fit (list writer V (008 T002), EntryFeeList empty; cstr as MtString wire; T005 marks: I 1, G 3) |
| 12.5.2 | `S2C_STAGE_UNISON_AREA_CHANGE_BEGIN_RECRUITMENT_RES` | 008 T005 | 3/3 fit (T005 marks: none (no fields)) |
| 12.9.16 | `S2C_STAGE_DUNGEON_START_NTC` | 008 T005 | 3/3 fit (EntryCostList empty; T005 marks: I 1, G 4, open 4) |
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
| 13.16.1 | `C2S_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_REQ` | 008 T005 | 1/1 fit (T005 marks: open 1) |
| 13.16.2 | `S2C_INSTANCE_TREASURE_POINT_GET_CATEGORY_LIST_RES` | 008 T005 | 1/1 fit (T005 marks: I 2, G 2) |
| 13.17.1 | `C2S_INSTANCE_TREASURE_POINT_GET_LIST_REQ` | 008 T005 | 1/1 fit (T005 marks: G 1) |
| 13.17.2 | `S2C_INSTANCE_TREASURE_POINT_GET_LIST_RES` | 008 T005 | 1/1 fit (T005 marks: I 2, G 2, open 1) |
| 13.20.1 | `C2S_INSTANCE_SET_OM_INSTANT_KEY_VALUE_REQ` | T004 §11 | 542/542 fit |
| 13.20.2 | `S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_RES` | T004 §11 | 559/559 fit |
| 13.20.16 | `S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_NTC` | T004 §11 | 571/571 fit (PS4 SET_OM_INSTANT_KEY_VALUE_NOTICE, V by behaviour) |
| 13.22.1 | `C2S_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_REQ` | T004 §12 | 150/150 fit (no body) |
| 13.22.2 | `S2C_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_RES` | T004 §12 | 150/150 fit |
| 13.23.1 | `C2S_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ` | T004 §13 | 44/44 fit |
| 13.23.2 | `S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_RES` | T004 §13 | 46/46 fit |
| 13.23.16 | `S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC` | 008 T005 | 46/46 fit (T005 marks: I 3) |
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
| 14.10.16 | `C2S_WARP_WARP_END_NTC` (was `C2S_WARP_WARP_START_NTC`) | T008 §2.7 | 62/62 fit (no body; code name C2S_WARP_END_NTC, V by call site: the old name WARP_START is contradicted) |
| 14.11.16 | `C2S_WARP_14_11_16_NTC` | 008 T003 | 57/57 fit (T003 marks: G 1) |
| 14.12.1 | `C2S_WARP_GET_RETURN_LOCATION_REQ` | T008 §2.9 | 9/9 fit (no body) |
| 14.12.2 | `S2C_WARP_GET_RETURN_LOCATION_RES` | T008 §2.9 | 9/9 fit |
| 14.14.1 | `C2S_WARP_GET_START_POINT_LIST_REQ` | 008 T003 | 42/42 fit (no body; T003 marks: none (no fields)) |
| 14.14.2 | `S2C_WARP_GET_START_POINT_LIST_RES` | 008 T003 | 42/42 fit (T003 marks: G 1) |
| 15.0.16 | `C2S_EVENT_START_NTC` | T013 §12 | 8/8 fit (no body; V by call graph) |
| 15.1.16 | `C2S_EVENT_END_NTC` | T013 §12 | 8/8 fit (no body; V by call graph) |
| 16.0.1 | `C2S_FRIEND_GET_FRIEND_LIST_REQ` | T011 §10 | 41/41 fit (no body) |
| 16.0.2 | `S2C_FRIEND_GET_FRIEND_LIST_RES` | T011 §10 | 41/41 fit (Season 3 through the list element's u8; the PS4 `CDataFriendInfo` fails 20/41) |
| 16.6.1 | `C2S_FRIEND_GET_RECENT_CHARACTER_LIST_REQ` | T011 §11 | 41/41 fit (no body) |
| 16.6.2 | `S2C_FRIEND_GET_RECENT_CHARACTER_LIST_RES` | T011 §11 | 41/41 fit (list never non-empty) |
| 17.0.1 | `C2S_BLACK_LIST_GET_BLACK_LIST_REQ` | T011 §12 | 41/41 fit (no body) |
| 17.0.2 | `S2C_BLACK_LIST_GET_BLACK_LIST_RES` | T011 §12 | 41/41 fit (list never non-empty) |
| 18.0.1 | `C2S_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_REQ` | T013 §11 | 41/41 fit (GroupID 0 in all) |
| 18.0.2 | `S2C_GROUP_CHAT_GROUP_CHAT_GET_MEMBER_LIST_RES` | P11b §18 | 41/41 fit |
| 19.1.1 | `C2S_SKILL_GET_ACQUIRABLE_SKILL_LIST_REQ` | T012 §2 | 4/4 fit, slack 2 (Season 3 + u32; the PS4 body fits too: the PC writer decides) |
| 19.1.2 | `S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES` | P11b §16 | 4/4 fit |
| 19.2.1 | `C2S_SKILL_GET_ACQUIRABLE_ABILITY_LIST_REQ` | T012 §2 | 16/16 fit, slack 2 (Season 3 + u32; the PS4 body fits too: the PC writer decides) |
| 19.2.2 | `S2C_SKILL_GET_ACQUIRABLE_ABILITY_LIST_RES` | P11b §17 | 16/16 fit |
| 19.28.1 | `C2S_SKILL_GET_CURRENT_SET_SKILL_LIST_REQ` | T012 §3 | 41/41 fit (no body) |
| 19.28.2 | `S2C_SKILL_GET_CURRENT_SET_SKILL_LIST_RES` | T012 §3 | 41/41 fit |
| 20.0.1 | `C2S_SHOP_GET_SHOP_GOODS_LIST_REQ` | T012 §4 | 18/18 fit |
| 20.0.2 | `S2C_SHOP_GET_SHOP_GOODS_LIST_RES` | T012 §6 | 18/18 fit (Season 3 body; the PS4 body fails 18/18) |
| 20.1.1 | `C2S_SHOP_BUY_SHOP_GOODS_REQ` | T012 §5 | 17/17 fit, slack 10 |
| 20.1.2 | `S2C_SHOP_BUY_SHOP_GOODS_RES` | T012 §7 | 17/17 fit, slack 14 (Season 3 drops the PS4 u32, V by the PC reader) |
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
| 24.6.16 | `S2C_JOB_MASTER_MARK_TARGETS_NTC` | 008 T003 | 150/150 fit, slack 15 (T003 marks: I 6, G 1) |
| 25.5.1 | `C2S_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_REQ` | T012 §8 | 43/43 fit (no body) |
| 25.5.2 | `S2C_ORB_DEVOTE_GET_ORB_GAIN_EXTEND_PARAM_RES` | T012 §8 | 43/43 fit |
| 26.1.1 | `C2S_PROFILE_GET_MY_CHARACTER_PROFILE_REQ` | T011 §14 | 4/4 fit (no body) |
| 26.1.2 | `S2C_PROFILE_GET_MY_CHARACTER_PROFILE_RES` | T011 §14 | 4/4 fit, slack 0 (Season 3: second job orb list, V; the PS4 body fails 4/4) |
| 26.12.1 | `C2S_PROFILE_SET_SHORTCUT_LIST_REQ` | T011 §15 | 42/42 fit |
| 26.12.2 | `S2C_PROFILE_SET_SHORTCUT_LIST_RES` | T011 §15 | 42/42 fit, slack 15 |
| 26.14.1 | `C2S_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_REQ` | T011 §16 | 41/41 fit |
| 26.14.2 | `S2C_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_RES` | T011 §16 | 41/41 fit, slack 15 |
| 27.0.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_GET_PROGRESS_LIST_REQ` | T012 §9 | 1/1 fit (no body) |
| 27.0.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_GET_PROGRESS_LIST_RES` | T012 §9 | 1/1 fit (678 entries) |
| 27.1.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_GET_REWARD_LIST_REQ` | T012 §9 | 1/1 fit (no body) |
| 27.1.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_GET_REWARD_LIST_RES` | T012 §9 | 1/1 fit, slack 1 (50 entries) |
| 27.2.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_REQ` | T012 §9 | 2/2 fit (no body) |
| 27.2.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_GET_FURNITURE_REWARD_LIST_RES` | T012 §9 | 2/2 fit (136 entries) |
| 27.3.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_REQ` | T012 §9 | 42/42 fit (no body) |
| 27.3.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_GET_RECEIVABLE_REWARD_LIST_RES` | T012 §9 | 42/42 fit |
| 27.4.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_REQ` | T012 §9 | 1/1 fit, slack 14 |
| 27.4.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_RES` | T012 §9 | 1/1 fit (both lists empty: code-only) |
| 27.8.16 | `S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC` | T012 §10 | 8/8 fit, slack 14 (code name V by behaviour; Season 3 element {u32, u8}; the PS4 framing fails 8/8, the PS4 element fits: the PC reader decides) |
| 27.9.16 | `S2C_ACHIEVEMENT_ACHIEVEMENT_RECEIVABLE_REWARD_NTC` | T012 §11 | 3/3 fit, slack 14 (code name V by list type and behaviour; the PS4 framing fails 3/3) |
| 27.10.1 | `C2S_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_REQ` | 008 T005 | 19/19 fit (T005 marks: G 1) |
| 27.10.2 | `S2C_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES` | 008 T005 | 19/19 fit (T005 marks: V 1) |
| 28.0.1 | `C2S_GP_GET_GP_REQ` | T010 §2 | 4/4 fit (no body) |
| 28.0.2 | `S2C_GP_GET_GP_RES` | T010 §2 | 4/4 fit |
| 28.2.1 | `C2S_GP_GET_GP_PERIOD_REQ` | T010 §3 | 42/42 fit (no body) |
| 28.2.2 | `S2C_GP_GET_GP_PERIOD_RES` | T010 §3 | 42/42 fit |
| 28.3.1 | `C2S_GP_GET_CAP_REQ` | T010 §4 | 2/2 fit (no body) |
| 28.3.2 | `S2C_GP_GET_CAP_RES` | T010 §4 | 2/2 fit |
| 28.6.1 | `C2S_GP_COG_GET_ID_REQ` | T010 §5 | 2/2 fit (no body) |
| 28.6.2 | `S2C_GP_COG_GET_ID_RES` | T010 §5 | 2/2 fit |
| 28.7.1 | `C2S_GP_GP_SHOP_DISPLAY_GET_TYPE_REQ` | T010 §6 | 2/2 fit (no body) |
| 28.7.2 | `S2C_GP_GP_SHOP_DISPLAY_GET_TYPE_RES` | T010 §6 | 2/2 fit |
| 28.8.1 | `C2S_GP_GP_SHOP_DISPLAY_GET_LINEUP_REQ` | T010 §7 | 38/38 fit |
| 28.8.2 | `S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES` | T010 §1.1, §7 | 38/38 fit (Season 3 element +MtString +u32; the PS4 element fails 38/38) |
| 28.9.1 | `C2S_GP_GP_SHOP_DISPLAY_BUY_REQ` | T010 §8 | 9/9 fit, slack 15 (Season 3 +u32; the PS4 body fails 9/9) |
| 28.9.2 | `S2C_GP_GP_SHOP_DISPLAY_BUY_RES` | T010 §8 | 9/9 fit (CommonIdList never non-empty) |
| 28.17.1 | `C2S_GP_GP_COURSE_GET_AVAILABLE_LIST_REQ` | T010 §9 | 10/10 fit (no body) |
| 28.17.2 | `S2C_GP_GP_COURSE_GET_AVAILABLE_LIST_RES` | T010 §1.1, §9 | 10/10 fit (list never non-empty: Season 3 element code-only) |
| 28.22.1 | `C2S_GP_GP_EDIT_GET_VOICE_LIST_REQ` | T010 §10 | 2/2 fit (no body) |
| 28.22.2 | `S2C_GP_GP_EDIT_GET_VOICE_LIST_RES` | T010 §10 | 2/2 fit |
| 28.23.1 | `C2S_GP_GP_SHOP_CAN_BUY_REQ` | 008 T003 | 9/9 fit (T003 marks: I 1, open 2) |
| 28.23.2 | `S2C_GP_GP_SHOP_CAN_BUY_RES` | 008 T003 | 9/9 fit (T003 marks: I 2, open 3) |
| 28.24.16 | `S2C_GP_28_24_16_NTC` | 008 T003 | 84/84 fit (T003 marks: open 1) |
| 28.25.16 | `S2C_GP_COURSE_START_NTC` | T010 §13 | 22/22 fit (code name V by behaviour; the PS4 framing fits too) |
| 28.26.16 | `S2C_GP_COURSE_EXTEND_NTC` | T010 §14 | 21/21 fit (code name V by behaviour; the PS4 framing fits too) |
| 28.34.1 | `C2S_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_REQ` | 008 T003 | 42/42 fit (no body; T003 marks: none (no fields)) |
| 28.34.2 | `S2C_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES` | 008 T003 | 42/42 fit (T003 marks: V 1) |
| 29.0.1 | `C2S_EQUIP_GET_CHARACTER_EQUIP_LIST_REQ` | T012 §13 | 41/41 fit (no body) |
| 29.0.2 | `S2C_EQUIP_GET_CHARACTER_EQUIP_LIST_RES` | T012 §13 | 41/41 fit |
| 29.1.1 | `C2S_EQUIP_CHANGE_CHARACTER_EQUIP_REQ` | T012 §13 | 5/5 fit |
| 29.1.2 | `S2C_EQUIP_CHANGE_CHARACTER_EQUIP_RES` | T012 §13 | 5/5 fit (Season 3 tail `CDataEquipChangeUnk`, always Job 10 + empty list; the PS4 body fits too: the PC reader decides) |
| 29.2.1 | `C2S_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_REQ` | T012 §13 | 2/2 fit |
| 29.2.2 | `S2C_EQUIP_CHANGE_CHARACTER_STORAGE_EQUIP_RES` | T012 §13 | 2/2 fit, slack 10 (Season 3 tail as 29.1.2) |
| 29.15.1 | `C2S_EQUIP_GET_CRAFT_LOCKED_ELEMENT_LIST_REQ` | T012 §13 | 2/2 fit (no body) |
| 29.15.2 | `S2C_EQUIP_GET_CRAFT_LOCKED_ELEMENT_LIST_RES` | T012 §13 | 2/2 fit (list never non-empty: Season 3 element code-only) |
| 29.17.16 | `S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC` | T012 §14 | 23/23 fit (code name V by shape and lobby check; Season 3 `CDataEquipItemInfo`: the PS4 element fails 23/23, the PS4 framing 23/23) |
| 29.23.16 | `S2C_EQUIP_29_23_16_NTC` | 008 T005 | 2/2 fit (handler ignores the body: capture shape only, marks G; T005 marks: G 8) |
| 30.0.1 | `C2S_CRAFT_GET_CRAFT_PROGRESS_LIST_REQ` | T013 §2 | 10/10 fit (no body) |
| 30.0.2 | `S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES` | T013 §1, §2 | 10/10 fit (progress list never non-empty: Season 3 `CDataCraftProgress` code-only) |
| 30.10.1 | `C2S_CRAFT_CRAFT_SKILL_UP_REQ` | T013 §3 | 1/1 fit |
| 30.10.2 | `S2C_CRAFT_CRAFT_SKILL_UP_RES` | T013 §3 | 1/1 fit |
| 30.12.1 | `C2S_CRAFT_RESET_CRAFTPOINT_REQ` | T013 §3 | 1/1 fit |
| 30.12.2 | `S2C_CRAFT_RESET_CRAFTPOINT_RES` | T013 §3 | 1/1 fit (5 skills) |
| 30.13.1 | `C2S_CRAFT_GET_CRAFT_SETTING_REQ` | T013 §4 | 2/2 fit (no body) |
| 30.13.2 | `S2C_CRAFT_GET_CRAFT_SETTING_RES` | T013 §1, §4 | 2/2 fit, slack 1 (Season 3 tail; the PS4 body fails 2/2) |
| 30.15.1 | `C2S_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_REQ` | T013 §3 | 2/2 fit (no body) |
| 30.15.2 | `S2C_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_RES` | T013 §3 | 2/2 fit (10 rates) |
| 31.4.1 | `C2S_CLAN_CLAN_GET_MY_MEMBER_LIST_REQ` | T010 §16 | 41/41 fit (no body) |
| 31.4.2 | `S2C_CLAN_CLAN_GET_MY_MEMBER_LIST_RES` | P11b §6 | 41/41 fit |
| 31.9.1 | `C2S_CLAN_CLAN_GET_JOIN_REQUESTED_LIST_REQ` | T010 §16 | 21/21 fit (no body) |
| 31.9.2 | `S2C_CLAN_CLAN_GET_JOIN_REQUESTED_LIST_RES` | T010 §17 | 21/21 fit (list never non-empty) |
| 31.17.1 | `C2S_CLAN_CLAN_SETTING_UPDATE_REQ` | T010 §16 | 42/42 fit |
| 31.17.2 | `S2C_CLAN_CLAN_SETTING_UPDATE_RES` | P11b §5 | 42/42 fit |
| 31.29.1 | `C2S_CLAN_CLAN_GET_MY_INFO_REQ` | P11b §1 | 41/41 fit |
| 31.29.2 | `S2C_CLAN_CLAN_GET_MY_INFO_RES` | P11b §4 | 41/41 fit |
| 31.30.1 | `C2S_CLAN_CLAN_GET_HISTORY_REQ` | T010 §16 | 1/1 fit (no body) |
| 31.30.2 | `S2C_CLAN_CLAN_GET_HISTORY_RES` | T010 §18 | 1/1 fit (87 entries) |
| 31.31.1 | `C2S_CLAN_CLAN_BASE_GET_INFO_REQ` | T010 §16 | 27/27 fit (no body) |
| 31.31.2 | `S2C_CLAN_CLAN_BASE_GET_INFO_RES` | T010 §19 | 27/27 fit (Season 3 furniture list; the PS4 body fails 27/27) |
| 31.34.1 | `C2S_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_REQ` | T010 §16 | 25/25 fit (no body) |
| 31.34.2 | `S2C_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_RES` | T010 §20 | 25/25 fit |
| 31.40.1 | `C2S_CLAN_CLAN_PARTNER_PAWN_DATA_GET_REQ` | T010 §21 | 28/28 fit (PS4 DWARF type; the triage's exclusive mark is contradicted) |
| 31.40.2 | `S2C_CLAN_CLAN_PARTNER_PAWN_DATA_GET_RES` | T010 §1.2, §21 | 28/28 fit (Season 3 second equip list; the PS4 body fails 22/28) |
| 31.53.1 | `C2S_CLAN_GET_FURNITURE_REQ` | 008 T003 | 27/27 fit (no body; T003 marks: none (no fields)) |
| 31.53.2 | `S2C_CLAN_GET_FURNITURE_RES` | 008 T003 | 27/27 fit (T003 marks: I 1) |
| 33.0.1 | `C2S_JOB_GET_JOB_CHANGE_LIST_REQ` | T006 §1.1 | 42/42 fit (no body) |
| 33.0.2 | `S2C_JOB_GET_JOB_CHANGE_LIST_RES` | T006 §1.1 | 42/42 fit |
| 33.11.16 | `S2C_JOB_CHARACTER_JOB_EXP_UP_NTC` | T006 §1.2 | 417/417 fit |
| 33.12.16 | `S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC` | T006 §1.3 | 1/1 fit |
| 33.13.16 | `S2C_JOB_CHARACTER_JOB_LEVEL_UP_MEMBER_NTC` | T006 §1.4 | 1/1 fit |
| 33.15.16 | `S2C_JOB_PAWN_JOB_EXP_UP_NTC` | T006 §1.5 | 1245/1245 fit |
| 33.16.16 | `S2C_JOB_PAWN_JOB_LEVEL_UP_NTC` | T006 §1.6 | 3/3 fit, slack 2 |
| 33.17.16 | `S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC` | T006 §1.7 | 3/3 fit |
| 33.20.16 | `S2C_JOB_PLAY_POINT_NTC` | T006 §1.8 | 14/14 fit (code name UPDATE_PLAY_POINT_NOTICE, V by behaviour) |
| 34.0.1 | `C2S_ENTRY_BOARD_ENTRY_BOARD_LIST_REQ` | 008 T005 | 1/1 fit (T001 `{4 8}` corrected to a u64 list; T005 marks: V 1) |
| 34.0.2 | `S2C_ENTRY_BOARD_ENTRY_BOARD_LIST_RES` | 008 T005 | 1/1 fit (T005 marks: G 5, open 4) |
| 34.1.1 | `C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_REQ` | T013 §6 | 3/3 fit, slack 1 (Season 3 search u32 x2; the PS4 body fits too: the PC writer decides) |
| 34.1.2 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_LIST_RES` | T013 §1, §6 | 3/3 fit (one item with 8 members; the PS4 element fails 1/3) |
| 34.2.1 | `C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_REQ` | T013 §6 | 1/1 fit (Season 3 recruit; the PS4 body fails 1/1) |
| 34.2.2 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CREATE_RES` | T013 §6 | 1/1 fit (Season 3 item; the PS4 body fails 1/1) |
| 34.6.1 | `C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_REQ` | T013 §7 | 1/1 fit (no body) |
| 34.6.2 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_RES` | T013 §7 | 1/1 fit, slack 15 (header only) |
| 34.6.16 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_READY_NTC` | T013 §7 | 1/1 fit (V by behaviour; the PS4 framing fails 1/1) |
| 34.7.1 | `C2S_ENTRY_BOARD_ENTRY_BOARD_ITEM_FORCE_START_REQ` | T013 §7 | 1/1 fit (no body) |
| 34.7.2 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_FORCE_START_RES` | T013 §7 | 1/1 fit, slack 15 (header only) |
| 34.14.16 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_CHANGE_MEMBER_NTC` | T013 §8 | 1/1 fit (the PS4 element and framing fail 1/1) |
| 34.16.16 | `S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_RESERVE_NTC` | T013 §8 | 1/1 fit, slack 15 (match and names I: unique {u32, u32} shape; the PS4 framing fits too) |
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
| 37.0.1 | `C2S_MAIL_MAIL_GET_LIST_HEAD_REQ` | T009 §13 | 42/42 fit (no body) |
| 37.0.2 | `S2C_MAIL_MAIL_GET_LIST_HEAD_RES` | T009 §13 | 42/42 fit |
| 37.1.1 | `C2S_MAIL_MAIL_GET_LIST_DATA_REQ` | T009 §13 | 42/42 fit |
| 37.1.2 | `S2C_MAIL_MAIL_GET_LIST_DATA_RES` | T009 §13 | 42/42 fit |
| 37.2.1 | `C2S_MAIL_MAIL_GET_LIST_FOOT_REQ` | T009 §13 | 42/42 fit (no body) |
| 37.2.2 | `S2C_MAIL_MAIL_GET_LIST_FOOT_RES` | T009 §13 | 42/42 fit, slack 15 |
| 37.6.1 | `C2S_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_REQ` | T009 §14 | 42/42 fit (no body) |
| 37.6.2 | `S2C_MAIL_SYSTEM_MAIL_GET_LIST_HEAD_RES` | T009 §14 | 42/42 fit |
| 37.7.1 | `C2S_MAIL_SYSTEM_MAIL_GET_LIST_DATA_REQ` | T009 §14 | 42/42 fit |
| 37.7.2 | `S2C_MAIL_SYSTEM_MAIL_GET_LIST_DATA_RES` | T009 §14 | 42/42 fit (up to 18 mails) |
| 37.8.1 | `C2S_MAIL_SYSTEM_MAIL_GET_LIST_FOOT_REQ` | T009 §14 | 42/42 fit (no body) |
| 37.8.2 | `S2C_MAIL_SYSTEM_MAIL_GET_LIST_FOOT_RES` | T009 §14 | 42/42 fit, slack 15 |
| 37.9.1 | `C2S_MAIL_SYSTEM_MAIL_GET_TEXT_REQ` | T009 §15 | 7/7 fit |
| 37.9.2 | `S2C_MAIL_SYSTEM_MAIL_GET_TEXT_RES` | T009 §15 | 7/7 fit (only item attachments in the captures) |
| 37.11.1 | `C2S_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_REQ` | T009 §16 | 5/5 fit (Season 3 u8: code-only, the PS4 body fits too) |
| 37.11.2 | `S2C_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_RES` | T009 §16 | 5/5 fit |
| 37.13.16 | `S2C_MAIL_SYSTEM_MAIL_SEND_NTC` | T009 §17 | 5/5 fit (code name V by behaviour; the PS4 framing fits too) |
| 39.0.1 | `C2S_GACHA_GACHA_LIST_REQ` | T012 §16 | 26/26 fit (no body) |
| 39.0.2 | `S2C_GACHA_GACHA_LIST_RES` | T012 §16 | 26/26 fit (Season 3 settlement u32; the PS4 settlement fails 26/26) |
| 39.1.1 | `C2S_GACHA_GACHA_BUY_REQ` | T012 §16 | 21/21 fit |
| 39.1.2 | `S2C_GACHA_GACHA_BUY_RES` | T012 §16 | 21/21 fit, slack 15 |
| 41.3.1 | `C2S_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_REQ` | T013 §9 | 1/1 fit, slack 6 (Season 3 price {u8, u32}; the PS4 body fits too: the PC writer decides) |
| 41.3.2 | `S2C_CHARACTER_EDIT_UPDATE_PAWN_EDIT_PARAM_RES` | T013 §9 | 1/1 fit, slack 15 (header only: Season 3 drops the PS4 u32 GP; the PS4 body fits too) |
| 41.5.1 | `C2S_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_REQ` | 008 T005 | 1/1 fit (T005 marks: V 1, I 1, G 2) |
| 41.5.2 | `S2C_CHARACTER_EDIT_UPDATE_CHARACTER_EDIT_PARAM_EX_RES` | 008 T005 | 1/1 fit (T005 marks: none (no fields)) |
| 41.8.1 | `C2S_CHARACTER_EDIT_GET_SHOP_PRICE_REQ` | 008 T005 | 4/4 fit (no body; T005 marks: none (no fields)) |
| 41.8.2 | `S2C_CHARACTER_EDIT_GET_SHOP_PRICE_RES` | 008 T005 | 4/4 fit (T005 marks: V 1, G 2) |
| 43.0.1 | `C2S_LOADING_INFO_LOADING_GET_INFO_REQ` | T012 §17 | 42/42 fit (no body) |
| 43.0.2 | `S2C_LOADING_INFO_LOADING_GET_INFO_RES` | T012 §17 | 42/42 fit |
| 44.0.1 | `C2S_CERT_CLIENT_CHALLENGE_REQ` | T003 §15 | 83/83 fit, slack 12 (no header, body at offset 0) |
| 44.0.2 | `S2C_CERT_CLIENT_CHALLENGE_RES` | T003 §16 | 83/83 fit |
| 44.1.16 | `S2C_CERT_GAME_SERVER_CERT_NTC` | T003 §1, §15 | 83/83 fit, slack 12 (no header, body at offset 0) |
| 45.0.1 | `C2S_STAMP_BONUS_GET_LIST_REQ` | T009 §18 | 81/81 fit (no body) |
| 45.0.2 | `S2C_STAMP_BONUS_GET_LIST_RES` | T009 §1.2, §18 | 81/81 fit (Season 3 restructured; the PS4 body fails 81/81) |
| 45.1.1 | `C2S_STAMP_BONUS_CHECK_REQ` | T009 §19 | 84/84 fit (no body) |
| 45.1.2 | `S2C_STAMP_BONUS_CHECK_RES` | T009 §1.2, §19 | 84/84 fit (Season 3 list: code-only, the PS4 body fits too) |
| 45.3.1 | `C2S_STAMP_BONUS_RECIEVE_DAILY_REQ` | 008 T003 | 40/40 fit, slack 15 (T003 marks: V 2) |
| 45.3.2 | `S2C_STAMP_BONUS_RECIEVE_DAILY_RES` | 008 T003 | 40/40 fit, slack 15 (T003 marks: none (no fields)) |
| 45.4.1 | `C2S_STAMP_BONUS_RECIEVE_TOTAL_REQ` | 008 T003 | 1/1 fit (no body; T003 marks: none (no fields)) |
| 45.4.2 | `S2C_STAMP_BONUS_RECIEVE_TOTAL_RES` | 008 T003 | 1/1 fit, slack 15 (T003 marks: none (no fields)) |
| 50.0.1 | `C2S_ITEM_SORT_GET_ITEM_SORTDATA_BIN_REQ` | T008 §4.1 | 46/46 fit |
| 50.0.2 | `S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_RES` | T008 §4.1 | 46/46 fit (list never non-empty) |
| 50.0.16 | `S2C_ITEM_SORT_GET_ITEM_SORTDATA_BIN_NTC` | 008 T005 | 48/48 fit (every bin all zero; T005 marks: I 1) |
| 50.1.1 | `C2S_ITEM_SORT_SET_ITEM_SORTDATA_BIN_REQ` | T008 §4.3 | 59/59 fit (Season 3 trailing bool: code-only, the PS4 body fits too) |
| 50.1.2 | `S2C_ITEM_SORT_SET_ITEM_SORTDATA_BIN_RES` | T008 §4.3 | 59/59 fit, slack 15 |
| 51.0.1 | `C2S_DISPEL_GET_DISPEL_ITEM_LIST_REQ` | T013 §10 | 1/1 fit |
| 51.0.2 | `S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES` | P11a §6 | 1/1 fit |
| 51.2.1 | `C2S_DISPEL_GET_DISPEL_ITEM_SETTING_REQ` | T013 §10 | 1/1 fit (Season 3 u32; the empty PS4 body fits too) |
| 51.2.2 | `S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES` | T013 §1, §10 | 1/1 fit (Season 3 u32 Category + bool; the PS4 body fails 1/1) |
| 52.1.1 | `C2S_MY_ROOM_FURNITURE_LIST_GET_REQ` | T013 §11 | 20/20 fit (no body) |
| 52.1.2 | `S2C_MY_ROOM_FURNITURE_LIST_GET_RES` | P11a §10 | 20/20 fit (T010b: `CDataFurnitureLayout` from `include/Furniture.hexpat`, `unOmID` renamed `OmID`) |
| 53.4.1 | `C2S_PARTNER_PAWN_PAWN_LIKABILITY_REWARD_LIST_GET_REQ` | T007 §3.1 | 40/40 fit (no body) |
| 53.4.2 | `S2C_PARTNER_PAWN_PAWN_LIKABILITY_REWARD_LIST_GET_RES` | T007 §3.1 | 40/40 fit (list never non-empty) |
| 53.6.1 | `C2S_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_REQ` | T007 §3.1 | 41/41 fit (no body) |
| 53.6.2 | `S2C_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES` | T007 §3.1 | 41/41 fit |
| 53.7.1 | `C2S_PARTNER_PAWN_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_REQ` | T007 §3.2 | 20/20 fit (no body) |
| 53.7.2 | `S2C_PARTNER_PAWN_PARTNER_PAWN_NEXT_PRESENT_TIME_GET_RES` | T007 §3.2 | 20/20 fit |
| 53.8.1 | `C2S_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_REQ` | T007 §3.3 | 20/20 fit |
| 53.8.2 | `S2C_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_RES` | T007 §3.3 | 20/20 fit |
| 53.9.16 | `S2C_PARTNER_PAWN_LIKABILITY_UP_NTC` | T007 §3.4 | 23/23 fit (code name PAWN_LIKABILITY_UP_NTC, V by behaviour; the PS4 framing fits too) |
| 54.0.1 | `C2S_CRAFT_RECIPE_GET_CRAFT_RECIPE_REQ` | T013 §14 | 3/3 fit |
| 54.0.2 | `S2C_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES` | T013 §1, §14 | 3/3 fit (Season 3 material bool; the PS4 material fails 3/3) |
| 57.0.1 | `C2S_BOX_GACHA_BOX_GACHA_LIST_REQ` | T013 §11 | 3/3 fit (no body) |
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
| 59.0.1 | `C2S_INFINITY_DELIVERY_GET_CURRENT_EVENT_REQ` | 008 T004 | 2/2 fit (no body; T004 marks: none (no fields)) |
| 59.0.2 | `S2C_INFINITY_DELIVERY_GET_CURRENT_EVENT_RES` | 008 T004 | 2/2 fit (T004 marks: G 1) |
| 59.4.1 | `C2S_INFINITY_DELIVERY_GET_CATEGORY_STATUS_REQ` | 008 T004 | 1/1 fit (T004 marks: G 1) |
| 59.4.2 | `S2C_INFINITY_DELIVERY_GET_CATEGORY_STATUS_RES` | 008 T004 | 1/1 fit (T004 marks: G 1) |
| 59.8.1 | `C2S_INFINITY_DELIVERY_GET_CATEGORY_LIST_REQ` | 008 T004 | 1/1 fit (no body; T004 marks: none (no fields)) |
| 59.8.2 | `S2C_INFINITY_DELIVERY_GET_CATEGORY_LIST_RES` | 008 T004 | 1/1 fit (T004 marks: G 9, open 1) |
| 59.9.1 | `C2S_INFINITY_DELIVERY_GET_CATEGORY_INFO_REQ` | 008 T004 | 1/1 fit (T004 marks: G 1) |
| 59.9.2 | `S2C_INFINITY_DELIVERY_GET_CATEGORY_INFO_RES` | 008 T004 | 1/1 fit (T004 marks: I 3, G 12, open 7) |
| 60.0.1 | `C2S_NPC_GET_NPC_EXTENDED_FACILITY_REQ` | P11b §12 | 219/219 fit |
| 60.0.2 | `S2C_NPC_GET_NPC_EXTENDED_FACILITY_RES` | 008 T003 | 219/219 fit (list non-empty in 4 files; T003 marks: G 6, open 5) |
| 61.2.1 | `C2S_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_REQ` | 008 T003 | 20/20 fit (no body; T003 marks: none (no fields)) |
| 61.2.2 | `S2C_PAWN_TRAINING_GET_PREPARETION_INFO_TO_ADVICE_RES` | 008 T003 | 20/20 fit (T003 marks: G 3, open 2) |
| 62.0.1 | `C2S_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_REQ` | 008 T005 | 4/4 fit (T005 marks: G 1) |
| 62.0.2 | `S2C_SEASON_DUNGEON_GET_ID_FROM_NPC_ID_RES` | 008 T005 | 4/4 fit (T005 marks: G 1) |
| 62.1.1 | `C2S_SEASON_DUNGEON_GET_INFO_REQ` | 008 T005 | 4/4 fit (T005 marks: G 1) |
| 62.1.2 | `S2C_SEASON_DUNGEON_GET_INFO_RES` | 008 T005 | 4/4 fit (T005 marks: G 2, open 1) |
| 62.7.1 | `C2S_SEASON_DUNGEON_GET_EXTENDABLE_BLOCKADE_LIST_FROM_NPC_ID_REQ` | 008 T005 | 4/4 fit (T005 marks: G 1) |
| 62.7.2 | `S2C_SEASON_DUNGEON_GET_EXTENDABLE_BLOCKADE_LIST_FROM_NPC_ID_RES` | 008 T005 | 4/4 fit (list empty in 4/4; T005 marks: G 1) |
| 62.8.1 | `C2S_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_REQ` | 008 T005 | 7/7 fit (T005 marks: I 1, G 1) |
| 62.8.2 | `S2C_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_RES` | 008 T005 | 7/7 fit (T005 marks: I 1) |
| 62.9.1 | `C2S_SEASON_DUNGEON_GET_EX_REQUIRED_ITEM_REQ` | 008 T005 | 7/7 fit (T005 marks: I 1) |
| 62.9.2 | `S2C_SEASON_DUNGEON_GET_EX_REQUIRED_ITEM_RES` | 008 T005 | 7/7 fit (T005 marks: G 1, open 2) |
| 62.10.1 | `C2S_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_REQ` | 008 T005 | 6/6 fit (T005 marks: I 2, open 1) |
| 62.10.2 | `S2C_SEASON_DUNGEON_DELIVER_ITEM_FOR_EX_RES` | 008 T005 | 12/12 fit (T005 marks: none (no fields)) |
| 62.12.16 | `C2S_SEASON_DUNGEON_62_12_16_NTC` | 008 T004 | 259/259 fit (T004 marks: I 1, G 1) |
| 62.14.16 | `S2C_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_NTC` | 008 T004 | 28/28 fit (T004 marks: I 1, G 1) |
| 62.15.16 | `S2C_SEASON_DUNGEON_END_SOUL_ORDEAL_NTC` | 008 T004 | 28/28 fit (T004 marks: I 2, G 1) |
| 62.16.16 | `S2C_SEASON_DUNGEON_UPDATE_SOUL_ORDEAL_OBJECTIVES_NTC` | 008 T004 | 53/53 fit (T004 marks: G 1) |
| 62.18.1 | `C2S_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_REQ` | 008 T004 | 61/61 fit (T004 marks: I 1, G 1) |
| 62.18.2 | `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_LIST_FROM_OM_RES` | 008 T004 | 61/61 fit (trial list with reward sets; T004 marks: I 2, G 8, open 11) |
| 62.20.1 | `C2S_SEASON_DUNGEON_SOUL_ORDEAL_READY_REQ` | 008 T004 | 28/28 fit (T004 marks: I 2, G 1) |
| 62.20.2 | `S2C_SEASON_DUNGEON_SOUL_ORDEAL_READY_RES` | 008 T004 | 28/28 fit, slack 15 (header only; T004 marks: none (no fields)) |
| 62.22.16 | `S2C_SEASON_62_22_16_NTC` | 008 T004 | 28/28 fit (no body; handler reads no body; T004 marks: none (no fields)) |
| 62.23.16 | `S2C_SEASON_DUNGEON_GROUP_READY_NTC` | 008 T004 | 28/28 fit (T004 marks: G 1) |
| 62.24.1 | `C2S_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_REQ` | 008 T004 | 28/28 fit (list writer V (008 T002), TrialCost empty in 28/28; T004 marks: I 2, G 4) |
| 62.24.2 | `S2C_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_RES` | 008 T004 | 28/28 fit, slack 15 (header only; T004 marks: none (no fields)) |
| 62.26.16 | `S2C_SEASON_DUNGEON_SET_OM_STATE_NTC` | 008 T004 | 428/428 fit (T004 marks: I 1) |
| 62.27.16 | `S2C_SEASON_62_27_16_NTC` | 008 T005 | 1/1 fit (T005 marks: open 1) |
| 62.33.1 | `C2S_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_REQ` | 008 T004 | 21/21 fit (T004 marks: I 1, G 1) |
| 62.33.2 | `S2C_SEASON_DUNGEON_GET_SOUL_ORDEAL_REWARD_LIST_RES` | 008 T004 | 21/21 fit (T004 marks: I 3, G 2) |
| 62.34.1 | `C2S_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_REQ` | 008 T004 | 21/21 fit (list writer V (008 T002); T004 marks: I 1, G 1) |
| 62.34.2 | `S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_RES` | 008 T004 | 21/21 fit (T004 marks: none (no fields)) |
| 62.35.1 | `C2S_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_BUFF_REQ` | 008 T004 | 21/21 fit (T004 marks: I 2, G 1, open 1) |
| 62.35.2 | `S2C_SEASON_DUNGEON_RECEIVE_SOUL_ORDEAL_REWARD_BUFF_RES` | 008 T004 | 21/21 fit, slack 15 (header only; T004 marks: none (no fields)) |
| 62.38.16 | `S2C_SEASON_DUNGEON_AREA_BUFFS_NTC` | 008 T005 | 148/148 fit (T005 marks: G 1) |
| 62.39.16 | `S2C_SEASON_DUNGEON_CHARACTER_AREA_BUFFS_NTC` | 008 T005 | 148/148 fit (raw name `S2C_SEASON_62_39_16_NTC`; T005 marks: G 2) |
| 62.40.16 | `C2S_SEASON_62_40_16_NTC` | 008 T004 | 3/3 fit (T004 marks: I 1, G 1) |
| 63.0.16 | `S2C_63_0_16_NTC` | 008 T005 | 1/1 fit (T005 marks: open 1) |
| 63.1.16 | `S2C_63_1_16_NTC` | 008 T005 | 1/1 fit (T005 marks: open 1) |
| 63.2.16 | `S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC` | 008 T005 | 21/21 fit (raw name `S2C_63_2_16_NTC`; T005 marks: G 1, open 6) |
| 63.3.16 | `S2C_63_3_16_NTC` | 008 T005 | 1/1 fit (no body; handler reads no body; T005 marks: none (no fields)) |
| 63.5.16 | `C2S_CHAIN_DUNGEON_END_CHAIN_NTC` | 008 T005 | 1/1 fit (no body; T005 marks: none (no fields)) |
| 63.6.16 | `S2C_CHAIN_DUNGEON_REWARD_CHEST_APPEAR_NTC` | 008 T005 | 1/1 fit (T005 marks: G 1) |
| 63.7.16 | `S2C_63_7_16_NTC` | 008 T005 | 8/8 fit (T005 marks: G 1) |
| 63.10.16 | `S2C_63_10_16_NTC` | 008 T005 | 12/12 fit (T005 marks: open 3) |
| 63.11.16 | `S2C_63_11_16_NTC` | P5 §7 | 1/1 fit |
| 64.0.1 | `C2S_MANDRAGORA_GET_MY_MANDRAGORA_REQ` | 008 T003 | 20/20 fit (no body; T003 marks: none (no fields)) |
| 64.0.2 | `S2C_MANDRAGORA_GET_MY_MANDRAGORA_RES` | P11a §2 | 20/20 fit |
| 65.3.1 | `C2S_EQUIP_ENHANCED_GET_PACKS_REQ` | 008 T005 | 2/2 fit (T005 marks: G 1) |
| 65.3.2 | `S2C_EQUIP_ENHANCED_GET_PACKS_RES` | 008 T005 | 2/2 fit (T005 marks: V 3, I 1, G 3, open 9) |
| 70.0.1 | `C2S_ACTION_SET_PLAYER_ACTION_HISTORY_REQ` | 008 T003 | 312/312 fit, slack 15 (list writer V (008 T002); T003 marks: G 3) |
| 70.0.2 | `S2C_ACTION_SET_PLAYER_ACTION_HISTORY_RES` | 008 T003 | 312/312 fit, slack 15 (T003 marks: none (no fields)) |
| 71.22.1 | `C2S_BATTLE_CONTENT_INFO_LIST_REQ` | 008 T004 | 42/42 fit (no body; T004 marks: none (no fields)) |
| 71.22.2 | `S2C_BATTLE_CONTENT_INFO_LIST_RES` | 008 T004 | 42/42 fit (includes its CDataBattleContent* types; T004 marks: I 5, G 14, open 5) |
| 72.0.1 | `C2S_DAILY_MISSION_LIST_GET_REQ` | 008 T004 | 117/117 fit (no body; T004 marks: none (no fields)) |
| 72.0.2 | `S2C_DAILY_MISSION_LIST_GET_RES` | 008 T004 | 117/117 fit (third list never non-empty; T004 marks: G 2, open 1) |
| 72.1.16 | `S2C_DAILY_MISSION_ACHIEVE_NTC` | 008 T004 | 64/64 fit (pattern name G (context; value 113/113); raws keep `S2C_DAILY_72_1_16_NTC`; T004 marks: I 1) |
| 72.2.1 | `C2S_DAILY_MISSION_REWARD_RECEIVE_REQ` | 008 T004 | 8/8 fit (list element one u32 (V; corrects T001); T004 marks: I 1, G 1) |
| 72.2.2 | `S2C_DAILY_MISSION_REWARD_RECEIVE_RES` | 008 T004 | 8/8 fit, slack 15 (header only; T004 marks: none (no fields)) |
| 72.3.1 | `C2S_DAILY_MISSION_EVENT_LIST_GET_REQ` | 008 T004 | 4/4 fit (T004 marks: open 1) |
| 72.3.2 | `S2C_DAILY_MISSION_EVENT_LIST_GET_RES` | 008 T004 | 4/4 fit (T004 marks: G 1, open 2) |
