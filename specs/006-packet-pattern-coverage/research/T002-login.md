# 006 T002: login group evidence (21 uncovered login-server ids)

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T002-login.md`; rows `L:*` of `research/T001-triage.tsv`.
Base `a564bde7f0`. Marks: **V** verified in code (or capture for walk results), **I** inferred,
**C** contradicted.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t002/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t002/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only queries through ida-mcp `execute_python`; no
  rename, retype, comment, patch, reanalysis or `create_insn`. All addresses are VAs.
- Many PC login handlers (e.g. `0x886d00`) are not defined as code in the database; they were read
  with `ida_ua.decode_insn` (decode only, nothing written), the defined readers with Hex-Rays.
- PC primitives: `nPacket::Read_u8 0x8bc410`, `Read_u16 0x8bc440`, `Read_s32 0x8bc480`,
  `Read_u32 0x8bc4d0`, `Read_MtString 0x8bc5b0`, `Read_u64 0x8bc6a0`, `Read_bool 0x8bc6e0`,
  `Write_u8 0x8bc860`, `Write_u32 0x8bc920`, `nUserSession::CPacket::WritePacket 0x8bcbb0`
  (`WritePacket(p, group, id, sub, -1)`, read from the pushes).
- PC login handler table `0x1bd6270` ({handler, key} pairs, key = `sub << 16 | id`, groups via the
  directory `0x1bd67f4` = {start, count} x6: 4, 2, 4, 2, 1, 7 entries). Decoded (V):

  | key | handler | | key | handler |
  | --- | --- | --- | --- | --- |
  | 0.0.2 | `0x887740` | | 3.0.2 | `0x886fd0` |
  | 0.1.2 | `0x886650` | | 3.0.16 | `0x887070` |
  | 0.2.2 | `0x886750` | | 4.0.2 | `0x8870b0` |
  | 0.3.16 | `0x886820` | | 5.0.2 | `0x887130` |
  | 1.0.2 | `0x886970` | | 5.1.2 | `0x887240` |
  | 1.1.16 | `0x886b00` | | 5.2.2 | `0x887320` |
  | 2.0.2 | `0x886c10` | | 5.3.2 | `0x8873d0` |
  | 2.1.2 | `0x886d00` | | 5.3.16 | `0x8874b0` |
  | 2.2.2 | `0x886e00` | | 5.4.2 | `0x8875b0` |
  | 2.3.16 | `0x886ec0` | | 5.5.16 | `0x887670` |

### 0.1 How the PS4 candidates were decided: the status slot

PS4 PC ids are not compared. Instead, every PS4 `cSeedLoginSvConnection::OnPacket_L2C_*` RES
handler stores its error into `cNetLoginServer::mErrorCode[i]` and its state into `mStatus[i]`,
and the matching `cNetLoginServer::<request>` caller of the `Send_C2L_*` sets the same `mStatus[i]`.
The index `i` is a per-request slot. On PC the same manager object (`[conn+0x110]`) has
`mStatus[i]` at `+4+4i` and `mErrorCode[i]` at `+0x4c+4i` (derived from the handlers below; the
two offsets agree for every handler). PS4 slots, from the Hex-Rays output of each handler (V):

| slot | PS4 handler (RES/NTC) | PS4 request (caller of Send/WritePacket) |
| --- | --- | --- |
| 3 | `OnPacket_L2C_PING_RES 0x37c6c0` | `cNetLoginServer::updateRTT 0x37ed40` |
| 4 | `OnPacket_L2C_LOGIN_RES 0x37c800` | |
| 5 | `OnPacket_L2C_LOGOUT_RES 0x37c9f0` (also clears `mGuardData.mSessionKey[64]`, sets `mStatus[4]`=NONE) | `cNetLoginServer::logout 0x37ff50` |
| 6 | `OnPacket_L2C_CLIENT_CHALLENGE_RES 0x37d010` | `cNetLoginServer::clientChallenge 0x37f980` |
| 7 | `OnPacket_L2C_GET_GAME_SERVER_LIST_RES 0x37cb60` | |
| 8 | `OnPacket_L2C_GET_GAME_SESSION_KEY_RES 0x37ccc0` | `cNetLoginServer::getGameSessionKey 0x3800d0` |
| 9 | `OnPacket_L2C_GET_ERROR_MESSAGE_LIST_RES 0x37d1f0` | `cNetLoginServer::getErrorMessageList 0x380160` |
| 10 | `OnPacket_L2C_GET_LOGIN_SETTING_RES 0x37d320` | `cNetLoginServer::getGameSetting 0x380270` |
| 11 | `OnPacket_L2C_GP_COURSE_GET_INFO_RES 0x37d4b0` | `cNetLoginServer::getGPCourseInfo 0x380300` |
| 12 | `OnPacket_L2C_GET_CHARACTER_LIST_RES 0x37d560` | `cNetLoginServer::getCharacterList 0x380390` |
| 13 | `OnPacket_L2C_DECIDE_CHARACTER_ID_RES 0x37d6f0` | `cNetLoginServer::decideCharacterId 0x380430` |
| 14 | `OnPacket_L2C_NEXT_CONNECT_SERVER_NTC 0x37dd60` | |
| 15 | `OnPacket_L2C_DECIDE_CANCEL_CHARACTER_RES 0x37d830` | |
| 16 | `OnPacket_L2C_DELETE_CHARACTER_INFO_RES 0x37dc60` | |
| 17 | `OnPacket_L2C_CREATE_CHARACTER_DATA_{RES,NTC}` | |

PC slots found (V): handler `0.0.2` 3 (`mov [mgr+0x58]`, `[mgr+0x10]`), `0.2.2` 5 (`+0x60`/`+0x18`,
then clears the session key via `0x88dae0`/`0x88db40` and sets `[mgr+0x14]` (slot 4) = 0, as PS4
LOGOUT), `1.0.2` 6 (`+0x64`/`+0x1c`), `2.1.2` 8 (`+0x6c`/`+0x24`), `2.2.2` 10 (`+0x74`/`+0x2c`),
`2.3.16` 14 (`+0x84`/`+0x3c`), `3.0.2` 9 (`+0x70`/`+0x28`), `4.0.2` 11 (`+0x78`/`+0x30`), `5.0.2` 12
(`+0x7c`/`+0x34`), `5.1.2` 13 (`+0x80`/`+0x38`); outside scope, consistent: `5.2.2` 15, `5.3.2` 17,
`5.4.2` 16. PC writers' callers set `mStatus[i] = 1` before the send (V): `0x88a540` caller
`0x88d142` slot 3; `0x88a480` caller `0x88cd90` slot 5; `0x88a780` caller `0x88c7a0` slot 8;
`0x88a840` caller `0x88c820` slot 10; `0x88a600` caller `0x88c6a0` slot 9; `0x88a6c0` caller
`0x88c720` slot 11; `0x88a2d0` caller `0x88c5a0` slot 12. Every slot agrees with the PS4 name of
the triage candidate. The two non-RES ids without a slot (3.0.16, 5.5.16) and the two writers with
arguments (1.0.1, 5.1.1) are matched by body and behaviour instead (sections 3, 11, 12).

### 0.2 RES and NTC header on PC (Season 3 difference)

- Every PC login RES reader (`0x889a30`, `0x8899a0`, `0x8894c0`, `0x889ce0`, `0x889d70`, `0x889b30`,
  `0x889bc0`, `0x8898a0`, `0x889780`, like `0x889920` of 0.1.2): `Read_s32` Error at `this+16`; if
  Error != 0: Result := Error, received, return (nothing more is read); else `Read_s32` Result and
  the body. Pattern form: `s32 Error; if (Error == 0) { s32 Result; ... }` (V). PS4 reads
  `u16 m_usError` then `s32 m_nResult` (GP course: `u32 m_unResult`) unconditionally (V PS4), so the
  PS4 header is 6 bytes and the PC header 4 or 8.
- PC login NTC readers read **no** u16/s32 error header except 2.3.16 (one s32, section 7);
  PS4 reads `u16 m_usError` first in every NTC (V both). The NTC difference is Season 3 / platform.
- Every reader ends with `this+12` = the header counter (byte-swapped u32 at header offset 5); that
  is not a body field.

### 0.3 Capture walk

Every login raw under `packets/decrypted_raw/` whose file name carries the raw name and id suffix
was decoded with the PC layouts below (inline stdlib Python, `python -X utf8 -I -` heredoc, run
from `D:/ddon-data`; not saved as a file): body from offset 0x09, fit = end within the last 15
bytes, no overrun. Header bytes checked separately (group, u16 id, sub, source 0x00/0x34): all
login raws pass except the 84 `C2L_CLIENT_CHALLENGE_REQ` raws (section 3). The `xxd` samples
below are one file per id; the counts are the whole set.

## 1. 0.0.1 C2L_PING_REQ / 0.0.2 L2C_PING_RES (L0)

- PC writer `0x88a540`: `WritePacket(p, 0, 0, 1, -1)`, `cSeedServerConnection::Send`; no body (V).
  PC reader `0x889a30` via handler `0x887740` (key 0x20000); after the read the handler calls
  `0x889450` on the manager (RTT update, I from PS4 `OnPacket_L2C_PING_RES` RTT code).
- PS4 match: **V** for both. `Send_C2L_PING_REQ 0x1a3ce70` writes only the 3-u16 PS4 header;
  slot 3 on both sides (0.1). DWARF `CPacket_L2C_PING_RES {u16 m_usError, s32 m_nResult}`.
- Wire: REQ empty. RES `s32 Error; if (Error == 0) s32 Result` (8 B) (V).
- Recompilation: no body for either (C2L.cpp only has DECIDE_CHARACTER_ID_REQ; L2C.cpp has no
  PING reader body); members agree. Arrowgene `C2LPingReq` empty, `L2CPingRes` ServerResponse: agree.
- Walk: REQ 75/75 fit, slack 7. `stream1-marked.pcapng_tcp-stream-33/11764_C2L_PING_REQ_…0_0_1`
  (16 B, sha256 `d0bda1a17e9e852d`): end 0x09. RES 75/75, slack 15, Error != 0 in 0:
  `…/11765_L2C_PING_RES_…0_0_2` (32 B, `66dcd2042f160995`): `00000000` Error 0, `00000000` Result 0,
  end 0x11.

## 2. 0.2.1 C2L_LOGOUT_REQ / 0.2.2 L2C_LOGOUT_RES (L0)

- PC writer `0x88a480`: `WritePacket(p, 0, 2, 1, -1)`, no body (V). PC reader `0x8899a0` via
  handler `0x886750` (key 0x20002); the handler clears the session key and resets slot 4 (V).
- PS4 match: **V** (slot 5 and the session-key clear, 0.1). `Send_C2L_LOGOUT_REQ 0x1a3c350` header
  only. DWARF `CPacket_L2C_LOGOUT_RES {u16 m_usError, s32 m_nResult}`.
- Wire: REQ empty; RES `s32 Error; if (Error == 0) s32 Result` (V).
- Arrowgene: agree. Recompilation: members only.
- Walk: REQ 42/42 slack 7 (`…/11873_C2L_LOGOUT_REQ_…0_2_1`, 16 B, `63770c481e6b5ca8`); RES 42/42
  slack 15 (`…/11877_L2C_LOGOUT_RES_…0_2_2`, 32 B, `85a9ecba913981cb`, Error 0, end 0x11).

## 3. 1.0.1 C2L_CLIENT_CHALLENGE_REQ (L1)

- PC writer `0x88a900`: `WritePacket(p, 1, 0, 1, -1)`, `Write_u8 [esp+0xc]`, `0x77cfa0`
  (loop `Write_u8` x **0x103 = 259**), `Write_u8`, `Write_u8`, `0x77cfe0` (loop `Write_u8` x
  **0x3e = 62**) (V, disassembly pushes). Caller: `0x889e70` (one caller).
- PS4 match: **V** by body. `nLoginSession::CPacket_C2L_CLIENT_CHALLENGE_REQ::WritePacket 0x1a409b0`
  signature `(u8 in_CommonKeySrcSize, const u8 (*in_CommonKeyEnc)[259], u8 in_PasswordSrcSize,
  u8 in_PasswordEncSize, const u8 (*in_PasswordEnc)[62])`, loops `> 0x102` and `> 0x3d`: the same
  five fields with the same array lengths; caller `cNetLoginServer::clientChallenge`.
- Wire (324 B, V): `u8 CommonKeySrcSize; u8 CommonKeyEnc[259]; u8 PasswordSrcSize;
  u8 PasswordEncSize; u8 PasswordEnc[62];`.
- Season 3: none in the layout.
- Recompilation: none (no C2L CLIENT_CHALLENGE class in C2L.h).
- **Walk: not run (no plaintext).** All 84 raws (42 x 304 B, 42 x 336 B; two per login stream) fail
  the header check: e.g. `…/11758_C2L_CLIENT_CHALLENGE_REQ_…1_0_1` (336 B, `c489c6ce2add5064`)
  starts `135b 767f f6e0 …` instead of `01 0000 01 00`. The pipeline did not decrypt this packet (it
  precedes the session key). 336 = 9 + 324 + 3 is consistent with the layout but proves nothing.
  A pattern for 1.0.1 can only be validated once the raws are re-decrypted; record as a coverage
  gap, not a failure.

## 4. 1.0.2 L2C_CLIENT_CHALLENGE_RES (L1)

- PC reader `0x8894c0` via handler `0x886970` (key 0x20000 of group 1): RES header, `Read_u8`
  (+24), `Read_u8` (+25), `0x757da0` (loop `Read_u8` x 0x3e = 62 into +26) (V).
- PS4 match: **V** (slot 6; reader `CPacket_L2C_CLIENT_CHALLENGE_RES::ReadPacket 0x1a3d360`: u16, s32,
  u8, u8, u8 loop). DWARF `{u16 m_usError, s32 m_nResult, u8 m_ucPasswordSrcSize,
  u8 m_ucPasswordEncSize, u8 m_ucPasswordEnc[62]}`.
- Recompilation: L2C.cpp has the body (Read m_usError, m_nResult, two u8, `m_ucPasswordEnc[i]`
  for i <= 61): agrees except the PC Error width (s32) (V).
- Wire: `s32 Error; if (Error == 0) { s32 Result; u8 PasswordSrcSize; u8 PasswordEncSize;
  u8 PasswordEnc[62]; }` (72 B) (V).
- Walk: 42/42 fit, slack 15. `…/11759_L2C_CLIENT_CHALLENGE_RES_…1_0_2` (96 B, `1959434e5e8a4e54`):
  Error 0, Result 0, sizes `0x10 0x10`, end 0x51.

## 5. 2.1.1 C2L_GET_GAME_SESSION_KEY_REQ / 2.1.2 L2C_GET_GAME_SESSION_KEY_RES (L2)

- PC writer `0x88a780`: `WritePacket(p, 2, 1, 1, -1)`, no body (V). PC reader `0x889ce0` (not a
  defined function in the database; decoded) via handler `0x886d00` (key 0x20001): RES header,
  `Read_MtString`, `Read_u16` (V).
- PS4 match: **V** (slot 8 both directions). PS4 `OnPacket_L2C_GET_GAME_SESSION_KEY_RES 0x37ccc0`
  reads u16, s32, MtString, u16; DWARF `{u16 m_usError, s32 m_nResult, MtString m_wstrSessionKey,
  u16 m_usGameServerUniqueID}`.
- Wire: REQ empty; RES `s32 Error; if (Error == 0) { s32 Result; MtString SessionKey;
  u16 GameServerUniqueID; }` (V).
- Walk: REQ 42/42 slack 7 (`…/11859_…2_1_1`, `942d4b840d532799`); RES 42/42, slack 12 in all:
  `…/11860_L2C_GET_GAME_SESSION_KEY_RES_…2_1_2` (64 B, `b837e78a6db8f8c5`): key length 0x20, end
  0x34 (key content not reproduced). Slack 12 > 2, so the u16 width rests on the code (R1 F3).

## 6. 2.2.1 C2L_GET_LOGIN_SETTING_REQ / 2.2.2 L2C_GET_LOGIN_SETTING_RES (L2)

- PC writer `0x88a840`: `WritePacket(p, 2, 2, 1, -1)`, no body (V). PC reader `0x889d70` via
  handler `0x886e00` (key 0x20002): RES header, CDataLoginSetting `0x887ab0` = `u32, u32, u8, bool,
  u32, list 0x77bbd0 {u32, MtString}, u32` (V).
- PS4 match: REQ **V** (slot 10, caller `cNetLoginServer::getGameSetting`); RES already matched in
  triage, slot 10 confirms (V). DWARF `CDataLoginSetting {u32 m_unJobLevelMax, u32 m_unClanMemberMax,
  u8 m_ucCharacterNumMax, b8 m_bEnableVisualEquip, u32 m_unFriendListMax,
  MtTypedArray<CDataURLInfo> m_UrlInfoList, u32 m_unNoOperationTimeOutTime}`, `CDataURLInfo
  {u32 m_unType, MtString m_wstrUrl}`: same order and widths (V); no Season 3 change.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; CDataLoginSetting LoginSetting; }`.
