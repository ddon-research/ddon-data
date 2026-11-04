// nNetMsg payloads (cNetMsg* RPC messages) as carried by the lobby and party binary packets of
// client 03040008 (PC, Season 3).
//
// Sources (transcribed, not re-derived):
//   P1 specs/005-netmsg-patterns/research/P1-ps4-wire-format.md  PS4 02020005 baseline
//   P2 specs/005-netmsg-patterns/research/P2-pc-deltas.md        PC 03040008 deltas (override P1)
//   P5 specs/005-netmsg-patterns/research/P5-pc-send-side.md     PC send side, Season 3 field roles
// "PC 0x..." is the decoder VA in the PC 03040008 database (image base 0x400000, P2 section 1),
// "PS4 0x..." the matching DDOORBIS.elf VA (P1). Every multi-byte value is big-endian: include
// this file after `#pragma endian big`. No type here depends on the default endianness otherwise.
//
// Wire layout of one message (P1 1.3, P2 2.1): Head (20 B) | class body. One message per packet,
// no batching; the packet's `len` is the only length. NetMsg<len> dispatches on
// `mMsgIdFull & 0xFFFFFF00` (the DTI id) and ends with `u8 unparsed[...]` for anything it does not
// decode; `fits` is true when the decoded message ends exactly at `len`.
//
// Markers: `// inferred` = the source marks the statement I (inferred); `unk_*` = Season 3 field
// without a name (P2 4, 7).

#pragma once

import std.mem;
import std.bit;
import std.io;
import std.math;
import std.sys;

// ---------------------------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------------------------

// DTI ids of the concrete message classes (P1 4.1, P2 1): mMsgIdFull & 0xFFFFFF00.
enum NET_MSG_DTI : u32 {
    cNetMsgCtrlAction = 0x40010000,
    cNetMsgGameNormal = 0x41000000,
    cNetMsgGameEasy   = 0x41010000,
    cNetMsgSetNormal  = 0x43000000,
    cNetMsgToolNormal = 0x4F000000,
    cNetMsgToolEasy   = 0x4F010000
};

// nNetMsgData::nCtrl::NET_MSG_ID (group 0x40, sub 0x01), P1 4.2; 0x3C/0x3D are Season 3 (P2 4).
// Aliases with the same value (not separate members): PERIODIC_TOP = PERIODIC_NORMAL 0x15,
// PERIODIC_ENEMY_CLIMB = PERIODIC_END 0x1C, PERIODIC_BOTTOM = CATCH_REQUEST 0x1E,
// DEFAULT = PERIODIC_DEFAULT 0xFF.
enum NET_MSG_ID : u8 {
    NET_MSG_ID_NOTHING = 0x00,
    NET_MSG_ID_ACT_BASE = 0x01,
    NET_MSG_ID_ACT_NORMAL = 0x02,
    NET_MSG_ID_ACT_NORMAL_EX = 0x03,
    NET_MSG_ID_ACT_RESET = 0x04,
    NET_MSG_ID_ACT_RESET_EX = 0x05,
    NET_MSG_ID_ACT_ACTION_ONLY = 0x06,
    NET_MSG_ID_ACT_ACTION_ONLY_EX = 0x07,
    NET_MSG_ID_ACT_SHL_SHOT = 0x08,
    NET_MSG_ID_ACT_TARGET = 0x09,
    NET_MSG_ID_ACT_DIE = 0x0A,
    NET_MSG_ID_ACT_ENEMY_CLIMB = 0x0B,
    NET_MSG_ID_ACT_CLIFF_HANG = 0x0C,
    NET_MSG_ID_ACT_BOW = 0x0D,
    NET_MSG_ID_ACT_REVIVE_CMC = 0x0E,
    NET_MSG_ID_ACT_WAND_MAGIC_SHL_SET = 0x0F,
    NET_MSG_ID_ACT_MAGIC_ITEM = 0x10,
    NET_MSG_ID_ACT_THROW_ITEM = 0x11,
    NET_MSG_ID_ACT_LIFT_BIGIN_ITEM = 0x12,
    NET_MSG_ID_ACT_RESPAWN = 0x13,
    NET_MSG_ID_ACT_WALL_CLIMB = 0x14,
    NET_MSG_ID_PERIODIC_NORMAL = 0x15,
    NET_MSG_ID_PERIODIC_ANGLE_Y = 0x16,
    NET_MSG_ID_PERIODIC_POS = 0x17,
    NET_MSG_ID_PERIODIC_CONDITION = 0x18,
    NET_MSG_ID_PERIODIC_TARGET = 0x19,
    NET_MSG_ID_PERIODIC_NOTHING = 0x1A,
    NET_MSG_ID_PERIODIC_CATCH = 0x1B,
    NET_MSG_ID_PERIODIC_ENEMY_CLIMB = 0x1C,
    NET_MSG_ID_PERIODIC_INTERFACE = 0x1D,
    NET_MSG_ID_CATCH_REQUEST = 0x1E,
    NET_MSG_ID_CAUGHT_RESULT = 0x1F,
    NET_MSG_ID_ACT_CAUGHT = 0x20,
    NET_MSG_ID_OM_PUT = 0x21,
    NET_MSG_ID_OM_THROW = 0x22,
    NET_MSG_ID_SHL_DELETE = 0x23,
    NET_MSG_ID_SHL_SHOT = 0x24,
    NET_MSG_ID_STICK_SHL = 0x25,
    NET_MSG_SHL_SLAVE_KILL_SEND = 0x26,
    NET_MSG_SHL_KILL_SYNC = 0x27,
    NET_MSG_STATE_LIVE = 0x28,
    NET_MSG_ID_EM5800 = 0x29,
    NET_MSG_ID_TARGET = 0x2A,
    NET_MSG_ID_SLAVE_DAMAGE = 0x2B,
    NET_MSG_ID_ACT_RESCUE = 0x2C,
    NET_MSG_ID_ACT_RESCUE_ONLY = 0x2D,
    NET_MSG_ID_ENEMYSTATUS_CTRL = 0x2E,
    NET_MSG_ID_ENEMYWAITTING = 0x2F,
    NET_MSG_ID_ENEMYSTARTWAIT = 0x30,
    NET_MSG_ID_CORE_POINT = 0x31,
    NET_MSG_ID_CORE_POINT_SLAVE = 0x32,
    NET_MSG_ID_OCD_HOLY_ABSORP = 0x33,
    NET_MSG_ID_ACT_DAMAGE = 0x34,
    NET_MSG_ID_MASTER_PARAM = 0x35,
    NET_MSG_ID_CUSTOM_SYNC = 0x36,
    NET_MSG_ID_SERVER_DAMAGE = 0x37,
    NET_MSG_ID_ACT_CATCH = 0x38,
    NET_MSG_ID_CS_CHANGE = 0x39,
    NET_MSG_ID_SOUL_ABSORP = 0x3A,
    NET_MSG_ID_SHL_REQUEST_FROM_SLAVE = 0x3B,
    NET_MSG_ID_UNK_0x3C = 0x3C,  // Season 3, no name found (PS4 NUM = 0x3C)
    NET_MSG_ID_UNK_0x3D = 0x3D,  // Season 3, no name found
    NET_MSG_ID_MAX = 0x7F,
    NET_MSG_ID_ACT_LOBBY_OFF = 0x80,
    NET_MSG_ID_DEFAULT = 0xFF
};

