# P2: PC 03040008 deltas against the PS4 nNetMsg wire format

Brief: `specs/005-netmsg-patterns/briefs/P2-pc-deltas.md`. Base 83835837099. Baseline:
`specs/005-netmsg-patterns/research/P1-ps4-wire-format.md` (PS4 02020005). This report lists
only what differs from P1, plus confirmations.

- Build: PC 03040008 (Season 3 truth, no symbols). Database: private copy
  `D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/ddon-data-p2/2022_01_29_DDO_DUMP_FIX.exe.i64`
  (made with `bash research/ida/private-copy.sh pc p2`; SHA-256 prefix at report time
  `717e862d1bb3a88a`). `idc.get_idb_path()` returned that path; 32-bit, image base `0x400000`,
  processor metapc. Queried read-only through ida-mcp `execute_python` (Hex-Rays, `ida_ua`
  decode of undefined bytes without creating items, `ida_bytes`). No renames, comments,
  function creation, or saves. The PS4 database was not opened (P1's VAs sufficed).
- Address basis: IDA VA in the PC database (image base 0x400000). Function names `sub_XXXXXX`
  are IDA defaults; the few existing names (`nNetwork::Decoder::readU32`, `nPacket::Read_*`,
  `nPacket::Write_*`, `MtDTI::from_0`) are cited as names, not proof.
- Status labels: **V** = read in the PC database; **I** = inferred; **C** = contradicts P1;
  **PC-cap** = from 03040008 captures only.
- Captures: every `*.3_3_16`, `*.6_25_16` and `*.6_23_16` file under `packets/decrypted_raw/`
  (59,881 + 29,176 + 8 = 89,065 files; read in the ida-mcp Python session, spot-checked with `xxd`).

## 0. Summary of the deltas

1. **Every unique-id / UID field that P1 left as u32 is u64 on PC, with three exceptions that
   stay u32**: ShlShot `mUid` (status bit 0x40), StickShl `mStickShlUniqueId`, and
   `mShlRequestShotSys` (not an id). The widened set is larger than P1's three (Head.mRpcId,
   CtrlBase.mUniqueId, mTargetUid): see the table in 2.0. **V**
2. **Changed field types that are not ids**: `mActFreeWork` u32 → u64 (popActionNo); ActBow
   `mBowNetBit` u8 → u16 (Up and Low). **V**
3. **Added fields**: CatchRequest (0x1E/0x38) gains u64 + u8 + u8 before mCatchHitPos;
   Caught (0x1F/0x20) gains u8 + u64 + u8 at the end; SetNormal CREATE_CONTEXT gains u8, u8,
   u64 at the end. **V**
4. **Changed conditions/clamps**: mOcdActiveMsgNum clamp 75 → 100 (Condition and
   CREATE_CONTEXT); the "shell owner" test is `(mAtkUID & 0xF) == 6` (PS4 `& 7`);
   SET_EM_DIE rejects the whole message when the count is 0 or ≥ 256 and uses different
   per-entry limits; CREATE_CONTEXT reads its body only when the first bool is **non-zero**. **V**
5. **New CtrlAction switch cases**: 0x3C (4 x u32) and 0x3D (1 x u32). **V**
6. **New GameNormal cases** 0x0F, 0x10, 0x11, 0x12, and **GameEasy ids shifted by +4**
   (PRT_SET 0x15 … NPC_MESSAGE 0x19, AREA_JUMP_SYNC 0x1A). **V**
7. **Include-packet table**: identical to PS4 for ids 0x01-0x38; PC has no entries beyond 0x38
   (0x39+ → 0). It is a `switch`, not a data table. **V**
8. **Head** = s32 mSessionId, **u64 mRpcId**, u32 mMsgIdFull, u32 mSearchId (20 B) **V**.
   Packet bodies of 3.3.16, 3.4.16, 6.23.16, 6.24.16, 6.25.16, 6.26.16 are as P1 section 1
   **V**; 6.22.16 is **not** a binary-message carrier (one u32) **V**.
9. With these PC rules, **all 89,065 captured payloads walk exactly to `len`** (0 failures).
   Reverting the PC-only widths to PS4 widths breaks every capture of 18 msg ids
   (section 6.1). **PC-cap**

## 1. Decoder locations (PC VAs)

Identification chain **V**: the six DTI name strings (`cNetMsgCtrlAction` @ `0x1bd76a0`, …) are
referenced only by their `MtDTI::MtDTI_0` static initialisers (`0x1a36d20` CtrlAction,
`0x1a36f20` GameNormal, `0x1a36ee0` GameEasy, `0x1a370a0` SetNormal, `0x1a37240` ToolNormal,
`0x1a37200` ToolEasy). They push the same DTI ids as PS4 (0x40010000, 0x41000000, 0x41010000,
0x43000000, 0x4F000000, 0x4F010000) and object size **0x44** (PS4 0x78). The DTI vtable's
`newInstance` installs the class vtable (DTI vtable + 8); class vtable slot 9 is the receive
method, slot 8 the send method. The decoders were then found from the callers of
`nNetwork::Decoder::readU32` (`0x15b3820`) and its sibling readers, all of which cluster in
`0x5fe8d0`-`0x6039xx`, and confirmed through the receive path (`receiveNetwork` → Head → createNetMsg
→ inline CtrlBase/CtrlAction) and the class receive methods.

PC decoders **allocate** their result struct and return it (`CtrlAction` allocates 0x670 bytes,
`GameNormal` 0x60, `GameEasy` 0x40, `SetNormal` 0x468, `ToolEasy` 0x248); the wire order is what
this report records.

### 1.1 Decoder primitives (`nNetwork::Decoder`, object: `+0` MtStream*, `+0x25` mIsDrain)

| Primitive | PC VA | Note | Status |
| --- | --- | --- | --- |
| readU16 | `0x15b37e0` | 2 bytes, byte-swapped (BE) | V |
| readU32 | `0x15b3820` (named) | 4 bytes BE | V |
| readF32 | `0x15b3750` | 4 bytes BE | V |
| readU64 | `0x15b38c0` | 8 bytes, swapped by `sub_13EF6F0` | V |
| readF64 | `0x15b3790` | 8 bytes, the same 64-bit swap as readU64 → **BE f64** (closes P1 open point for PC) | V |
| u8/bool | inline | `MtStream` vtable +0x30 read of 1 byte | V |
| readBits `0x15b3640`, readBits64 `0x15b36b0`, LEB128 `0x15b3860` | | exist on PC but are **not called by any nNetMsg decoder** (callers are `0x190xxxx` code) | V |
| drain check before a loop element | `sub_5ff730` | | I (name by use) |

### 1.2 Framing functions

