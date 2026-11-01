# 006 T003: game-server connection setup (groups 0 CONNECTION, 1 SERVER, 44 CERT)

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T003-connection-server-cert.md`; rows of groups 0, 1, 44 in
`research/T001-triage.tsv` (27 ids). Brief base `20a4617cd4`; observed at HEAD `199aabf497` (no
`packets/` change in the working tree). Marks: **V** verified in code (or by capture for walk
results), **I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t003/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t003/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only queries through ida-mcp `execute_python` (Hex-Rays,
  `idautils`, `ida_ua.decode_insn` for undefined code, `ida_typeinf` for DWARF types); nothing
  renamed, retyped, commented, patched or reanalysed.
- PC primitives as in T002 § 0 (`nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32 0x8bc480`,
  `Read_u32 0x8bc4d0`, `Read_MtString 0x8bc5b0`, `Read_u64 0x8bc6a0`, `Read_bool 0x8bc6e0`,
  `Write_u8 0x8bc860`, `Write_u16 0x8bc890`, `Write_u32 0x8bc920`, `Write_cstr 0x8bca30` (u16 BE length +
  bytes = MtString wire), `nUserSession::CPacket::WritePacket 0x8bcbb0`, pushes
  `(p, group, id, sub, -1)`).
- PC handler table (V): directory `0x1bc0110` `{table, count}`; group 0 `0x212bb48`/12, group 1
  `0x212f568`/14, group 44 `0x212b0c8`/2; entries stride 0x18, key `(sub<<16)|id` at +0x10; handler
  pointers from the initializer stores at `0x1a2a189..0x1a2a407` (group 0), `0x1a35009..0x1a352fb`
  (group 1), `0x1a287c3`/`0x1a287fd` (group 44):

  | key | handler | | key | handler | | key | handler |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | 0.0.2 | `0x7cea40` | | 0.9.16 | `0x7cdf50` | | 1.6.2 | `0x7f9c90` |
  | 0.1.2 | `0x7ce490` | | **0.10.16** | `0x7cec00` | | 1.7.2 | `0x7f9d50` (not a function; decoded) |
  | 0.2.2 | `0x7ce5c0` | | 0.11.16 | `0x7ce0e0` | | 1.8.2 | `0x7f8f30` |
  | 0.3.2 | `0x7ce240` | | 0.12.16 | `0x7ce850` | | 1.9.2 | `0x7f9690` |
  | 0.4.16 | `0x7ce330` | | 1.0.2 | `0x7f9740` | | 1.10-14.16 | `0x7f9ab0 0x7f9ec0 0x7f8ea0 0x7f9e00 0x7f98e0` |
  | 0.5.2 | `0x7ce660` | | 1.1.2 | `0x7f9070` | | 44.0.2 | `0x7c70c0` |
  | 0.6.2 | `0x7ce720` | | 1.2.2 | `0x7f9820` | | **44.1.16** | `0x7c7250` |
  | 0.7.2 | `0x7cead0` | | 1.4.2 `0x7f95c0`, 1.5.2 `0x7f99c0` | | | | |

  Every in-scope RES handler that has one references its `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>`
  string (e.g. `0x7ce490` -> "OnPacket_CONNECTION_LOGIN_RES"); NTC handlers have none (V).
- PS4 match: by the PC name string where present **and** by body (PS4 `OnPacket_*`/`Send_*`/
  `CPacket_*::{Read,Write}Packet` primitive sequence compared with the PC reader/writer) and DWARF
  `nUserSession::CPacket_*` members; 0.10.16 by behaviour. Never by PS4 packet number.
- PC RES header (V, every RES reader below has the T002 form): `Read_s32` Error at `this+16`; if
  Error != 0, Result := Error and return; else `Read_s32` Result and the body. Pattern form
  `s32 Error; if (Error == 0) { s32 Result; ... }`. PS4 reads `u16 m_usError` then `s32 m_nResult`.
  The NTC readers in scope (0.10.16, 44.1.16) read no error header (V).
- **Walk**: inline stdlib Python (`python -X utf8 -I - packets/decrypted_raw` heredoc from
  `D:/ddon-data`; not saved, the role writes only this report): every file in the 125 stream dirs
  whose raw name starts `C2S_`/`S2C_` and whose suffix group is 0, 1 or 44 (the `C2L_`/`L2C_` login
  files are excluded by name). Header check: group, u16 id, sub, source (0x00 C2S, 0x34 S2C). Body from
  0x09 (44.0.1: from 0x00), fit = end within the last 15 bytes, no overrun. Sample `xxd -g1` per id;
  sha256 shown as its first 16 hex digits.

## 1. Connection crypto: why the challenge writer writes a header the wire does not carry (44.0.1 and login 1.0.1)

Settles T002c § 3 "Contradiction" (V, PC code):

- `cSeedServerConnection::Send 0x9d6a20` parses the 9-byte header the writer produced (`0x9d6820`:
  group u8, id u16, sub u8 at +4) and picks a mode:
  1. `sub_9D78C0` = the byte at `conn+0x109` (`mIsEnableCipher`; `conn+0xd8` holds the 49-byte
     `mCommonKey`, copied by `0x869e20`; PS4 `cGuardData {char mCommonKey[49]; bool
     mIsEnableCipher;}`). False -> plain send.
  2. If the header's group == vtable `+0x5c`, id == vtable `+0x64` and **sub == 1**
     (`0x9d6aeb..0x9d6b01`) -> mode 5 (`0x9d6bb4`): `cryptCamellia(src + 9, count - 9, pKey)`, i.e.
     **the 9 header bytes are dropped** and only the body is encrypted, with `pKey` `0x2135d90` ->
     `"f23e98HafJdSoaj80QBjhh23oajgklSadrhogh2IJnwJEF58"` (the static key T002c found; first 32 used).
  3. Else vtable `+0x58` (`0x875b30`, `xor al,al; retn 4` = PS4 `isNoCipher` false) -> plain; else if
     `mCommonKey` is non-empty (`0x9d78e0`) -> mode 2 (`0x9d6c35`): `cryptCamellia(src, count, 0)` over
     header + body (session key); else nothing is sent.
- Vtable values (raw bytes, the functions sit in the protected region and are not IDA functions):

  | Connection (vtable) | +0x5c send group | +0x64 send id | +0x60 recv group | +0x68 recv id |
  | --- | --- | --- | --- | --- |
  | game `0x1bc5c38` (getDTI `0x86a9d0` at +0x10) | `0x86c900` = 0x2c | `0x86c910` = 0 | `0x86c8e0` = 0x2c | `0x86c8f0` = 1 |
  | login `0x1bd6af8` (getDTI `0x88c690` at +0x10) | `0x88c8e0` = 1 | `0x88c8f0` = 0 | `0x88c8c0` = 1 | `0x88c8d0` = 1 |

  So 44.0.1 (game writer `0x840630`, `WritePacket(p, 0x2c, 0, 1, -1)`, caller `0x820a10` -> `Send`) and
  1.0.1 (login writer `0x88a900`, `WritePacket(p, 1, 0, 1, -1)`) are both the "handshake send command":
  the writer builds the normal header, `Send` strips it and encrypts the body with the static key.
- Receive (`0x9d6d20`, V): while `mIsEnableCipher` and `mCommonKey` is empty, the packet is
  decrypted with `pKey` into `buf+9` (`0x9d6e2c..0x9d6e44`) and a header is **synthesised**: group =
  vtable `+0x60`, id = vtable `+0x68`, sub = 0x10, counter 0 (`0x9d6e49..0x9d6e7d`). The server's first
  packet is therefore dispatched as **44.1.16** on the game connection (handler `0x7c7250`) and
  **1.1.16** on the login connection (T002's handler `0x886b00`).
- PS4 is the same design (V): `cSeedServerConnection::Send 0x55bb80` compares the u16 id with vtable
  slot 25 = `getHandShakeSendCommandNo` (`cSeedGameSvConnection 0x19e08e0` = 0x1e5, the id that
  `CPacket_C2S_CLIENT_CHALLENGE_REQ::WritePacket 0x1a3aaf0` writes; login `0x1a3e400` = 6), sends
  `pBuf + 6, dwSize - 6` (drops its 6-byte header) with the static key; `analyzePacket 0x55aee0`
  synthesises the header with `getHandShakeRecvCommandNo` (game `0x19e08f0` = 0x2b0, login 6).
  The receive command is `OnPacket_S2C_GAME_SERVER_CERT_NOTICE 0x330310` / `OnPacket_L2C_LOGIN_SERVER_CERT_NOTICE 0x37ceb0`.
- Consequences: (a) T002c's "304-byte server public key" is the **S2C_CERT_GAME_SERVER_CERT_NTC
  44.1.16** body (login: **L2C_LOGIN_SERVER_CERT_NTC 1.1.16**), filed by the CLI under 44.0.1/1.0.1;
  (b) its "12 unknown bytes" are cipher padding: the client reads 292 bytes (§ 27); (c) Arrowgene
  already names both ids (`PacketId.cs:162`, `:1737`).

## 2. 0.0.1 C2S_CONNECTION_PING_REQ / 0.0.2 S2C_CONNECTION_PING_RES

- PC writer `0x824750`: `WritePacket(p, 0, 0, 1, -1)`, then `0x77db60` = `Write_u32` count + per element
  `Write_u8 [+4], Write_u8 [+5], Write_u32 [+8], Write_u32 [+12], Write_u32 [+16]` (V). Not empty.
- PC reader `0x804c80` via `0x7cea40` (string "OnPacket_CONNECTION_PING_RES"): RES header only (V).
- PS4 match **V**: `Send_C2S_PING_REQ 0x19c3110` writes the header and `Write_CDataCheatInfo_`
  (u32 count, u8, u8, u32, u32, u32); DWARF `CPacket_C2S_PING_REQ {u16 m_usError,
  MtTypedArray<CDataCheatInfo> m_Info}`, `CDataCheatInfo {u8 m_ucId, u8 m_ucCount, u32 m_unParam1,
  u32 m_unParam2, u32 m_unParam3}`. RES `OnPacket_S2C_PING_RES 0x2dcc70` u16, s32; DWARF
  `{u16 m_usError, s32 m_nResult}`.
- Wire: REQ `MtTypedArray<CDataCheatInfo> Info;`. RES `s32 Error; if (Error == 0) s32 Result;` (8 B).
- Season 3: none. Recompilation: no PING body (members only).
- Walk: REQ 2134/2134 fit, slack 3-5, count 0 in 2026, 1 in 108. `stream85-marked.pcapng_tcp-stream-11/
  102644_C2S_CONNECTION_PING_REQ_…0_0_1` (32 B, `7034257c5ce81c72`): `00000001` count, `02` Id,
  `01` Count, three `00000000`, end 0x1b. Empty list: `stream1-…-34/11872_…0_0_1` (16 B,
  `4379c1a915632261`), end 0x0d. RES 2133/2133, slack 15: `stream1-…-34/11874_S2C_CONNECTION_PING_RES_…0_0_2`
  (32 B, `7a4835903baf9fd1`): Error 0, Result 0, end 0x11.

## 3. 0.1.1 C2S_CONNECTION_LOGIN_REQ / 0.1.2 S2C_CONNECTION_LOGIN_RES

- PC writer `0x8243b0`: `WritePacket(p, 0, 1, 1, -1)`, `Write_cstr`, `Write_u8`, `Write_u32` (V).
- PC reader `0x804a50` via `0x7ce490` ("OnPacket_CONNECTION_LOGIN_RES"): RES header, `Read_bool` (+24),
  `Read_MtString` (+28) (V).
- PS4 match **V**: `CPacket_C2S_LOGIN_REQ::WritePacket 0x1a3aa40` writes MT_CSTR, u8, u32; DWARF
  `{MtString m_wstrSessionKey, u8 m_ucPlatform, u32 m_unClientVersion}`. `OnPacket_S2C_LOGIN_RES
  0x2dcde0` reads u16, s32, bool, MtString; DWARF `{u16 m_usError, s32 m_nResult, b8 m_bIsCogLogin,
  MtString m_wstrOnetimeToken}`.
- Recompilation: `CPacket_C2S_LOGIN_REQ::WritePacket(const char* in_strSessionKey, u8 in_Platform,
  u32 in_ClientVersion)` stub: signature agrees.
- Wire: REQ `MtString SessionKey; u8 Platform; u32 ClientVersion;`. RES `s32 Error; if (Error == 0)
  { s32 Result; bool IsCogLogin; MtString OnetimeToken; }`.
- Shares 0.1.1/0.1.2 with C2L_LOGIN_REQ / L2C_LOGIN_RES: use `// packet-select: C2S_CONNECTION_LOGIN_REQ`
  / `S2C_CONNECTION_LOGIN_RES` (the login patterns already select theirs).