// nGame::NET_MSG_ID_GAME (group 0x41, sub 0x00), P1 4.2; 0x0F-0x12 are Season 3 (P2 2.22), so the
// PC NUM is 0x13 (inferred).
enum NET_MSG_ID_GAME : u8 {
    NET_MSG_ID_GAME_NOTHING = 0x0,
    NET_MSG_ID_GAME_STAGE = 0x1,
    NET_MSG_ID_GAME_REVIVE_STOCK = 0x2,
    NET_MSG_ID_GAME_PERIOD = 0x3,
    NET_MSG_ID_GAME_FLAG = 0x4,
    NET_MSG_ID_GAME_OM = 0x5,
    NET_MSG_ID_GAME_PAWN_ENTRY_PARTY = 0x6,
    NET_MSG_ID_GAME_PAWN_MSG = 0x7,
    NET_MSG_ID_GAME_ENTRY_PARTY = 0x8,
    NET_MSG_ID_GAME_DROP_ITEM = 0x9,
    NET_MSG_ID_GAME_SET_EM_DIE = 0xA,
    NET_MSG_ID_GAME_OPEN_DOOR = 0xB,
    NET_MSG_ID_GAME_FREEMARKER = 0xC,
    NET_MSG_ID_GAME_LOST_RETURN_REQ = 0xD,
    NET_MSG_ID_GAME_PAWN_ORDER = 0xE,
    NET_MSG_ID_GAME_UNK_0x0F = 0xF,
    NET_MSG_ID_GAME_UNK_0x10 = 0x10,
    NET_MSG_ID_GAME_UNK_0x11 = 0x11,
    NET_MSG_ID_GAME_UNK_0x12 = 0x12,
    NET_MSG_ID_GAME_NUM = 0x13,  // inferred (PS4 0xF)
    NET_MSG_ID_GAME_MAX = 0x7F
};

// nGame::NET_MSG_ID_GAME_EASY (group 0x41, sub 0x01): PS4 ids + 4 on PC (P2 2.23). Names carried
// over from PS4 by body shape and handler use (inferred); NOTHING and WEAPON_LOAD ids inferred.
enum NET_MSG_ID_GAME_EASY : u8 {
    NET_MSG_ID_GAME_EASY_NOTHING = 0x13,         // inferred (PS4 0x0F)
    NET_MSG_ID_GAME_EASY_WEAPON_LOAD = 0x14,     // inferred (PS4 0x10)
    NET_MSG_ID_GAME_EASY_PRT_SET = 0x15,
    NET_MSG_ID_GAME_EASY_PRT_INFO = 0x16,
    NET_MSG_ID_GAME_EASY_AREA_RELEASE = 0x17,
    NET_MSG_ID_GAME_EASY_EVENT = 0x18,
    NET_MSG_ID_GAME_EASY_NPC_MESSAGE = 0x19,
    NET_MSG_ID_GAME_EASY_AREA_JUMP_SYNC = 0x1A,
    NET_MSG_ID_GAME_EASY_NUM = 0x1B              // inferred (PS4 0x17)
};

// nSetMgr::NET_MSG_ID_SET (group 0x43, sub 0x00), P1 4.2.
enum NET_MSG_ID_SET : u8 {
    NET_MSG_ID_SET_NOTHING = 0x0,
    NET_MSG_ID_SET_BASE = 0x1,
    NET_MSG_ID_SET_REQUEST_MASTER = 0x2,
    NET_MSG_ID_SET_CHANGE_MASTER = 0x3,
    NET_MSG_ID_SET_RELEASE_MASTER = 0x4,
    NET_MSG_ID_SET_MASTER_INFO = 0x5,
    NET_MSG_ID_SET_THROW_MASTER = 0x6,
    NET_MSG_ID_SET_REQUEST_CREATE_CONTEXT = 0x7,
    NET_MSG_ID_SET_CREATE_CONTEXT = 0x8,
    NET_MSG_ID_SET_NUM = 0x9,
    NET_MSG_ID_SET_MAX = 0x7F
};

// nTool::NET_MSG_ID_TOOL (group 0x4F, sub 0x00), P1 4.2.
enum NET_MSG_ID_TOOL : u8 {
    NET_MSG_ID_TOOL_NOTHING = 0x0,
    NET_MSG_ID_TOOL_BASE = 0x1,
    NET_MSG_ID_TOOL_PAWN_SET = 0x2,
    NET_MSG_ID_TOOL_NUM = 0x3,
    NET_MSG_ID_TOOL_MAX = 0x7F
};

// nTool::NET_MSG_ID_TOOL_EASY (group 0x4F, sub 0x01), P1 4.2.
enum NET_MSG_ID_TOOL_EASY : u8 {
    NET_MSG_ID_TOOL_EASY_NOTHING = 0x3,
    NET_MSG_ID_TOOL_EASY_DIP = 0x4,
    NET_MSG_ID_TOOL_EASY_DAMAGE_PROFILE_START = 0x5,
    NET_MSG_ID_TOOL_EASY_DAMAGE_PROFILE_END = 0x6,
    NET_MSG_ID_TOOL_EASY_DAMAGE_PROFILE_NODE = 0x7,
    NET_MSG_ID_TOOL_EASY_TEST = 0x8,
    NET_MSG_ID_TOOL_EASY_NUM = 0x9
};