- Walk: REQ 41/41 slack 7; RES 41/41, slack 15: `…/11841_L2C_GET_LOGIN_SETTING_RES_…2_2_2` (992 B,
  `3b62eb045cc5c5ad`), end 0x3d1.

## 7. 2.3.16 L2C_NEXT_CONNECT_SERVER_NTC (L2, matched)

- PC reader `0x889df0` via handler `0x886ec0` (key 0x100003): `Read_s32` (+16), CDataGameServerListInfo
  `0x768ae0` = `u16, MtString, MtString, MtString, u32, u32, u32, MtString, u16, bool`, `Read_u8`
  (+60). All read unconditionally (V).
- The s32 is an error: the handler stores a non-zero value into `mErrorCode[14]` (`[mgr+0x84]`), sets
  `mStatus[14]` = 4 and raises the error dialog (`0xbb3980`) (V); on zero it compares the u8
  (object +0x3c) with `[mgr+0x12a0]` (expected counter) (V).
- PS4 match: **V** (slot 14). PS4 reads u16 Error, s32 Result, GameServerListInfo, u8; DWARF
  `{u16 m_usError, s32 m_nResult, CGameServerListInfo m_GameServer, u8 m_ucCounter}`.
  **Season 3 difference (V):** PC reads one s32 where PS4 reads u16 + s32 (4 B vs 6 B). Name it
  `Error` (it sits in the slot RES readers use for Error and is handled as one) (I for the name).