- Walk: REQ 42/42, slack 1: `stream1-…-34/11870_C2S_CONNECTION_LOGIN_REQ_…0_1_1` (48 B, `f28774a852d218be`):
  key length 0x1f at 0x09, `01` Platform at 0x2a, `3040001b` at 0x2b, end 0x2f. RES 42/42, slack 13:
  `stream1-…-34/11871_S2C_CONNECTION_LOGIN_RES_…0_1_2` (64 B, `34d2c39c3a959943`): Error 0, Result 0,
  `01` IsCogLogin at 0x11, token length 0x1f at 0x12, end 0x33. A u16 IsCogLogin (Arrowgene) would read
  the length as 0x1f31 and overrun: the 1-byte width is capture-confirmed.

## 4. 0.2.1 C2S_CONNECTION_LOGOUT_REQ / 0.2.2 S2C_CONNECTION_LOGOUT_RES

- PC writer `0x8244c0` `WritePacket(p, 0, 2, 1, -1)`, no body (V). Reader `0x804ae0` via `0x7ce5c0`:
  RES header only (V).
- PS4 **V**: `Send_C2S_LOGOUT_REQ 0x19afdf0` header only; `OnPacket_S2C_LOGOUT_RES 0x2dd050` u16, s32;
  DWARF agrees.
