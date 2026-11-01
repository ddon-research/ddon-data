# 005 research notes

## Sources

- PS4 02020005 decoder: `nNetMsgData::Head::deserialize` reads `mSessionId, mRpcId, mMsgIdFull,
  mSearchId` (4 x u32 BE). `cNetMsgCtrlAction::receiveMessage`: Head, `CtrlBase::deserialize`
  (`mUniqueId` u32), then `CtrlAction::deserialize(head, dec, isSameVer=1)`.
- `CtrlAction::deserialize` reads four bools (`mIsEnemy, mIsCharacter, mIsHuman, mIsEnemyLarge`),
  then blocks gated by `include = table[(u8)msgIdFull - 1]` (table at PS4 `0x1BECE20`, 56 u32,
  `nNetMsgData::createIncludePacketCtrl`), then a switch on the low byte of `mMsgIdFull`.
- Arrowgene: `C2SLobbyLobbyDataMsgReq` = `u8 Type, u32 CharacterId, u32 len, byte[len]`;
  `S2CLobbyLobbyDataMsgNtc` adds a trailing `u8 OnlineStatus`; `C2SPartySendBinaryMsgNtc` =
  `List<u32> CharacterIdList, u32 len, byte[len]`; `..._ALL_NTC` = `u32 len, byte[len]`.
  `RpcPacketHeader` reads `u32 Unk0, u32 Unk1, u32 RpcId, u16 Dti, u16 MsgId, u32 SearchId`.
- DDON_RE `GamePackets.md` (clone `D:/GitHub/sebastian-heinz/DDON_RE` at f282f2a): PC receive
  handlers `S2C_LOBBY_3_4_16_NTC` 0x7e2ad0, `S2C_PARTY_6_22_16_NTC` 0x7e72b0,
  `S2C_PARTY_6_24_16_NTC` 0x7e97a0, `S2C_PARTY_6_26_16_NTC` 0x7e9880 (no C2S rows).

## Captured bytes (03040008)

Lobby 3.3.16 payload (after `u8 Type=2, u32 CharacterId=0, u32 len=0x9a`):
`00000002 00000000 000007d0 40010015 00000000 80000000 00000001 | 00 01 01 00 | f64 -162.35 f32 12338.7 f64 159.2 ...`
Read as `u32 ?=2`, Head `{session 0, rpc 0x7d0, msgIdFull 0x40010015, search 0}`, then two u32
before the four bools: one more than PS4's single `mUniqueId` (open question Q1).

Binary 6.25.16 payload (after empty `CharacterIdList`, `u32 len=0x8b`):
`00000000 80000000 28112a5a 4001 0002 | 00000000 80000000 28111ea2 01 0100 ...`: not a single
Head; framing open (Q2).

## Open questions

- Q1 What precedes the Head in the lobby payload, and what is the extra u32 before the CtrlAction
  bools on PC?
- Q2 The binary-message framing (record list, per-record header) on send and receive.
- Q3 The include-packet table and per-message decoders on PC 03040008, and every field Season 3
  added.