| P1 function (PS4 VA) | PC VA | How identified | Status |
| --- | --- | --- | --- |
| `Head::deserialize` (`0x172920`) | `0x5ff4a0` (in-place, called by `0x757480`) and `0x5ff260` (allocating, called by receiveNetwork) | readU32, readU64, readU32, readU32 | V |
| `Head::serialize` (`0x172890`) | `0x603d00` | writeU32, writeU64 (`0x15b3bd0`), writeU32, writeU32 | V |
| `createNetMsg` (`0x382df0`) | `0x88e0a0` | `MtDTI::from_0(msgIdFull & 0xFFFFFF00)`; mMsgGroup at +0x30, mMsgId at +0x31 | V |
| `sRemoteProcedureExt::receiveNetwork` (`0x8306e0`) | `0xbeb6d0` | Head (`0x5ff260`), `createNetMsg`, RPC dispatch, inline group 0x40 decode: `Base` `0x5feaa0`, `CtrlBase` `0x5feff0`, `CtrlAction` `0x5feac0` | V |
| `cNetGameServer::sendBinary` (`0x346910`) | `0x87d720` | size ≤ 0x400; 0x20000 → 6.23.16; 0x30000 → 6.25.16 with every other member in state 1; 0x40000 → 6.25.16 with an empty list; default → 6.25.16 with `[charId]` when non-zero | V |
| `cNetGameServer::sendLobbyMessage` (`0x343c30`) | `0x87e010` | type byte 2 for 0x20000/0x30000, 4 for 0x40000, else 0; msgType 1 → raw RPC buffer, else cLobbyDataMessage (`0x89aa30`: two values); ≤ 0x400 | V |
| `cLobbyDataMessage::deserialize` (`0x392490`) | `0x898050` | value a; a != 0 → type 1 (RPC), else type = next value | V |
| `createIncludePacketCtrl` (`0x172500`) | `0x5fe8d0` | `switch(msgId)` returning the include mask (section 3) | V |

createNetMsg session rule (PC) **V**: group 0x40 → `mSessionInstanceIndex = 2` when the sender
object's RpcId satisfies `sub_b2cb90`: **`2000 ≤ RpcId ≤ 2999`** (u64 compare); group 0x41 sub 0
msgId 1 → 2; otherwise 0. Same rule as P1; the player-RPC range is now explicit, and matches the
lobby captures (RpcId 0x7D0 = 2000).

receiveNetwork extra **V**: when the Head's RpcId is in 2000-2999, the RPC object is resolved via
`sub_b2c690(rpcId, characterId, mSearchId)` instead of directly by RpcId. Not wire-relevant.

### 1.3 Class receive methods (vtable slot 9)

| Class | Class vtable | Receive (slot 9) | Decoders | Status |
| --- | --- | --- | --- | --- |
| cNetMsgCtrlBase | `0x1bd7638` | `0x88e9f0` | Base check `0x88e450`, CtrlBase `0x5feff0` | V |
| cNetMsgCtrlAction | `0x1bd7668` | `0x88e98e` (IDA func start; vtable entry `0x88e990`) | CtrlBase receive `0x88e9f0`, then CtrlAction `0x5feac0`, apply `0x88ea60` | V |
| cNetMsgGameNormal | `0x1bd7ba0` | `0x8949d0` | GameBase `0x5ff030` (allocates 4 B, reads nothing), GameNormal `0x5ff130` | V |
| cNetMsgGameEasy | `0x1bd7bd0` | `0x894560` | GameBase `0x5ff030`, GameEasy `0x5ff050` | V |
| cNetMsgSetNormal | `0x1bd8118` | `0x895d00` (bytes not defined as code) | SetNormal `0x5ff2e0` (not defined as a function; decoded with `ida_ua`) | V (decoder) / I (link from the receive method) |
| cNetMsgToolNormal | `0x1bd8650` | `0x896040` (bytes not defined as code; slot 8 is `0x8960e0`) | not read | not checked |
| cNetMsgToolEasy | `0x1bd8680` | `0x895fd0` (undefined) | ToolEasy `0x5ff3e0` (undefined; decoded with `ida_ua`) | V (decoder) / I (link) |

The SetBase/ToolBase/ToolNormal counterparts that read nothing are likely the three
"allocate 4 bytes, zero, return" stubs at `0x5ff2c0`, `0x5ff3c0`, `0x5ff480` **I**.

### 1.4 CtrlAction helpers (P1 2.4-2.20)

| P1 helper (PS4 VA) | PC VA | Status |
| --- | --- | --- |
| popNetPos (`0x172530`) | `0x5ff7e0` | V |
| popNormalPos (`0x1726e0`) | `0x5ff980` | V |
| popPos 2.4 (`0x1755b0`) | `0x5ffb20` (BASE wrapper incl. mAngleY: `0x603200`) | V |
| popActionNo 2.5 (`0x1756b0`) | `0x5ff750` | V |
| receivePktCondition 2.6 (`0x173280`) | `0x6033d0` | V |
| receivePktCliffHang 2.7 (`0x1737c0`) | `0x603270` | V |
| receivePktEnemyClimb 2.8 (`0x173950`) | `0x603810` | V |
| receivePktShlShot 2.9 (`0x173a00`) | `0x6038e0` | V |
| KILLAREA block | `0x6038a0` | V |
| receiveMsgEnemyStatusCtrl 2.10 (`0x173ea0`) | `0x600940` | V |
| receiveMsgWallClimb 2.11 (`0x1740c0`) | `0x6030b0` | V |
| receiveMsgActBow 2.12 (`0x174570`) | `0x5ffbf0` | V |
| receiveMsgCatchRequest 2.13 (`0x174470`) | `0x5fff80` | V |
| CAUGHT_RESULT / ACT_CAUGHT block | `0x6000b0` | V |
| receiveMsgOmRelease 2.14 (`0x174bc0`) | `0x6018a0` | V |
| receiveMsgShlStickParam 2.15 (`0x174e00`) | `0x602b20` | V |
| SHL_KILL_SYNC | `0x6029e0` | V |
| receiveMsgSlaveDamage 2.16 (`0x174250`) | `0x602d80` | V |
| CORE_POINT_SLAVE | `0x6001d0` | V |
| OCD_HOLY_ABSORP | `0x601850` | V |
| receiveMsgMasterParam 2.17 (`0x174a30`) | `0x6016b0` | V |
| receiveMsgCustomSkillSync 2.18 (`0x1750d0`) | `0x600260` | V |
| receiveMsgSlaveDamageSv 2.19 (`0x175330`) | `0x602f80` | V |
| CS_CHANGE | `0x600220` | V |
| SOUL_ABSORP | `0x603060` | V |
| receiveMsgShlRequestFromSlave 2.20 (`0x175410`) | `0x602a20` | V |
| new 0x3C | `0x600900` | V |
| new 0x3D | `0x6008a0` | V |
| UID kind (`uid & 0xF`) | `0xa41990` | V |

## 2. Per-decoder deltas

### 2.0 Width table (every *Uid / *UniqueId / *ID field P1 lists)