- Wire: REQ empty; RES `s32 Error; if (Error == 0) s32 Result;`. Shares the id with the C2L/L2C
  LOGOUT patterns: `packet-select` needed.
- Walk: REQ 42/42 slack 7 (`stream1-…-35/26548_…0_2_1`, 16 B, `bb8ad1d5f294e789`); RES 42/42 slack 15
  (`stream1-…-35/26551_S2C_CONNECTION_LOGOUT_RES_…0_2_2`, 32 B, `44c4569db312e415`, Error 0, end 0x11).

## 5. 0.3.1 C2S_CONNECTION_GET_LOGIN_ANNOUNCEMENT_REQ / 0.3.2 …_RES

- PC writer `0x8242f0` `WritePacket(p, 0, 3, 1, -1)`, no body (V). Reader `0x8049d0` via `0x7ce240`:
  RES header, `Read_MtString` (+24) (V).
- PS4 **V**: `Send_… 0x19aff20` header only; `OnPacket_S2C_GET_LOGIN_ANNOUNCEMENT_RES 0x2dd200` u16, s32,
  MtString; DWARF `{…, MtString m_wstrMessage}`.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; MtString Message; }`.
- Walk: REQ 41/41 slack 7 (`stream1-…-35/12229_…0_3_1`, `1d6c4a396632d837`); RES 41/41 slack 14
  (`stream1-…-35/12232_…0_3_2`, 48 B, `ef7495ea0c0b5666`): length 0x000f, UTF-8 text, end 0x22.

## 6. 0.5.1 C2S_CONNECTION_MOVE_IN_SERVER_REQ / 0.5.2 …_RES

- PC writer `0x824580` `WritePacket(p, 0, 5, 1, -1)`, `Write_cstr`, `Write_u8`, `Write_u32` (V).
  Reader `0x804b70` via `0x7ce660`: RES header only (V).
- PS4 **V**: `CPacket_C2S_MOVE_IN_SERVER_REQ::WritePacket 0x1a3a990` MT_CSTR, u8, u32; DWARF
  `{MtString m_wstrSessionKey, u8 m_ucPlatform, u32 m_unClientVersion}`; RES `0x2dd3a0` u16, s32.
  Recompilation stub signature `(const char* in_strSessionKey, u8 in_Platform, u32 in_ClientVersion)`.
- Wire: REQ `MtString SessionKey; u8 Platform; u32 ClientVersion;` RES `s32 Error; if (Error == 0) s32 Result;`.
- Walk: REQ 41/41 slack 1 (`stream1-…-35/11959_…0_5_1`, 48 B, `e5eb4f98e4ff30d3`, key length 0x1f,
  `01`, `3040001b`, end 0x2f); the key equals the one 0.6.2 returned just before on the other
  connection (§ 7). RES 41/41 slack 15 (`stream1-…-35/11964_…0_5_2`, 32 B, `23e4de6da1f35f7b`, end 0x11).

## 7. 0.6.1 C2S_CONNECTION_MOVE_OUT_SERVER_REQ / 0.6.2 …_RES

- PC writer `0x824690` `WritePacket(p, 0, 6, 1, -1)`, no body (V). Reader `0x804c00` via `0x7ce720`:
  RES header, `Read_MtString` (+24) (V).
- PS4 **V**: `Send_… 0x19b0180` header only; `OnPacket_S2C_MOVE_OUT_SERVER_RES 0x2dd530` u16, s32,
  MtString; DWARF `{…, MtString m_wstrSessionKey}`.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; MtString SessionKey; }`.
- Walk: REQ 41/41 slack 7 (`stream1-…-34/11944_…0_6_1`, `e34ebf3fdffd9b8c`); RES 41/41 slack 14
  (`stream1-…-34/11945_…0_6_2`, 64 B, `33221af564aa578e`): key length 0x1f at 0x11, end 0x32.

## 8. 0.7.1 C2S_CONNECTION_RESERVE_SERVER_REQ / 0.7.2 …_RES

- PC writer `0x840930` `WritePacket(p, 0, 7, 1, -1)`, `Write_u16`, `Write_u8`, `Write_u8`, `0x77df90`
  (`Write_u32` count + `Write_u32` per element) (V). Reader `0x804d10` via `0x7cead0`: RES header,
  `Read_u16` (+24), list `0x75e8e0` (CDataCommonU32) (V).
- PS4 **V**: `CPacket_C2S_RESERVE_SERVER_REQ::WritePacket 0x1a3a730` u16, u8, u8, CommonU32 list; DWARF
  `{u16 m_usGameServerUniqueID, u8 m_ucType, u8 m_ucRotationServerID, MtTypedArray<CDataCommonU32>
  m_ReserveInfoList}`; RES `0x2df750` u16, s32, u16, CommonU32 list; DWARF `{…, u16
  m_usGameServerUniqueID, MtTypedArray<CDataCommonU32> m_ReserveInfoList}`. Recompilation stub signature agrees.
- Wire: REQ `u16 GameServerUniqueID; u8 Type; u8 RotationServerID; MtTypedArray<CDataCommonU32>
  ReserveInfoList;` RES `s32 Error; if (Error == 0) { s32 Result; u16 GameServerUniqueID;
  MtTypedArray<CDataCommonU32> ReserveInfoList; }`.
- Walk: REQ 41/41 slack 11: `stream1-…-34/11941_…0_7_1` (32 B, `ab2d6a08b7aa8d06`): `000b` `05` `00`
  count 1, `0020b8f8` (the character id of T002 § 12), end 0x15. RES 41/41 slack 5:
  `stream1-…-34/11942_…0_7_2` (32 B, `960cc0fde2f9de74`): Error 0, Result 0, `0005`, count 1,
  `0020b8f8`, end 0x1b. (REQ server id 0x0b, RES 0x05: values, not checked further.)

## 9. 0.10.16 S2C_CONNECTION_0_10_16_NTC = SESSION_STATUS_NTC (settled)

- PC handler `0x7cec00` (no name string): reader `0x804da0` = `Read_u32` (+16), `Read_u8` (+20); no
  error header (V). Then `0x7cebb0(mgr = [conn+0x13c], pkt)`: walks the pointer array at
  `mgr+0x45e8` (count `mgr+0x45dc`), finds the element whose `+8` equals the u32, and stores the u8
  to that element's `+0x21` (V, disassembly `0x7cebc8..0x7cebee`).
