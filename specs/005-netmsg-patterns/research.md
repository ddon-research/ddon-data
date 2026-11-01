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

## Capture profile (all of `packets/decrypted_raw`, 2026-11-01)

Command: `python -X utf8 -I <scratchpad>/profile.py packets/decrypted_raw` (reads the packet
header, the outer fields, then u32s of the payload; 15 s).

- Lobby (3.3.16 and 3.4.16, 80,881 packets): every payload starts `u32 2, u32 0, u32 rpc`, rpc
  2000 (40,626), 2005 (18,106), 2001 (10,033), 2006 (9,164), 2004 (2,381), 2002 (323), 1010 = sGame
  (248). Type byte 2 (`LOBBY_MSG_ALL`) except msg 0x37 with type 4 (`LOBBY_MSG_SERVER`, 1,067).
- Lobby `msgIdFull` (C2S count): 0x40010002 ACT_NORMAL 24,850; 0x40010015 PERIODIC_NORMAL 22,713;
  0x4001000d ACT_BOW 7,475; 0x40010008 1,288; 0x40010037 SERVER_DAMAGE 1,067; 0x40010025 815;
  0x4001000b 676; 0x40010024 306; 0x40010034 232; 0x41000001 GameNormal STAGE 150; then
  0x1c, 0x39, 0x0c, 0x28, 0x18, 0x17, 0x14, 0x09, 0x1e, 0x2c, 0x20, 0x13, 0x1f (< 100 each).
  The same message id has 2-4 sizes 2 bytes apart (152/154/156/158 for 0x15): variable fields.
- S2C 3.4.16 has 1-16 bytes after the payload: the 1-byte `OnlineStatus` plus block padding
  of the decrypted packet (inferred).
- Binary 6.25.16 (29,176): payload starts `00000000 8000000n` (n = 0..5; 67 start with
  `00000000 00000000`); `msgIdFull` at payload offset 12: 0x40010037 9,216; 0x02 7,706; 0x19
  2,352; 0x18 2,255; 0x15 1,841; 0x23 1,539; 0x2e 1,076; 0x28 782; 0x34 634; 0x3c 448; 0x35 441;
  0x31 333. 0x3c is beyond the PS4 enum's last id 0x3b (Season 3 addition, inferred).

## Open questions

- Q1 (answered by P1, 81 IDA calls, 12.5 min) The leading u32 is `Head.mSessionId` (2 = lobby, 0 = party binary). The
  extra u32 is Season 3 widening: captures fit only with `u64 mRpcId`, `u64 CtrlBase.mUniqueId`
  and `u64 mTargetUid` (inferred from captures; P2 checks the PC binary).
- Q2 (answered by P1) No batching: one nNetMsg per packet, the packet's `len` is the only length.
  The "several records" reading above is contradicted.
- Q3 The include-packet table and per-message decoders on PC 03040008, and every field Season 3
  added (P2).

Reports: `research/P1-ps4-wire-format.md` (PS4 decoders with VAs, include table, enums).
