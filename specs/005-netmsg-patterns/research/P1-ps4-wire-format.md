# P1: PS4 02020005 wire format of the nNetMsg payloads

Brief: `specs/005-netmsg-patterns/briefs/P1-ps4-wire-format.md`. Base a9a2f2dea48.

- Build: PS4_02020005 (seed, symbols). Database: private copy
  `D:/research/DDON-binaries/IDA9.5/PS4_DDON_02020005_2016_12_21/ddon-data-p1/DDOORBIS.elf.i64`
  (made with `bash research/ida/private-copy.sh ps4 p1`). `idc.get_idb_path()` returned that path;
  64-bit, image base `0x0`, processor metapc. Queried read-only through ida-mcp `execute_python`
  (Hex-Rays pseudocode, local types, enums, `ida_bytes`). No renames, comments or saves.
- Address basis: IDA VA in that database (= ELF VA, image base 0).
- Captures (Season 3, client 03040008, read with `xxd` and a byte walker in the IDA Python
  session): see section 5 for paths and SHA-256 prefixes.
- Status labels: **V** = verified (read in IDA, PS4); **I** = inferred; **C** = contradicted;
  **PC-cap** = observed in 03040008 captures only (PC binary not opened in this task).

All multi-byte integers and floats are big-endian (`nNetwork::Decoder::readU32` @ `0x11960b0`
reads 4 bytes and calls `MtNetByteOrder::netToHost32`) **V**. A `u8`/`bool` field is read
inline as a 1-byte `MtStream::read` (vtable slot 13) **V**. Every read is skipped once the decoder
is drained (`mIsDrain`), so a short buffer zero-fills the tail instead of failing **V**.

## 1. Framing

### 1.1 Send path (PS4) — one nNetMsg per packet

| Step | Function (VA) | What it does | Status |
| --- | --- | --- | --- |
| 1 | `nNetBase::cNetCtrl::sendNetMessage` `0x2dc3c0` (also `cNetGame` `0x2dc8f0`, `cNetSet` `0x3927a0`, `cNetTool` `0x3933c0`) | `createNetMsg(netMsgId)`; 1024-byte `MtMemoryStream` + `nNetwork::Coder`; fills `stMsgHead {mSessionId = msg->mSessionInstanceIndex, mRpcId = this->mRpcId, mMsgIdFull = netMsgId, mSearchId = pawnId if human type 1 else 0}`; `Head::serialize`; then the class `sendMessage` (vtable +9) appends the body to the same stream; `castMsgAddress` | V (cNetCtrl); I (other three, same callee set) |
| 2 | `nNetMsgData::Head::serialize` `0x172890` | `writeU32` x4: mSessionId, mRpcId, mMsgIdFull, mSearchId | V |
| 3 | `nNetMsg::cNetMsgBase::createNetMsg` `0x382df0` | `MtDTI::from(msgIdFull & 0xFFFFFF00)`; sets `mMsgGroup = msgIdFull>>24`, `mMsgId = (u8)msgIdFull`; `mSessionInstanceIndex = 2` if group 0x40 and the sender's RpcId is a player RPC id, or if group 0x41 / sub 0 / msgId 1 (GameNormal STAGE); otherwise 0 | V |
| 4 | `nNetBase::cNetBase::castMsgAddress` `0x2dbfb0` | MSG_ADR → `sRemoteProcedureExt::sendNetwork(msg, sendMemberType, charId, prio, rpcId)`: ALL `0x20000` (+ local echo), OTHER `0x30000`, PEER `0` (charId), SERVER `0x40000` (prio LOW); LOCAL only `sendLocal` | V |
| 5 | `sRemoteProcedureExt::sendNetwork` `0x8309f0` | `data = msg->mpStream->getBuffer()` (MtMemoryStream vtable 23), `size = getPosition()` (vtable 10), `sessionId = msg->mSessionInstanceIndex`; calls `cNetSessionManager::sendRpc` | V |
| 6 | `nSessionManager::cNetSessionManager::sendRpc` `0x392400` | sessionId 2 → `cNetGameServer::sendLobbyMessage(msgType=1, …)`; sessionId 0 → `cNetGameServer::sendBinary`; any other value is dropped | V |
| 7a | `cNetGameServer::sendLobbyMessage` `0x343c30` | msgType 1: payload = the RPC buffer verbatim; else payload = `cLobbyDataMessage::serialize` (BitWriter: s32 0, s32 mMsgType). Type byte: `(smt & ~0x10000) == 0x20000` → 2 (ALL/OTHER); `smt == 0x40000` → 4 (SERVER); else 0 with CharacterId = target. Max 0x400 bytes. `Send_C2S_LOBBY_DATA_MSG_REQ` `0x19b1150` | V |
| 7b | `cNetGameServer::sendBinary` `0x346910` | size ≤ 0x400. `0x40000` SERVER → `Send_C2S_SEND_BINARY_MSG_NOTICE` (`0x19b3560`) with an **empty** CharacterIdList; `0x30000` OTHER → NOTICE with every party member except self whose state byte == 1; `0x20000` ALL → `Send_C2S_SEND_BINARY_MSG_ALL_NOTICE` (`0x19b33f0`); otherwise (PEER) → NOTICE with `[characterId]` when non-zero | V |

Packet bodies (PS4 `WritePacket`/`ReadPacket`; the PS4 packet ids differ from the PC 3.3.16
numbering, the field order is what matters) **V**:

| Packet | Function (VA) | Body after the packet header |
| --- | --- | --- |
| C2S_LOBBY_DATA_MSG_REQ (PC 3.3.16) | `CPacket_C2S_LOBBY_DATA_MSG_REQ::WritePacket` `0x1a3a4c0` | u8 Type, u32 CharacterID, s32 len, u8[len] Data |
| S2C_LOBBY_DATA_MSG_NOTICE (PC 3.4.16) | `CPacket_S2C_LOBBY_DATA_MSG_NOTICE::ReadPacket` `0x19d4b40` | u8 Type, u32 CharacterID, s32 len, u8[len] Data, u8 OnlineStatus |
| C2S_SEND_BINARY_MSG_NOTICE (PC 6.25.16) | `…_C2S_SEND_BINARY_MSG_NOTICE::WritePacket` `0x1a39a70` | u32 count, u32 CharacterId[count], s32 len, u8[len] Data |
| C2S_SEND_BINARY_MSG_ALL_NOTICE (PC 6.23.16) | `…_ALL_NOTICE::WritePacket` `0x1a39ba0` | s32 len, u8[len] Data |
| S2C_RECV_BINARY_MSG_NOTICE / _ALL_NOTICE | `ReadPacket` `0x19d5290` / `0x19d5190` | u32 CharacterID, s32 len, u8[len] Data, u8 OnlineStatus |

### 1.2 Receive path (PS4)