- That array is the **lobby member list** (V): `OnPacket_LOBBY_LOBBY_JOIN_RES 0x7e2ce0` reads its
  member list with `0x76d6f0` and `0x7e2c60` -> `0x8814e0` refills `mgr+0x45d8` (count +4, data +0x10)
  with 0x24-byte elements read by `0x76d7f0`: `u32 (+8), MtString (+0x10), MtString (+0x14),
  MtString (+0x18), u32 (+0x1c), u8 (+0x20), u8 (+0x21), u8 (+0x22)`.
- PS4 match **V by behaviour**: `cSeedGameSvConnection::OnPacket_S2C_SESSION_STATUS_NTC 0x2deb90` reads
  u16, u32, u8, finds the `cNetGameServer::mLobbyMembers` entry whose `m_CommunityCharacterBaseInfo.
  m_unCharacterID` (+0x10) equals the u32 and writes the u8 to `+0x3e` = `CDataLobbyMemberInfo::
  m_ucSessionStatus`. DWARF `CPacket_S2C_SESSION_STATUS_NTC {u16 m_usError, u32 m_unCharacterID,
  u8 m_ucSessionStatus}`. Of the 9 PS4 bodies with the shape u16, u32, u8 (listed by a scan of all
  `OnPacket_S2C_*`), only this one and `PARTY_MEMBER_SESSION_STATUS_NTC 0x2e1940` touch member state;
  the PC target is the lobby list, so SESSION_STATUS_NTC. Arrowgene's own comment says the same
  (`PacketId.cs:258` "S2C_SESSION_STATUS_NTC?").
- **Season 3 differences (V):** no `u16` error header. PC `CDataLobbyMemberInfo` reads **3** trailing
  u8 (`0x76d7f0`), PS4 reads 4 (`Read_CDataLobbyMemberInfo__0 0x1a2f460`; DWARF `u8 m_ucPlatform,
  u8 m_ucClientVersion, u8 m_ucSessionStatus, u8 m_ucOnlineStatus`). PC stores SessionStatus in the
  second of the three; which of Platform/ClientVersion was dropped is I.
- Wire: `u32 CharacterID; u8 SessionStatus;` (5 B).
- Walk: 2/2 fit, slack 2. `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/10325_S2C_CONNECTION_0_10_16_NTC_…0_10_16`
  (16 B, `44585f7ef8625fbc`): `00133393` CharacterID, `01` SessionStatus, end 0x0e.

## 10. 1.0.1 C2S_SERVER_GET_SERVER_LIST_REQ / 1.0.2 …_RES

- PC writer `0x83c3a0` `WritePacket(p, 1, 0, 1, -1)`, no body (V). Reader `0x81a880` via `0x7f9740`
  ("OnPacket_SERVER_GET_SERVER_LIST_RES"): RES header, list `0x7689f0` of `0x768ae0`
  (`u16, MtString x3, u32 x3, MtString, u16, bool`) = the existing `CDataGameServerListInfo` (V).
- PS4 **V**: `Send_C2S_GET_SERVER_LIST_REQ 0x19b02b0` header only; `OnPacket_S2C_GET_SERVER_LIST_RES
  0x2dda40` u16, s32, `Read_CDataGameServerListInfo_` (same 10 fields); DWARF `{…,
  MtTypedArray<CDataGameServerListInfo> m_ServerList}`.
- Wire: REQ empty; RES `s32 Error; if (Error == 0) { s32 Result; MtTypedArray<CDataGameServerListInfo>
  ServerList; }`. Shares 1.0.1/1.0.2 with C2L_CLIENT_CHALLENGE_REQ / L2C_CLIENT_CHALLENGE_RES:
  `packet-select` needed (the 1.0.1 login pattern also uses `packet-size: 336`).
- Walk: REQ 43/43 slack 7 (`stream1-…-34/11934_…1_0_1`, `b2c3aebbbbefae79`); RES 43/43, slack 0-13,
  24-25 servers: `stream1-…-34/11936_S2C_SERVER_GET_SERVER_LIST_RES_…1_0_2` (1840 B,
  `6f9475fab1c8cda8`): count 0x19, first Id 0x0001, name length 0x0f, end 0x724.

## 11. 1.1.1 C2S_SERVER_GET_GAME_SETTING_REQ / 1.1.2 …_RES

- PC writer `0x83c160` `WritePacket(p, 1, 1, 1, -1)`, no body (V). Reader `0x81a6f0` via `0x7f9070`
  ("OnPacket_SERVER_GET_GAME_SETTING_RES"): RES header, CDataGameSetting `0x768bb0` (V):
  `u32 x9, u8, list 0x75c570 {u8, u16}, u32, u8, bool, u8, u32 x7, list 0x77bbd0 {u32, MtString},
  list 0x7717e0 {u32, u32}, u32 x4, u8, list 0x76afb0 {u8, u8}, u32 x6, list 0x75e8e0 {u32}, u32,
  bool, u32 x3, list 0x77c4b0 {u32, u32}, u16, list 0x766800 {u8, list 0x766910 {u8, u32}}`.
- PS4 **V** (name, header, all fields up to MailCacheExpireTime except the two strings):
  `Read_CDataGameSetting_` via `OnPacket_S2C_GET_GAME_SETTING_RES 0x2ddbc0`; DWARF `CGameSetting`/
  `CDataGameSetting {u32 m_unMainPawnMax, m_unSupportPawnMax, m_unJobLevelMax, m_unCraftLevelMax,
  m_unCraftSkillLevelMax, m_unUserListMax, m_unClanLvMax, m_unClanMemberMax, m_unClanLeaveIntervalTime,
  u8 m_ucCharacterNumMax, MtTypedArray<CDataCharacterItemSlotInfo> m_GlobalItemSlotNumMaxList,
  u32 m_unPawnCreateItemID, u8 m_ucPawnCreateItemNum, b8 m_bEnableVisualEquip, u8
  m_ucEquipColorChangeGrade, u32 m_unFriendListMax, m_unRecentPlayerMax, m_unBlackListMax,
  m_unHistoryListMax, m_unCharacterReviveGP, m_unPawnReviveGP, m_unLostPawnReviveGP,
  MtTypedArray<CDataURLInfo> m_UrlInfoList, MtTypedArray<CDataPartyMemberMaxNum>
  m_PartyMemberMaxNumList, u32 m_unGroupChatMemberMax, m_unEventCodeInputLockFailNum,
  m_unEventCodeLockTime, MtString m_wstrCapLinkServerVerion, MtString m_wstrCapLinkApiVerion,
  u32 m_unPawnPresentItemID, u8 m_ucPawnPresentItemNum, MtTypedArray<CDataJewelryEquipLimit>
  m_JewelryEquipLimitList, u32 m_unJobPointMax, m_unPlayPointMax, m_unPlayPointLevelMin,
  m_unBazaarSerchTime, m_unBazaarSerchCautionTime, m_unBazaarSerchCautionCount,
  MtTypedArray<CDataCommonU32> m_ClanBaseStageList, u32 m_unMailCacheExpireTime}`. Element types:
  `CDataCharacterItemSlotInfo {u8 m_ucStorageType, u16 m_usSlotMax}`, `CDataPartyMemberMaxNum
  {u32 m_unContentType, u32 m_unNum}`, `CDataJewelryEquipLimit {u8 m_ucJewelryType, u8
  m_ucEquipNumMax}`: PC element readers have the same widths (V).