- CDataGameServerListInfo: DWARF `{u16 m_usId, MtString m_wstrName, MtString m_wstrBrief,
  MtString m_wstrTrafficName, u32 m_unTrafficLevel, u32 m_unMaxLoginNum, u32 m_unLoginNum,
  MtString m_wstrAddr, u16 m_usPort, b8 m_bIsHide}`: PC agrees (V).
- Wire: `s32 Error; CDataGameServerListInfo GameServer; u8 Counter;` (no `if`).
- Walk: 42/42, slack 0-15. `…/11857_L2C_NEXT_CONNECT_SERVER_NTC_…2_3_16` (112 B,
  `2ae50981e367dfde`): Error 0, Id 0x12, name length 0x0f, …, end 0x61.

## 8. 3.0.1 C2L_GET_ERROR_MESSAGE_LIST_REQ / 3.0.2 L2C_GET_ERROR_MESSAGE_LIST_RES (L3)

- PC writer `0x88a600`: `WritePacket(p, 3, 0, 1, -1)`, no body (V). PC reader `0x889b30` via
  handler `0x886fd0` (key 0x20000): RES header only (V).
- PS4 match: **V** (slot 9; caller `cNetLoginServer::getErrorMessageList`). DWARF
  `CPacket_L2C_GET_ERROR_MESSAGE_LIST_RES {u16 m_usError, s32 m_nResult}`. The list itself arrives
  in 3.0.16 NTCs before the RES (capture order: REQ, n x NTC, RES).