// nSessionManager::cLobbyDataMessage::LOBBY_MSG_TYPE (P1 1.2, 4.2).
enum LOBBY_MSG_TYPE : s32 {
    LOBBY_MSG_TYPE_DUMMY = 0,
    LOBBY_MSG_TYPE_RPC = 1
};

// nNetSv::LOBBY_MSG_TYPE: the u8 Type of the lobby data packets (sendLobbyMessage writes 2 for
// MSG_ADR ALL/OTHER, 4 for SERVER, else 0 with CharacterId = target; P1 1.1 step 7a, P2 1.2).
// Values from the previous stub pattern (PS4 DWARF).
enum LOBBY_PACKET_TYPE : u8 {
    LOBBY_MSG_PEER = 0x0,
    LOBBY_MSG_OTHER = 0x1,
    LOBBY_MSG_ALL = 0x2,
    LOBBY_MSG_ALL_AND_PARTY = 0x3,
    LOBBY_MSG_SERVER = 0x4
};

// PS4 DWARF nCharacter::E_ONLINE_STATUS (binaries/PS4_02020005/DDOORBIS.elf.h:97775-97788, an
// __int32 enum; the packets carry it as u8): 0x0-0xC, ONLINE_STATUS_NUM = 0xD on PS4 02020005.
// 0xD is named here from the server C# (PtPawn = 0xD, Num = 0xE): Season 3?, server lead, not
// evidence, and it contradicts the PS4 NUM.
enum ONLINE_STATUS : u8 {
    ONLINE_STATUS_NONE = 0x0,
    ONLINE_STATUS_ONLINE = 0x1,
    ONLINE_STATUS_OFFLINE = 0x2,
    ONLINE_STATUS_LEAVING = 0x3,
    ONLINE_STATUS_BUSY = 0x4,
    ONLINE_STATUS_ENTRY_BOARD = 0x5,
    ONLINE_STATUS_QUICK_MATCH = 0x6,
    ONLINE_STATUS_EVENT = 0x7,
    ONLINE_STATUS_CONTENTS = 0x8,
    ONLINE_STATUS_PT_LEADER = 0x9,
    ONLINE_STATUS_PT_MEMBER = 0xA,
    ONLINE_STATUS_LOST = 0xB,
    ONLINE_STATUS_SERVER_MOVE = 0xC,
    ONLINE_STATUS_PT_PAWN_SEASON3_SERVER_LEAD = 0xD
};

// ---------------------------------------------------------------------------------------------
// Include-packet table: createIncludePacketCtrl, PC 0x5fe8d0 (a switch), PS4 0x172500 / table
// 0x1BECE20 (P1 3, P2 3). Same 56 entries as PS4; every id above 0x38 (0x3C, 0x3D) gets 0.
// ---------------------------------------------------------------------------------------------

#define INC_BASE             0x1
#define INC_ACTION           0x8
#define INC_CONDITION        0x20
#define INC_CLIFF_HANG       0x400
#define INC_ENEMY_CLIMB      0x800
#define INC_TARGET           0x1000
#define INC_SHL_DELETE       0x2000
#define INC_SHL_SHOT         0x4000
#define INC_KILLAREA         0x8000
#define INC_ENEMYSTATUS_CTRL 0x10000
#define INC_WALL_CLIMB       0x20000
#define INC_STATE_LIVE       0x40000
#define INC_DAMAGE_ACT       0x80000
#define INC_ENEMYWAITTING    0x100000
#define INC_ENEMYSTARTWAIT   0x200000
#define INC_CORE_POINT       0x400000
#define INC_SAFE_POS         0x800000

fn nNetMsg_includePacket(u8 msgId) {
    match (msgId) {
        (0x01): return 0x801021;
        (0x02 | 0x04 | 0x0A | 0x13): return 0x801029;
        (0x03 | 0x05): return 0x001031;
        (0x06): return 0x001028;
        (0x07): return 0x001030;
        (0x08): return 0x005029;
        (0x09 | 0x20 | 0x2C): return 0x001029;
        (0x0B): return 0x000829;
        (0x0C): return 0x000429;
        (0x10 | 0x11 | 0x21 | 0x22): return 0x000001;
        (0x14): return 0x020029;
        (0x15): return 0x809021;
        (0x16 | 0x17): return 0x809001;
        (0x18): return 0x000020;
        (0x19 | 0x1E | 0x2A): return 0x001000;
        (0x1B): return 0x0080A1;
        (0x1C): return 0x000820;
        (0x1D): return 0x000061;
        (0x23): return 0x002000;
        (0x24): return 0x004000;
        (0x28): return 0x040000;
        (0x2E): return 0x010000;
        (0x2F): return 0x100000;
        (0x30): return 0x200000;
        (0x31): return 0x400000;
        (0x34): return 0x081029;
        (0x38): return 0x0010A9;
        (_): return 0;
    }
};

// ---------------------------------------------------------------------------------------------
// Head and position primitives
// ---------------------------------------------------------------------------------------------

// nNetMsgData::Head: PC 0x5ff4a0 / 0x5ff260 (PS4 0x172920). 20 bytes on PC (P2 2.1).
struct Head {
    s32 mSessionId;    // 2 = lobby session, 0 = party binary (P1 1.3)
    u64 mRpcId;        // PS4 u32
    u32 mMsgIdFull;    // group<<24 | sub<<16 | 0<<8 | msgId
    u32 mSearchId;
};

// popNetPos: PC 0x5ff7e0 (PS4 0x172530). Each value NaN/Inf -> 0, clamped to +-1e10 on read.
struct NetPos {
    double x;
    float y;
    double z;
};

// popNormalPos: PC 0x5ff980 (PS4 0x1726e0).
struct NormalPos {
    float x;
    float y;
    float z;
};

// Three inline f32 (NaN/Inf -> 0).
struct Vec3f {
    float x;
    float y;
    float z;
};

// popPos: PC 0x5ffb20 (PS4 0x1755b0).
struct Pos {
    NetPos mPos;
    float mMoveSpeed;
    float mMoveAngle;
};

// popActionNo: PC 0x5ff750 (PS4 0x1756b0).
struct ActionNo {
    u32 mActNo;
    u8 mActReqPrio;
    u16 mActAtkAdjustUniqueId;
    u64 mActFreeWork;  // PS4 u32
};