| Field (P1 section) | PS4 | PC | Status |
| --- | --- | --- | --- |
| Head.mRpcId (2.1) | u32 | **u64** | V |
| CtrlBase.mUniqueId (2.2) | u32 | **u64** | V |
| CtrlAction TARGET mTargetUid (2.3 #10) | u32 | **u64** | V |
| popActionNo mActAtkAdjustUniqueId (2.5) | u16 | u16 | V (same) |
| EnemyClimb mClimbEnemyUId (2.8) | u32 | **u64** | V |
| ShlShot mUid (status 0x40) (2.9) | u32 | u32 | V (same) |
| ShlShot mId (status 0x4) (2.9) | u32 | **u64** | V |
| ActBow Up.mTargetUId[i] (2.12) | u32 | **u64** (mLockOnId[i] stays u32) | V |
| CatchRequest mCatchRequestUid (2.13) | u32 | **u64** | V |
| CAUGHT mCatchInfo.mCatchUid (2.3 switch) | u32 | **u64** | V |
| StickShl mStickShlUniqueId (2.15) | u32 | u32 | V (same) |
| StickShl mStickUniqueId (2.15) | u32 | **u64** | V |
| SlaveDamage / SlaveDamageSv mAtkUID (2.16, 2.19) | u32 | **u64** | V |
| SlaveDamage / SlaveDamageSv mShlOwnerUID | u32 | **u64** | V |
| mAtkParamUID, mdfdNodeUID | u64 | u64 | V (same) |
| OCD_HOLY_ABSORP mHolyAbsorpAtkUID | u32 | **u64** | V |
| SOUL_ABSORP mSoulAbsorpAtkUID | u32 | **u64** | V |
| ShlRequestFromSlave mShlRequestShlOwnerUID, mShlRequestTargetUID (2.20) | u32, u32 | **u64, u64** | V |
| GameNormal OPEN_DOOR mUid (2.22) | u32 | **u64** | V |
| GameEasy PRT_INFO mPRTUniqueId (2.23) | u32 | **u64** | V |
| SetNormal mUniqueId in REQUEST_MASTER, CHANGE_MASTER, RELEASE_MASTER, MASTER_INFO, REQUEST_CREATE_CONTEXT, CREATE_CONTEXT; THROW_MASTER mThrowUniqueId (2.25) | u32 | **u64** | V |
| CREATE_CONTEXT mClimbEnemyUId, mTargetUid, mCatchTargetUID | u32 | **u64** | V |
| ToolEasy mProfileTargetID, mProfileAttckerID[8] (DAMAGE_PROFILE_START) | u32 | **u64** | V |
| ToolEasy mProfileTargetUID, mProfileAttackerUID (DAMAGE_PROFILE_NODE) | u32 | **u64** | V |
| ToolEasy mDpsHandle | u32 | u32 | V (same) |

### 2.1 Head — `0x5ff4a0` / `0x5ff260`

| # | Type | Field | Delta |
| --- | --- | --- | --- |
| 1 | s32 | mSessionId | same |
| 2 | **u64** | mRpcId | widened (P1 PC-cap now **V**) |
| 3 | u32 | mMsgIdFull | same; in memory at +0x10, so `(u8)` msgId is the byte at +0x10 |
| 4 | u32 | mSearchId | same |

Wire size 20 bytes **V**.

### 2.2 CtrlBase — `0x5feff0`: u64 mUniqueId (P1: u32; PC-cap now **V**).

### 2.3 CtrlAction — `0x5feac0`

Body order identical to P1 2.3 rows 1-21 (four bools; BASE, ACTION, CONDITION, CLIFF_HANG,
ENEMY_CLIMB, TARGET, SHL_DELETE, SHL_SHOT; KILLAREA and SAFE_POS only when mIsHuman;
ENEMYSTATUS_CTRL, ENEMYWAITTING, ENEMYSTARTWAIT, CORE_POINT (before) DAMAGE_ACT, WALL_CLIMB,
STATE_LIVE with popPos if 513) **V**. There is no `isSameVer` parameter on PC (signature
`(head, decoderWrapper)`) **V**. Deltas:

| # | P1 | PC | Status |
| --- | --- | --- | --- |
| 10 TARGET | u32 mTargetUid + NetPos | **u64** mTargetUid + NetPos | V |
| switch | cases 0x0D, 0x1E/0x38, 0x1F/0x20, 0x21/0x22, 0x25, 0x27, 0x2B, 0x32, 0x33, 0x35, 0x36, 0x37, 0x39, 0x3A, 0x3B | same cases **plus 0x3C and 0x3D** | V |
| 0x3C (new) | — | 4 x u32 (`unk3C[0..3]`, struct +0x658) | V |
| 0x3D (new) | — | 1 x u32 (`unk3D`, struct +0x668) | V |
| 0x1F/0x20 | u8 mCatchType, u32 mCatchUid, u8 mJointNo | u8 mCatchType, **u64** mCatchUid, u8 mJointNo, **u8 (new), u64 (new), u8 (new)** | V |
| 0x27, 0x39 | u8 | u8 (same) | V |
| 0x32 | u16, u16 | same | V |
| 0x33 | u32 mHolyAbsorpAtkUID, u16 | **u64**, u16 | V |
| 0x3A | u32 mSoulAbsorpAtkUID, u16 | **u64**, u16 | V |

### 2.4 popPos `0x5ffb20` — same (NetPos, f32, f32) **V**. popNetPos `0x5ff7e0` — same (f64, f32,
f64; NaN/limit sanitising) **V**. popNormalPos `0x5ff980` — same (3 x f32) **V**.

### 2.5 popActionNo `0x5ff750`

u32 mActNo, u8 mActReqPrio, u16 mActAtkAdjustUniqueId, **u64 mActFreeWork** (P1: u32) **V**.
This adds 4 bytes to every message with ACTION (0x8): 0x02, 0x04, 0x06, 0x08, 0x09, 0x0A, 0x0B,
0x0C, 0x13, 0x14, 0x20, 0x2C, 0x34, 0x38.

### 2.6 receivePktCondition `0x6033d0`

Same as P1 except **mOcdActiveMsgNum clamp 100** (P1 75) **V**. HP branch, region-rate width
(popcount of bits 1-9: ≤ 4 → u16, ≤ 8 → u32, 9 → u64), the (u8, u8) bit packing with bank
clamped to 6, and the enemy-only shake/rage floats are unchanged **V**.

### 2.7 CliffHang `0x603270` — same **V**.

### 2.8 EnemyClimb `0x603810`
**u64 mClimbEnemyUId**, u32 mJointNo, NormalPos, u16, u16 **V**.

### 2.9 ShlShot `0x6038e0`
u8 mReceiveNum (clamp 8); per shot: u8 mIndex (clamp 8), u32 mShlStatus, u8 mShlGroup, u8
mShlIndex; 0x40 → u32 mUid (same); 0x1 → NetPos; 0x2 → NetPos; **0x4 → u64 mId** (P1 u32);
0x8 → Vec3f; 0x100 → u8 mShlLockOnId **V**.

### 2.10 EnemyStatusCtrl `0x600940` — same (count ≥ 16 → 0) **V**.
### 2.11 WallClimb `0x6030b0` — same **V**.

### 2.12 ActBow `0x5ffbf0`

| # | Condition (f = u32 mBowNetUpdateFlag) | PC reads | Delta |
| --- | --- | --- | --- |
| 2 | f & 1 | u8 Up.mType, u8 Up.mActNo (clamp 6), u8 Up.mSkillType, **u16 Up.mBowNetBit**, u8 mBowArrowType | mBowNetBit u8 → u16 |
| 3 | f & 1 && f & 0x10 | u8 n; n x (**u64** Up.mTargetUId, u32 Up.mLockOnId) (no clamp) | target u32 → u64 |
| 4 | f & 1 && f & 0x20 | u8 Up.mArrowNum | same |
| 5 | f & 2 | u8 Low.mType, u8 Low.mActNo (clamp 7), u8 Low.mSkillType, **u16 Low.mBowNetBit** | u8 → u16 |
| 6-8 | | same as P1 | |