- Wire: REQ empty; RES `s32 Error; if (Error == 0) s32 Result`.
- Walk: REQ 41/41 slack 7 (`…/11766_…3_0_1`, `d0194b742d004328`); RES 41/41 slack 15
  (`…/11838_L2C_GET_ERROR_MESSAGE_LIST_RES_…3_0_2`, 32 B, `b3f6bf5bcfcdd9e5`, Error 0, end 0x11).

## 9. 3.0.16 L2C_GET_ERROR_MESSAGE_LIST_NTC (L3, matched)

- PC reader `0x889ac0` via handler `0x887070` (key 0x100000): list `0x887990` (`Read_u32` count, then
  per element `u32, u32, MtString, MtString`), then **`Read_u32`** (+36) (V). No error header.
- The handler first grows the persistent array at `[conn+0x160]+0x10` to the u32 kept at `+0x24`
  from the previous NTC (`0x88c530`) (V): the trailing u32 is a count used for reservation.
- PS4 match: already matched; PS4 `OnPacket_L2C_GET_ERROR_MESSAGE_LIST_NTC 0x37d2e0` reads u16 Error,
  list `Read_CDataErrorMessage_` (u32, u32, MtString, MtString) and nothing after. DWARF
  `{u16 m_usError, MtTypedArray<CDataErrorMessage> m_ErrorMessage}`, `CDataErrorMessage
  {u32 m_unMessageID, u32 m_unErrorID, MtString m_wstrMessage, MtString m_wstrDevelopMessage}`.
  **Season 3 differences (V):** no u16 error header, and the trailing u32 is new.
- Trailing u32 value (walk, V): in every stream it runs 950, 850, …, 150 with 100 entries, then 50
  with 50 entries: it is the number of messages from this chunk's first entry to the end
  (remaining including this chunk). Name `RemainingNum` is I (no PS4 member, no PC string).
- Wire: `MtTypedArray<CDataErrorMessage> ErrorMessage; u32 RemainingNum;`.
- Walk: 410/410 fit, slack 2-13. `…/11773_L2C_GET_ERROR_MESSAGE_LIST_NTC_…3_0_16` (6176 B,
  `ae84ceaf21b40a4a`): count 0x64, first element MessageID 1, ErrorID 0x7d0; trailing
  `000003b6` (950) at 0x1817, end 0x181b, slack 5.