// nObjCondition::stOcdActiveMsg, two bit-packed bytes (P1 2.6 row 6). The decoded values are
// exported next to the raw bytes.
struct OcdActiveMsg {
    u8 bankIndex;       // mBank = bankIndex >> 5 (7 -> 6), mIndex = bankIndex & 0x1F
    u8 activeImmuneLv;  // mActiveLv = activeImmuneLv >> 4, mImmuneLv = activeImmuneLv & 0xF
    u8 mBank = (bankIndex >> 5) == 7 ? 6 : (bankIndex >> 5) [[export]];
    u8 mIndex = bankIndex & 0x1F [[export]];
    u8 mActiveLv = activeImmuneLv >> 4 [[export]];
    u8 mImmuneLv = activeImmuneLv & 0xF [[export]];
};

// mRegionRateBit width by popcount of mUseRegionBit bits 1..9 (P1 2.6 row 3, P2 2.6).
fn nNetMsg_regionRateWidth(u16 useRegionBit) {
    u8 n = std::bit::popcount(useRegionBit & 0x3FE);
    if (n < 5) return 2;
    if (n < 9) return 4;
    return 8;
};

// ---------------------------------------------------------------------------------------------
// CtrlAction helpers (parent = CtrlAction, for the four bools)
// ---------------------------------------------------------------------------------------------

// receivePktCondition: PC 0x6033d0 (PS4 0x173280).
struct Condition {
    if (!parent.mIsEnemyLarge && !parent.mIsEnemy) {
        if (parent.mIsHuman) {
            u16 mHp;
            u16 mHpWhite;
            u32 mStamina;
        } else {
            u16 mHp;
        }
    } else {
        u32 mHp;
    }
    u16 mUseRegionBit;
    match (nNetMsg_regionRateWidth(mUseRegionBit)) {
        (2): u16 mRegionRateBit;
        (4): u32 mRegionRateBit;
        (8): u64 mRegionRateBit;
    }
    u16 mCommonWork;
    u16 mCustomWork;
    if (parent.mIsCharacter) {
        u32 mOcdActiveMsgNum;  // clamped to 100 (PS4 75); entries read = the clamped count
        OcdActiveMsg mOcdActiveMsgArray[std::math::min(mOcdActiveMsgNum, 100)];
    }
    float mEnchantRate;
    float mAilmentDamage;
    if (parent.mIsEnemy) {
        float mShakeEndurance;
        float mRageShrinkEndurance;
    }
};

// receivePktCliffHang: PC 0x603270 (PS4 0x1737c0).
struct CliffHang {
    NetPos mCliffPos;
    Vec3f mCliffNormal;
    NetPos mCliffStartPos;
    NetPos mCliffStartOldPos;
};

// receivePktEnemyClimb: PC 0x603810 (PS4 0x173950).
struct EnemyClimb {
    u64 mClimbEnemyUId;  // PS4 u32
    u32 mJointNo;
    NormalPos mJointOffset;
    u16 mNodeIndex;
    u16 mGeomIndex;
};

// stShlShot entry of receivePktShlShot: PC 0x6038e0 (PS4 0x173a00).
struct ShlShot {
    u8 mIndex;  // value clamped to 8
    u32 mShlStatus;
    u8 mShlGroup;
    u8 mShlIndex;
    if (mShlStatus & 0x40) u32 mUid;  // stays u32 on PC
    if (mShlStatus & 0x1) NetPos mPos;
    if (mShlStatus & 0x2) NetPos mTargetPos;
    if (mShlStatus & 0x4) u64 mId;    // PS4 u32
    if (mShlStatus & 0x8) Vec3f mDir;
    if (mShlStatus & 0x100) u8 mShlLockOnId;
};

// receivePktShlShot: PC 0x6038e0 (PS4 0x173a00).
struct ShlShotList {
    u8 mReceiveNum;  // clamped to 8
    ShlShot mShots[std::math::min(mReceiveNum, 8)];
};

// receiveMsgEnemyStatusCtrl: PC 0x600940 (PS4 0x173ea0).
struct EnemyStatusGroup {
    u32 mEnemyStatusGroupNo;
    u32 mEnemyStatusSubGroupNo;
};

struct EnemyStatusCtrl {
    u32 mEnemyStatusGroupNoNum;  // >= 16 -> 0, no entries read
    EnemyStatusGroup mGroups[mEnemyStatusGroupNoNum < 16 ? mEnemyStatusGroupNoNum : 0];
    u64 mEnemyBitCtrlCollision;
    u8 mEnemyCtrlRegionSelectNo;
    u64 mEnemyBitCtrlParts;
    u64 mEnemyBitCtrlWorkRate;
    u64 mEnemyBitCtrlScale;
    u64 mEnemyBitCtrlMontage;
    u32 mEnemyBitCtrlSyncBit;
};

// receiveMsgWallClimb: PC 0x6030b0 (PS4 0x1740c0).
struct WallClimb {
    NetPos mWallClimbPos;
    Vec3f mWallClimbNormal;
    NetPos mWallClimbLandPos;
};

// receiveMsgActBow: PC 0x5ffbf0 (PS4 0x174570).
struct BowTarget {
    u64 mTargetUId;  // PS4 u32
    u32 mLockOnId;
};

struct ActBow {
    u32 mBowNetUpdateFlag;
    if (mBowNetUpdateFlag & 0x1) {
        u8 mUpType;
        u8 mUpActNo;          // value clamped to 6
        u8 mUpSkillType;
        u16 mUpBowNetBit;     // PS4 u8
        u8 mBowArrowType;
        if (mBowNetUpdateFlag & 0x10) {
            u8 mUpShlShotNum;  // no clamp
            BowTarget mUpTargets[mUpShlShotNum];
        }
        if (mBowNetUpdateFlag & 0x20) u8 mUpArrowNum;
    }
    if (mBowNetUpdateFlag & 0x2) {
        u8 mLowType;
        u8 mLowActNo;         // value clamped to 7
        u8 mLowSkillType;
        u16 mLowBowNetBit;    // PS4 u8
        if (mBowNetUpdateFlag & 0x20) u8 mLowArrowNum;
    }
    if ((mBowNetUpdateFlag & 0x24) == 0x24) u8 mUpArrowNumAgain;  // Up.mArrowNum read again
    if (mBowNetUpdateFlag & 0x8) NetPos mBowNetAimPos;
};