All **V**.

### 2.13 CatchRequest `0x5fff80` (0x1E, 0x38)
**u64** mCatchRequestUid, u8 mCatchRequestType, u8 mCatchJointNo, **u64 (new), u8 (new),
u8 (new)**, NormalPos mCatchHitPos **V**. Names of the new fields: none found.

### 2.14 OmRelease `0x6018a0` — same (quaternion only when msgId == 0x22) **V**.

### 2.15 StickShl `0x602b20`
u8 mStickCreateControl; == 1 → u32 mStickShlUniqueId (same); **u64 mStickUniqueId**; u8, u8,
u8; NormalPos; Vec3f **V**.

### 2.16 SlaveDamage `0x602d80` and 2.19 SlaveDamageSv `0x602f80`
**u64 mAtkUID**, u64, u64, u16, [Vec3f mDamageDir in 2.16 only], u32 mAttackAttr; if
**`(mAtkUID & 0xF) == 6`** (`sub_a41990` returns `a1 & 0xF`; P1 `& 7`) → **u64 mShlOwnerUID** **V**.

### 2.17 MasterParam `0x6016b0` — same (bits 1-9; u32 if large or enemy, else u16) **V**.
### 2.18 CustomSkillSync `0x600260` — same (2 x 8 u8, interleaved per j) **V**.
### 2.20 ShlRequestFromSlave `0x602a20`
**u64, u64**, u32 mShlRequestShotSys, u8, u8, u8 **V**.

### 2.21 GameBase `0x5ff030` — reads nothing (same) **V**.

### 2.22 GameNormal `0x5ff130`

PC helpers return a status; a 0 drops the whole message (`sub_5ff5c0` frees it) **V**.

| msgId | P1 | PC (helper VA) | Delta / status |
| --- | --- | --- | --- |
| 1 STAGE | s32, s32 | `0x601670` | same, V |
| 2 REVIVE_STOCK | u8 | `0x6014b0` | same, V |
| 4 FLAG | s32 n; n x u32 | `0x6010c0` | same, V |
| 7 PAWN_MSG | u32 n; n x (u32, u32) | `0x6013d0` | same, V |
| 0xA SET_EM_DIE | u32 n; n x 5 u16; discard entry if mArea > 998, mGroup > 511, mSetNo > 31, mEmId > 998 | `0x6014f0` | **n == 0 or n ≥ 256 → message rejected** (nothing more read); entry discarded (still consumed) if **mArea ≥ 9999**, mGroup ≥ 512, mSetNo ≥ 32, **mEmId ≥ 532**; V |
| 0xB OPEN_DOOR | u32 n; n x u32 | `0x601330` | n x **u64** mUid, V |
| 0xC FREEMARKER | u32 n; n x (f32 x3, s32, s32, u8) | `0x601140` | same, V |
| 0xE PAWN_ORDER | u32, u32 | `0x601470` | same, V |
| **0xF (new)** | — | `0x601060` | u32, **u64, u64** (the receive handler `0x894bf0` passes both u64 through `sub_88e380`, a UID lookup **I**); V |
| **0x10 (new)** | — | `0x601030` | u32; V |
| **0x11 (new)** | — | `0x601300` | u32; V |
| **0x12 (new)** | — | `0x6012d0` | u32; V |
| other | nothing | | same |

No enum, string or log text names 0x0F-0x12: call them `NET_MSG_ID_GAME_UNK_0x0F` …
`_0x12`. Consequence **I**: the PC `NET_MSG_ID_GAME` enum has four more members, so `NUM` is
0x13 and the GameEasy ids move up by 4 (2.23).

### 2.23 GameEasy `0x5ff050` (msg ids shifted by +4)

u8 mType first (same), then switch on the Head msgId. The receive method `0x894560` switches on
mType over the same values, and its 0x1A case touches `sAreaPointer` (AREA_JUMP_SYNC) **V**.

| PS4 id | PC id | Name | PC reads | Delta / status |
| --- | --- | --- | --- | --- |
| 0x11 | **0x15** | PRT_SET | `0x600d10`: u32 n (clamp 30); n x (u32, u16, u16, u8, u8, f32 x4) | same body, V |
| 0x12 | **0x16** | PRT_INFO | `0x600be0`: **u64** mPRTUniqueId, 5 x bool | widened, V |
| 0x13 | **0x17** | AREA_RELEASE | `0x600ab0`: u32 n (clamp 200); n x u32 | same, V |
| 0x14 | **0x18** | EVENT | `0x600b40`: 3 x u32 | same, V |
| 0x15 | **0x19** | NPC_MESSAGE | `0x600b90`: 3 x u32 | same, V |
| 0x16 | **0x1A** | AREA_JUMP_SYNC | nothing beyond mType | same, V |
| 0x10 | 0x14 (I) | WEAPON_LOAD | nothing beyond mType | I |

Names on PC are carried over from the PS4 enum by body shape and handler use: **I**.
Captures: `0x41010015` (7), `0x41010016` (18), `0x41010018` (15) **PC-cap**, all exact fits.

### 2.24 SetBase — no reads (I, see 1.3).

### 2.25 SetNormal `0x5ff2e0` (jump table `0x5ff39c`, msgId − 2, 7 entries)

| msgId | PC helper | PC reads | Delta / status |
| --- | --- | --- | --- |
| 2 REQUEST_MASTER | `0x602900` | s32 n; n x **u64** | V (disassembly) |
| 3 CHANGE_MASTER | `0x601ab0` | s32 n; n x (**u64** mUniqueId, s32 mMasterIndex) | V |
| 4 RELEASE_MASTER | `0x602770` | s32 n; n x **u64** | V (disassembly) |
| 5 MASTER_INFO | `0x602670` | s32 n; n x (**u64**, s32); bool mTerminateFlag | V |
| 6 THROW_MASTER | `0x6029a0` | **u64** mThrowUniqueId, s32 mThrowIndex | V |
| 7 REQUEST_CREATE_CONTEXT | `0x602810` | s32 n; n x (u32 mId, **u64** mUniqueId, s32 mStageNo, s32 mEncountArea) | V |
| 8 CREATE_CONTEXT | `0x601b80` | below | V |

CREATE_CONTEXT on PC **V** (rows as P1; deltas bold):