## 10. 4.0.1 C2L_GP_COURSE_GET_INFO_REQ / 4.0.2 L2C_GP_COURSE_GET_INFO_RES (L4)

- PC writer `0x88a6c0`: `WritePacket(p, 4, 0, 1, -1)`, no body (V). PC reader `0x889bc0` via
  handler `0x8870b0` (key 0x20000): RES header; list `0x767340` of CDataGPCourseInfo `0x767440`
  (`u32, MtString, bool, u8, u8, u8, CDataCommonU32 list 0x75e8e0`); list `0x767220` of
  CDataGPCourseEffectParam (`u32 x4`); `Read_u32` (V).
- PS4 match: REQ **V** (slot 11, caller `getGPCourseInfo`); RES already matched (slot 11 confirms).
  PS4 `CPacket_L2C_GP_COURSE_GET_INFO_RES::ReadPacket 0x1a3d430`: u16, **u32**, CourseInfo list,
  EffectParam list, u32. DWARF `{u16 m_usError, u32 m_unResult, MtTypedArray<CDataGPCourseInfo>
  m_CourseInfo, MtTypedArray<CDataGPCourseEffectParam> m_Effects, u32 m_unVersion}`;
  `CDataGPCourseInfo {u32 m_unCourseID, MtString m_wstrCourseName, b8 m_bDoubleCourseTarget,
  u8 m_ucPrioGroup, u8 m_ucPrioSameTime, u8 m_ucAnnounceType, MtTypedArray<CDataCommonU32>
  m_EffectUIDList}`; `CDataGPCourseEffectParam {u32 m_unEffectUID, u32 m_unEffectID, u32 m_unParam0,
  u32 m_unParam1}`: PC agrees (V). PC reads Result as s32 (PS4 u32): signedness only.