// receiveMsgCatchRequest: PC 0x5fff80 (PS4 0x174470); ids 0x1E, 0x38.
struct CatchRequest {
    u64 mCatchRequestUid;  // PS4 u32
    u8 mCatchRequestType;
    u8 mCatchJointNo;
    // Season 3: the second triple = cpCatchCtrl::mCaughtInfo (PS4 cCaughtInfo {mCatchUid,
    // mCatchType, mJointNo}; "Caught" prefix ours). T001c 6 (V): PC 0x8e7220 = disconnectEscape
    // writes the second triple, 0x8e72f0 = forceCancel the first.
    u64 mCaughtUid;
    u8 mCaughtType;
    u8 mCaughtJointNo;
    NormalPos mCatchHitPos;
};

// CAUGHT_RESULT / ACT_CAUGHT block: PC 0x6000b0; ids 0x1F, 0x20. The PC apply 0x88f6e0 reads only
// the second triple (P5 1). The sender 0x891f60 (send switch 0x8915e3, cases 31/32) writes the same
// six fields in this order (T001c 4, V).
struct CatchInfo {
    u8 mCatchType;
    u64 mCatchUid;   // PS4 u32
    u8 mJointNo;
    // Season 3: cpCatchCtrl::mCaughtInfo (PS4 cCaughtInfo; "Caught" prefix ours). T001c 6 (V):
    // PC 0x8e7220 = disconnectEscape, 0x8e72f0 = forceCancel.
    u8 mCaughtType;
    u64 mCaughtUid;
    u8 mCaughtJointNo;
};

// receiveMsgOmRelease: PC 0x6018a0 (PS4 0x174bc0); ids 0x21, 0x22.
struct OmRelease<auto MsgId> {
    NetPos mOmReleasePos;
    float mOmReleaseAngle;
    if (MsgId == 0x22) {
        float mOmReleaseQuatW;
        float mOmReleaseQuatX;
        float mOmReleaseQuatY;
        float mOmReleaseQuatZ;
    }
};

// receiveMsgShlStickParam: PC 0x602b20 (PS4 0x174e00); id 0x25.
struct StickShl {
    u8 mStickCreateControl;
    if (mStickCreateControl == 1) u32 mStickShlUniqueId;  // stays u32 on PC
    u64 mStickUniqueId;   // PS4 u32
    u8 mStickJointNo;
    u8 mStickShlGroup;
    u8 mStickShlIndex;
    NormalPos mStickJointOffset;
    Vec3f mStickDirection;
};

// receiveMsgSlaveDamage: PC 0x602d80 (PS4 0x174250); id 0x2B. The shell-owner test is
// (mAtkUID & 0xF) == 6 on PC (PS4 & 7).
struct SlaveDamage {
    u64 mAtkUID;          // PS4 u32
    u64 mAtkParamUID;
    u64 mdfdNodeUID;
    u16 mAtkAdjustUniqueId;
    Vec3f mDamageDir;
    u32 mAttackAttr;
    if ((mAtkUID & 0xF) == 6) u64 mShlOwnerUID;  // PS4 u32
};

// receiveMsgSlaveDamageSv: PC 0x602f80 (PS4 0x175330); id 0x37. As SlaveDamage without mDamageDir.
struct SlaveDamageSv {
    u64 mAtkUID;          // PS4 u32
    u64 mAtkParamUID;
    u64 mdfdNodeUID;
    u16 mAtkAdjustUniqueId;
    u32 mAttackAttr;
    if ((mAtkUID & 0xF) == 6) u64 mShlOwnerUID;  // PS4 u32
};

// receiveMsgMasterParam: PC 0x6016b0 (PS4 0x174a30); id 0x35. One mRegionHp per set bit 1..9 of
// mUseRegionBit, in bit order (bit i+1 -> mRegionHp[i]); u32 for (large) enemies, else u16.
struct MasterParam {
    u16 mUseRegionBit;
    if (parent.mIsEnemyLarge || parent.mIsEnemy)
        u32 mRegionHp[std::bit::popcount(mUseRegionBit & 0x3FE)];
    else
        u16 mRegionHp[std::bit::popcount(mUseRegionBit & 0x3FE)];
};

// receiveMsgCustomSkillSync: PC 0x600260 (PS4 0x1750d0); id 0x36. Two iterations j, interleaved.
struct CustomSkillSet {
    u8 mCustom1;
    u8 mCustom2;
    u8 mCustom3;
    u8 mCustom4;
    u8 mCustom1Lv;
    u8 mCustom2Lv;
    u8 mCustom3Lv;
    u8 mCustom4Lv;
};

// receiveMsgShlRequestFromSlave: PC 0x602a20 (PS4 0x175410); id 0x3B.
struct ShlRequestFromSlave {
    u64 mShlRequestShlOwnerUID;  // PS4 u32
    u64 mShlRequestTargetUID;    // PS4 u32
    u32 mShlRequestShotSys;
    u8 mShlRequestShotGroup;
    u8 mShlRequestShotIndex;
    u8 mShlRequestLockOnIndex;
};

// ---------------------------------------------------------------------------------------------
// Class bodies
// ---------------------------------------------------------------------------------------------

// nNetMsgData::CtrlBase: PC 0x5feff0 (PS4 0x172a40).
struct CtrlBase {
    u64 mUniqueId;  // PS4 u32
};