| Function (VA) | What it does | Status |
| --- | --- | --- |
| `cSeedGameSvConnection::OnPacket_S2C_LOBBY_DATA_MSG_NOTICE` `0x2df220` | ReadPacket; `cLobbyDataMessage::deserialize` (`0x392490`) on a BitReader over Data: `s32 a`; if a == 0 then `mMsgType = s32` else `mMsgType = LOBBY_MSG_TYPE_RPC (1)`. If mMsgType == 1: `sRemoteProcedureExt::receiveNetwork(sessionId=1, CharacterID, Data, len)` with the **whole** Data from offset 0. Then sets OnlineStatus. | V |
| `OnPacket_S2C_RECV_BINARY_MSG_NOTICE` `0x2f2a70`, `…_ALL_NOTICE` `0x2f2950` | ReadPacket; `receiveNetwork(sessionId=0, CharacterID, Data, len)`; OnlineStatus | V |
| `sRemoteProcedureExt::receiveNetwork` `0x8306e0` | `Head::deserialize` (`0x172920`, 4 x readU32); requires `mSessionId != 0` or session 0 online; `createNetMsg(mMsgIdFull)`; dispatches to the RPC object (`cRemoteProcedure` vtable +8 → the class `receiveMessage`) found by RpcId; if no object and group 0x40, decodes inline: `Base::deserialize`, `CtrlBase::deserialize`, `CtrlAction::deserialize(head, dec, true)` | V |
| `BitReader::readS32` `0x38d080` | not Elias-delta here (`mIsEliasDelta = false`): 4 bytes, byte-swapped (BE) | V |

`cLobbyDataMessage` (`LOBBY_MSG_TYPE_DUMMY = 0`, `LOBBY_MSG_TYPE_RPC = 1`) **V**: a non-RPC lobby
payload is exactly `00000000 <s32 mMsgType>`; an RPC payload is a Head whose first u32
(`mSessionId`) is 2, so it is non-zero and selects RPC.

### 1.3 Answers to the framing questions