- Recompilation: `ReadPacket` is a stub (no body); members as above.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; MtTypedArray<CDataGPCourseInfo> CourseInfo;
  MtTypedArray<CDataGPCourseEffectParam> Effects; u32 Version; }`.
- Walk: REQ 41/41 slack 7 (`…/11843_…4_0_1`, `3815fc20b377b0ae`); RES 41/41 slack 6-14:
  `…/11847_L2C_GP_COURSE_GET_INFO_RES_…4_0_2` (2832 B, `e8d9bb3a89f6e9f3`), end 0xb02.

## 11. 5.0.1 C2L_GET_CHARACTER_LIST_REQ / 5.0.2 L2C_GET_CHARACTER_LIST_RES (L5)

- PC writer `0x88a2d0`: `WritePacket(p, 5, 0, 1, -1)`, no body (V). PC reader `0x8898a0` via
  handler `0x887130` (key 0x20000): RES header, list `0x8877f0` (u32 count) of CDataCharacterListInfo
  `0x8878c0` (V):
  1. `nPacket::Read_CDataCharacterListElement_ 0x75ccf0` (existing `CDataCharacterListElement`,
     Character.hexpat, incl. the Season 3 trailing u8) (V).
  2. CDataEditInfo `0x764550` (existing `CDataEditInfo`, Context.hexpat, 122 B) (V).
  3. CDataMatchingProfile `0x76ed10`: `u8, u32, u8, u32, u32, u32, u32, MtString, bool` (V) = DWARF
     `{u8 m_ucEntryJob, u32 m_unEntryJobLevel, u8 m_ucCurrentJob, u32 m_unCurrentJobLevel,
     u32 m_unObjectiveType1, u32 m_unObjectiveType2, u32 m_unPlayStyle, MtString m_wstrComment,
     b8 m_bIsJoinParty}` (V; PS4 `Read_CDataMatchingProfile_ 0x19f2ff0` same sequence).
  4. list `0x765fb0` of CDataEquipItemInfo `0x766070`: `u32, u8, u8, u16, u8, u8, list 0x765a90
     {u8, u32, u16}, list 0x765ba0 {u8, u8, u16, u16}, list 0x766210 {u8, u16}` (V).
  5. list `0x7674d0` of CDataGPCourseValid `0x7675d0`: `u32, u32, MtString, MtString, u64, u64` (V).
  6. `u8` NextFlowType, `MtString` ClanName, `MtString` ClanShortName, `bool` IsClanMemberNotice (V).
- PS4 match: REQ **V** (slot 12, caller `getCharacterList`); RES already matched (slot 12 confirms).
  DWARF `CDataCharacterListInfo {CCharacterListElement, CEditInfo, CMatchingProfile,
  MtTypedArray<CDataEquipItemInfo> m_EquipList, MtTypedArray<CDataGPCourseValid> m_GpCourseValidList,
  u8 m_ucNextFlowType, MtString m_wstrClanName, MtString m_wstrClanShortName,
  b8 m_bIsClanMemberNotice}`: same order (V).
- **Season 3 differences (V, against PS4 readers):**
  - CDataEquipItemInfo: PS4 `Read_CDataEquipItemInfo_ 0x19e36a0` reads `u8 m_ucEquipType,
    u8 m_ucEquipSlot, u32 m_unItemID, u8 m_ucColor, u8 m_ucPlusValue, list CDataEquipElementParam
    {u8 m_ucSlotNo, u32 m_unItemID}`. PC reads `u32, u8, u8, u16, u8, u8` + three lists. Width
    sequence and the field at +4 (u32) suggest ItemID first (I); the u8/u8/u16 triple has no
    code-backed names (lead: Arrowgene `SafetySetting, EquipType, u16 EquipSlot`). The three lists
    have the shapes of the existing Context.hexpat `EquipElementParam` (PC `0x765a90`, same reader),
    `AddStatusParam` (PC `0x765ba0`, same reader) and `EquipStatParam` {u8, u16} (shape only; Context
    uses reader `0x7605e0`, here `0x766210`).
  - CDataGPCourseValid: PS4 `Read_CDataGPCourseValid_ 0x1a10d20` reads `u32 m_unID, u32 m_unCourseID,
    MtString m_wstrName, u32 m_unIconID, u64 m_ullStartTime, u64 m_ullEndTime`; PC reads a second
    **MtString** where PS4 has `u32 m_unIconID` (C for carrying the PS4 layout). Name I.
- Wire: RES `s32 Error; if (Error == 0) { s32 Result; MtTypedArray<CDataCharacterListInfo>
  CharacterList; }`.
- Walk: REQ 42/42 slack 7 (`…/11849_…5_0_1`, `d32fb580bb34490f`); RES 42/42, slack 0-15:
  `…/11850_L2C_GET_CHARACTER_LIST_RES_…5_0_2` (1040 B, `b3cfce35e6aa7869`), end 0x408, slack 8.
  Equip lists of 4-19 entries per character are exercised; every GpCourseValid list in the captures
  is empty, so the MtString-vs-u32 difference is **not** capture-tested (code only).

## 12. 5.1.1 C2L_DECIDE_CHARACTER_ID_REQ / 5.1.2 L2C_DECIDE_CHARACTER_ID_RES (L5)

- PC writer `0x88a980` (caller `0x88a110`): `WritePacket(p, 5, 1, 1, -1)`, `Write_u32 [esp+0xc]`,
  `Write_u32 [+0x10]`, `Write_u8 [+0x14]`, `Write_u8 [+0x18]`, `Write_u32 [+0x1c]`, `Write_u8 [+0x20]`
  (V, pushes). PC reader `0x889780` via handler `0x887240` (key 0x20001): RES header, `Read_u32`,
  `Read_u32` (V).
- PS4 match: REQ already matched; `CPacket_C2L_DECIDE_CHARACTER_ID_REQ::WritePacket 0x1a408d0`
  `(u32 in_CharacterID, u32 in_ClientVersion, u8 in_Type, u8 in_RotationServerID, u32 in_WaitNum,
  u8 in_Counter)`, same writes (V). RES **V** (slot 13; PS4 `0x37d6f0` reads u16, s32, u32, u32;
  DWARF `{u16 m_usError, s32 m_nResult, u32 m_unCharacterID, u32 m_unWaitNum}`).
- Recompilation: C2L.cpp WritePacket is a stub; signature and members agree.
- Wire: REQ `u32 CharacterID; u32 ClientVersion; u8 Type; u8 RotationServerID; u32 WaitNum;
  u8 Counter;` (14 B). RES `s32 Error; if (Error == 0) { s32 Result; u32 CharacterID; u32 WaitNum; }`.
- Walk: REQ 42/42 slack 8. `…/11853_C2L_DECIDE_CHARACTER_ID_REQ_…5_1_1` (32 B,
  `1aa19973d46eb1b0`): `0020b8f8 30401b01 02 00 00000000 01`, end 0x18. RES 42/42 slack 7:
  `…/11855_L2C_DECIDE_CHARACTER_ID_RES_…5_1_2` (32 B, `ed6de4481e81ce03`): Error 0, Result 0,
  CharacterID 0x0020b8f8 (same as the REQ), WaitNum 0, end 0x19.

## 13. 5.5.16 L2C_LOGIN_WAIT_NUM_NTC (L5)

- PC: no separate reader; handler `0x887670` (key 0x100005) calls `Read_u32` directly, stores it to
  `[mgr+0x1294]` and the time from `0x13ef5c0` to `[mgr+0x1078/0x107c]` (V).
- PS4 match: **V** by behaviour: `OnPacket_L2C_LOGIN_WAIT_NUM_NTC 0x37d930` stores the value to
  `mLoginWaitNum` and `MtNetTime::getTotalTime` to `mCreateCharacterUpdateTime`: the same two
  stores, and it is the only login NTC that stores a time. PS4 reads `u16 m_usError` first; PC does
  not (Season 3 difference, V).
- Wire: `u32 WaitNum;` (4 B).
- Walk: 9/9 fit, slack 3. `stream10-musicplayer-marked.pcapng_tcp-stream-7/10149_L2C_LOGIN_WAIT_NUM_NTC_…5_5_16`
  (16 B, `1f8514c9e0b92fe6`): `0000000b` (11), end 0x0d.

## 14. Summary

PS4 mark: V = candidate confirmed by code (slot, body or behaviour); "matched" = already matched in
T001 and re-confirmed. Body bytes for Error == 0; "var" with the sample's body length.

| id | name | PS4 match | body bytes | walked capture (count) | fits |
| --- | --- | --- | --- | --- | --- |
| 0.0.1 | C2L_PING_REQ | V (slot 3) | 0 | 11764 (75) | 75/75 |
| 0.0.2 | L2C_PING_RES | V (slot 3) | 8 | 11765 (75) | 75/75 |
| 0.2.1 | C2L_LOGOUT_REQ | V (slot 5) | 0 | 11873 (42) | 42/42 |
| 0.2.2 | L2C_LOGOUT_RES | V (slot 5, key clear) | 8 | 11877 (42) | 42/42 |
| 1.0.1 | C2L_CLIENT_CHALLENGE_REQ | V (body, arrays 259/62) | 324 | none: 84 raws are not plaintext | not run |
| 1.0.2 | L2C_CLIENT_CHALLENGE_RES | V (slot 6, body) | 72 | 11759 (42) | 42/42 |
| 2.1.1 | C2L_GET_GAME_SESSION_KEY_REQ | V (slot 8) | 0 | 11859 (42) | 42/42 |
| 2.1.2 | L2C_GET_GAME_SESSION_KEY_RES | V (slot 8) | var (43) | 11860 (42) | 42/42 |
| 2.2.1 | C2L_GET_LOGIN_SETTING_REQ | V (slot 10) | 0 | 11840 (41) | 41/41 |
| 2.2.2 | L2C_GET_LOGIN_SETTING_RES | matched (slot 10) | var (968) | 11841 (41) | 41/41 |
| 2.3.16 | L2C_NEXT_CONNECT_SERVER_NTC | matched (slot 14) | var (88) | 11857 (42) | 42/42 |
| 3.0.1 | C2L_GET_ERROR_MESSAGE_LIST_REQ | V (slot 9) | 0 | 11766 (41) | 41/41 |
| 3.0.2 | L2C_GET_ERROR_MESSAGE_LIST_RES | V (slot 9) | 8 | 11838 (41) | 41/41 |
| 3.0.16 | L2C_GET_ERROR_MESSAGE_LIST_NTC | matched (body) | var (6162) | 11773 (410) | 410/410 |
| 4.0.1 | C2L_GP_COURSE_GET_INFO_REQ | V (slot 11) | 0 | 11843 (41) | 41/41 |
| 4.0.2 | L2C_GP_COURSE_GET_INFO_RES | matched (slot 11) | var (2809) | 11847 (41) | 41/41 |
| 5.0.1 | C2L_GET_CHARACTER_LIST_REQ | V (slot 12) | 0 | 11849 (42) | 42/42 |
| 5.0.2 | L2C_GET_CHARACTER_LIST_RES | matched (slot 12) | var (1023) | 11850 (42) | 42/42 |
| 5.1.1 | C2L_DECIDE_CHARACTER_ID_REQ | matched (body) | 14 | 11853 (42) | 42/42 |
| 5.1.2 | L2C_DECIDE_CHARACTER_ID_RES | V (slot 13) | 16 | 11855 (42) | 42/42 |
| 5.5.16 | L2C_LOGIN_WAIT_NUM_NTC | V (behaviour) | 4 | 10149 (9) | 9/9 |

Captures without a folder are in `stream1-marked.pcapng_tcp-stream-33/`. No candidate was
rejected. No captured RES has Error != 0, so the error branch is code-only (V code, not run on
captures). Header-only REQs (slack 7) and the fixed slack-15 RES files fit any body of up to 7/15
more bytes: their emptiness rests on the PC writers/readers (R1 F3).

## 15. Shared types for pattern authors

Reuse: `Packet.hexpat` `CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`;
`Character.hexpat` `CDataCharacterListElement`; `Context.hexpat` `CDataEditInfo`,
`EquipElementParam`, `AddStatusParam`, `EquipStatParam` (shape {u8, u16}). The existing
`C2L_LOGIN_REQ` / `L2C_LOGIN_RES` patterns' header (`sourceOk`, inline RES `Error`/`Result`, fit
block) fits every login pattern unchanged.

Add (all V from the PC readers named above; names from PS4 DWARF unless marked I):

| Include (proposal) | Struct | PC reader | Wire |
| --- | --- | --- | --- |
| new `Login.hexpat` (includes Packet) | `CDataURLInfo` | `0x77bbd0` (list) | u32 Type, MtString Url |
| `Login.hexpat` | `CDataLoginSetting` | `0x887ab0` | u32 JobLevelMax, u32 ClanMemberMax, u8 CharacterNumMax, bool EnableVisualEquip, u32 FriendListMax, MtTypedArray<CDataURLInfo> UrlInfoList, u32 NoOperationTimeOutTime |
| `Login.hexpat` | `CDataGameServerListInfo` | `0x768ae0` | u16 Id, MtString Name, MtString Brief, MtString TrafficName, u32 TrafficLevel, u32 MaxLoginNum, u32 LoginNum, MtString Addr, u16 Port, bool IsHide |
| `Login.hexpat` | `CDataErrorMessage` | `0x887990` (list) | u32 MessageID, u32 ErrorID, MtString Message, MtString DevelopMessage |
| new `GP.hexpat` (includes Packet) | `CDataGPCourseInfo` | `0x767440` (list `0x767340`) | u32 CourseID, MtString CourseName, bool DoubleCourseTarget, u8 PrioGroup, u8 PrioSameTime, u8 AnnounceType, MtTypedArray<CDataCommonU32> EffectUIDList |
| `GP.hexpat` | `CDataGPCourseEffectParam` | list `0x767220` | u32 EffectUID, u32 EffectID, u32 Param0, u32 Param1 |
| `GP.hexpat` | `CDataGPCourseValid` | `0x7675d0` (list `0x7674d0`) | u32 ID, u32 CourseID, MtString Name, MtString unk_MtString (Season 3; PS4 u32 IconID), u64 StartTime, u64 EndTime |
| `Character.hexpat` | `CDataMatchingProfile` | `0x76ed10` | u8 EntryJob, u32 EntryJobLevel, u8 CurrentJob, u32 CurrentJobLevel, u32 ObjectiveType1, u32 ObjectiveType2, u32 PlayStyle, MtString Comment, bool IsJoinParty |
| `Item.hexpat` (move `EquipElementParam`, `AddStatusParam`, `EquipStatParam` here from Context.hexpat, or include Context) | `CDataEquipItemInfo` | `0x766070` (list `0x765fb0`) | u32 ItemID (I), u8 unk_u8_0, u8 unk_u8_1, u16 unk_u16, u8 Color (I), u8 PlusValue (I), MtTypedArray<EquipElementParam>, MtTypedArray<AddStatusParam>, MtTypedArray<EquipStatParam> |
| `Character.hexpat` (needs `CDataEditInfo` from Context.hexpat and the two above) | `CDataCharacterListInfo` | `0x8878c0` (list `0x8877f0`) | CDataCharacterListElement, CDataEditInfo, CDataMatchingProfile, MtTypedArray<CDataEquipItemInfo> EquipList, MtTypedArray<CDataGPCourseValid> GpCourseValidList, u8 NextFlowType, MtString ClanName, MtString ClanShortName, bool IsClanMemberNotice |

The CDataEquipItemInfo field names after ItemID follow neither PS4 (u8 EquipType, u8 EquipSlot, no
u16) nor code; keep `unk_` names. Placing `CDataCharacterListInfo` where Context.hexpat is visible
(e.g. a new `Login.hexpat` that includes Character, Context, Item and GP) avoids an include cycle;
the choice is the implementer's.

## 16. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`,
`Arrowgene.Ddon.Shared/Entity/PacketStructure/` and `Entity/Structure/`:

1. `C2LClientChallengeReq`: `CommonKeyEnc = ReadByteArray(256)` + `ReadBytes(3) // Padding?` (and the
   writer's `new byte[3]`). The 3 bytes are the tail of `u8 CommonKeyEnc[259]` (PC `0x77cfa0` loop
   0x103; PS4 `in_CommonKeyEnc[259]`), not padding.
2. `C2LClientChallengeReq`: `PasswordEnc = ReadBytesTerminated(0)`; the client writes a fixed
   `u8 PasswordEnc[62]` (PC `0x77cfe0`, PS4 `[62]`), so a 0 byte inside the ciphertext truncates it.
3. `L2CClientChallengeRes`: writes `PasswordEnc` plus `64 - PasswordEncSize` padding (64 B) and reads
   `PasswordEncSize` bytes; the client reads exactly 62 (PC `0x757da0`). The server sends 2 bytes the
   client ignores; the reader under-reads.
4. `L2CGetGameSessionKeyRes`: `uint Unknown` (u32) after the key; the client reads `u16`
   GameServerUniqueID (PC `0x889ce0` `Read_u16`; PS4 `m_usGameServerUniqueID`). 2 extra bytes.
5. `L2CGetErrorMessageListNtc`: no trailing u32; the client reads `u32` after the list (PC
   `0x889ac0`, `this+36`), the remaining-message count (section 9). The server omits it.