// nNetMsgData::CtrlAction: PC 0x5feac0 (PS4 0x172ac0). Order as P1 2.3 rows 1-22, PC widths.
struct CtrlAction<auto MsgId> {
    u32 inc = nNetMsg_includePacket(MsgId) [[export]];  // include-packet mask of this id
    bool mIsEnemy;
    bool mIsCharacter;
    bool mIsHuman;
    bool mIsEnemyLarge;
    if (inc & INC_BASE) {
        Pos mPos;            // BASE wrapper PC 0x603200
        float mAngleY;
    }
    if (inc & INC_ACTION) ActionNo mAction;
    if (inc & INC_CONDITION) Condition mCondition;
    if (inc & INC_CLIFF_HANG) CliffHang mCliffHang;
    if (inc & INC_ENEMY_CLIMB) EnemyClimb mEnemyClimb;
    if (inc & INC_TARGET) {
        u64 mTargetUid;      // PS4 u32
        NetPos mTargetPos;
    }
    if (inc & INC_SHL_DELETE) u32 mShlDelFlag;
    if (inc & INC_SHL_SHOT) ShlShotList mShlShot;
    if (mIsHuman && (inc & INC_KILLAREA)) s32 mEncountArea[3];  // KILLAREA PC 0x6038a0
    if (mIsHuman && (inc & INC_SAFE_POS)) NetPos mSafePos;
    if (inc & INC_ENEMYSTATUS_CTRL) EnemyStatusCtrl mEnemyStatusCtrl;
    if (inc & INC_ENEMYWAITTING) bool mEnemyWaitting;
    if (inc & INC_ENEMYSTARTWAIT) bool mEnemyStartWait;
    if (inc & INC_CORE_POINT) {   // read before DAMAGE_ACT (the PS4 and PC senders write it after;
                                  // no include mask sets both bits, P5 6)
        u16 mRegionCorePointID;
        u16 mActiveTimer;
    }
    if (inc & INC_DAMAGE_ACT) u64 mAttackParamUIDForDmVec;
    if (inc & INC_WALL_CLIMB) WallClimb mWallClimb;
    if (inc & INC_STATE_LIVE) {
        u32 mStateLive;
        if (mStateLive == 513) Pos mStateLivePos;
    }
    match (MsgId) {
        (0x0D): ActBow mActBow;
        (0x1E | 0x38): CatchRequest mCatchRequest;
        (0x1F | 0x20): CatchInfo mCatchInfo;
        (0x21 | 0x22): OmRelease<MsgId> mOmRelease;
        (0x25): StickShl mStickShl;
        (0x27): u8 mShlKillSync;                     // PC 0x6029e0
        (0x2B): SlaveDamage mSlaveDamage;
        (0x32): {                                    // PC 0x6001d0
            u16 mRegionCorePointID_Slave;
            u16 mActiveTimer_Slave;
        }
        (0x33): {                                    // PC 0x601850
            u64 mHolyAbsorpAtkUID;                   // PS4 u32
            u16 mHolyAbsorpHealVal;
        }
        (0x35): MasterParam mMasterParam;
        (0x36): CustomSkillSet mCustomSkill[2];
        (0x37): SlaveDamageSv mSlaveDamageSv;
        (0x39): u8 mCustomSkillGroup;                // PC 0x600220
        (0x3A): {                                    // PC 0x603060
            u64 mSoulAbsorpAtkUID;                   // PS4 u32
            u16 mSoulAbsorpHealVal;
        }
        (0x3B): ShlRequestFromSlave mShlRequestFromSlave;
        (0x3C): u32 unk_0x3C[4];                     // PC 0x600900, struct +0x658; context array
                                                     // cContext+0xC48, absolute (P5 1); same
                                                     // array as SetAdditional unk_u32[4] and
                                                     // 35.12.16 u32[4], cContextInstEm only
                                                     // (setter 0x479fd0, T001c 6, V); name open.
                                                     // T014b V (flow); I (role): a per-enemy work
                                                     // array synchronised to the party, read via
                                                     // getter 0x475520 by 0x851700, 0x8927f0 and
                                                     // enemy code (0xccddc0, 0xcd5c80); no string
                                                     // or PS4 member names it
        (0x3D): s32 unk_0x3D;                        // PC 0x6008a0, struct +0x668; signed gauge
                                                     // delta for uEm024000 into slot 0 of that
                                                     // array (P5 1); name open. T014b V (flow),
                                                     // name open: readers are those of unk_0x3C
        (_): {}
    }
};

// GameNormal SET_EM_DIE entry (PC 0x6014f0). Entries outside mArea < 9999, mGroup < 512,
// mSetNo < 32, mEmId < 532 are discarded by the client but still consumed.
struct EmDieData {
    u16 mArea;
    u16 mGroup;
    u16 mSetNo;
    u16 mCount;
    u16 mEmId;
};

struct PawnMsg {
    u32 mMemberIndex;
    u32 mMsgNo;
};

struct FreeMarker {
    float mPosX;
    float mPosY;
    float mPosZ;
    s32 mStageNo;
    s32 mGroupNo;
    u8 mUpdateIndex;
};

// nNetMsgData::GameNormal: PC 0x5ff130 (PS4 0x175800); GameBase PC 0x5ff030 reads nothing.
struct GameNormal<auto MsgId> {
    match (MsgId) {
        (0x1): {                       // STAGE, PC 0x601670
            s32 mStageNo;
            s32 mStartPosNo;
        }
        (0x2): u8 mReviveStock;        // PC 0x6014b0
        (0x4): {                       // FLAG, PC 0x6010c0
            s32 mFlagNum;
            u32 mFlag[std::math::max(mFlagNum, 0)];
        }
        (0x7): {                       // PAWN_MSG, PC 0x6013d0
            u32 mPawnMsgNum;
            PawnMsg mPawnMsg[mPawnMsgNum];
        }
        (0xA): {                       // SET_EM_DIE, PC 0x6014f0
            u32 mEmDieNum;             // 0 or >= 256: message rejected, nothing more read
            if (mEmDieNum != 0 && mEmDieNum < 256) EmDieData mEmDie[mEmDieNum];
        }
        (0xB): {                       // OPEN_DOOR, PC 0x601330
            u32 mDoorNum;
            u64 mUid[mDoorNum];        // PS4 u32
        }
        (0xC): {                       // FREEMARKER, PC 0x601140
            u32 mFreeMarkerNum;
            FreeMarker mFreeMarker[mFreeMarkerNum];
        }
        (0xE): {                       // PAWN_ORDER, PC 0x601470
            u32 mPawnOrderMemberIndex;
            u32 mPawnOrderNo;
        }
        (0xF): {                       // Season 3, PC 0x601060
            // T014b V (flow); I (role): GameNormal 0x0F: receive 0x894bf0 builds {u32 (+60 of the
            // message), uid (+64), uid (+72)} and adds it to the sEnemyManager +0xDB0 block (getter
            // 0xb551e0) with 0x4d3060 (...)
            u32 unk_u32;
            // T014b V (flow); I (role): first UID of the GameNormal 0x0F entry stored in the
            // sEnemyManager +0xDB0 block (0x894bf0 -> 0x4d3060); 0x5a12b0 looks up the block by a
            // pair of character UIDs (0x4d2fd0). Which UID of the pair is which was not resolved;
            // name open
            u64 unk_uid_0;             // a UID: receive 0x894bf0 looks it up (P5 2), sEnemyManager+0xDB0 block
            // T014b V (flow); I (role): second UID of the same entry; see GameNormal.unk_uid_0
            u64 unk_uid_1;             // a UID (P5 2)
        }
        (0x10): u32 unk_u32;           // Season 3, PC 0x601030; sEnemyManager+0xDB0+0x28 (P5 2)
        // 0x11, 0x12: the PC senders 0x8958b0 / 0x895870 write the u32 only when sGame+0x74 is
        // non-null, else an empty body (P5 2), so the u32 is read only when bytes remain.
        // Names of 0x0F-0x12 unresolved (T001c 6: no strings in the callers): 0x0F/0x10 feed the
        // sEnemyManager+0xDB0 block (0xb551e0), 0x11/0x12 cContextInstPl+0x3A94 (setter 0x478e40) /
        // +0x3A90 (getter 0x477380).
        (0x11 | 0x12): {               // Season 3, PC 0x601300 / 0x6012d0
            if ($ + 4 <= parent.msgEnd) u32 unk_u32;
        }
        (_): {}
    }
};