- **The leading `u32 2` of the 3.3.16 payload is `Head.mSessionId`** (= `mSessionInstanceIndex`,
  2 = lobby session; `createNetMsg` + `sendRpc` + `cNetCtrl::sendNetMessage`) **V** on PS4,
  consistent with every 03040008 lobby capture walked (section 5) **PC-cap**. It is not a prefix
  before the Head. On the party binary path the same field is 0 **V**/**PC-cap**.
- **No batching.** One `cNetMsg` is serialized into one stream and handed to one
  `sendRpc` call; one Head is parsed per received Data block; there is no record count or
  per-record length. The packet's `len` is the only length **V**. The 03040008 6.25.16 sample
  that looked like several records is a single message whose RpcId and UniqueId are u64 values
  with high word `0x80000000` (section 5.2) **PC-cap**; research.md Q2's "several records"
  reading is **C**.
- **Message layout** (PS4) **V**: `Head (16 B) | <group base> | <group body>`, where
  `nNetMsgData::Base::deserialize` (`0x1729e0`) reads nothing, `CtrlBase` reads u32 mUniqueId,
  and `GameBase` (`0x1757a0`), `SetBase` (`0x176a70`), `ToolBase` (`0x177cd0`) and
  `ToolNormal` (`0x177d30`) read nothing.

Per class `receiveMessage` (all call `cNetMsgBase::receiveMessageCore` `0x382f40` first, which
only calls `Base::deserialize`) **V**:

| Class (VA of receiveMessage) | Decoders in order |
| --- | --- |
| cNetMsgCtrlAction `0x386810` | CtrlBase, CtrlAction(isSameVer=1) |
| cNetMsgGameNormal `0x38a2b0` | GameBase, GameNormal |
| cNetMsgGameEasy `0x38af50` | GameBase, GameEasy |
| cNetMsgSetNormal `0x38b750` | SetBase, SetNormal |
| cNetMsgToolNormal `0x38bb50` | ToolBase, ToolNormal |
| cNetMsgToolEasy `0x38bcd0` | ToolBase, ToolEasy |

### 1.4 Season 3 differences seen in captures (PC 03040008, not checked in the PC binary)

| Field | PS4 02020005 (V) | 03040008 captures (PC-cap) |
| --- | --- | --- |
| Head | s32 mSessionId, u32 mRpcId, u32 mMsgIdFull, u32 mSearchId (16 B) | s32 mSessionId, **u64 mRpcId**, u32 mMsgIdFull, u32 mSearchId (20 B) |
| CtrlBase.mUniqueId | u32 | **u64** |
| CtrlAction TARGET block mTargetUid | u32 | **u64** |

The PC widening is **I** (it is the only reading that makes all four walked captures end
exactly at `len`); this explains the "extra u32 before the bools" (Q1) and Arrowgene's
`u32 Unk0, u32 Unk1, u32 RpcId` (= session, RpcId high, RpcId low). Other unique-id fields
(mClimbEnemyUId, mAtkUID, mCatchRequestUid, mStickUniqueId, SetNormal mUniqueId, …) are not
exercised by the samples and may also be u64 on PC: **not checked**.

## 2. Decoders (PS4, read order)

Notation: `NetPos` = `nNetMsgData::popNetPos` `0x172530`: **f64 x, f32 y, f64 z** (20 B; each
value NaN/Inf → 0, clamped to ±1e10). `NormalPos` = `popNormalPos` `0x1726e0`: f32 x, y, z
(12 B). `Vec3f` = three inline f32 (NaN/Inf → 0). All V unless marked.

### 2.1 Head — `Head::deserialize` `0x172920` / `deserializeCore` `0x1728d0`

| # | Type | Field |
| --- | --- | --- |
| 1 | s32 | mSessionId (0 = party/binary, 2 = lobby on send; receiver overrides the local index to 1 for lobby, 0 for binary) |
| 2 | u32 | mRpcId |
| 3 | u32 | mMsgIdFull = `group<<24 | sub<<16 | 0x00<<8 | msgId` (byte 1 must be 0 for the DTI lookup) |
| 4 | u32 | mSearchId (pawn id when the sender context is human type 1, else 0) |

### 2.2 CtrlBase — `CtrlBase::deserialize` `0x172a40`

| # | Type | Field |
| --- | --- | --- |
| 1 | u32 | mUniqueId (PC-cap: u64) |

### 2.3 CtrlAction — `CtrlAction::deserialize` `0x172ac0`

`inc = table[(u8)mMsgIdFull - 1]` if that index ≤ 0x37, else 0 (section 3). `isSameVer` is in
the signature but **never used** in the body (one occurrence in the pseudocode, the
prototype) **V**.

| # | Condition | Type | Field / helper |
| --- | --- | --- | --- |
| 1 | always | bool(u8) | mIsEnemy |
| 2 | always | bool | mIsCharacter |
| 3 | always | bool | mIsHuman |
| 4 | always | bool | mIsEnemyLarge |
| 5 | inc & 0x1 BASE | | popPos (2.4), then f32 mAngleY |
| 6 | inc & 0x8 ACTION | | popActionNo (2.5) |
| 7 | inc & 0x20 CONDITION | | receivePktCondition (2.6) |
| 8 | inc & 0x400 CLIFF_HANG | | receivePktCliffHang (2.7) |
| 9 | inc & 0x800 ENEMY_CLIMB | | receivePktEnemyClimb (2.8) |
| 10 | inc & 0x1000 TARGET | u32 + NetPos | mTargetUid (PC-cap: u64), mTargetPos |
| 11 | inc & 0x2000 SHL_DELETE | u32 | mShlDelFlag |
| 12 | inc & 0x4000 SHL_SHOT | | receivePktShlShot (2.9) |
| 13 | mIsHuman && inc & 0x8000 KILLAREA | 3 x u32 | mEncountArea[0..2] (s32) |
| 14 | mIsHuman && inc & 0x800000 SAFE_POS | NetPos | mSafePos |
| 15 | inc & 0x10000 ENEMYSTATUS_CTRL | | receiveMsgEnemyStatusCtrl (2.10) |
| 16 | inc & 0x100000 ENEMYWAITTING | bool | mEnemyWaitting |
| 17 | inc & 0x200000 ENEMYSTARTWAIT | bool | mEnemyStartWait |
| 18 | inc & 0x400000 CORE_POINT | u16, u16 | mRegionCorePointID, mActiveTimer |
| 19 | inc & 0x80000 DAMAGE_ACT | u64 | mAttackParamUIDForDmVec |
| 20 | inc & 0x20000 WALL_CLIMB | | receiveMsgWallClimb (2.11) |
| 21 | inc & 0x40000 STATE_LIVE | u32 (+ popPos if value == 513) | mStateLive |
| 22 | switch (u8)mMsgIdFull | | see table below |

Bits 0x2, 0x4, 0x10, 0x40, 0x80, 0x100, 0x200 are never tested by this decoder (nor by
`cNetMsgCtrlAction::sendMessage` `0x383410`) **V**.

Send/receive order mismatch **V**: `sendMessage` writes DAMAGE_ACT (u64) *before* CORE_POINT
(u16,u16), the decoder reads CORE_POINT first. No include-table entry sets both 0x80000 and
0x400000 (section 3), so the mismatch is latent.

Switch on the low byte (only when > 0x1D, or == 0x0D):

| msgId | Name | Reads |
| --- | --- | --- |
| 0x0D | ACT_BOW | receiveMsgActBow (2.12) |
| 0x1E, 0x38 | CATCH_REQUEST, ACT_CATCH | receiveMsgCatchRequest (2.13) |
| 0x1F, 0x20 | CAUGHT_RESULT, ACT_CAUGHT | u8 mCatchInfo.mCatchType, u32 mCatchInfo.mCatchUid, u8 mCatchInfo.mJointNo |
| 0x21, 0x22 | OM_PUT, OM_THROW | receiveMsgOmRelease (2.14) |
| 0x25 | STICK_SHL | receiveMsgShlStickParam (2.15) |
| 0x27 | SHL_KILL_SYNC | u8 mShlKillSync |
| 0x2B | SLAVE_DAMAGE | receiveMsgSlaveDamage (2.16) |
| 0x32 | CORE_POINT_SLAVE | u16 mRegionCorePointID_Slave, u16 mActiveTimer_Slave |
| 0x33 | OCD_HOLY_ABSORP | u32 mHolyAbsorpAtkUID, u16 mHolyAbsorpHealVal |
| 0x35 | MASTER_PARAM | receiveMsgMasterParam (2.17) |
| 0x36 | CUSTOM_SYNC | receiveMsgCustomSkillSync (2.18) |
| 0x37 | SERVER_DAMAGE | receiveMsgSlaveDamageSv (2.19) |
| 0x39 | CS_CHANGE | u8 mCustomSkillGroup |
| 0x3A | SOUL_ABSORP | u32 mSoulAbsorpAtkUID, u16 mSoulAbsorpHealVal |
| 0x3B | SHL_REQUEST_FROM_SLAVE | receiveMsgShlRequestFromSlave (2.20) |
| other | | nothing |

### 2.4 popPos `0x1755b0`
NetPos mPos, f32 mMoveSpeed, f32 mMoveAngle.

### 2.5 popActionNo `0x1756b0`
u32 mActNo, u8 mActReqPrio, u16 mActAtkAdjustUniqueId, u32 mActFreeWork.

### 2.6 receivePktCondition `0x173280`

| # | Condition | Type | Field |
| --- | --- | --- | --- |
| 1a | !mIsEnemyLarge && !mIsEnemy && !mIsHuman | u16 | mHp |
| 1b | !mIsEnemyLarge && !mIsEnemy && mIsHuman | u16, u16, u32 | mHp, mHpWhite, mStamina |
| 1c | mIsEnemy or mIsEnemyLarge | u32 | mHp |
| 2 | always | u16 | mUseRegionBit |
| 3 | n = popcount(mUseRegionBit & 0x3FE) (bits 1..9): n < 5 → u16; 5 ≤ n < 9 → u32; n == 9 → u64 | u16/u32/u64 | mRegionRateBit (**width depends on a previous field**) |
| 4 | always | u16, u16 | mCommonWork, mCustomWork |
| 5 | mIsCharacter | u32 | mOcdActiveMsgNum (clamped to 75) |
| 6 | mIsCharacter, x count | u8 a, u8 b | **bit-packed**: a → mBank = a>>5 (7 → 6), mIndex = a & 0x1F; b → mActiveLv = b>>4, mImmuneLv = b & 0xF |
| 7 | always | f32, f32 | mEnchantRate, mAilmentDamage |
| 8 | mIsEnemy | f32, f32 | mShakeEndurance, mRageShrinkEndurance |

### 2.7 receivePktCliffHang `0x1737c0`
NetPos mCliffPos, Vec3f mCliffNormal, NetPos mCliffStartPos, NetPos mCliffStartOldPos.

### 2.8 receivePktEnemyClimb `0x173950`
u32 mClimbEnemyUId, u32 mJointNo, NormalPos mJointOffset, u16 mNodeIndex, u16 mGeomIndex.

### 2.9 receivePktShlShot `0x173a00`
u8 mReceiveNum (clamped to 8), then per shot (`stShlShot`, 80 B in memory):

| # | Condition | Type | Field |
| --- | --- | --- | --- |
| 1 | | u8 | mIndex (clamped to 8) |
| 2 | | u32 | mShlStatus |
| 3 | | u8, u8 | mShlGroup, mShlIndex |
| 4 | mShlStatus & 0x40 | u32 | mUid |
| 5 | mShlStatus & 0x1 | NetPos | mPos |
| 6 | mShlStatus & 0x2 | NetPos | mTargetPos |
| 7 | mShlStatus & 0x4 | u32 | mId |
| 8 | mShlStatus & 0x8 | Vec3f | mDir |
| 9 | mShlStatus & 0x100 | u8 | mShlLockOnId |

### 2.10 receiveMsgEnemyStatusCtrl `0x173ea0`
u32 mEnemyStatusGroupNoNum (≥ 16 → 0, nothing more read in the loop); per entry u32
mEnemyStatusGroupNo[i], u32 mEnemyStatusSubGroupNo[i]; then u64 mEnemyBitCtrlCollision, u8
mEnemyCtrlRegionSelectNo, u64 mEnemyBitCtrlParts, u64 mEnemyBitCtrlWorkRate, u64
mEnemyBitCtrlScale, u64 mEnemyBitCtrlMontage, u32 mEnemyBitCtrlSyncBit.

### 2.11 receiveMsgWallClimb `0x1740c0`
NetPos mWallClimbPos, Vec3f mWallClimbNormal, NetPos mWallClimbLandPos.

### 2.12 receiveMsgActBow `0x174570`

| # | Condition (f = mBowNetUpdateFlag) | Type | Field |
| --- | --- | --- | --- |
| 1 | | u32 | mBowNetUpdateFlag |
| 2 | f & 1 | u8 x5 | Up.mType, Up.mActNo (clamped 6), Up.mSkillType, Up.mBowNetBit, mBowArrowType |
| 3 | f & 1 && f & 0x10 | u8 n, then n x (u32, u32) | Up.mShlShotNum; Up.mTargetUId[i], Up.mLockOnId[i] (no clamp) |
| 4 | f & 1 && f & 0x20 | u8 | Up.mArrowNum (sets mIsArrowNum) |
| 5 | f & 2 | u8 x4 | Low.mType, Low.mActNo (clamped 7), Low.mSkillType, Low.mBowNetBit |
| 6 | f & 2 && f & 0x20 | u8 | Low.mArrowNum |
| 7 | (f & 0x24) == 0x24 | u8 | Up.mArrowNum (again) |
| 8 | f & 8 | NetPos | mBowNetAimPos |

### 2.13 receiveMsgCatchRequest `0x174470`
u32 mCatchRequestUid, u8 mCatchRequestType, u8 mCatchJointNo, NormalPos mCatchHitPos.

### 2.14 receiveMsgOmRelease `0x174bc0` (msgId passed in)
NetPos mOmReleasePos, f32 mOmReleaseAngle; if msgId == 0x22 (OM_THROW): f32 mOmReleaseQuatW,
QuatX, QuatY, QuatZ.

### 2.15 receiveMsgShlStickParam `0x174e00`
u8 mStickCreateControl; if == 1: u32 mStickShlUniqueId; u32 mStickUniqueId, u8 mStickJointNo,
u8 mStickShlGroup, u8 mStickShlIndex, NormalPos mStickJointOffset, Vec3f mStickDirection.

### 2.16 receiveMsgSlaveDamage `0x174250`
u32 mAtkUID, u64 mAtkParamUID, u64 mdfdNodeUID, u16 mAtkAdjustUniqueId, Vec3f mDamageDir, u32
mAttackAttr; if (mAtkUID & 7) == 6: u32 mShlOwnerUID.

### 2.17 receiveMsgMasterParam `0x174a30`
u16 mUseRegionBit; for i in 0..8 where bit (i+1) of mUseRegionBit is set: mRegionHp[i] =
u32 if mIsEnemyLarge or mIsEnemy, else u16.

### 2.18 receiveMsgCustomSkillSync `0x1750d0`
2 iterations j = 0, 1, each 8 x u8: mCustom1[j], mCustom2[j], mCustom3[j], mCustom4[j],
mCustom1Lv[j], mCustom2Lv[j], mCustom3Lv[j], mCustom4Lv[j] (interleaved per j; resolved from
the struct offsets 1306..1321, the pseudocode indexes from -2) **V**.

### 2.19 receiveMsgSlaveDamageSv `0x175330`
u32 mAtkUID, u64 mAtkParamUID, u64 mdfdNodeUID, u16 mAtkAdjustUniqueId, u32 mAttackAttr; if
(mAtkUID & 7) == 6: u32 mShlOwnerUID. (No mDamageDir, unlike 2.16.)

### 2.20 receiveMsgShlRequestFromSlave `0x175410`
u32 mShlRequestShlOwnerUID, u32 mShlRequestTargetUID, u32 mShlRequestShotSys, u8
mShlRequestShotGroup, u8 mShlRequestShotIndex, u8 mShlRequestLockOnIndex.

### 2.21 GameBase `0x1757a0`: reads nothing.

### 2.22 GameNormal `0x175800` (switch on (u8)mMsgIdFull)

| msgId | Name | Reads |
| --- | --- | --- |
| 1 | STAGE | s32 mStageNo, s32 mStartPosNo |
| 2 | REVIVE_STOCK | u8 mReviveStock |
| 4 | FLAG | s32 mFlagNum; mFlagNum x u32 mFlag |
| 7 | PAWN_MSG | receiveMsgGamePawnMessage `0x175b70`: u32 mPawnMsgNum; per entry u32 mMemberIndex, u32 mMsgNo |
| 0xA | SET_EM_DIE | receiveMsgGameSetEmDie `0x175c60`: u32 mEmDieNum; per entry u16 mArea, u16 mGroup, u16 mSetNo, u16 mCount, u16 mEmId (entry discarded but consumed if mArea > 998, mGroup > 511, mSetNo > 31 or mEmId > 998) |
| 0xB | OPEN_DOOR | u32 mDoorNum; mDoorNum x u32 mUid |
| 0xC | FREEMARKER | receiveMsgGameFreeMarker `0x175e60`: u32 mFreeMarkerNum; per entry f32 mPosX, f32 mPosY, f32 mPosZ, s32 mStageNo, s32 mGroupNo, u8 mUpdateIndex |
| 0xE | PAWN_ORDER | u32 mPawnOrderMemberIndex, u32 mPawnOrderNo |
| other (3, 5, 6, 8, 9, 0xD) | | nothing |

No count is clamped in GameNormal **V**.

### 2.23 GameEasy `0x1761c0`

| # | Condition | Reads |
| --- | --- | --- |
| 1 | always | u8 mType |
| 2 | msgId 0x11 PRT_SET | receiveMsgGameEasyPRTSet `0x1763c0`: u32 mPRTNum (clamped 30); per entry u32 mSetMember, u16 mStageNo, u16 mQuestNo, u8 mBlockNo, u8 mProcessNo, f32, f32, f32, f32 (mPos.x/y/z, mScale: order **I**, the pseudocode routes the four floats through sanitising temporaries) |
| 3 | 0x12 PRT_INFO | receiveMsgGameEasyPRTInfo `0x1767d0`: u32 mPRTUniqueId, bool mIsFinalAnswer, bool mIsCancel, bool mIsAdvance, bool mIsReady, bool mIsReadyOK |
| 4 | 0x13 AREA_RELEASE | receiveMsgGameEasyAreaRelease `0x176950`: u32 mAreaReleaseIdNum (clamped 200); n x u32 |
| 5 | 0x14 EVENT | u32 mReadyBit, u32 mCancelBit, u32 mFinishBit |
| 6 | 0x15 NPC_MESSAGE | u32 mEventMsgType, u32 mEventQstNo, u32 mEventMsgGrpNo |
| | other (0x10, 0x16) | nothing beyond mType |

### 2.24 SetBase `0x176a70`: reads nothing.

### 2.25 SetNormal `0x176ad0`

| msgId | Name | Reads |
| --- | --- | --- |
| 2 | REQUEST_MASTER | s32 mRequestNum; n x u32 mUniqueId |
| 3 | CHANGE_MASTER | receiveMsgSetChangeMaster `0x176cf0`: s32 mChangeNum; per entry u32 mUniqueId, s32 mMasterIndex |
| 4 | RELEASE_MASTER | s32 mReleaseNum; n x u32 mUniqueId |
| 5 | MASTER_INFO | receiveMsgSetMasterInfo `0x176df0`: s32 mInfoNum; per entry u32 mUniqueId, s32 mMasterIndex; then bool mTerminateFlag |
| 6 | THROW_MASTER | u32 mThrowUniqueId, s32 mThrowIndex |
| 7 | REQUEST_CREATE_CONTEXT | receiveMsgSetRequestCreateContext `0x176f40`: s32 n; per entry u32 mId, u32 mUniqueId, s32 mStageNo, s32 mEncountArea |
| 8 | CREATE_CONTEXT | receiveMsgSetCreateContext `0x177060` (below) |

receiveMsgSetCreateContext, into `mCreateContextInfo` (`stCreateContext`):

| # | Condition | Type | Field |
| --- | --- | --- | --- |
| 1 | | u32, u32, s32, s32 | mId, mUniqueId, mStageNo, mEncountArea |
| 2 | | bool | mAdditionalData |
| 3 | !mAdditionalData | s32 | mMasterIndex |
| 4 | | NetPos, f32, f32, f32 | mPos, mMoveSpeed, mMoveAngle, mAngleY |
| 5 | | u32, u8, u16, u32 | mActNo, mActReqPrio, mActAtkAdjustUniqueId, mActFreeWork |
| 6 | | 10 x u64 | mHp[0..9] (HP_DATATYPE is 8 bytes here) |
| 7 | | u16, u64, u16, u16 | mUseRegionBit, mHpWhite, mCommonWork, mCustomWork |
| 8 | | u32 (clamp 75), n x (u8, u8) | mOcdActiveMsgNum, mOcdActiveMsgArray (same bit packing as 2.6) |
| 9 | | f32, f32 | mEnchantRate, mAilmentDamage |
| 10 | | NetPos, Vec3f, NetPos, NetPos | mCliffPos, mCliffNormal, mCliffStartPos, mCliffStartOldPos |
| 11 | | u32, u32, NormalPos, u16, u16 | mClimbEnemyUId, mJointNo, mJointOffset, mNodeIndex, mGeomIndex |
| 12 | | u32, NetPos | mTargetUid, mTargetPos |
| 13 | | 3 x u32 | mEncountAreaBuff[0..2] |
| 14 | | u32 (≥ 16 → 0), n x (u32, u32) | mEnemyStatusGroupNoNum, GroupNo[i], SubGroupNo[i] |
| 15 | | u64, u8, u64, u64, u64, u64, u32, u64 | mEnemyBitCtrlCollision, mEnemyCtrlRegionSelectNo, mEnemyBitCtrlParts, …WorkRate, …Scale, …Montage, mEnemyBitCtrlSyncBit, mAttackParamUIDForDmVec |
| 16 | | NetPos, Vec3f, NetPos | mWallClimbPos, mWallClimbNormal, mWallClimbLandPos |
| 17 | | u32, u8, u8, u32 | mStateLive, mCatchType, mCatchJointNo, mCatchTargetUID |

The CREATE_CONTEXT body is unconditional (no include bits); the struct fields
mShakeEndurance, mRageShrinkEndurance, mEnemyWaitting, mEnemyStartWait, mRegionCorePointID and
mActiveTimer are **not** read **V**.

### 2.26 ToolBase `0x177cd0`, ToolNormal `0x177d30`: read nothing.

### 2.27 ToolEasy `0x177d90`

| msgId | Name | Reads |
| --- | --- | --- |
| 4 | DIP | u8[448] mDipData (one raw read) |
| 5 | DAMAGE_PROFILE_START | receiveMsgDamageProfileStart `0x177ea0`: u32 mDpsHandle, u32 mProfileTargetID, 8 x u32 mProfileAttckerID |
| 6 | DAMAGE_PROFILE_END | u32 mDpsHandle |
| 7 | DAMAGE_PROFILE_NODE | receiveMsgDamageProfileNode `0x177ff0`: u32 mDpsHandle, u32 mProfileTargetUID, u32 mProfileAttackerUID, u8 mProfileUnitState, u8 mProfileRegionNo_HP, u8 mProfileRegionNo_SH, u64 mProfileDamage, f32 mProfileShrink, f32 mProfileBlow, f32 mProfileShake, f32 mProfileDown, bool mProfileIsShrink, bool mProfileIsBlow, bool mProfileIsShake, bool mProfileIsDown, bool mProfileIsToMain |
| other (3, 8) | | nothing |

## 3. Include-packet table (PS4 `0x1BECE20`, 56 x u32, index = msgId − 1) **V**

Read by `nNetMsgData::createIncludePacketCtrl` `0x172500` (`msgId − 1 > 0x37` → 0) and inline in
`CtrlAction::deserialize`. Bit names from enum `nNetMsgData::nCtrl::INCLUDE_PACKET` (DWARF/local
type): BASE 0x1, POS 0x2, ANGLE_Y 0x4, ACTION 0x8, ACTION_EX 0x10, CONDITION 0x20, PL_INTERFACE
0x40, PERIODIC_CATCH 0x80, PERIODIC_MOVE 0x100, PERIODIC_TARGET 0x200, CLIFF_HANG 0x400,
ENEMY_CLIMB 0x800, TARGET 0x1000, SHL_DELETE 0x2000, SHL_SHOT 0x4000, KILLAREA 0x8000,
ENEMYSTATUS_CTRL 0x10000, WALL_CLIMB 0x20000, STATE_LIVE 0x40000, DAMAGE_ACT 0x80000,
ENEMYWAITTING 0x100000, ENEMYSTARTWAIT 0x200000, CORE_POINT 0x400000, SAFE_POS 0x800000,
FREE 0x80000000.

| idx | msgId | NET_MSG_ID | value | bits |
| --- | --- | --- | --- | --- |
| 0 | 0x01 | ACT_BASE | 0x801021 | BASE CONDITION TARGET SAFE_POS |
| 1 | 0x02 | ACT_NORMAL | 0x801029 | BASE ACTION CONDITION TARGET SAFE_POS |
| 2 | 0x03 | ACT_NORMAL_EX | 0x001031 | BASE ACTION_EX CONDITION TARGET |
| 3 | 0x04 | ACT_RESET | 0x801029 | BASE ACTION CONDITION TARGET SAFE_POS |
| 4 | 0x05 | ACT_RESET_EX | 0x001031 | BASE ACTION_EX CONDITION TARGET |
| 5 | 0x06 | ACT_ACTION_ONLY | 0x001028 | ACTION CONDITION TARGET |
| 6 | 0x07 | ACT_ACTION_ONLY_EX | 0x001030 | ACTION_EX CONDITION TARGET |
| 7 | 0x08 | ACT_SHL_SHOT | 0x005029 | BASE ACTION CONDITION TARGET SHL_SHOT |
| 8 | 0x09 | ACT_TARGET | 0x001029 | BASE ACTION CONDITION TARGET |
| 9 | 0x0A | ACT_DIE | 0x801029 | BASE ACTION CONDITION TARGET SAFE_POS |
| 10 | 0x0B | ACT_ENEMY_CLIMB | 0x000829 | BASE ACTION CONDITION ENEMY_CLIMB |
| 11 | 0x0C | ACT_CLIFF_HANG | 0x000429 | BASE ACTION CONDITION CLIFF_HANG |
| 12 | 0x0D | ACT_BOW | 0x000000 | - |
| 13 | 0x0E | ACT_REVIVE_CMC | 0x000000 | - |
| 14 | 0x0F | ACT_WAND_MAGIC_SHL_SET | 0x000000 | - |
| 15 | 0x10 | ACT_MAGIC_ITEM | 0x000001 | BASE |
| 16 | 0x11 | ACT_THROW_ITEM | 0x000001 | BASE |
| 17 | 0x12 | ACT_LIFT_BIGIN_ITEM | 0x000000 | - |
| 18 | 0x13 | ACT_RESPAWN | 0x801029 | BASE ACTION CONDITION TARGET SAFE_POS |
| 19 | 0x14 | ACT_WALL_CLIMB | 0x020029 | BASE ACTION CONDITION WALL_CLIMB |
| 20 | 0x15 | PERIODIC_TOP / PERIODIC_NORMAL | 0x809021 | BASE CONDITION TARGET KILLAREA SAFE_POS |
| 21 | 0x16 | PERIODIC_ANGLE_Y | 0x809001 | BASE TARGET KILLAREA SAFE_POS |
| 22 | 0x17 | PERIODIC_POS | 0x809001 | BASE TARGET KILLAREA SAFE_POS |
| 23 | 0x18 | PERIODIC_CONDITION | 0x000020 | CONDITION |
| 24 | 0x19 | PERIODIC_TARGET | 0x001000 | TARGET |
| 25 | 0x1A | PERIODIC_NOTHING | 0x000000 | - |
| 26 | 0x1B | PERIODIC_CATCH | 0x0080A1 | BASE CONDITION PERIODIC_CATCH KILLAREA |
| 27 | 0x1C | PERIODIC_ENEMY_CLIMB / PERIODIC_END | 0x000820 | CONDITION ENEMY_CLIMB |
| 28 | 0x1D | PERIODIC_INTERFACE | 0x000061 | BASE CONDITION PL_INTERFACE |
| 29 | 0x1E | PERIODIC_BOTTOM / CATCH_REQUEST | 0x001000 | TARGET |
| 30 | 0x1F | CAUGHT_RESULT | 0x000000 | - |
| 31 | 0x20 | ACT_CAUGHT | 0x001029 | BASE ACTION CONDITION TARGET |
| 32 | 0x21 | OM_PUT | 0x000001 | BASE |
| 33 | 0x22 | OM_THROW | 0x000001 | BASE |
| 34 | 0x23 | SHL_DELETE | 0x002000 | SHL_DELETE |
| 35 | 0x24 | SHL_SHOT | 0x004000 | SHL_SHOT |
| 36 | 0x25 | STICK_SHL | 0x000000 | - |
| 37 | 0x26 | SHL_SLAVE_KILL_SEND | 0x000000 | - |
| 38 | 0x27 | SHL_KILL_SYNC | 0x000000 | - |
| 39 | 0x28 | STATE_LIVE | 0x040000 | STATE_LIVE |
| 40 | 0x29 | EM5800 | 0x000000 | - |
| 41 | 0x2A | TARGET | 0x001000 | TARGET |
| 42 | 0x2B | SLAVE_DAMAGE | 0x000000 | - |
| 43 | 0x2C | ACT_RESCUE | 0x001029 | BASE ACTION CONDITION TARGET |
| 44 | 0x2D | ACT_RESCUE_ONLY | 0x000000 | - |
| 45 | 0x2E | ENEMYSTATUS_CTRL | 0x010000 | ENEMYSTATUS_CTRL |
| 46 | 0x2F | ENEMYWAITTING | 0x100000 | ENEMYWAITTING |
| 47 | 0x30 | ENEMYSTARTWAIT | 0x200000 | ENEMYSTARTWAIT |
| 48 | 0x31 | CORE_POINT | 0x400000 | CORE_POINT |
| 49 | 0x32 | CORE_POINT_SLAVE | 0x000000 | - |
| 50 | 0x33 | OCD_HOLY_ABSORP | 0x000000 | - |
| 51 | 0x34 | ACT_DAMAGE | 0x081029 | BASE ACTION CONDITION TARGET DAMAGE_ACT |
| 52 | 0x35 | MASTER_PARAM | 0x000000 | - |
| 53 | 0x36 | CUSTOM_SYNC | 0x000000 | - |
| 54 | 0x37 | SERVER_DAMAGE | 0x000000 | - |
| 55 | 0x38 | ACT_CATCH | 0x0010A9 | BASE ACTION CONDITION PERIODIC_CATCH TARGET |

Note: the `_EX` messages carry ACTION_EX (0x10) instead of ACTION (0x8), and the PS4 decoder
reads no action block for them. `cNetCtrl::sendNetMessage` updates `mLastSendFrame` when
`inc & 0x1027` **V**.

## 4. Message classes, DTI ids and NET_MSG_ID enums

### 4.1 DTI ids (from the `MtDTI::MtDTI_0` static initialisers) **V**

`createNetMsg` looks up `MtDTI::from(mMsgIdFull & 0xFFFFFF00)`, so the class id is the
high 24 bits with byte 1 = 0; `(u8)mMsgIdFull` is the NET_MSG_ID.

| Class | DTI object | DTI id | Parent | Size |
| --- | --- | --- | --- | --- |
| cNetMsgCtrlAction | `dti__2371` @ `0x2544948` | 0x40010000 | cNetMsgCtrlBase (id 0, abstract) | 0x78 |
| cNetMsgGameNormal | `dti__2372` | 0x41000000 | cNetMsgGameBase (id 0) | 0x78 |
| cNetMsgGameEasy | `dti__2374` | 0x41010000 | cNetMsgGameBase | 0x78 |
| cNetMsgSetNormal | `dti__2375` | 0x43000000 | cNetMsgSetBase (id 0) | 0x78 |
| cNetMsgToolNormal | `dti__2376` | 0x4F000000 | cNetMsgToolBase (id 0) | 0x78 |
| cNetMsgToolEasy | `dti__2377` | 0x4F010000 | cNetMsgToolBase | 0x78 |
| cNetMsgBase, cNetMsgReceiveInfo, cLobbyDataMessage | | 0 | | |

These six are the only concrete `cNetMsg*` classes in the database (name search over
`nNetMsg::cNetMsg*` DTI symbols and over every string starting `cNetMsg`) **V**. Group 0x42
(`nItemMgr::NET_MSG_ID_ITEM`: NOTHING 0, NUM 1, MAX 0x7F) has an enum but no class **V**. The
lobby path can also carry the non-RPC `cLobbyDataMessage` dummy (`00000000 <s32 type>`) **V**.

### 4.2 NET_MSG_ID enums (local types, DWARF-derived) **V**

`nNetMsgData::nCtrl::NET_MSG_ID` (group 0x40/0x01): NOTHING 0x00, ACT_BASE 0x01, ACT_NORMAL
0x02, ACT_NORMAL_EX 0x03, ACT_RESET 0x04, ACT_RESET_EX 0x05, ACT_ACTION_ONLY 0x06,
ACT_ACTION_ONLY_EX 0x07, ACT_SHL_SHOT 0x08, ACT_TARGET 0x09, ACT_DIE 0x0A, ACT_ENEMY_CLIMB 0x0B,
ACT_CLIFF_HANG 0x0C, ACT_BOW 0x0D, ACT_REVIVE_CMC 0x0E, ACT_WAND_MAGIC_SHL_SET 0x0F,
ACT_MAGIC_ITEM 0x10, ACT_THROW_ITEM 0x11, ACT_LIFT_BIGIN_ITEM 0x12, ACT_RESPAWN 0x13,
ACT_WALL_CLIMB 0x14, PERIODIC_TOP = PERIODIC_NORMAL 0x15, PERIODIC_ANGLE_Y 0x16, PERIODIC_POS
0x17, PERIODIC_CONDITION 0x18, PERIODIC_TARGET 0x19, PERIODIC_NOTHING 0x1A, PERIODIC_CATCH 0x1B,
PERIODIC_ENEMY_CLIMB = PERIODIC_END 0x1C, PERIODIC_INTERFACE 0x1D, PERIODIC_BOTTOM =
CATCH_REQUEST 0x1E, CAUGHT_RESULT 0x1F, ACT_CAUGHT 0x20, OM_PUT 0x21, OM_THROW 0x22, SHL_DELETE
0x23, SHL_SHOT 0x24, STICK_SHL 0x25, NET_MSG_SHL_SLAVE_KILL_SEND 0x26, NET_MSG_SHL_KILL_SYNC
0x27, NET_MSG_STATE_LIVE 0x28, EM5800 0x29, TARGET 0x2A, SLAVE_DAMAGE 0x2B, ACT_RESCUE 0x2C,
ACT_RESCUE_ONLY 0x2D, ENEMYSTATUS_CTRL 0x2E, ENEMYWAITTING 0x2F, ENEMYSTARTWAIT 0x30,
CORE_POINT 0x31, CORE_POINT_SLAVE 0x32, OCD_HOLY_ABSORP 0x33, ACT_DAMAGE 0x34, MASTER_PARAM
0x35, CUSTOM_SYNC 0x36, SERVER_DAMAGE 0x37, ACT_CATCH 0x38, CS_CHANGE 0x39, SOUL_ABSORP 0x3A,
SHL_REQUEST_FROM_SLAVE 0x3B, NUM 0x3C, MAX 0x7F, ACT_LOBBY_OFF 0x80, DEFAULT /
PERIODIC_DEFAULT 0xFF.

`nGame::NET_MSG_ID_GAME` (0x41/0x00): NOTHING 0, STAGE 1, REVIVE_STOCK 2, PERIOD 3, FLAG 4,
OM 5, PAWN_ENTRY_PARTY 6, PAWN_MSG 7, ENTRY_PARTY 8, DROP_ITEM 9, SET_EM_DIE 0xA, OPEN_DOOR 0xB,
FREEMARKER 0xC, LOST_RETURN_REQ 0xD, PAWN_ORDER 0xE, NUM 0xF, MAX 0x7F.

`nGame::NET_MSG_ID_GAME_EASY` (0x41/0x01): NOTHING 0xF, WEAPON_LOAD 0x10, PRT_SET 0x11,
PRT_INFO 0x12, AREA_RELEASE 0x13, EVENT 0x14, NPC_MESSAGE 0x15, AREA_JUMP_SYNC 0x16, NUM 0x17.

`nSetMgr::NET_MSG_ID_SET` (0x43/0x00): NOTHING 0, BASE 1, REQUEST_MASTER 2, CHANGE_MASTER 3,
RELEASE_MASTER 4, MASTER_INFO 5, THROW_MASTER 6, REQUEST_CREATE_CONTEXT 7, CREATE_CONTEXT 8,
NUM 9, MAX 0x7F.

`nTool::NET_MSG_ID_TOOL` (0x4F/0x00): NOTHING 0, BASE 1, PAWN_SET 2, NUM 3, MAX 0x7F.

`nTool::NET_MSG_ID_TOOL_EASY` (0x4F/0x01): NOTHING 3, DIP 4, DAMAGE_PROFILE_START 5,
DAMAGE_PROFILE_END 6, DAMAGE_PROFILE_NODE 7, TEST 8, NUM 9.

`nItemMgr::NET_MSG_ID_ITEM` (0x42): NOTHING 0, NUM 1, MAX 0x7F (no class).

Related: `nNetMsg::MSG_ADR` LOCAL 0, ALL 1, OTHER 2, PEER 3, SERVER 4;
`nSessionManager::cLobbyDataMessage::LOBBY_MSG_TYPE` DUMMY 0, RPC 1.

## 5. Captured payloads walked (03040008)

Outer layout in these `decrypted_raw` files: u8 group, u16 handler, u8 sub, u8 0, u32 counter
(9 bytes), then the packet body; files are padded to 16 bytes **PC-cap**.

### 5.1 3.3.16 `C2S_LOBBY_LOBBY_DATA_MSG_REQ`

File `packets/decrypted_raw/stream13-charcreation-marked.pcapng_tcp-stream-31/11709_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-07-18T12_14_33.4240000-07_00.3_3_16`
(176 B, SHA-256 prefix `13aa5489788dd2fe`). File offsets:

| Off | Bytes | Field | Note |
| --- | --- | --- | --- |
| 0x09 | 02 | Type = 2 | ALL/OTHER (sendLobbyMessage) |
| 0x0A | 00000000 | CharacterID = 0 | |
| 0x0E | 0000009a | len = 154 | payload 0x12..0xAB |
| 0x12 | 00000002 | Head.mSessionId = 2 | lobby, fits PS4 |
| 0x16 | 00000000 000007d0 | Head.mRpcId = 0x7D0 | **PS4 stops fitting here**: PS4 reads u32 0 as mRpcId and 0x7D0 as mMsgIdFull; fits as PC u64 |
| 0x1E | 40010015 | mMsgIdFull: cNetMsgCtrlAction, PERIODIC_NORMAL | |
| 0x22 | 00000000 | mSearchId | |
| 0x26 | 80000000 00000001 | CtrlBase.mUniqueId (PC u64) | |
| 0x2E | 00 01 01 00 | mIsEnemy 0, mIsCharacter 1, mIsHuman 1, mIsEnemyLarge 0 | |
| 0x32 | c05c9edc60000000 / 46403985 / 4089743f40000000 | BASE popPos: mPos (-114.48, 12302.38, 814.53) | inc 0x809021 |
| 0x46 | 00000000 bfd16abe | mMoveSpeed 0, mMoveAngle -1.636 | |
| 0x4E | bfd16abe | mAngleY -1.636 | |
| 0x52 | 02f8 02f8 000001c2 | CONDITION, human: mHp 760, mHpWhite 760, mStamina 450 | |
| 0x5A | 000f | mUseRegionBit 0xF → popcount(bits 1..9) = 3 | |
| 0x5C | 0000 | mRegionRateBit (u16) | |
| 0x5E | ede0 0000 | mCommonWork 0xEDE0, mCustomWork 0 | |
| 0x62 | 00000001 62 10 | mOcdActiveMsgNum 1: bank 3 / index 2, activeLv 1 / immuneLv 0 | |
| 0x68 | 00000000 00000000 | mEnchantRate 0, mAilmentDamage 0 | |
| 0x70 | 0000000000000000 + 20 x 00 | TARGET: mTargetUid (PC u64) 0, mTargetPos 0 | PS4 u32 would leave 4 bytes over |
| 0x8C | ffffffff x3 | KILLAREA mEncountArea {-1,-1,-1} | |
| 0x98 | c05c9edc… 46403985 4089743f… | SAFE_POS = mPos | |
| 0xAC | | end = 0x12 + 154 | exact fit with the three PC widenings |

Two more lobby samples in the same folder fit exactly with the same rule:
`11645_…3_3_16` (SHA-256 `d4c1a23546c1d21f`, len 0x21): Head {2, rpc 0x7D0, 0x40010039
CS_CHANGE, 0}, uniqueId 0x8000000000000001, bools 00 01 01 00, table[0x38] = 0, switch 0x39 →
u8 mCustomSkillGroup = 0; 33 bytes.
`11527_…3_3_16` (len 0x1C): Head {2, rpc 0x3F2, 0x41000001 GameNormal STAGE, 0}, no CtrlBase,
u32 mStageNo 200, u32 mStartPosNo 35; 28 bytes. This also confirms that STAGE goes over the lobby
session (createNetMsg rule) **PC-cap**.

### 5.2 6.25.16 `C2S_PARTY_SEND_BINARY_MSG_NTC`

File `packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/100357_C2S_PARTY_SEND_BINARY_MSG_NTC_2019-11-18T12_21_59.5040000-08_00.6_25_16`
(96 B, SHA-256 prefix `f6efcaf1b89988cb`):

| Off | Bytes | Field |
| --- | --- | --- |
| 0x09 | 00000000 | CharacterIdList count 0 (SERVER-addressed per sendBinary) |
| 0x0D | 00000040 | len 64 (payload 0x11..0x50) |
| 0x11 | 00000000 | Head.mSessionId 0 (binary) |
| 0x15 | 80000000 2c112a5a | mRpcId (PC u64) |
| 0x1D | 40010018 | cNetMsgCtrlAction, PERIODIC_CONDITION (inc 0x20) |
| 0x21 | 00000000 | mSearchId |
| 0x25 | 80000000 2c111ea2 | CtrlBase.mUniqueId (PC u64) |
| 0x2D | 01 01 00 01 | enemy, character, not human, large |
| 0x31 | 00002b97 | mHp (enemy: u32) 11159 |
| 0x35 | 0001 | mUseRegionBit 1 → popcount 0 → u16 |
| 0x37 | 0000 0000 0400 | mRegionRateBit, mCommonWork, mCustomWork 0x400 |
| 0x3D | 00000000 | mOcdActiveMsgNum 0 |
| 0x41 | 00000000 00000000 | mEnchantRate, mAilmentDamage |
| 0x49 | 461c3c00 4559999a | mShakeEndurance 9999.0, mRageShrinkEndurance 3481.6 |
| 0x51 | | end = 0x11 + 64, exact fit |

With the PS4 16-byte Head the walk breaks at 0x15 (mRpcId would be 0x80000000 and mMsgIdFull
0x2C112A5A, no such DTI). This is the "several records" pattern of research.md: one message,
not a batch.

TARGET width check: `…/100792_C2S_PARTY_SEND_BINARY_MSG_NTC_…6_25_16` (SHA-256 prefix
`446c639f63be6ae1`, len 0x3C), msg 0x40010019 PERIODIC_TARGET (inc 0x1000 only), bools
01 01 00 00: `80000000 00000001` (mTargetUid u64), then NetPos f64/f32/f64 → exactly 60 bytes.
`100646_…` (SHA-256 prefix `287f4a910167a03e`) fits the same way with mTargetUid 0.

6.23.16 (ALL) samples exist (8 files under `packets/decrypted_raw/`) but were not walked:
**not run**.

## 6. Open points

- PC 03040008: confirm in the PC binary (Head::deserialize, CtrlBase, CtrlAction TARGET) that
  mRpcId, mUniqueId and mTargetUid are u64, and check every other *Uid / *UniqueId field the
  samples do not exercise. Include table on PC not read (four entries — 0x15, 0x18, 0x19, 0x39
  — are consistent with the captures).
- Whether `nNetwork::Decoder::readF64` byte-swaps was not read to the end (the pseudocode was
  truncated after the read); the captures decode as BE f64 **PC-cap**.
- PRTSet float order (2.23) is **I**.