6. Not misplacements (agree with PC): `L2CNextConnectionServerNtc` (u32 Error = PC s32),
   `L2CDecideCharacterIdRes`, `C2LDecideCharacterIdReq`, `L2CLoginWaitNumNtc`, `L2CGpCourseGetInfoRes`,
   `L2CGetLoginSettingRes`, `L2CGetCharacterListRes`, the empty REQs, and the entities
   `CDataGameServerListInfo`, `CDataErrorMessage`, `CDataLoginSetting`, `CDataURLInfo`,
   `CDataGPCourseInfo`, `CDataGPCourseEffectParam`, `CDataCharacterListElement`, `CDataMatchingProfile`,
   `CDataEquipItemInfo` (widths agree; names unproven), `CDataGPCourseValid` (`NameA`, `NameB` agree
   with PC's two MtStrings). `WriteServerResponse` always writes `u32 Error, u32 Result`; the client
   reads Result only when Error == 0 (a server sending an error still sends Result; harmless excess).

## 17. Open items

- 1.0.1 has no plaintext capture: a pattern cannot be walked until the 84 raws are re-decrypted
  (the packet is encrypted with something other than the session cipher; not investigated here).
- Names without code backing: 2.3.16 `Error` (I), 3.0.16 `RemainingNum` (I), CDataEquipItemInfo
  fields after ItemID, CDataGPCourseValid second MtString.
- CDataGPCourseValid is not capture-tested (all lists empty).

## Errata (R1, 2026-11-02)

Appended after the R1 review of T002-T004; the sections above stay as written.

- **§ 12, sample bytes and body size.** The grouping `0020b8f8 30401b01 02 00 00000000 01` is
  wrong, and "(14 B)" for the REQ (also the § 14 table) undercounts. Correct: CharacterID
  0x0020b8f8, ClientVersion 0x3040001b, Type 1, RotationServerID 2, WaitNum 0, Counter 1; the body is
  4 + 4 + 1 + 1 + 4 + 1 = 15 B (9 + 15 = 0x18 = the stated end; paddingSize 8 in the 32-byte file).
  Source: the plbatch export of `stream1-marked.pcapng_tcp-stream-33/11853_…5_1_1.json`
  (ClientVersion 809500699, Type 1, RotationServerID 2, paddingSize 8); T003 § 3.
- **§ 5, session-key length.** "key length 0x20" is wrong: the length is 0x1f (31), which the
  section's own end 0x34 implies (0x09 + 4 + 4 + 2 + 31 + 2 = 0x34). Source: the export of
  `stream1-marked.pcapng_tcp-stream-33/11860_…2_1_2.json` (`SessionKey.length` 31, paddingSize 12).
- **§ 3, § 14, § 17, 1.0.1 not walkable.** Superseded. The raws are now re-decrypted with the fixed
  client key (T002c § 1, § 5; T002d, commit 40f80dc80fa); 336 = 324 + 12 bytes of cipher block
  padding, not 9 + 324 + 3, and the packet carries no header (T002c § 3; T003 § 1: `Send` drops
  the 9 header bytes). The 304-byte files are the server's certificate notice, filed since T002e
  (commit 70201832e19) as 1.1.16 L2C_LOGIN_SERVER_CERT_NTC. Walk: 42/42 fit
  (`C2L_CLIENT_CHALLENGE_REQ-pattern.cpp`; packets README).