| # | Condition | Type | Field |
| --- | --- | --- | --- |
| 1 | | u32, **u64**, s32, s32 | mId, mUniqueId, mStageNo, mEncountArea |
| 2 | | bool | mAdditionalData |
| 3 | **mAdditionalData != 0** | s32 | (P1's mMasterIndex slot, +0x5C) |
| 4-17 | **mAdditionalData != 0** (P1: unconditional) | | as P1, with: ActionNo **u64 mActFreeWork**; mOcdActiveMsgNum **clamp 100**; mClimbEnemyUId **u64**; mTargetUid **u64**; mCatchTargetUID **u64** |
| 18 (new) | mAdditionalData != 0 | u8, u8, u64 | unnamed (struct +0x458, +0x459, +0x460) |

**C** against P1: P1 reads row 3 when the bool is **zero** and rows 4-17 unconditionally; on PC
the whole tail, including the s32, is inside `if (bool != 0)`; a zero bool ends the message
after 21 bytes. Not exercised by the captures (no group 0x43 message was captured).

### 2.26 ToolBase / ToolNormal — not checked on PC.

### 2.27 ToolEasy `0x5ff3e0` (jump table `0x5ff468`, msgId − 4, 4 entries)

| msgId | PC helper | PC reads | Delta / status |
| --- | --- | --- | --- |
| 4 DIP | `0x6008d0` | u8[0x1C0 = 448] | same, V |
| 5 DAMAGE_PROFILE_START | `0x600820` | u32 mDpsHandle, **u64** mProfileTargetID, 8 x **u64** mProfileAttckerID | V |
| 6 DAMAGE_PROFILE_END | `0x600430` | u32 mDpsHandle | same, V |
| 7 DAMAGE_PROFILE_NODE | `0x600460` | u32, **u64**, **u64**, u8 x3, u64, f32 x4, bool x5 | V |

## 3. Include-packet table on PC — `createIncludePacketCtrl` `0x5fe8d0` **V**

A compiled `switch (msgId)` (also called inline by CtrlAction `0x5feac0` and by
receiveNetwork `0xbeb6d0`). Every case, in PS4 terms (index = msgId − 1):

| msgId | PC value | = P1? |
| --- | --- | --- |
| 0x01 | 0x801021 | yes |
| 0x02, 0x04, 0x0A, 0x13 | 0x801029 | yes |
| 0x03, 0x05 | 0x001031 | yes |
| 0x06 | 0x001028 | yes |
| 0x07 | 0x001030 | yes |
| 0x08 | 0x005029 | yes |
| 0x09, 0x20, 0x2C | 0x001029 | yes |
| 0x0B | 0x000829 | yes |
| 0x0C | 0x000429 | yes |
| 0x10, 0x11, 0x21, 0x22 | 0x000001 | yes |
| 0x14 | 0x020029 | yes |
| 0x15 | 0x809021 | yes |
| 0x16, 0x17 | 0x809001 | yes |
| 0x18 | 0x000020 | yes |
| 0x19, 0x1E, 0x2A | 0x001000 | yes |
| 0x1B | 0x0080A1 | yes |
| 0x1C | 0x000820 | yes |
| 0x1D | 0x000061 | yes |
| 0x23 | 0x002000 | yes |
| 0x24 | 0x004000 | yes |
| 0x28 | 0x040000 | yes |
| 0x2E | 0x010000 | yes |
| 0x2F | 0x100000 | yes |
| 0x30 | 0x200000 | yes |
| 0x31 | 0x400000 | yes |
| 0x34 | 0x081029 | yes |
| 0x38 | 0x0010A9 | yes |
| everything else (0x0D-0x0F, 0x12, 0x1A, 0x1F, 0x25-0x27, 0x29, 0x2B, 0x2D, 0x32, 0x33, 0x35-0x37, **0x39 and above, including 0x3C, 0x3D**) | 0 | yes for ≤ 0x38; new ids get 0 |

The PC table has the same 56 effective entries as PS4 (ids 0x01-0x38); there are **no new
include bits** on PC, and the decoder tests the same bit set as P1 (0x2, 0x4, 0x10, 0x40,
0x80, 0x100, 0x200 never tested) **V**.

## 4. Season 3 msg ids beyond the PS4 enum

No enum, string or log text names them (the PC binary has no symbols; no strings reference
these decoders) **V** for "no name found". Names below are placeholders.

| Group / id | Name | Reads (after Head + CtrlBase + 4 bools for 0x40) | Captured | Status |
| --- | --- | --- | --- | --- |
| 0x40/0x01 id 0x3C | `NET_MSG_ID_UNK_0x3C` | include 0; 4 x u32 | 448 x 6.25.16; all from enemy+character+large senders, all four values 0 | V / PC-cap |
| 0x40/0x01 id 0x3D | `NET_MSG_ID_UNK_0x3D` | include 0; 1 x u32 | none | V |
| 0x41/0x00 id 0x0F | `NET_MSG_ID_GAME_UNK_0x0F` | u32, u64, u64 | none | V |
| 0x41/0x00 id 0x10-0x12 | `NET_MSG_ID_GAME_UNK_0x10` … `_0x12` | u32 each | none | V |
| 0x41/0x01 | GameEasy ids 0x14-0x1A | see 2.23 | 0x15, 0x16, 0x18 | V / I (names) |

## 5. Packet bodies on PC

| Packet | PC function | Body | Status |
| --- | --- | --- | --- |
| C2S 3.3.16 (lobby data msg) | writer `0x841b60` (`WritePacket(3, 3, 0x10)`), sender `0x82ed10` | u8 Type, u32 CharacterID, s32 len, u8[len] | V (= P1) |
| S2C 3.4.16 | handler `0x7e2ad0`, reader `0x80e970` | u8 Type, u32 CharacterID, s32 len, u8[len], u8 OnlineStatus; then cLobbyDataMessage check and `receiveNetwork(session 1, CharacterID, Data, len)` when type 1 | V (= P1) |
| C2S 6.23.16 (binary all) | `0x832260` (`WritePacket(6, 23, 0x10)`) | s32 len, u8[len] | V (= P1) |
| C2S 6.25.16 (binary) | writer `0x841d20` (`WritePacket(6, 25, 0x10)`), list writer `0x77df90`, sender `0x832360` | u32 count, u32 CharacterId[count], s32 len, u8[len] | V (= P1) |
| S2C 6.24.16 | handler `0x7e97a0`, reader `0x811560` | u32 CharacterID, s32 len, u8[len], u8 OnlineStatus; `receiveNetwork(session 0, …)` | V (= P1) |
| S2C 6.26.16 | handler `0x7e9880`, reader `0x811600` | same as 6.24.16 | V (= P1) |
| S2C 6.22.16 | handler `0x7e72b0` (packet vtable `0x1bc3b70`) | **one u32 only**, read and dropped; no receiveNetwork | V; P1 did not list it |

The raw writer of the data block is `sub_8bcac0` (bytes) **I** (by use). The data length on
send is the MtMemoryStream size (vtable +0x24) **V**.

## 6. Capture walks

### 6.1 Population check (all files) **PC-cap**

Walker: the PC rules of sections 2-3 implemented in the ida-mcp Python session (struct
unpack, BE), over every `3_3_16`, `6_25_16`, `6_23_16` file in `packets/decrypted_raw/`.
Offsets: 3.3.16 payload at file 0x12 (len at 0x0E); 6.25.16 payload at 0x0D + 4 x count + 4;
6.23.16 payload at 0x0D. Result: **89,065 / 89,065 payloads end exactly at `len`, 0 overruns,
0 unhandled**.

| Packet | msgIdFull (count) |
| --- | --- |
| 3.3.16 | 0x40010002 (24,850), 08 (1,288), 09 (10), 0B (676), 0C (39), 0D (7,475), 13 (4), 14 (15), 15 (22,713), 17 (25), 18 (27), 1C (84), 1E (9), 1F (2), 20 (6), 24 (306), 25 (815), 28 (36), 2C (9), 34 (232), 37 (1,067), 39 (43); 0x41000001 (150) |
| 6.23.16 | 0x4001001E (8) |
| 6.25.16 | 0x40010002 (7,706), 08 (140), 09 (7), 0D (255), 15 (1,841), 18 (2,255), 19 (2,352), 1B (40), 23 (1,539), 24 (11), 27 (23), 28 (782), 2E (1,076), 2F (2), 30 (32), 31 (333), 34 (634), 35 (441), 37 (9,216), 38 (2), 3C (448); 0x4100000A (1); 0x41010015 (7), 16 (18), 18 (15) |

Branch coverage in that population: mActFreeWork 35,618 messages; ShlShot mId (0x4) 911,
mUid (0x40) 11; ActBow Up.mBowNetBit 2,813, Low 92, Up.mTargetUId 318; mShlOwnerUID 8,951;
mStickShlUniqueId 652; mClimbEnemyUId 760; CatchRequest new u64 27; mCatchUid 8;
mPRTUniqueId 18; STATE_LIVE 818 (513 → popPos: 330); max mOcdActiveMsgNum seen 5 (the 75 → 100
clamp change is not exercised).

Discrimination: replacing the PC-only widths with P1's (mActFreeWork, ShlShot mId, mBowNetBit,
Up.mTargetUId, mClimbEnemyUId, mAtkUID, mShlOwnerUID, mCatchRequestUid, mCatchUid,
mStickUniqueId, Holy/Soul AtkUID, mPRTUniqueId back to u32/u8) makes **every** capture of
0x02, 0x08, 0x09, 0x0B, 0x0C, 0x13, 0x14, 0x1C, 0x1E, 0x1F, 0x20, 0x24, 0x25, 0x2C, 0x34, 0x37,
0x38 and 0x41010016 fail, and 2,851 of 7,730 ActBow (0x0D) captures. Not run per field.

