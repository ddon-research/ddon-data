# 006 T011: groups 5, 6 PARTY, 16 FRIEND, 17 BLACK_LIST, 24 JOB_MASTER, 26 PROFILE

Build **03040008** (PC, Season 3 truth), seed **PS4 02020005** (symbols). Brief:
`specs/006-packet-pattern-coverage/briefs/T011-party-profile-friend.md`; the 27 rows of groups 5, 6, 16,
17, 24 and 26 in `research/T001-triage.tsv` (2 + 11 + 4 + 2 + 1 + 7 ids, 1,151 captures). Base
`d670cb0f9b` (HEAD was `fbffdd461c` when the report was written; that commit only adds the T012 brief,
no input of this report changed). Marks: **V** verified in code (or by capture for walk results),
**I** inferred, **C** contradicted. All addresses are VAs.

## 0. Sources and method

- PC database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-t011/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (checked: 32-bit, image base `0x400000`). PS4 database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-t011/DDOORBIS.elf.i64`
  (checked: 64-bit, image base `0`). Read-only ida-mcp `execute_python` (Hex-Rays; `ida_ua.decode_insn`
  with `GENDSM_FORCE_CODE` for linear decoding; `ida_typeinf` for DWARF members). Nothing renamed,
  retyped, commented, patched or reanalysed.
- PC primitives and framing as T003/T005/T010 § 0 (`nPacket::Read_*`, `Write_*`, `WritePacket 0x8bcbb0`).
- **PC handler table (V)**: directory `0x1bc0110` (8-byte entries `{table, count}` per group) -> group 5
  `{0x212fdd8, 4}`, 6 `{0x212dba0, 36}`, 16 `{0x212c778, 11}`, 17 `{0x212b020, 3}`, 24 `{0x212d5d0, 7}`,
  26 `{0x212e488, 18}`; stride 0x18, key `(sub<<16)|id` at +0x10; entry +0 is filled by the initializer
  (`mov [esp], <handler>` + `movq` store). Each entry of this package was traced to its initializer store:
  every S2C `pc_va` of the triage equals its table handler (**V, 16/16**; e.g. `0x1a28613` stores
  `0x7c6ba0` into 17.0.2 `0x212b020`, `0x1a2ea2f` stores `0x7e0b70` into 24.6.16 `0x212d660`).
- **Not normal functions in the PC database** (decoded linearly, no database change): 5.2.16 handler
  `0x7fe5e0` (`loc_`; the enclosing function starts at `0x7fe5de`); 24.6.16 handler `0x7e0b70`
  (`dword_7E0B70`, data in the database); 6.8.16 `0x7e8a30` and 6.10.16 `0x7e8e50` are functions but
  Hex-Rays shows them `__noreturn` after the gate call `sub_407AC0`, so their read paths
  (`0x7e8a6f`, `0x7e8e80`) were read instruction by instruction.
- PC writers (C2S): `WritePacket(p, group, id, 1, -1)` with group/id read from the call (V each, 11/11).
- PS4 match by code only (symbol + body, DWARF `nUserSession::CPacket_*` members, behaviour), never by PS4
  id. RES header (V, every PC RES reader here): `Read_s32` Error (+16); non-zero -> return; else `Read_s32`
  Result, body. PS4 reads `u16 m_usError` + `s32 m_nResult`. PC NTC readers read **no** header (V:
  5.2.16, 5.3.16, 6.8.16, 6.10.16, 6.18.16, 24.6.16; capture: the PS4-framed variant fails 148/148 and
  162/162 on 5.2.16 and 5.3.16). PS4 C2S writers start with `Write_u16 0, Write_u16 <flat id>, Write_u16 0`
  (PS4 framing); PC C2S bodies hold only the fields listed.
- **Walk**: `specs/006-packet-pattern-coverage/research/T011-walk.py` (stdlib; run from `D:/ddon-data`
  with `python -X utf8 -I specs/006-packet-pattern-coverage/research/T011-walk.py`; sha256 prefix
  `f60ad17d5ed5040b`; holds every PC layout below, the PS4 counter-test variants, `tally` fields and an
  extra block of value sets). Input `packets/decrypted_raw/*/`, every file whose suffix is `.<g>_<id>_<sub>`
  of the 27 ids (each suffix carries exactly one packet name). Header check: group, u16 id, sub, source
  (0x00 C2S, 0x34 S2C). Body from 0x09; fit = end within the last 15 bytes, no overrun. **Totals: 1151
  files, header 1151/1151, fit 1151/1151, no RES with Error != 0.** Samples: file (relative to
  `packets/decrypted_raw/`), size, sha256 first 16 hex digits, body end offset.
- Recompilation cross-check (`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/Protocol/UserSession/`):
  `S2C.cpp` implements only `CPacket_S2C_PARTY_JOIN_RES::ReadPacket` of this package (u16 Error, s32
  Result, u8 MemberIndex, u64 ContentNumber, u32 PartyId: agrees with PS4 and PC); the other RES/NTC have
  DTI boilerplate only. `C2S.cpp`: `CPacket_C2S_SET_SHORTCUT_LIST_REQ` and
  `CPacket_C2S_SET_COMMUNICATION_SHORTCUT_LIST_REQ::WritePacket` are `DDON_STUB`. `PacketData/`
  (`Community.h` CDataFriendInfo, `Lobby.h` CDataLobbyMemberInfo, `Party.h` CDataPartyMember,
  `JobOrbTree.h` CDataJobOrbTreeStatus) declares the same members and offsets as the PS4 DWARF. Nothing
  contradicts the PS4 DWARF. Triage `recompiled_body` "yes" for 6.8.2 holds; for 26.12.1 and 26.14.1 the
  recompilation body is a `DDON_STUB` (no body).

Field-name sources: PS4 DWARF member (`m_`/type prefix dropped) **V**; other names **I** with the basis
stated; a Season 3 field without code backing is `unk_*` (server names only as leads in comments).

## 1. Shared structures

Already in the includes and confirmed here (no change): `CDataCommunityCharacterBaseInfo` (PC list
`0x75ebc0`, element {u32, MtString x3}), `CDataCharacterListElement` (`0x75ccf0`, list `0x75cbd0`, Season 3
trailing u8), `CDataPartyMember` (`0x771580`, list `0x7714c0`), `CDataLobbyMemberInfo` (`0x76d7f0`, list
`0x76d6f0`: re-read here, three `Read_u8` at +0x20/+0x21/+0x22), `CDataCommonU32` (`0x75e8e0`),
`CDataOrbPageStatus` (`0x7702d0`), `CDataJobOrbTreeStatus` (`0x76c270`), `CDataShortCut`,
`CDataCommunicationShortCut` (`Character.hexpat`).

New:

| Struct | PC reader | PS4 02020005 | Wire (PC 03040008) |
| --- | --- | --- | --- |
| `CDataFriendInfo` | list `0x766e20` | `Read_CDataFriendInfo_ 0x1a0b520` {CCharacterListElement m_CharacterListElement, u8 m_ucPendingStatus, u32 m_unFriendNo, b8 m_bFavorite} | CDataCharacterListElement (`0x75ccf0`, **S3 trailing u8**), u8 PendingStatus, u32 FriendNo, bool Favorite (V) |
| `CDataHistoryElement` | list `0x7698c0` | `0x19f19a0` {u8 m_ucType, u32 m_unTargetID, u32 m_unParam, u64 m_ullDateTime} | same (V, = PS4) |
| `CDataAchieveCategoryStatus` | list `0x7583b0` | `0x19f16a0` {u8 m_ucCategoryID, u16 m_usAchieveNum, u16 m_usTargetNum} | same (V, = PS4) |
| JOB_MASTER target element (24.6.16) | list `0x76c500`, element `0x76c5f0` (only caller: the 24.6.16 handler) | none (§ 13) | u8, u32, u8, u8, u32, u32 (V shape; names I, § 13) |

PC writers of the shortcut lists (V): `0x780f20` writes count + {u32 x5, u8} (`CDataShortCut`, the
same shape as the reader `0x778990`); `0x77e0b0` writes count + {u32, u32, u8, u8, u32}
(`CDataCommunicationShortCut`, reader `0x75ea80`).

## 2. 5.2.16 USER_LIST_JOIN_NTC (unresolved -> matched, V)

- PC handler `0x7fe5e0` (not a function start): `loc_76D6F0(packet, list)` = list CDataLobbyMemberInfo;
  then per element `sub_8434F0(mgr, elem)` and `sub_B5C870(elem+8, elem+0x1c)` (CharacterID, PawnId).
  No header.
- PS4 `cSeedGameSvConnection::OnPacket_S2C_USER_LIST_JOIN_NTC 0x2de740`: `Read_u16` error,
  `Read_CDataLobbyMemberInfo_` into `m_LobbyMemberInfoList`, per element `cNetGameServer::addLobbyMember`
  + `sGame::callbackEntryLobby(m_unCharacterID, m_unPawnId)`: same flow, **match V (behaviour + list
  type)**. Field name `LobbyMemberInfoList` (V, DWARF).
- Season 3: element has 3 u8 after PawnId, PS4 4 (V, reader). Counter-test: the PS4 4-u8 element fails
  **50/148** (T006 found no 3.0.2 capture that separated them; this does), PS4 u16 framing fails 148/148.
- Walk 148/148; lists up to 25; tuple (u8, SessionStatus, OnlineStatus) has 25 distinct values, first
  u8 in {1, 2, 3}; sample `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/519_S2C_USER_LIST_JOIN_NTC_…5_2_16`
  (768 B, `544d3354f9dae801`) end 0x2fd.

## 3. 5.3.16 USER_LIST_LEAVE_NTC (unresolved -> matched, V)

- PC handler `0x7fe7a0`: `sub_75E8E0` (list CDataCommonU32); `sub_7FE6E0` removes from the lobby member
  array every element with +8 == id and +0x1c == 0, then `sub_B5CB80(id, 0)`.
- PS4 `0x2dea20` reads `u16 m_usError`, `m_CharacterList` (CDataCommonU32); `cNetGameServer::
  OnPacket_S2C_USER_LIST_LEAVE_NTC` does the same removal (`+8 == id && +28 == 0`) and
  `sGame::callbackLeaveLobby(id, 0)`: **match V (behaviour)**. Field `CharacterList` (V).
- Walk 162/162 (ps4frame fails 162/162); lists up to 9; xxd
  `stream6-annilot-hobo-marked.pcapng_tcp-stream-2/30703_…5_3_16` (64 B, `32441b1d0c2a67b2`):
  `0500 0310 34 | 0000 0009 | 0012 1c62 …` count 9, nine u32 ids, end 0x31.

## 4. 6.0.1 PARTY_CREATE_REQ / 6.0.2 PARTY_CREATE_RES

- REQ `0x831890`: `WritePacket(6, 0, 1)`, empty (V); PS4 `Send_C2S_PARTY_CREATE_REQ 0x19b1680` empty (V).
- RES handler `0x7e7790` ("cSeedGameSvConnection::OnPacket_PARTY_PARTY_CREATE_RES") -> `0x810a10`:
  header, u32, u64. PS4 `OnPacket_S2C_PARTY_CREATE_RES 0x2df970` {u32 m_unPartyId, u64
  m_ullContentNumber}: **= PS4 (V)**.
- Walk 42/42 + 42/42; sample `stream1-marked.pcapng_tcp-stream-35/12124_…6_0_2` (32 B,
  `4c840c95f63575c9`) end 0x1d.

## 5. 6.8.1 PARTY_JOIN_REQ / 6.8.2 PARTY_JOIN_RES

- REQ `0x831e30`: `WritePacket(6, 8, 1)`, `Write_u32 a3` (V). PS4 `Send_C2S_PARTY_JOIN_REQ 0x19b27c0(u32
  in_PartyId)`: field `PartyId` (V).
- RES handler `0x7e8b20` (string "…OnPacket_PARTY_PARTY_JOIN_RES") -> `0x8111a0`: header, u8, u64, u32.
  PS4 `CPacket_S2C_PARTY_JOIN_RES::ReadPacket 0x19d4f50` {u8 m_ucMemberIndex, u64 m_ullContentNumber,
  u32 m_unPartyId}; recompilation identical: **= PS4 (V)**.
- Walk 1/1 + 1/1. xxd 6.8.1 `stream85-marked.pcapng_tcp-stream-11/139009_…6_8_1` (16 B,
  `8b5769f1f96efef6`): `0600 0801 00 | 0000 015b 17 | 00 000d a4` -> PartyId 0x0da4 = 3492, end 0x0d.
  6.8.2 `…/139012_…6_8_2` (32 B, `04dad69886fd26a1`): Error 0, Result 0, MemberIndex 0, u64
  `0x0000000400 04d104`, PartyId 3492, end 0x1e. The same PartyId 3492 arrives in 6.18.16 (§ 9) 3 s
  before: capture flow invite-accept -> join (V by capture).

## 6. 6.8.16 PARTY_JOIN_NTC (unresolved -> matched, V)

- PC handler `0x7e8a30` (gate `sub_407AC0`, then flags `+0x467a`, `+0x98`, `+0x74` of the manager may
  return 1 without reading); read path `0x7e8a6f` -> `0x811120`: u32, u32, list `0x7714c0`
  (CDataPartyMember `0x771580`). No header. Then `sub_7E8890`: `sub_843BE0(mgr, list)` and
  `sub_882B90(mgr, u32_0, u32_1, list, state == 1)`.
- PS4 `OnPacket_S2C_PARTY_JOIN_NTC 0x2e1410`: u16 m_usError, u32 m_unLeaderCharacterID, u32
  m_unHostCharacterID, `Read_CDataPartyMember__0` m_PartyMember; `cNetGameServer::OnPacket_S2C_PARTY_JOIN_NTC
  0x36d330`: `addUserListFromPartyMember` per element, `setPartyMemberInfoList(leader, host, list,
  mStatus[28] == NET_STAT_REQ)`: same flow, **match V**. Fields `LeaderCharacterID`, `HostCharacterID`,
  `PartyMember` (V).
- Season 3: only through `CDataCharacterListElement`'s trailing u8 (include). Counter-test: the PS4
  element (no trailing u8) also fits 43/43 (every list holds one member, slack 2-4 absorbs one byte):
  inconclusive, the reader decides. PS4 framing fails 43/43.
- Walk 43/43; trailing u8 always 1. xxd `stream1-marked.pcapng_tcp-stream-35/12121_…6_8_16` (80 B,
  `e2b41d2fd88b2cc6`): `0020b8f8 0020b8f8 | 00000001 | 0020b8f8 "Diana" "Seelix" "S;R" …` end 0x4d.

## 7. 6.10.1 PARTY_LEAVE_REQ / 6.10.2 PARTY_LEAVE_RES / 6.10.16 PARTY_LEAVE_NTC

- REQ `0x831f10`: `WritePacket(6, 10, 1)`, empty (V); PS4 `Send_C2S_PARTY_LEAVE_REQ 0x19b2900` empty.
- RES `0x7e8f30` (string "…OnPacket_PARTY_PARTY_LEAVE_RES") -> `0x811240`: header only. PS4 `0x2e1740`
  header only: **= PS4 (V)**.
- NTC `0x7e8e50` (gate as § 6, early return if `+0x467a`); read path `0x7e8e80`: one `Read_u32` into the
  packet object, then `sub_7E8D00`, which raises `sGUIExt::requestInfomation(n3_0, 22)` under the
  large-party / quest-board checks and calls `sub_B616F0(sGame, 0, 0)`. PS4 `OnPacket_S2C_PARTY_LEAVE_NTC
  0x2e1870` {u16 m_usError, u32 m_unCharacterID}; `cNetGameServer::OnPacket_S2C_PARTY_LEAVE_NTC 0x36d780`
  raises `requestInfomation(INFO_FLAG_NO_LEADER)` under the same checks, then
  `sGame::setPartyWarpInfo(0, 0)`, `callbackLeaveParty`: **match V (behaviour)**. Field `CharacterID` (V).
- Counter-test: ps4frame fits 43/43 (slack 3 absorbs u16; inconclusive, the reader decides).
- Walk 43/43 x3; xxd 6.10.16 `stream1-marked.pcapng_tcp-stream-35/26541_…6_10_16` (16 B,
  `ab5cd937073e1bbb`): `0600 0a10 34 | 0000 06e0 | 0020 b8f8` -> CharacterID 0x20b8f8, end 0x0d.
  6.10.2 sample `…/26542_…6_10_2` (32 B, `3c53028c688ab127`) end 0x11.

## 8. 6.15.1 PARTY_MEMBER_SET_VALUE_REQ / 6.15.2 …_RES

- REQ `0x8320b0` (`cSeedGameSvConnection::Send_C2S_PARTY_MEMBER_SET_VALUE_REQ`, a hand-given name in the
  database; lead only): `WritePacket(6, 15, 1)`, `Write_u8`, `Write_u8` (V). PS4
  `Send_C2S_PARTY_MEMBER_SET_VALUE_REQ 0x19b2160(u8 in_Index, u8 in_Value)`: fields `Index`, `Value` (V).
  Captured Index 2 (6/6), Value 0 or 1.
- RES `0x7e95c0` (string "…OnPacket_PARTY_PARTY_MEMBER_SET_VALUE_RES") -> `0x811450`: header only (V,
  = PS4 `0x2e23e0`).
- Walk 6/6 + 6/6; sample `stream85-marked.pcapng_tcp-stream-11/121503_…6_15_1` (16 B, `f4716cb05fad5570`)
  end 0x0b.

## 9. 6.18.16 PARTY_INVITE_ACCEPT_NTC (unresolved -> matched, V)

- PC handler `0x7e78d0` -> `0x810b30`: u16, u32, u32, u32, u8; no header; then `sub_4096F0(mgr, pkt)`.
- PS4 `CPacket_S2C_PARTY_INVITE_ACCEPT_NTC::ReadPacket 0x19d4e90` (via `OnPacket_… 0x2e0b50`): u16
  m_usError, u16 m_usServerId, u32 m_unPartyId, u32 m_unStageId, u32 m_unPositionId, u8 m_ucMemberIndex.
  Same widths and order after the PS4 error; the delivered PartyId is the one the client then sends in
  6.8.1 (§ 5): **match V (code shape + capture flow)**. Fields `ServerId`, `PartyId`, `StageId`,
  `PositionId`, `MemberIndex` (V).
- Walk 1/1 (ps4frame also fits: slack 8). xxd `stream85-marked.pcapng_tcp-stream-11/138974_…6_18_16`
  (32 B, `cc7d15784962e46e`): `0600 1210 34 | 0000 1690 | 0005 | 0000 0da4 | 0000 0002 | 0000 0018 | 00`
  -> ServerId 5, PartyId 3492, StageId 2, PositionId 24, MemberIndex 0, end 0x18.

## 10. 16.0.1 GET_FRIEND_LIST_REQ / 16.0.2 GET_FRIEND_LIST_RES

- REQ `0x828c90`: `WritePacket(16, 0, 1)`, empty (V; PS4 `0x19c6000` empty).
- RES `0x7d6750` (string "…OnPacket_FRIEND_GET_FRIEND_LIST_RES") -> `0x808900`: header, list
  `0x766e20` (CDataFriendInfo), list `0x75ebc0`, list `0x75ebc0` (CDataCommunityCharacterBaseInfo).
  PS4 `CPacket_S2C_GET_FRIEND_LIST_RES::ReadPacket 0x19d9a60` {m_FriendInfoList, m_ApplyingCharacterList,
  m_ApprovingCharacterList}: = PS4 except the list element's S3 trailing u8 (V).
- Counter-test: PS4 CDataFriendInfo (no trailing u8) fails **20/41** (the 21 non-empty lists, one
  single-element list absorbed by slack). Walk 41/41 + 41/41; friend lists 0, 1 or 7 entries; both
  community lists always empty (code-only); trailing u8 0 (140) or 1 (1); sample
  `stream21-failedlogin-marked.pcapng_tcp-stream-48/12368_…16_0_2` (304 B, `8293ab4a7d70b128`) end 0x121.

## 11. 16.6.1 GET_RECENT_CHARACTER_LIST_REQ / 16.6.2 …_RES

- REQ `0x828d50` empty (V; PS4 `0x19ca810` empty). RES `0x7d6840` (string
  "…OnPacket_FRIEND_GET_RECENT_CHARACTER_LIST_RES") -> `0x8089a0`: header, list `0x75cbd0`
  (CDataCharacterListElement). PS4 `0x2fa830` {m_RecentCharacterList}: = PS4 except the S3 trailing u8 (V).
- Walk 41/41 + 41/41; list always empty (element code-only; PS4 counter-test cannot separate, 0/41);
  sample `stream1-marked.pcapng_tcp-stream-35/12076_…16_6_2` (32 B, `6aa3bad158b8af19`) end 0x15.

## 12. 17.0.1 GET_BLACK_LIST_REQ / 17.0.2 …_RES

- REQ `0x820520` empty (V; PS4 `0x19ca940` empty). RES `0x7c6ba0` (string
  "…OnPacket_BLACK_LIST_GET_BLACK_LIST_RES") -> `0x8016c0`: header, list `0x75ebc0`. PS4 `0x2faa40`
  {m_BlackList: CDataCommunityCharacterBaseInfo}: **= PS4 (V)**.
- Walk 41/41 + 41/41; list always empty (code-only); sample `…/12079_…17_0_2` (32 B, `85caeb30232a2e7c`)
  end 0x15.

## 13. 24.6.16 JOB_MASTER target list NTC (unresolved -> exclusive, V)

- Group 24 = JOB_MASTER (V: RES strings "cSeedGameSvConnection::OnPacket_JOB_MASTER_GET_JOB_MASTER_ORDER_
  PROGRESS_RES", "…_REPORT_JOB_ORDER_PROGRESS_RES", "…_ACTIVATE_JOB_ORDER_RES"). The 24.6.16 handler has
  no string; the packet name stays the triage raw name (server lead `S2C_JOB_MASTER_MARK_TARGETS_NTC`).
- PC handler `0x7e0b70` (data in the database, decoded linearly): packet object tagged group 0x18, id 6,
  sub 0x10; `sub_76C500(packet, list)` (count + elements of 0x20 bytes, element reader `0x76c5f0`:
  `Read_u8 +8, Read_u32 +0xc, Read_u8 +0x10, Read_u8 +0x14, Read_u32 +0x18, Read_u32 +0x1c`); no header;
  if `sAreaExt::isStage` then `sub_416BB0(sArea+0x3834, list)`.
- PS4: no `nUserSession` packet or `Read_*` with this element. Nearest: `CDataActiveJobOrder` {u8
  m_ucReleaseType, u32 m_unReleaseID, u8 m_ucReleaseLv, list CDataJobOrderProgress} and
  `CDataJobOrderProgress` {u8 m_ucConditionType, u32 m_unTargetID, u32 m_unTargetRank, u32 m_unTargetNum,
  u32 m_unCurrentNum}; neither has this shape. **Exclusive (V by code: element reader `0x76c5f0` has one
  caller, the PS4 has no matching body)**. Counter-test: a list of PS4 CDataJobOrderProgress fails
  **117/150** (the 33 passes are empty lists).
- Names (I, by width parallel): the element is the head of CDataActiveJobOrder (u8 ReleaseType, u32
  ReleaseID, u8 ReleaseLv) followed by the head of CDataJobOrderProgress with TargetRank narrowed:
  (u8 ConditionType, u32 TargetID, u32 TargetRank). Captured values support it: first u8 in {1, 2}, third
  5-10, fourth always 1, last 40-80. Keep `unk_` names in patterns unless the implementer accepts the I
  basis; the server serializer `CDataJobMasterTargetData` writes the same widths (lead).
- Walk 150/150 (ps4frame fails 123/150); lists 0, 12, 35 or 45 entries; xxd
  `stream85-marked.pcapng_tcp-stream-11/100267_…24_6_16` (688 B, `6ff32729c7cccc6c`): `1800 0610 34 |
  0000 109b | 0000 002d | 01 0000 0001 07 01 0000 0083 0000 0008 | …` count 45, element 15 B, end 0x2b0.

## 14. 26.1.1 GET_MY_CHARACTER_PROFILE_REQ / 26.1.2 …_RES

- REQ `0x835960` empty (V; PS4 `0x19b08f0` empty).
- RES `0x7eec80` (string "…OnPacket_PROFILE_GET_MY_CHARACTER_PROFILE_RES") -> `0x814620`: header, list
  `0x7698c0` (CDataHistoryElement), MtString, u32, list `0x7583b0` (CDataAchieveCategoryStatus), list
  `0x7702d0` (CDataOrbPageStatus), list `0x76c270` (CDataJobOrbTreeStatus), **list `0x76c270` again**.
  PS4 `CPacket_S2C_GET_MY_CHARACTER_PROFILE_RES::ReadPacket 0x19de980` {m_HistoryElementList,
  m_wstrOnlineId, m_unAbilityCostMax, m_AchieveCategoryStatusList, m_OrbStatusList,
  m_JobOrbTreeStatusList}. **S3: + second CDataJobOrbTreeStatus list (V shape)**.
- Consumer `0x84d1f0(dst, list6, list7)` fills two 11-job tables (index 0 from list 6, index 1 from list
  7) with each element's f32 and a presence byte; the bool is not used there. Name `unk_JobOrbTreeStatusList`
  (I: a second per-job orb-tree table; server lead `JobOrbHiBOStatusList`). Same pair of lists as 8.36.16
  (`Pawn.hexpat`).
- Counter-test: PS4 body fails **4/4**. Walk 4/4 + 4/4; History 20, Achieve 5, OrbPage 4 (empty inner),
  11 + 11 job entries; list 6 has flag 0 rate 0, list 7 flag 1 rate 0 for jobs 1-11; sample
  `stream1-marked.pcapng_tcp-stream-35/26333_…26_1_2` (560 B, `f7482c818ce069c5`) end 0x230 (slack 0).

## 15. 26.12.1 SET_SHORTCUT_LIST_REQ / 26.12.2 …_RES

- REQ `0x835fa0`: `WritePacket(26, 12, 1)`, `sub_780F20` = list CDataShortCut (V). PS4
  `CPacket_C2S_SET_SHORTCUT_LIST_REQ::WritePacket 0x1a3a0b0` writes `m_ShortcutList` (count +
  `Write_CDataShortCut_`): **= PS4 (V)**. Field `ShortcutList` (V).
- RES `0x7ef2a0` (string "…OnPacket_PROFILE_SET_SHORTCUT_LIST_RES") -> `0x814b80`: header only (V, = PS4
  `0x315ee0`).
- Walk 42/42 + 42/42; list always 12; sample `…/26531_…26_12_1` (272 B, `af0e23de8759f753`) end 0x109.

## 16. 26.14.1 SET_COMMUNICATION_SHORTCUT_LIST_REQ / 26.14.2 …_RES

- REQ `0x835b00`: `WritePacket(26, 14, 1)`, `sub_77E0B0` = list CDataCommunicationShortCut (V). PS4
  `0x1a39f70` writes count + {u32, u32, u8, u8, u32} into `m_ShortcutList`: **= PS4 (V)**.
- RES `0x7eef40` (string "…OnPacket_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_RES") -> `0x814820`: header
  only (V, = PS4 `0x3161e0`).
- Walk 41/41 + 41/41; list always 40; sample `…/26532_…26_14_1` (576 B, `23cd19ab0541ffd1`) end 0x23d.

## 17. Summary

| id | name | PS4 mark | body bytes | walked capture | fits |
| --- | --- | --- | --- | --- | --- |
| 5.2.16 | S2C_USER_LIST_JOIN_NTC | V (S3 element 3 u8) | 4+var | 519 | 148/148 |
| 5.3.16 | S2C_USER_LIST_LEAVE_NTC | V | 4+4n | 30703 | 162/162 |
| 6.0.1 | C2S_PARTY_PARTY_CREATE_REQ | V | 0 | 12118 | 42/42 |
| 6.0.2 | S2C_PARTY_PARTY_CREATE_RES | V | 8+12 | 12124 | 42/42 |
| 6.8.1 | C2S_PARTY_PARTY_JOIN_REQ | V | 4 | 139009 | 1/1 |
| 6.8.2 | S2C_PARTY_PARTY_JOIN_RES | V | 8+13 | 139012 | 1/1 |
| 6.8.16 | S2C_PARTY_PARTY_JOIN_NTC | V (S3 via list element) | 8+4+var | 12121 | 43/43 |
| 6.10.1 | C2S_PARTY_PARTY_LEAVE_REQ | V | 0 | 26533 | 43/43 |
| 6.10.2 | S2C_PARTY_PARTY_LEAVE_RES | V | 8 | 26542 | 43/43 |
| 6.10.16 | S2C_PARTY_PARTY_LEAVE_NTC | V (behaviour) | 4 | 26541 | 43/43 |
| 6.15.1 | C2S_PARTY_PARTY_MEMBER_SET_VALUE_REQ | V | 2 | 121503 | 6/6 |
| 6.15.2 | S2C_PARTY_PARTY_MEMBER_SET_VALUE_RES | V | 8 | 121506 | 6/6 |
| 6.18.16 | S2C_PARTY_PARTY_INVITE_ACCEPT_NTC | V (shape + flow) | 15 | 138974 | 1/1 |
| 16.0.1 | C2S_FRIEND_GET_FRIEND_LIST_REQ | V | 0 | 12061 | 41/41 |
| 16.0.2 | S2C_FRIEND_GET_FRIEND_LIST_RES | V (S3 via list element) | 8+var | 12368 | 41/41 |
| 16.6.1 | C2S_FRIEND_GET_RECENT_CHARACTER_LIST_REQ | V | 0 | 12075 | 41/41 |
| 16.6.2 | S2C_FRIEND_GET_RECENT_CHARACTER_LIST_RES | V (always empty) | 8+4 | 12076 | 41/41 |
| 17.0.1 | C2S_BLACK_LIST_GET_BLACK_LIST_REQ | V | 0 | 12078 | 41/41 |
| 17.0.2 | S2C_BLACK_LIST_GET_BLACK_LIST_RES | V (always empty) | 8+4 | 12079 | 41/41 |
| 24.6.16 | S2C_JOB_MASTER_MARK_TARGETS_NTC (raw name) | X (exclusive) | 4+15n | 100267 | 150/150 |
| 26.1.1 | C2S_PROFILE_GET_MY_CHARACTER_PROFILE_REQ | V | 0 | 26318 | 4/4 |
| 26.1.2 | S2C_PROFILE_GET_MY_CHARACTER_PROFILE_RES | V (S3 + list) | var | 26333 | 4/4 |
| 26.12.1 | C2S_PROFILE_SET_SHORTCUT_LIST_REQ | V | 4+21n | 26531 | 42/42 |
| 26.12.2 | S2C_PROFILE_SET_SHORTCUT_LIST_RES | V | 8 | 26538 | 42/42 |
| 26.14.1 | C2S_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_REQ | V | 4+14n | 26532 | 41/41 |
| 26.14.2 | S2C_PROFILE_SET_COMMUNICATION_SHORTCUT_LIST_RES | V | 8 | 26539 | 41/41 |

Total 27 ids, 1151/1151 fit. Triage corrections: 5.2.16, 5.3.16, 6.8.16, 6.10.16, 6.18.16 unresolved ->
matched (V); 24.6.16 unresolved -> exclusive (V). `recompiled_body` "yes" for 6.8.2 holds; for 26.12.1
and 26.14.1 the recompilation writer is a `DDON_STUB`. The 16.0.2 and 16.6.2 read-seq ratios below 1.0
come from the Season 3 trailing u8 of CDataCharacterListElement.

## 18. Shared types for pattern authors

Reuse unchanged: `Packet.hexpat` (`CPacket`, `MtString`, `MtTypedArray<T>`, `CDataCommonU32`),
`Character.hexpat` (`CDataCommunityCharacterBaseInfo`, `CDataCharacterListElement`, `CDataPartyMember`,
`CDataLobbyMemberInfo`, `CDataShortCut`, `CDataCommunicationShortCut`), `Pawn.hexpat`
(`CDataOrbPageStatus`, `CDataJobOrbTreeStatus`). Framing as T003 § 18 (inline RES header; NTCs without
header).

Add to `include/Character.hexpat` (names PS4 DWARF):

| Struct | PC reader | Wire |
| --- | --- | --- |
| `CDataFriendInfo` | `0x766e20` | CDataCharacterListElement CharacterListElement, u8 PendingStatus, u32 FriendNo, bool Favorite |
| `CDataHistoryElement` | `0x7698c0` | u8 Type, u32 TargetID, u32 Param, u64 DateTime |
| `CDataAchieveCategoryStatus` | `0x7583b0` | u8 CategoryID, u16 AchieveNum, u16 TargetNum |

Update the `CDataLobbyMemberInfo` comment in `Character.hexpat`: the 3-u8 count no longer rests on the
reader alone; 5.2.16 captures reject the PS4 4-u8 element 50/148 (§ 2).

Add to `include/Job.hexpat` (new type, names I by § 13; or `unk_` names):
`CDataJobMasterTarget` (`0x76c5f0`) {u8 ReleaseType, u32 ReleaseID, u8 ReleaseLv, u8 ConditionType,
u32 TargetID, u32 TargetRank}. The struct name is not code-backed either (I).

Packet bodies (after the header): 5.2.16 `MtTypedArray<CDataLobbyMemberInfo> LobbyMemberInfoList`; 5.3.16
`MtTypedArray<CDataCommonU32> CharacterList`; 6.0.2 `u32 PartyId, u64 ContentNumber`; 6.8.1 `u32 PartyId`;
6.8.2 `u8 MemberIndex, u64 ContentNumber, u32 PartyId`; 6.8.16 `u32 LeaderCharacterID, u32
HostCharacterID, MtTypedArray<CDataPartyMember> PartyMember`; 6.10.16 `u32 CharacterID`; 6.15.1 `u8 Index,
u8 Value`; 6.18.16 `u16 ServerId, u32 PartyId, u32 StageId, u32 PositionId, u8 MemberIndex`; 16.0.2
`MtTypedArray<CDataFriendInfo> FriendInfoList, MtTypedArray<CDataCommunityCharacterBaseInfo>
ApplyingCharacterList, ApprovingCharacterList`; 16.6.2 `MtTypedArray<CDataCharacterListElement>
RecentCharacterList`; 17.0.2 `MtTypedArray<CDataCommunityCharacterBaseInfo> BlackList`; 24.6.16
`MtTypedArray<CDataJobMasterTarget> unk_TargetList`; 26.1.2 `HistoryElementList, MtString OnlineId, u32
AbilityCostMax, AchieveCategoryStatusList, OrbStatusList, JobOrbTreeStatusList,
MtTypedArray<CDataJobOrbTreeStatus> unk_JobOrbTreeStatusList`; 26.12.1 `MtTypedArray<CDataShortCut>
ShortcutList`; 26.14.1 `MtTypedArray<CDataCommunicationShortCut> ShortcutList`. Empty bodies: 6.0.1,
6.10.1, 16.0.1, 16.6.1, 17.0.1, 26.1.1 (REQ); 6.10.2, 6.15.2, 26.12.2, 26.14.2 (RES header only).

## 19. Arrowgene leads: misplacements found

Clone `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` at `88d82caf07b980c031ec7f34e668921f6f494c90`:

1. `S2CSwitchStorageNtc` declares `Id => PacketId.S2C_USER_LIST_JOIN_NTC` (5.2.16) with a body `bool
   IsStart, List<CDataSwitchStorage>`; PC 5.2.16 reads only a CDataLobbyMemberInfo list (§ 2).
   Misplacement (C): wrong packet id for that structure (the class has no other reference in the clone).
2. `CDataHistoryElement` writes `DateTime` with `WriteInt64` (PC `Read_u64`, PS4 `u64 m_ullDateTime`):
   signedness only, same bytes.
3. 16.6.2 and 17.0.2 have no structure: the handlers send canned dumps (`InGameDump.Dump_71`, `Dump_73`).
4. Agree with PC: `S2CUserListJoinNtc` / `CDataLobbyMemberInfo` (3 u8: `Unk0`, `Unk1`, `OnlineStatus`),
   `S2CUserListLeaveNtc`, `S2CPartyPartyCreateRes`, `C2SPartyPartyJoinReq`, `S2CPartyPartyJoinRes`,
   `S2CPartyPartyJoinNtc`, `S2CPartyPartyLeaveNtc`, `C2SPartyPartyMemberSetValueReq`,
   `S2CPartyPartyInviteAcceptNtc`, `S2CFriendGetFriendListRes` / `CDataFriendInfo`,
   `S2CProfileGetMyCharacterProfileRes` (incl. the second `JobOrbHiBOStatusList`),
   `CDataAchieveCategoryStatus`, `CDataJobOrbTreeStatus`, `C2SSetShortcutReq` / `CDataShortCut`,
   `C2SSetCommunicationShortcutReq` / `CDataCommunicationShortCut`, `S2CJobMasterMarkTargetsNtc` /
   `CDataJobMasterTargetData` (u8, u32, u8, u8, u32, u32).

## 20. Open items and checks not run

- Names without code backing (I): the 24.6.16 element fields and struct name (§ 13), the 26.1.2 second
  JobOrbTreeStatus list, the first u8 of CDataLobbyMemberInfo (include, unchanged), the trailing u8 of
  CDataCharacterListElement (include, unchanged).
- The 24.6.16 consumer `sub_416BB0` (on `sArea+0x3834`) was not traced; the I names rest on widths and
  value ranges.
- 6.18.16 PC consumer `sub_4096F0` was not traced (match rests on the identical read sequence and the
  capture flow).
- Counter-tests that could not separate PC from PS4 layouts (code decides): 6.8.16 element (43/43 fit
  both), 6.10.16 and 6.18.16 PS4 framing (slack), 16.6.2 (always empty).
- Code-only (never non-empty in captures): 16.0.2 Applying/Approving lists, 16.6.2 list, 17.0.2 list,
  26.1.2 OrbPage inner lists.
- ImHex not run (not on `PATH`); no pattern written (outside this package).