- **Season 3 differences (V code, names I):**
  - The two `MtString CapLink…` fields are gone: PC reads `u32 x4, u8` where PS4 has `u32 x3,
    MtString, MtString, u32, u8`. Alignment (I): GroupChatMemberMax, EventCodeInputLockFailNum,
    EventCodeLockTime, PawnPresentItemID, PawnPresentItemNum. Support: in the capture the fourth u32
    is 10133, the same value as PawnCreateItemID.
  - New after MailCacheExpireTime: `bool, u32, u32, u32, MtTypedArray<{u32, u32}>, u16,
    MtTypedArray<{u8, MtTypedArray<{u8, u32}>}>`. No PS4 or PC names; Arrowgene leads `Unk0..Unk3`,
    `CDataWalletLimit {u32 WalletType, u32 MaxValue}`, `Unk5`, `CDataExpSetting {u8 Type,
    MtTypedArray<CDataExpRequirement {u8, u32}>}` agree in width (I names). Capture values fit the
    leads: 16 pairs with ids 1-16 and maxima (999999999, 50000, 99999 …); two outer entries (1, 2)
    with 120 and 55 inner (level, exp) rows starting (1, 0), (2, 300).
- Recompilation: members only (stubbed). Arrowgene `CDataGameSetting` agrees with PC field by field.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; CDataGameSetting GameSetting; }`.
- Walk: REQ 42/42 slack 7 (`stream1-…-34/11880_…1_1_1`, `89fc91d575f50bd1`); RES 42/42, **slack 1 in
  all** (2272 B each): `stream1-…-34/11885_S2C_SERVER_GET_GAME_SETTING_RES_…1_1_2` (`d7a5981335ca5e96`):
  ItemSlot 17, URL 19, PartyMax 10, Jewelry 4, ClanBaseStage 1 (347), MailCacheExpireTime 300, pairs
  16, u16 150, outer 2 (inner 120, 55), end 0x8df. Slack 1 leaves no room for the two PS4 strings.

## 12. 1.4.1 C2S_SERVER_GET_REAL_TIME_REQ / 1.4.2 …_RES

- PC writer `0x83c220` `WritePacket(p, 1, 4, 1, -1)`, no body (V). Reader `0x81a770` via `0x7f95c0`:
  RES header, `Read_u64` (+24), `Read_u16` (+32) (V).
- PS4 **V** (name string, body): `OnPacket_S2C_GET_REAL_TIME_RES 0x2de130` reads `u16, u64, u16` only;
  DWARF `{u16 m_usError, u64 m_ullRealTime, u16 m_usMilliseconds}`. **Season 3 difference (V):** PC
  reads a Result after the Error (standard RES header); PS4 has none.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; u64 RealTime; u16 Milliseconds; }`.