### 6.2 Walks, one capture per requested id

Offsets are relative to the payload start (given per file); "walk ends at" is in payload bytes.
Field names for new fields are placeholders. Values: integers hex, floats `%g`. Each walk was
produced by the walker above; the 0x3C file was also checked by hand with `xxd`. Every walk ends
at `len`.

#### 0x02 (3.3.16)

`packets/decrypted_raw/stream1-marked.pcapng_tcp-stream-35/12390_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-07-06T11_06_03.6580000-07_00.3_3_16` (176 B, SHA-256 prefix `4dc3405241062ee1`), payload at file offset 0x12, len 155 (0x9B); walk ends at 155 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d0 |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010002 |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000000000001 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | f64 | mPos.x | -208.919 |
| 0x28 | f32 | mPos.y | 12338.7 |
| 0x2C | f64 | mPos.z | -201.54 |
| 0x34 | f32 | mMoveSpeed | 0 |
| 0x38 | f32 | mMoveAngle | -1.64976 |
| 0x3C | f32 | mAngleY | -1.64976 |
| 0x40 | u32 | mActNo | 0x2 |
| 0x44 | u8 | mActReqPrio | 0x1 |
| 0x45 | u16 | mActAtkAdjustUniqueId | 0x0 |
| 0x47 | u64 | mActFreeWork | 0x0 |
| 0x4F | u16 | mHp | 0xa32 |
| 0x51 | u16 | mHpWhite | 0xa32 |
| 0x53 | u32 | mStamina | 0x5aa |
| 0x57 | u16 | mUseRegionBit | 0xf |
| 0x59 | u16 | mRegionRateBit | 0x0 |
| 0x5B | u16 | mCommonWork | 0x0 |
| 0x5D | u16 | mCustomWork | 0x0 |
| 0x5F | u32 | mOcdActiveMsgNum | 0x0 |
| 0x63 | f32 | mEnchantRate | 0 |
| 0x67 | f32 | mAilmentDamage | 0 |
| 0x6B | u64 | mTargetUid | 0x0 |
| 0x73 | f64 | mTargetPos.x | 0 |
| 0x7B | f32 | mTargetPos.y | 0 |
| 0x7F | f64 | mTargetPos.z | 0 |
| 0x87 | f64 | mSafePos.x | -208.919 |
| 0x8F | f32 | mSafePos.y | 12338.7 |
| 0x93 | f64 | mSafePos.z | -201.54 |

#### 0x08 (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/100756_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_22_30.7430000-08_00.3_3_16` (208 B, SHA-256 prefix `d270e9bd8909ef08`), payload at file offset 0x12, len 186 (0xBA); walk ends at 186 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d6 |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010008 |
| 0x10 | u32 | Head.mSearchId | 0xdcb1d3 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x80000000000000c1 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | f64 | mPos.x | -447.068 |
| 0x28 | f32 | mPos.y | 41.6416 |
| 0x2C | f64 | mPos.z | -5778.9 |
| 0x34 | f32 | mMoveSpeed | 0 |
| 0x38 | f32 | mMoveAngle | 1.56217 |
| 0x3C | f32 | mAngleY | 1.56217 |
| 0x40 | u32 | mActNo | 0x1056 |
| 0x44 | u8 | mActReqPrio | 0x1 |
| 0x45 | u16 | mActAtkAdjustUniqueId | 0x0 |
| 0x47 | u64 | mActFreeWork | 0x200 |
| 0x4F | u16 | mHp | 0xb5e |
| 0x51 | u16 | mHpWhite | 0xb5e |
| 0x53 | u32 | mStamina | 0x5e0 |
| 0x57 | u16 | mUseRegionBit | 0xf |
| 0x59 | u16 | mRegionRateBit | 0x0 |
| 0x5B | u16 | mCommonWork | 0x33f0 |
| 0x5D | u16 | mCustomWork | 0x1 |
| 0x5F | u32 | mOcdActiveMsgNum | 0x1 |
| 0x63 | u8 | ocd[0].bank|index | 0x41 |
| 0x64 | u8 | ocd[0].activeLv|immuneLv | 0x10 |
| 0x65 | f32 | mEnchantRate | 0.1 |
| 0x69 | f32 | mAilmentDamage | 30 |
| 0x6D | u64 | mTargetUid | 0x0 |
| 0x75 | f64 | mTargetPos.x | -389.121 |
| 0x7D | f32 | mTargetPos.y | 130.958 |
| 0x81 | f64 | mTargetPos.z | -5795.5 |
| 0x89 | u8 | mReceiveNum | 0x1 |
| 0x8A | u8 | shot[0].mIndex | 0x0 |
| 0x8B | u32 | shot[0].mShlStatus | 0x10d |
| 0x8F | u8 | mShlGroup | 0x14 |
| 0x90 | u8 | mShlIndex | 0x0 |
| 0x91 | f64 | mPos.x | -447.068 |
| 0x99 | f32 | mPos.y | 41.6416 |
| 0x9D | f64 | mPos.z | -5778.9 |
| 0xA5 | u64 | mId | 0x8000000028111ea2 |
| 0xAD | f32 | mDir.x | 0.999963 |
| 0xB1 | f32 | mDir.y | 0 |
| 0xB5 | f32 | mDir.z | 0.00862598 |
| 0xB9 | u8 | mShlLockOnId | 0x0 |