// GameEasy PRT_SET entry (PC 0x600d10). Wire order V (T001c 4): the PC decoder stores each field in
// the slot of PS4 DWARF nNetMsgData::GameEasy::stPRTData {u16 mStageNo +0, u16 mQuestNo +2,
// u8 mBlockNo +4, u8 mProcessNo +5, u32 mSetMember +8, stVector3 mPos +12, f32 mScale +24}, and the
// sender 0x895163 writes the same order. The PC client always sends mSetMember = 0.
struct PRTSet {
    u32 mSetMember;
    u16 mStageNo;
    u16 mQuestNo;
    u8 mBlockNo;
    u8 mProcessNo;
    float mPosX;
    float mPosY;
    float mPosZ;
    float mScale;   // sender default 1.0f
};

// nNetMsgData::GameEasy: PC 0x5ff050 (PS4 0x1761c0). PC ids = PS4 ids + 4.
struct GameEasy<auto MsgId> {
    u8 mType;
    match (MsgId) {
        (0x15): {                      // PRT_SET, PC 0x600d10
            u32 mPRTNum;               // clamped to 30 on receive; sender 0x895163 does not clamp
            PRTSet mPRT[std::math::min(mPRTNum, 30)];
        }
        (0x16): {                      // PRT_INFO, PC 0x600be0
            u64 mPRTUniqueId;          // PS4 u32
            bool mIsFinalAnswer;
            bool mIsCancel;
            bool mIsAdvance;
            bool mIsReady;
            bool mIsReadyOK;
        }
        (0x17): {                      // AREA_RELEASE, PC 0x600ab0
            u32 mAreaReleaseIdNum;     // clamped to 200 on receive; sender 0x8953a5 does not clamp
            u32 mAreaReleaseId[std::math::min(mAreaReleaseIdNum, 200)];
        }
        (0x18): {                      // EVENT, PC 0x600b40. Sender 0x8953f6 writes 0/1 flags: its
                                       // own member's bit in sEventManager +0xE4/+0xE8/+0xEC (T001c 4)
            u32 mReadyBit;
            u32 mCancelBit;
            u32 mFinishBit;
        }
        (0x19): {                      // NPC_MESSAGE, PC 0x600b90
            u32 mEventMsgType;
            u32 mEventQstNo;
            u32 mEventMsgGrpNo;
        }
        (_): {}                        // WEAPON_LOAD, AREA_JUMP_SYNC: nothing beyond mType
    }
};

struct SetMaster {
    u64 mUniqueId;     // PS4 u32
    s32 mMasterIndex;
};

struct SetRequestCreateContext {
    u32 mId;
    u64 mUniqueId;     // PS4 u32
    s32 mStageNo;
    s32 mEncountArea;
};

// receiveMsgSetCreateContext: PC 0x601b80 (PS4 0x177060). On both platforms the whole tail,
// including the s32, is read only when mAdditionalData != 0 (P2 2.25; P5 3: PS4 0x177060 returns
// when it is zero).
struct SetCreateContext {
    u32 mId;
    u64 mUniqueId;          // PS4 u32
    s32 mStageNo;
    s32 mEncountArea;
    bool mAdditionalData;
    if (mAdditionalData) {
        s32 mMasterIndex;   // P1's mMasterIndex slot (+0x5C)
        Pos mPos;
        float mAngleY;
        ActionNo mAction;
        u64 mHp[10];        // HP_DATATYPE is 8 bytes
        u16 mUseRegionBit;
        u64 mHpWhite;
        u16 mCommonWork;
        u16 mCustomWork;
        u32 mOcdActiveMsgNum;  // clamped to 100 (PS4 75)
        OcdActiveMsg mOcdActiveMsgArray[std::math::min(mOcdActiveMsgNum, 100)];
        float mEnchantRate;
        float mAilmentDamage;
        CliffHang mCliffHang;
        EnemyClimb mEnemyClimb;
        u64 mTargetUid;     // PS4 u32
        NetPos mTargetPos;
        s32 mEncountAreaBuff[3];
        u32 mEnemyStatusGroupNoNum;  // >= 16 -> 0
        EnemyStatusGroup mGroups[mEnemyStatusGroupNoNum < 16 ? mEnemyStatusGroupNoNum : 0];
        u64 mEnemyBitCtrlCollision;
        u8 mEnemyCtrlRegionSelectNo;
        u64 mEnemyBitCtrlParts;
        u64 mEnemyBitCtrlWorkRate;
        u64 mEnemyBitCtrlScale;
        u64 mEnemyBitCtrlMontage;
        u32 mEnemyBitCtrlSyncBit;
        u64 mAttackParamUIDForDmVec;
        WallClimb mWallClimb;
        u32 mStateLive;
        u8 mCatchType;
        u8 mCatchJointNo;
        u64 mCatchTargetUID;  // PS4 u32
        // Season 3: the caught triple by shape (inferred, shape; T001c 6, I): same shape after the
        // catch triple as cpCatchCtrl::mCaughtInfo; no consumer found in defined code.
        u8 mCaughtType;       // struct +0x458 (inferred, shape)
        u8 mCaughtJointNo;    // struct +0x459 (inferred, shape)
        u64 mCaughtUid;       // struct +0x460 (inferred, shape)
    }
};