- Walk: REQ 87/87 slack 7 (`stream1-…-34/11872_…1_4_1`, `fd8cf1afe08b6de2`); RES 87/87 slack 5:
  `stream1-…-34/11875_S2C_SERVER_GET_REAL_TIME_RES_…1_4_2` (32 B, `14cef742dffc18cc`): Error 0,
  Result 0, RealTime `000000005d20e2ed` (2019-07-06 18:05:33 UTC, the capture's 11:05:33 -07:00),
  Milliseconds `016e` (366), end 0x1b.

## 13. 1.7.1 C2S_SERVER_WEATHER_FORECAST_GET_REQ / 1.7.2 …_RES

- PC writer `0x83c7c0` `WritePacket(p, 1, 7, 1, -1)`, no body (V). Handler `0x7f9d50` (not an IDA
  function; decoded) calls reader `0x81ac30`: RES header, `Read_u32` (+24), `Read_u32` (+28), list
  `0x77c960` (`Read_u32` count, `Read_u32` per element) (V).
- PS4 **V**: `OnPacket_S2C_WEATHER_FORECAST_GET_RES 0x32e310` -> `ReadPacket`: u16, s32, u32, u32,
  `Read_CDataWeatherForecast_` (u32); DWARF `{…, u32 m_unIntervalGameHour, u32 m_unGameDayToEarthMin,
  MtTypedArray<CDataWeatherForecast> m_ForecastList}`, `CDataWeatherForecast {u32 m_unWeather}`.
- Recompilation: `ReadPacket` is a **stub** (T001's `recompiled_body yes` is C).
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; u32 IntervalGameHour; u32 GameDayToEarthMin;
  MtTypedArray<CDataWeatherForecast> ForecastList; }`.
- Walk: REQ 1/1 slack 7 (`stream76-marked.pcapng_tcp-stream-11/11559_…1_7_1`, `d0cc97942a560774`);
  RES 1/1 slack 3: `stream76-…-11/11562_S2C_SERVER_WEATHER_FORECAST_GET_RES_…1_7_2` (48 B,
  `d05f0a56da18554a`): Error 0, Result 0, `00000006`, `0000005a`, count 4 (1, 1, 2, 2), end 0x2d.

## 14. 1.8.1 C2S_SERVER_GAME_TIME_GET_BASEINFO_REQ / 1.8.2 …_RES

- PC writer `0x83c0a0` `WritePacket(p, 1, 8, 1, -1)`, no body (V). Reader `0x81a620` via `0x7f8f30`:
  RES header, `0x769030` (`u32 x6, s64, s64, u32, u32`), list `0x77ca30` {u8, u32}, list `0x77cb20`
  {u8, s64, s64}, `Read_u32` (+120), list `0x76f0f0` {u8, s64, s64} (V).
- PS4 **V**: `OnPacket_S2C_GAME_TIME_GET_BASEINFO_RES 0x332380` -> `ReadPacket`, the same sequence;
  DWARF `{…, CGameTimeBaseInfo m_GameTimeBaseInfo, MtTypedArray<CDataWeatherLoop> m_WeatherLoop,
  MtTypedArray<CDataWeatherSchedule> m_WeatherSchedule, u32 m_unMoonAgeLoopSec,
  MtTypedArray<CDataMoonSchedule> m_MoonSchedule}`; `CDataGameTimeBaseInfo {u32 m_unGameTimeOneDayMin,
  m_unGameTimeYearMonth, m_unGameTimeMonthDay, m_unGameTimeDayHour, m_unGameTimeWeekDay,
  m_unGameTimeMoonAge, s64 m_llOriginalRealTimeSec, s64 m_llOriginalGameTimeSec, u32 m_unOriginalWeek,
  u32 m_unOriginalMoonAge}`, `CDataWeatherLoop {u8 m_ucWeatherId, u32 m_unTimeSec}`,
  `CDataWeatherSchedule {u8 m_ucWeatherId, s64 m_llBeginTimeSec, s64 m_llEndTimeSec}`,
  `CDataMoonSchedule {u8 m_ucMoonAge, s64 m_llBeginTimeSec, s64 m_llEndTimeSec}`. No Season 3 change.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; CDataGameTimeBaseInfo GameTimeBaseInfo;
  MtTypedArray<CDataWeatherLoop> WeatherLoop; MtTypedArray<CDataWeatherSchedule> WeatherSchedule;
  u32 MoonAgeLoopSec; MtTypedArray<CDataMoonSchedule> MoonSchedule; }`.
- Walk: REQ 41/41 slack 7 (`stream1-…-35/11984_…1_8_1`, `ad8df7c1171fbc35`); RES 41/41 slack 7
  (160 B each; WeatherLoop 11, WeatherSchedule 1, MoonSchedule 0 in all):
  `stream1-…-35/12009_S2C_SERVER_GAME_TIME_GET_BASEINFO_RES_…1_8_2` (`f0ea28da658ad8c9`): OneDayMin 90,
  YearMonth 12, MonthDay 30, DayHour 24, WeekDay 7, MoonAge 30, end 0x99. MoonSchedule elements are not
  capture-tested (code only).

## 15. 44.0.1 C2S_CERT_CLIENT_CHALLENGE_REQ (336-byte files) and 44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC (304-byte files)

- PC writer `0x840630`: `WritePacket(p, 0x2c, 0, 1, -1)`, `Write_u8`, `0x77cfa0` (loop `Write_u8` x 0x103),
  `Write_u8`, `Write_u8`, `0x77cfe0` (loop `Write_u8` x 0x3e) (V; the same loop helpers as login 1.0.1
  `0x88a900`, T002 § 3). Identical body to 1.0.1; only the group/id differ. Header dropped on the wire
  (§ 1).
- PS4 **V**: `CPacket_C2S_CLIENT_CHALLENGE_REQ::WritePacket 0x1a3aaf0` `(u8 in_CommonKeySrcSize,
  const u8 (*in_CommonKeyEnc)[259], u8 in_PasswordSrcSize, u8 in_PasswordEncSize, const u8
  (*in_PasswordEnc)[62])`, loops `> 0x102`, `> 0x3d`; DWARF the same members.
- Wire (no header; offset 0): `u8 CommonKeySrcSize; u8 CommonKeyEnc[259]; u8 PasswordSrcSize;
  u8 PasswordEncSize; u8 PasswordEnc[62];` (324 B) + 12 B padding = 336.
- 44.1.16 (server's first packet, filed as `C2S_CERT_CLIENT_CHALLENGE_REQ` 44_0_1, 304 B): PC handler
  `0x7c7250` (table key 0x100001 of group 44), reader `0x801a80`: loop `Read_u8` x 0x100 (+16),
  `0x757d20` loop `Read_u8` x 0x10 (+272), `0x757ea0` loop `Read_u32` x 5 (+288); no error header (V).
  The handler compares the five u32 with a hash of the 272 bytes (`0x13ee820(…, 272)`) and installs
  the key (`0x13ec6d0(buf, modulus, 256)`, `(…, expo, 16)`) (V for the calls, I for "SHA-1"). PS4
  **V**: `CPacket_S2C_GAME_SERVER_CERT_NOTICE::ReadPacket 0x19defe0` u16 error, then the same three
  loops; DWARF `{u16 m_usError, u8 m_ucOpenModulo[256], u8 m_ucOpenExpo[16], u32 m_unOpenHash[5]}`.
  **Season 3/platform difference (V):** PC reads no u16 error (the synthesised header carries none).
- Wire 44.1.16 (offset 0): `u8 OpenModulo[256]; u8 OpenExpo[16]; u32 OpenHash[5];` (292 B) + 12 B
  padding = 304.
- Naming: Sam keeps the file names. Two patterns with `// packet-id: 44.0.1`, `// packet-select:
  C2S_CERT_CLIENT_CHALLENGE_REQ` and `// packet-size: 336` resp. `304`, like
  `C2L_CLIENT_CHALLENGE_REQ-pattern.cpp`. The 304 pattern's struct can carry the code name
  `S2C_CERT_GAME_SERVER_CERT_NTC` (Arrowgene `PacketId.cs:1737`; PS4 `S2C_GAME_SERVER_CERT_NOTICE`).
  The same applies to the 42 login 304-byte `*.1_0_1` files: `L2C_LOGIN_SERVER_CERT_NTC` 1.1.16
  (PC recv command group 1 id 1, § 1; T002 handler `0x886b00`), a T002 follow-up.
- Walk: 336: 83/83 fit, slack 12: `stream1-…-34/11867_C2S_CERT_CLIENT_CHALLENGE_REQ_…44_0_1` (336 B,
  `fdceb69f9668bff2`): `30` CommonKeySrcSize (48), CommonKeyEnc to 0x103 (last 3 bytes `000000`),
  `10 10` at 0x104, PasswordEnc `8979eed6…` + zeros, end 0x144. 304: 83/83 fit, slack 12:
  `stream1-…-34/11865_…44_0_1` (304 B, `92abaf221becc73e`): modulus 0x00-0xff, exponent
  `00…0011` at 0x100, hash 0x110-0x123, end 0x124. (T002c verified the hash in 83/83.)

## 16. 44.0.2 S2C_CERT_CLIENT_CHALLENGE_RES

- PC reader `0x8019e0` via `0x7c70c0` ("OnPacket_CERT_CLIENT_CHALLENGE_RES"): RES header, `Read_u8`
  (+24), `Read_u8` (+25), `0x757da0` (loop `Read_u8` x 62) (V) = login 1.0.2 (T002 § 4).
- PS4 **V**: `OnPacket_S2C_CLIENT_CHALLENGE_RES 0x330470` -> `ReadPacket 0x19df0e0` u16, s32, u8, u8, u8 loop;
  DWARF `{…, u8 m_ucPasswordSrcSize, u8 m_ucPasswordEncSize, u8 m_ucPasswordEnc[62]}`.
  Recompilation S2C.cpp:2002 has the body (u16, s32, two u8, 62 x u8): agrees except the PC Error width.
- Wire: `s32 Error; if (Error == 0) { s32 Result; u8 PasswordSrcSize; u8 PasswordEncSize;
  u8 PasswordEnc[62]; }` (72 B).
- Walk: 83/83 fit, slack 15: `stream1-…-34/11868_S2C_CERT_CLIENT_CHALLENGE_RES_…44_0_2` (96 B,
  `69094acd40d9e366`): Error 0, Result 0, `10 10`, `8979eed6…` (the client's PasswordEnc), end 0x51.
  Bytes after the 16 password bytes are not zero (server-side residue), unlike the client's.

## 17. Summary

PS4 mark: V = confirmed by code (name string + body, or behaviour). Body bytes for Error == 0 (var:
sample length). All walks pass the header check (n/n) except 44.0.1, which has no header by design.

| id | name (file) | PS4 match | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 0.0.1 | C2S_CONNECTION_PING_REQ | V `Send_C2S_PING_REQ` | 4 + 14n | 102644 / 11872 | 2134/2134 |
| 0.0.2 | S2C_CONNECTION_PING_RES | V | 8 | 11874 | 2133/2133 |
| 0.1.1 | C2S_CONNECTION_LOGIN_REQ | V | var (38) | 11870 | 42/42 |
| 0.1.2 | S2C_CONNECTION_LOGIN_RES | V | var (42) | 11871 | 42/42 |
| 0.2.1 | C2S_CONNECTION_LOGOUT_REQ | V | 0 | 26548 | 42/42 |
| 0.2.2 | S2C_CONNECTION_LOGOUT_RES | V | 8 | 26551 | 42/42 |
| 0.3.1 | C2S_CONNECTION_GET_LOGIN_ANNOUNCEMENT_REQ | V | 0 | 12229 | 41/41 |
| 0.3.2 | S2C_CONNECTION_GET_LOGIN_ANNOUNCEMENT_RES | V | var (25) | 12232 | 41/41 |
| 0.5.1 | C2S_CONNECTION_MOVE_IN_SERVER_REQ | V | var (38) | 11959 | 41/41 |
| 0.5.2 | S2C_CONNECTION_MOVE_IN_SERVER_RES | V | 8 | 11964 | 41/41 |
| 0.6.1 | C2S_CONNECTION_MOVE_OUT_SERVER_REQ | V | 0 | 11944 | 41/41 |
| 0.6.2 | S2C_CONNECTION_MOVE_OUT_SERVER_RES | V | var (41) | 11945 | 41/41 |
| 0.7.1 | C2S_CONNECTION_RESERVE_SERVER_REQ | V | 8 + 4n | 11941 | 41/41 |
| 0.7.2 | S2C_CONNECTION_RESERVE_SERVER_RES | V | 14 + 4n | 11942 | 41/41 |
| 0.10.16 | S2C_CONNECTION_0_10_16_NTC = SESSION_STATUS_NTC | V (behaviour) | 5 | 10325 | 2/2 |
| 1.0.1 | C2S_SERVER_GET_SERVER_LIST_REQ | V | 0 | 11934 | 43/43 |
| 1.0.2 | S2C_SERVER_GET_SERVER_LIST_RES | V | var (1819) | 11936 | 43/43 |
| 1.1.1 | C2S_SERVER_GET_GAME_SETTING_REQ | V | 0 | 11880 | 42/42 |
| 1.1.2 | S2C_SERVER_GET_GAME_SETTING_RES | V (S3 changes) | var (2262) | 11885 | 42/42 |
| 1.4.1 | C2S_SERVER_GET_REAL_TIME_REQ | V | 0 | 11872 | 87/87 |
| 1.4.2 | S2C_SERVER_GET_REAL_TIME_RES | V (PC adds Result) | 18 | 11875 | 87/87 |
| 1.7.1 | C2S_SERVER_WEATHER_FORECAST_GET_REQ | V | 0 | 11559 | 1/1 |
| 1.7.2 | S2C_SERVER_WEATHER_FORECAST_GET_RES | V | 20 + 4n | 11562 | 1/1 |
| 1.8.1 | C2S_SERVER_GAME_TIME_GET_BASEINFO_REQ | V | 0 | 11984 | 41/41 |
| 1.8.2 | S2C_SERVER_GAME_TIME_GET_BASEINFO_RES | V | var (144) | 12009 | 41/41 |
| 44.0.1 (336) | C2S_CERT_CLIENT_CHALLENGE_REQ | V | 324, no header | 11867 | 83/83 |
| 44.0.1 (304) | = S2C_CERT_GAME_SERVER_CERT_NTC 44.1.16 | V `S2C_GAME_SERVER_CERT_NOTICE` | 292, no header | 11865 | 83/83 |
| 44.0.2 | S2C_CERT_CLIENT_CHALLENGE_RES | V | 72 | 11868 | 83/83 |

No candidate was rejected. No captured RES has Error != 0 (error branch code-only). Header-only REQs
(slack 7) and slack-15 RES files fit any body up to 7/15 bytes longer: their emptiness rests on the
PC writers/readers (R1 F3). Code-only, not capture-tested: MoonSchedule elements, the PING CheatInfo
list beyond one element, and every list count above those seen.

## 18. Shared types for pattern authors

Reuse: `Packet.hexpat` `CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`; `Login.hexpat`
`CDataGameServerListInfo`, `CDataURLInfo`. The login patterns' framing (`sourceOk`, inline RES
`Error`/`Result`, fit block, `packet-select`) fits unchanged; the 44.0.1 pair follows
`C2L_CLIENT_CHALLENGE_REQ-pattern.cpp` (no CPacket, `packet-size`).

Add (V from the PC readers named; names from PS4 DWARF unless marked I):

| Include (proposal) | Struct | PC reader/writer | Wire |
| --- | --- | --- | --- |
| new `Server.hexpat` (includes Packet, Login) | `CDataCheatInfo` | writer `0x77db60` | u8 Id, u8 Count, u32 Param1, u32 Param2, u32 Param3 |
| `Server.hexpat` | `CDataCharacterItemSlotInfo` | list `0x75c570` | u8 StorageType, u16 SlotMax |
| `Server.hexpat` | `CDataPartyMemberMaxNum` | list `0x7717e0` | u32 ContentType, u32 Num |
| `Server.hexpat` | `CDataJewelryEquipLimit` | list `0x76afb0` | u8 JewelryType, u8 EquipNumMax |
| `Server.hexpat` | `CDataWalletLimit` (I name) | list `0x77c4b0` | u32 WalletType (I), u32 MaxValue (I) |
| `Server.hexpat` | `CDataExpRequirement` (I name) | list `0x766910` | u8 unk_u8 (level, I), u32 unk_u32 (exp, I) |
| `Server.hexpat` | `CDataExpSetting` (I name) | list `0x766800` | u8 Type (I), MtTypedArray<CDataExpRequirement> |
| `Server.hexpat` | `CDataGameSetting` | `0x768bb0` | § 11 order: 9 x u32 (MainPawnMax … ClanLeaveIntervalTime), u8 CharacterNumMax, MtTypedArray<CDataCharacterItemSlotInfo> GlobalItemSlotNumMaxList, u32 PawnCreateItemID, u8 PawnCreateItemNum, bool EnableVisualEquip, u8 EquipColorChangeGrade, 7 x u32 (FriendListMax … LostPawnReviveGP), MtTypedArray<CDataURLInfo> UrlInfoList, MtTypedArray<CDataPartyMemberMaxNum> PartyMemberMaxNumList, u32 GroupChatMemberMax, u32 EventCodeInputLockFailNum, u32 EventCodeLockTime, u32 PawnPresentItemID (I pos), u8 PawnPresentItemNum (I pos), MtTypedArray<CDataJewelryEquipLimit>, 6 x u32 (JobPointMax … BazaarSerchCautionCount), MtTypedArray<CDataCommonU32> ClanBaseStageList, u32 MailCacheExpireTime, bool unk_bool, u32 unk_u32_0..2, MtTypedArray<CDataWalletLimit>, u16 unk_u16, MtTypedArray<CDataExpSetting> |
| `Server.hexpat` | `CDataWeatherForecast` | list `0x77c960` | u32 Weather |
| `Server.hexpat` | `CDataGameTimeBaseInfo` | `0x769030` | u32 GameTimeOneDayMin, u32 GameTimeYearMonth, u32 GameTimeMonthDay, u32 GameTimeDayHour, u32 GameTimeWeekDay, u32 GameTimeMoonAge, s64 OriginalRealTimeSec, s64 OriginalGameTimeSec, u32 OriginalWeek, u32 OriginalMoonAge |
| `Server.hexpat` | `CDataWeatherLoop` | list `0x77ca30` | u8 WeatherId, u32 TimeSec |
| `Server.hexpat` | `CDataWeatherSchedule` | list `0x77cb20` | u8 WeatherId, s64 BeginTimeSec, s64 EndTimeSec |
| `Server.hexpat` | `CDataMoonSchedule` | list `0x76f0f0` | u8 MoonAge, s64 BeginTimeSec, s64 EndTimeSec |
| (future lobby include) | `CDataLobbyMemberInfo` | `0x76d7f0` (list `0x76d6f0`) | u32 CharacterID, MtString FirstName, MtString LastName, MtString ClanName, u32 PawnId, u8 unk (Platform or ClientVersion, I), u8 SessionStatus, u8 OnlineStatus (I) |

PS4 spells `BazaarSerch…`; keep the DWARF spelling or Arrowgene's `BazaarSearch…` consistently.

## 19. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`,
`Arrowgene.Ddon.Shared/Entity/`:

1. `C2SConnectionLoginReq`: reads `MtString SessionKey, byte Platform` and stops; the client writes
   `u32 ClientVersion` after the u8 (PC `0x8243b0` `Write_u32`; PS4 `m_unClientVersion`). 4 bytes unread.
2. `C2SConnectionMoveInServerReq`: reads only `MtString SessionKey`; the client writes `u8 Platform,
   u32 ClientVersion` after it (PC `0x824580`). 5 bytes unread.
3. `S2CConnectionLoginRes`: `IsCogLogin` written/read as **u16**; the client reads `Read_bool` (1 byte)
   (PC `0x804a50`; PS4 `b8 m_bIsCogLogin`). The official server's captures carry 1 byte (§ 3); an
   Arrowgene-served client would read the u16's high byte as the bool and its low byte as the first
   length byte of the token.
4. `C2SCertClientChallengeReq`: as T002 § 16 items 1-2 for the login twin: `ReadByteArray(256)` +
   `ReadBytes(3)` "padding" are `u8 CommonKeyEnc[259]`; `PasswordEnc` is a fixed `u8[62]`, read as
   `PasswordEncSize` bytes (under-read of 62 - size).
5. `S2CCertClientChallengeRes`: writes `PasswordEnc` plus `64 - PasswordEncSize` padding (64 B); the
   client reads exactly 62 (PC `0x757da0`); 2 excess bytes, harmless. Its reader takes only
   `PasswordEncSize` bytes.
6. `S2CConnection_10_Ntc` (`Unk0` u32, `Unk1` u8): widths agree; the fields are `CharacterID` and
   `SessionStatus` (§ 9), not unknowns.
7. `CDataLobbyMemberInfo`: widths agree; `Unk1` ("always 0") is `SessionStatus` (the byte 0.10.16
   updates, PC `+0x21`); `Unk0` is the dropped-pair survivor (Platform or ClientVersion, I).
8. Not misplacements (agree with PC): `C2SConnectionPingReq` + `CDataCheatInfo`, `S2CConnectionPingRes`,
   the LOGOUT pair, `S2CConnectionGetLoginAnnouncementRes`, `S2CConnectionMoveInServerRes`,
   `S2CConnectionMoveOutServerRes`, `C2SConnectionReserveServerReq` (u16, u8, u8, list in both
   directions), `S2CConnectionReserveServerRes`,
   `S2CServerGetServerListRes` + `CDataGameServerListInfo`, `S2CServerGetGameSettingRes` +
   `CDataGameSetting` (incl. the Season 3 tail), `S2CServerGetRealTimeRes` (has the Result PS4 lacks:
   agrees with PC), `S2CServerWeatherForecastGetRes`, `S2CServerGameTimeGetBaseInfoRes` +
   `CDataGameTimeBaseInfo`, the empty REQs. `WriteServerResponse` always writes `u32 Error, u32 Result`;
   the client reads Result only when Error == 0 (excess bytes on error only).

## 20. Open items and checks not run

- Names without code backing: the five GameSetting Season 3 tail fields and their element structs
  (Arrowgene leads only), the position of PawnPresentItemID/Num after the CapLink strings were removed
  (width alignment + one value match), which lobby-member u8 Season 3 dropped.
- "SHA-1" for the 44.1.16 hash is I on PC (T002c checked SHA-1 on captures, 83/83).
- The T001 `recompiled_body yes` flags for 0.1.1, 0.5.1, 0.7.1 (signatures only, stub bodies) and 1.7.2
  (stub) overstate the recompilation: only 44.0.2's reader has a body.
- Login follow-up for T002/T002b: the 42 login 304-byte `*.1_0_1` files are L2C_LOGIN_SERVER_CERT_NTC
  1.1.16 (same reader shape expected as 44.1.16; the login reader behind `0x886b00` was not decoded here).
- ImHex not run (not on `PATH`); no pattern written (outside this package).