#### 0x0B (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/101788_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_23_47.7930000-08_00.3_3_16` (160 B, SHA-256 prefix `d0bc1b394674636b`), payload at file offset 0x12, len 139 (0x8B); walk ends at 139 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d0 |
| 0x0C | u32 | Head.mMsgIdFull | 0x4001000b |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000000000001 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | f64 | mPos.x | -4666.56 |
| 0x28 | f32 | mPos.y | 3156.99 |
| 0x2C | f64 | mPos.z | -9331.13 |
| 0x34 | f32 | mMoveSpeed | 1 |
| 0x38 | f32 | mMoveAngle | 2.98603 |
| 0x3C | f32 | mAngleY | 2.98603 |
| 0x40 | u32 | mActNo | 0x24 |
| 0x44 | u8 | mActReqPrio | 0x1 |
| 0x45 | u16 | mActAtkAdjustUniqueId | 0x2 |
| 0x47 | u64 | mActFreeWork | 0x0 |
| 0x4F | u16 | mHp | 0x10a9 |
| 0x51 | u16 | mHpWhite | 0x10a9 |
| 0x53 | u32 | mStamina | 0xb87 |
| 0x57 | u16 | mUseRegionBit | 0xf |
| 0x59 | u16 | mRegionRateBit | 0x0 |
| 0x5B | u16 | mCommonWork | 0x0 |
| 0x5D | u16 | mCustomWork | 0x200 |
| 0x5F | u32 | mOcdActiveMsgNum | 0x2 |
| 0x63 | u8 | ocd[0].bank|index | 0x41 |
| 0x64 | u8 | ocd[0].activeLv|immuneLv | 0x10 |
| 0x65 | u8 | ocd[1].bank|index | 0x62 |
| 0x66 | u8 | ocd[1].activeLv|immuneLv | 0x10 |
| 0x67 | f32 | mEnchantRate | 0.1 |
| 0x6B | f32 | mAilmentDamage | 30 |
| 0x6F | u64 | mClimbEnemyUId | 0x8000000012121ea2 |
| 0x77 | u32 | mJointNo | 0x52 |
| 0x7B | f32 | mJointOffset.x | -24.792 |
| 0x7F | f32 | mJointOffset.y | 60.0764 |
| 0x83 | f32 | mJointOffset.z | 19.978 |
| 0x87 | u16 | mNodeIndex | 0x1 |
| 0x89 | u16 | mGeomIndex | 0x0 |

#### 0x0D (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/101126_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_22_56.2770000-08_00.3_3_16` (96 B, SHA-256 prefix `98070bb9320a9eb2`), payload at file offset 0x12, len 75 (0x4B); walk ends at 75 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d5 |
| 0x0C | u32 | Head.mMsgIdFull | 0x4001000d |
| 0x10 | u32 | Head.mSearchId | 0xdc92da |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x80000000000000a1 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u32 | mBowNetUpdateFlag | 0x19 |
| 0x24 | u8 | Up.mType | 0x1 |
| 0x25 | u8 | Up.mActNo | 0x4 |
| 0x26 | u8 | Up.mSkillType | 0x2 |
| 0x27 | u16 | Up.mBowNetBit | 0x21 |
| 0x29 | u8 | mBowArrowType | 0x0 |
| 0x2A | u8 | Up.mShlShotNum | 0x1 |
| 0x2B | u64 | Up.mTargetUId[0] | 0x8000000000000001 |
| 0x33 | u32 | Up.mLockOnId[0] | 0x0 |
| 0x37 | f64 | mBowNetAimPos.x | 611.579 |
| 0x3F | f32 | mBowNetAimPos.y | 181.448 |
| 0x43 | f64 | mBowNetAimPos.z | -6155.79 |

#### 0x24 (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/101999_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_24_08.0530000-08_00.3_3_16` (112 B, SHA-256 prefix `486f940c7541429d`), payload at file offset 0x12, len 81 (0x51); walk ends at 81 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d5 |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010024 |
| 0x10 | u32 | Head.mSearchId | 0xdc92da |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x80000000000000a1 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u8 | mReceiveNum | 0x1 |
| 0x21 | u8 | shot[0].mIndex | 0x0 |
| 0x22 | u32 | shot[0].mShlStatus | 0x12d |
| 0x26 | u8 | mShlGroup | 0x11 |
| 0x27 | u8 | mShlIndex | 0x2 |
| 0x28 | f64 | mPos.x | -4741.06 |
| 0x30 | f32 | mPos.y | 3116.58 |
| 0x34 | f64 | mPos.z | -8144.02 |
| 0x3C | u64 | mId | 0x8000000012121ea2 |
| 0x44 | f32 | mDir.x | 0.171214 |
| 0x48 | f32 | mDir.y | 0.142055 |
| 0x4C | f32 | mDir.z | -0.974939 |
| 0x50 | u8 | mShlLockOnId | 0x0 |

#### 0x25 (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/100531_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_22_16.8530000-08_00.3_3_16` (96 B, SHA-256 prefix `87cace3220585442`), payload at file offset 0x12, len 72 (0x48); walk ends at 72 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d0 |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010025 |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000000000001 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u8 | mStickCreateControl | 0x1 |
| 0x21 | u32 | mStickShlUniqueId | 0x4c6d6 |
| 0x25 | u64 | mStickUniqueId | 0x8000000026111ea2 |
| 0x2D | u8 | mStickJointNo | 0x50 |
| 0x2E | u8 | mStickShlGroup | 0x3 |
| 0x2F | u8 | mStickShlIndex | 0x0 |
| 0x30 | f32 | mStickJointOffset.x | -2.76951 |
| 0x34 | f32 | mStickJointOffset.y | -0.704408 |
| 0x38 | f32 | mStickJointOffset.z | -4.10288 |
| 0x3C | f32 | mStickDirection.x | 0.35623 |
| 0x40 | f32 | mStickDirection.y | -0.0868166 |
| 0x44 | f32 | mStickDirection.z | -0.930357 |

#### 0x34 (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/102161_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_24_21.3230000-08_00.3_3_16` (176 B, SHA-256 prefix `ed47ab5c84cae810`), payload at file offset 0x12, len 147 (0x93); walk ends at 147 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d0 |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010034 |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000000000001 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | f64 | mPos.x | -4966.81 |
| 0x28 | f32 | mPos.y | 3293 |
| 0x2C | f64 | mPos.z | -10679.5 |
| 0x34 | f32 | mMoveSpeed | 0 |
| 0x38 | f32 | mMoveAngle | 0.779252 |
| 0x3C | f32 | mAngleY | 0.779252 |
| 0x40 | u32 | mActNo | 0x87 |
| 0x44 | u8 | mActReqPrio | 0xd |
| 0x45 | u16 | mActAtkAdjustUniqueId | 0x2 |
| 0x47 | u64 | mActFreeWork | 0x6 |
| 0x4F | u16 | mHp | 0xddd |
| 0x51 | u16 | mHpWhite | 0xfbf |
| 0x53 | u32 | mStamina | 0xbb0 |
| 0x57 | u16 | mUseRegionBit | 0xf |
| 0x59 | u16 | mRegionRateBit | 0x0 |
| 0x5B | u16 | mCommonWork | 0x1 |
| 0x5D | u16 | mCustomWork | 0x201 |
| 0x5F | u32 | mOcdActiveMsgNum | 0x2 |
| 0x63 | u8 | ocd[0].bank|index | 0x41 |
| 0x64 | u8 | ocd[0].activeLv|immuneLv | 0x10 |
| 0x65 | u8 | ocd[1].bank|index | 0x62 |
| 0x66 | u8 | ocd[1].activeLv|immuneLv | 0x10 |
| 0x67 | f32 | mEnchantRate | 0.1 |
| 0x6B | f32 | mAilmentDamage | 30 |
| 0x6F | u64 | mTargetUid | 0x0 |
| 0x77 | f64 | mTargetPos.x | 0 |
| 0x7F | f32 | mTargetPos.y | 0 |
| 0x83 | f64 | mTargetPos.z | 0 |
| 0x8B | u64 | mAttackParamUIDForDmVec | 0x29d01b0000007c |