// nNetMsgData::SetNormal: PC 0x5ff2e0 (jump table 0x5ff39c; PS4 0x176ad0). SetBase reads nothing.
// No group 0x43 message was captured.
struct SetNormal<auto MsgId> {
    match (MsgId) {
        (0x2 | 0x4): {                 // REQUEST_MASTER PC 0x602900, RELEASE_MASTER PC 0x602770
            s32 mNum;
            u64 mUniqueId[std::math::max(mNum, 0)];  // PS4 u32
        }
        (0x3): {                       // CHANGE_MASTER, PC 0x601ab0
            s32 mChangeNum;
            SetMaster mChange[std::math::max(mChangeNum, 0)];
        }
        (0x5): {                       // MASTER_INFO, PC 0x602670
            s32 mInfoNum;
            SetMaster mInfo[std::math::max(mInfoNum, 0)];
            bool mTerminateFlag;
        }
        (0x6): {                       // THROW_MASTER, PC 0x6029a0
            u64 mThrowUniqueId;        // PS4 u32
            s32 mThrowIndex;
        }
        (0x7): {                       // REQUEST_CREATE_CONTEXT, PC 0x602810
            s32 mRequestNum;
            SetRequestCreateContext mRequest[std::math::max(mRequestNum, 0)];
        }
        (0x8): SetCreateContext mCreateContextInfo;
        (_): {}
    }
};

struct DamageProfileNode {
    u32 mDpsHandle;
    u64 mProfileTargetUID;     // PS4 u32
    u64 mProfileAttackerUID;   // PS4 u32
    u8 mProfileUnitState;
    u8 mProfileRegionNo_HP;
    u8 mProfileRegionNo_SH;
    u64 mProfileDamage;
    float mProfileShrink;
    float mProfileBlow;
    float mProfileShake;
    float mProfileDown;
    bool mProfileIsShrink;
    bool mProfileIsBlow;
    bool mProfileIsShake;
    bool mProfileIsDown;
    bool mProfileIsToMain;
};

// nNetMsgData::ToolEasy: PC 0x5ff3e0 (jump table 0x5ff468; PS4 0x177d90). ToolBase and
// ToolNormal read nothing (checked on PC: 0x5ff3c0, 0x5ff480; P5 5).
struct ToolEasy<auto MsgId> {
    match (MsgId) {
        (0x4): u8 mDipData[448];       // DIP, PC 0x6008d0
        (0x5): {                       // DAMAGE_PROFILE_START, PC 0x600820
            u32 mDpsHandle;
            u64 mProfileTargetID;      // PS4 u32
            u64 mProfileAttckerID[8];  // PS4 u32
        }
        (0x6): u32 mDpsHandle;         // DAMAGE_PROFILE_END, PC 0x600430
        (0x7): DamageProfileNode mNode;  // PC 0x600460
        (_): {}
    }
};

// ---------------------------------------------------------------------------------------------
// One nNetMsg of Len bytes (the packet's len). Never fails on an unknown id: what is not decoded
// ends in `unparsed`.
// ---------------------------------------------------------------------------------------------

struct NetMsg<auto Len> {
    // len is an s32: a negative value would move the cursor backwards (R1 F8).
    std::assert(Len >= 0, "negative nNetMsg len");
    u128 msgStart = $;
    u128 msgEnd = msgStart + Len;
    bool known = false;
    str msgIdFull = "SHORT";   // read by the packet patterns, which export it
    if (Len >= 20) {
        Head head;
        u32 msgClass = head.mMsgIdFull & 0xFFFFFF00;
        u8 msgId = head.mMsgIdFull & 0xFF;
        msgIdFull = std::format("0x{:08X}", head.mMsgIdFull);
        match (msgClass) {
            (0x40010000): {
                NET_MSG_ID msgName @ addressof(head.mMsgIdFull) + 3;
                CtrlBase ctrlBase;
                CtrlAction<msgId> ctrlAction;
                known = true;
            }
            (0x41000000): {
                NET_MSG_ID_GAME msgName @ addressof(head.mMsgIdFull) + 3;
                GameNormal<msgId> gameNormal;
                known = true;
            }
            (0x41010000): {
                NET_MSG_ID_GAME_EASY msgName @ addressof(head.mMsgIdFull) + 3;
                GameEasy<msgId> gameEasy;
                known = true;
            }
            (0x43000000): {
                NET_MSG_ID_SET msgName @ addressof(head.mMsgIdFull) + 3;
                SetNormal<msgId> setNormal;
                known = true;
            }
            (0x4F000000): {
                NET_MSG_ID_TOOL msgName @ addressof(head.mMsgIdFull) + 3;
                known = true;          // ToolNormal reads nothing
            }
            (0x4F010000): {
                NET_MSG_ID_TOOL_EASY msgName @ addressof(head.mMsgIdFull) + 3;
                ToolEasy<msgId> toolEasy;
                known = true;
            }
            (_): {}
        }
    }
    bool fits = known && $ == msgEnd;  // read by the packet patterns, which export it
    if ($ < msgEnd) u8 unparsed[msgEnd - $];
    $ = msgEnd;
};

// Lobby data (3.3.16, 3.4.16): cLobbyDataMessage::deserialize, PC 0x898050 (PS4 0x392490). A first
// s32 of 0 is the non-RPC dummy `00000000 <s32 mMsgType>`; anything else is an RPC NetMsg whose
// Head.mSessionId is that value.
struct LobbyDataMessage<auto Len> {
    std::assert(Len >= 0, "negative lobby data len");  // R1 F8
    u128 dataStart = $;
    bool fits = false;
    str msgIdFull = "";
    if (Len >= 4 && std::mem::read_unsigned($, 4, std::mem::Endian::Big) == 0) {
        s32 zero;
        LOBBY_MSG_TYPE mMsgType;
        msgIdFull = "LOBBY_DUMMY";
        fits = $ == dataStart + Len;
        if ($ < dataStart + Len) u8 unparsed[dataStart + Len - $];
    } else {
        NetMsg<Len> msg;
        msgIdFull = msg.msgIdFull;
        fits = msg.fits;
    }
    $ = dataStart + Len;
};