#### 0x37 (3.3.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/102346_C2S_LOBBY_LOBBY_DATA_MSG_REQ_2019-11-18T12_24_35.4760000-08_00.3_3_16` (96 B, SHA-256 prefix `1597c6dbc443e7db`), payload at file offset 0x12, len 70 (0x46); walk ends at 70 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x2 |
| 0x04 | u64 | Head.mRpcId | 0x7d6 |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010037 |
| 0x10 | u32 | Head.mSearchId | 0xdcb1d3 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x80000000000000c1 |
| 0x1C | u8 | mIsEnemy | 0x0 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x1 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u64 | mAtkUID | 0x4d7f6 |
| 0x28 | u64 | mAtkParamUID | 0x67986ffb00000003 |
| 0x30 | u64 | mdfdNodeUID | 0x5821231200010000 |
| 0x38 | u16 | mAtkAdjustUniqueId | 0x0 |
| 0x3A | u32 | mAttackAttr | 0x1 |
| 0x3E | u64 | mShlOwnerUID | 0x8000000012121ea2 |

#### 0x23 (6.25.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/108903_C2S_PARTY_SEND_BINARY_MSG_NTC_2019-11-18T12_38_35.1820000-08_00.6_25_16` (64 B, SHA-256 prefix `aa38616515cf55d6`), payload at file offset 0x11, len 36 (0x24); walk ends at 36 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x0 |
| 0x04 | u64 | Head.mRpcId | 0x800000000001302a |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010023 |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000000012472 |
| 0x1C | u8 | mIsEnemy | 0x1 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x0 |
| 0x1F | u8 | mIsEnemyLarge | 0x1 |
| 0x20 | u32 | mShlDelFlag | 0x1 |

#### 0x2E (6.25.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/100314_C2S_PARTY_SEND_BINARY_MSG_NTC_2019-11-18T12_21_56.0050000-08_00.6_25_16` (128 B, SHA-256 prefix `986cfe0e4b676752`), payload at file offset 0x11, len 97 (0x61); walk ends at 97 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x0 |
| 0x04 | u64 | Head.mRpcId | 0x800000002e112a5a |
| 0x0C | u32 | Head.mMsgIdFull | 0x4001002e |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x800000002e111ea2 |
| 0x1C | u8 | mIsEnemy | 0x1 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x0 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u32 | mEnemyStatusGroupNoNum | 0x2 |
| 0x24 | u32 | GroupNo[0] | 0x0 |
| 0x28 | u32 | SubGroupNo[0] | 0x0 |
| 0x2C | u32 | GroupNo[1] | 0x1 |
| 0x30 | u32 | SubGroupNo[1] | 0x1 |
| 0x34 | u64 | mEnemyBitCtrlCollision | 0x5000000080000001 |
| 0x3C | u8 | mEnemyCtrlRegionSelectNo | 0x1 |
| 0x3D | u64 | mEnemyBitCtrlParts | 0x0 |
| 0x45 | u64 | mEnemyBitCtrlWorkRate | 0x0 |
| 0x4D | u64 | mEnemyBitCtrlScale | 0x0 |
| 0x55 | u64 | mEnemyBitCtrlMontage | 0x1 |
| 0x5D | u32 | mEnemyBitCtrlSyncBit | 0x0 |

#### 0x31 (6.25.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/100573_C2S_PARTY_SEND_BINARY_MSG_NTC_2019-11-18T12_22_20.1440000-08_00.6_25_16` (64 B, SHA-256 prefix `1cb7d258324a6698`), payload at file offset 0x11, len 36 (0x24); walk ends at 36 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x0 |
| 0x04 | u64 | Head.mRpcId | 0x800000002e112a5a |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010031 |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x800000002e111ea2 |
| 0x1C | u8 | mIsEnemy | 0x1 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x0 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u16 | mRegionCorePointID | 0x200 |
| 0x22 | u16 | mActiveTimer | 0xb |

#### 0x35 (6.25.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/101068_C2S_PARTY_SEND_BINARY_MSG_NTC_2019-11-18T12_22_51.3930000-08_00.6_25_16` (64 B, SHA-256 prefix `8bd9d27152089f88`), payload at file offset 0x11, len 42 (0x2A); walk ends at 42 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x0 |
| 0x04 | u64 | Head.mRpcId | 0x8000000028112a5a |
| 0x0C | u32 | Head.mMsgIdFull | 0x40010035 |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000028111ea2 |
| 0x1C | u8 | mIsEnemy | 0x1 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x0 |
| 0x1F | u8 | mIsEnemyLarge | 0x0 |
| 0x20 | u16 | mUseRegionBit | 0x7 |
| 0x22 | u32 | mRegionHp[0] | 0x0 |
| 0x26 | u32 | mRegionHp[1] | 0x0 |

#### 0x3C (6.25.16)

`packets/decrypted_raw/stream85-marked.pcapng_tcp-stream-11/107301_C2S_PARTY_SEND_BINARY_MSG_NTC_2019-11-18T12_36_23.7780000-08_00.6_25_16` (80 B, SHA-256 prefix `19badcf42282dc5f`), payload at file offset 0x11, len 48 (0x30); walk ends at 48 = len

| Off | Type | Field | Value |
| --- | --- | --- | --- |
| 0x00 | s32 | Head.mSessionId | 0x0 |
| 0x04 | u64 | Head.mRpcId | 0x800000000001302a |
| 0x0C | u32 | Head.mMsgIdFull | 0x4001003c |
| 0x10 | u32 | Head.mSearchId | 0x0 |
| 0x14 | u64 | CtrlBase.mUniqueId | 0x8000000000012472 |
| 0x1C | u8 | mIsEnemy | 0x1 |
| 0x1D | u8 | mIsCharacter | 0x1 |
| 0x1E | u8 | mIsHuman | 0x0 |
| 0x1F | u8 | mIsEnemyLarge | 0x1 |
| 0x20 | u32 | unk3C[0] | 0x0 |
| 0x24 | u32 | unk3C[1] | 0x0 |
| 0x28 | u32 | unk3C[2] | 0x0 |
| 0x2C | u32 | unk3C[3] | 0x0 |

## 7. Open points

- Names for CtrlAction 0x3C/0x3D, GameNormal 0x0F-0x12 and the new CatchRequest/Caught/CREATE_CONTEXT fields: none found in the PC binary; the senders (class vtable slot 8, e.g. CtrlAction `0x891750`) were not read.
- SetNormal CREATE_CONTEXT bool polarity (2.25) contradicts P1; recheck P1 PS4 `0x177060` if a pattern needs group 0x43 (no captures).
- ToolNormal / ToolBase / SetBase on PC: not checked (1.3).
- The send-side order of CORE_POINT vs DAMAGE_ACT on PC (P1 latent mismatch) was not read.
