#pragma endian big

#define f32 float
#define HP_DATATYPE u64
#define f64 double

struct MtTypedArray<T>
{
    u32 arraySize;
    T array[arraySize];
};

enum nNetMsgData_nGame_NET_MSG_ID_GAME : u16
{
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

};

enum nNetMsgData_nGame_NET_MSG_ID_GAME_EASY : u16
{
    NET_MSG_ID_GAME_EASY_NOTHING = 0xF,
    NET_MSG_ID_GAME_EASY_WEAPON_LOAD = 0x10,
    NET_MSG_ID_GAME_EASY_PRT_SET = 0x11,
    NET_MSG_ID_GAME_EASY_PRT_INFO = 0x12,
    NET_MSG_ID_GAME_EASY_AREA_RELEASE = 0x13,
    NET_MSG_ID_GAME_EASY_EVENT = 0x14,
    NET_MSG_ID_GAME_EASY_NPC_MESSAGE = 0x15,
    NET_MSG_ID_GAME_EASY_AREA_JUMP_SYNC = 0x16,

};

enum nNetMsgData_nSetMgr_NET_MSG_ID_SET : u16
{
    NET_MSG_ID_SET_NOTHING = 0x0,
    NET_MSG_ID_SET_BASE = 0x1,
    NET_MSG_ID_SET_REQUEST_MASTER = 0x2,
    NET_MSG_ID_SET_CHANGE_MASTER = 0x3,
    NET_MSG_ID_SET_RELEASE_MASTER = 0x4,
    NET_MSG_ID_SET_MASTER_INFO = 0x5,
    NET_MSG_ID_SET_THROW_MASTER = 0x6,
    NET_MSG_ID_SET_REQUEST_CREATE_CONTEXT = 0x7,
    NET_MSG_ID_SET_CREATE_CONTEXT = 0x8,

};

enum nNetMsgData_nItemMgr_NET_MSG_ID_ITEM : u16
{
    NET_MSG_ID_ITEM_NOTHING = 0x0,

};

enum nNetMsgData_nTool_NET_MSG_ID_TOOL : u16
{
    NET_MSG_ID_TOOL_NOTHING = 0x0,
    NET_MSG_ID_TOOL_BASE = 0x1,
    NET_MSG_ID_TOOL_PAWN_SET = 0x2,

};

enum nNetMsgData_nTool_NET_MSG_ID_TOOL_EASY : u16
{
    NET_MSG_ID_TOOL_EASY_NOTHING = 0x3,
    NET_MSG_ID_TOOL_EASY_DIP = 0x4,
    NET_MSG_ID_TOOL_EASY_DAMAGE_PROFILE_START = 0x5,
    NET_MSG_ID_TOOL_EASY_DAMAGE_PROFILE_END = 0x6,
    NET_MSG_ID_TOOL_EASY_DAMAGE_PROFILE_NODE = 0x7,
    NET_MSG_ID_TOOL_EASY_TEST = 0x8,

};

enum nNetMsgData_nCtrl_NET_MSG_ID : u16
{
    NET_MSG_ID_NOTHING = 0x0,
    NET_MSG_ID_ACT_BASE = 0x1,
    NET_MSG_ID_ACT_NORMAL = 0x2,
    NET_MSG_ID_ACT_NORMAL_EX = 0x3,
    NET_MSG_ID_ACT_RESET = 0x4,
    NET_MSG_ID_ACT_RESET_EX = 0x5,
    NET_MSG_ID_ACT_ACTION_ONLY = 0x6,
    NET_MSG_ID_ACT_ACTION_ONLY_EX = 0x7,
    NET_MSG_ID_ACT_SHL_SHOT = 0x8,
    NET_MSG_ID_ACT_TARGET = 0x9,
    NET_MSG_ID_ACT_DIE = 0xA,
    NET_MSG_ID_ACT_ENEMY_CLIMB = 0xB,
    NET_MSG_ID_ACT_CLIFF_HANG = 0xC,
    NET_MSG_ID_ACT_BOW = 0xD,
    NET_MSG_ID_ACT_REVIVE_CMC = 0xE,
    NET_MSG_ID_ACT_WAND_MAGIC_SHL_SET = 0xF,
    NET_MSG_ID_ACT_MAGIC_ITEM = 0x10,
    NET_MSG_ID_ACT_THROW_ITEM = 0x11,
    NET_MSG_ID_ACT_LIFT_BIGIN_ITEM = 0x12,
    NET_MSG_ID_ACT_RESPAWN = 0x13,
    NET_MSG_ID_ACT_WALL_CLIMB = 0x14,
    NET_MSG_ID_PERIODIC_TOP = 0x15,
    NET_MSG_ID_PERIODIC_NORMAL = 0x15,
    NET_MSG_ID_PERIODIC_ANGLE_Y = 0x16,
    NET_MSG_ID_PERIODIC_POS = 0x17,
    NET_MSG_ID_PERIODIC_CONDITION = 0x18,
    NET_MSG_ID_PERIODIC_TARGET = 0x19,
    NET_MSG_ID_PERIODIC_NOTHING = 0x1A,
    NET_MSG_ID_PERIODIC_CATCH = 0x1B,
    NET_MSG_ID_PERIODIC_ENEMY_CLIMB = 0x1C,
    NET_MSG_ID_PERIODIC_END = 0x1C,
    NET_MSG_ID_PERIODIC_INTERFACE = 0x1D,
    NET_MSG_ID_PERIODIC_BOTTOM = 0x1E,
    NET_MSG_ID_CATCH_REQUEST = 0x1E,
    NET_MSG_ID_CAUGHT_RESULT = 0x1F, //=> cContextInterface::isCaughtResult
    NET_MSG_ID_ACT_CAUGHT = 0x20,
    NET_MSG_ID_OM_PUT = 0x21,     //=> cContextInterface::getIsOmReleasePut
    NET_MSG_ID_OM_THROW = 0x22,   //=> cContextInterface::getIsOmReleaseThrow
    NET_MSG_ID_SHL_DELETE = 0x23, //=> cContextInterface::getShlDelte
    NET_MSG_ID_SHL_SHOT = 0x24,   //=> cContextInterface::isShotReqNoAct
    NET_MSG_ID_STICK_SHL = 0x25,  //=>cContextInterface::requestShlStickInfoContext
    NET_MSG_SHL_SLAVE_KILL_SEND = 0x26,
    NET_MSG_SHL_KILL_SYNC = 0x27,
    NET_MSG_STATE_LIVE = 0x28,
    NET_MSG_ID_EM5800 = 0x29,
    NET_MSG_ID_TARGET = 0x2A,
    NET_MSG_ID_SLAVE_DAMAGE = 0x2B,
    NET_MSG_ID_ACT_RESCUE = 0x2C,
    NET_MSG_ID_ACT_RESCUE_ONLY = 0x2D,
    NET_MSG_ID_ENEMYSTATUS_CTRL = 0x2E, //=> cContextInterface::setEnemyStatusChange
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

    NET_MSG_ID_ACT_LOBBY_OFF = 0x80,
    NET_MSG_ID_DEFAULT = 0xFF,
    NET_MSG_ID_PERIODIC_DEFAULT = 0xFF,
};

enum nNetMsg_MSG_PRIO : s32
{
    MSG_PRIO_MAX = 0x10,
    MSG_PRIO_HIGH = 0xF,
    MSG_PRIO_NORMAL = 0x4,
    MSG_PRIO_LOW = 0x0,
    MSG_PRIO_H_H = 0xF,
    MSG_PRIO_H_N = 0xE,
    MSG_PRIO_H_L = 0xD,
    MSG_PRIO_N_H = 0x6,
    MSG_PRIO_N_N = 0x5,
    MSG_PRIO_N_L = 0x4,
    MSG_PRIO_L_H = 0x2,
    MSG_PRIO_L_N = 0x1,
    MSG_PRIO_L_L = 0x0,
    MSG_PRIO_DEFAULT = 0xFFFFFFFF,
};

enum nNetMsg_MSG_ADR : s32
{
    MSG_ADR_LOCAL = 0x0,
    MSG_ADR_ALL = 0x1,
    MSG_ADR_OTHER = 0x2,
    MSG_ADR_PEER = 0x3,
    MSG_ADR_SERVER = 0x4,
    MSG_ADR_MAX = 0x5,
    MSG_ADR_DEFAULT = 0xFFFFFFFF,
};

enum nNetSv_LOBBY_MSG_TYPE : s32
{
    LOBBY_MSG_PEER = 0x0,
    LOBBY_MSG_OTHER = 0x1,
    LOBBY_MSG_ALL = 0x2,
    LOBBY_MSG_ALL_AND_PARTY = 0x3,
    LOBBY_MSG_SERVER = 0x4,
};

enum NET_MSG_DTI : u16
{
    cNetMsgCtrlAction = 0x4001u, // MtDTI_MtDTI_0(&stru_2544948, "cNetMsgCtrlAction", &stru_2544910, 0x78uLL, 0x40010000u, 0, 0);
    cNetMsgToolNormal = 0x4F00u,
    cNetMsgToolEasy = 0x4F01u,
    cNetMsgSetNormal = 0x4300u,
    cNetMsgGameNormal = 0x4100u,
    cNetMsgGameEasy = 0x4101u
};

enum RPC_ID : u32
{
    sGame = 1010,
    sSetManager = 1030,

};

struct MtVector3
{
    f32 x;
    f32 y;
    f32 z;
    f32 pad_;
};

struct nNetMsgData_Head_stMsgHead
{
    s32 mSessionId;
    u32 mRpcId;
    u32 mMsgIdFull;
    u32 mSearchId;
};

struct MtObject
{
};

struct cRemoteCall : MtObject
{
    // u32 mAttribute;
};

struct RpcTypeSet : cRemoteCall
{
};

struct nNetMsg_cNetMsgBase : RpcTypeSet
{
    // MtMemoryStream *mpStream;
    // nNetMsg::cCoder mCod;
    // nNetMsg::cDecoder mDec;
    // nNetBase::cNetBase *mpNetBase;
    // nNetMsgData_Head_stMsgHead mpMsgHead; //*
    // u32 mCharacterId;
    // u32 mIncludePacket;
    // u32 mSessionInstanceIndex;
    // u8 mMsgGroup;
    // u8 mMsgId;
    // nNetMsg_MSG_ADR mAdr;
    // nNetMsgData_Base_stMsgBaseData *mpMsgBaseData;
};

struct nNetBase_cNetBase //: cRemoteProcedure
{
    u8 mGroup;
    u8 mId;
    u8 mType;
    u8 mKind;
    u32 mRpcId;
    u32 mLastSendFrame;
    nNetMsg_MSG_PRIO mPrio;
    nNetMsg_MSG_ADR mAdr;
    u32 mCharacterId;
    u8 mLastSendMsgId;
    u8 mLastRecvMsgId;
};

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct nNetMsgData_GameNormal_stFlagData
{
    u32 mFlag;
};

struct nNetMsgData_GameNormal_stPawnMsg
{
    u32 mMemberIndex;
    u32 mMsgNo;
};

struct nNetMsgData_GameNormal_stEmDieData
{
    u16 mArea;
    u16 mGroup;
    u16 mSetNo;
    u16 mCount;
    u16 mEmId;
};

struct nNetMsgData_GameNormal_stDoorData
{
    u32 mUid;
};

struct nNetMsgData_GameNormal_stFreeMarker
{
    f32 mPosXFreeMarker;
    f32 mPosYFreeMarker;
    f32 mPosZFreeMarker;
    s32 mStageNoFreeMarker;
    s32 mGroupNoFreeMarker;
    u8 mUpdateIndex;
};

struct nNetMsgData_GameNormal_stMsgGameNormalData
{
    // based on NET_MSG_ID a different object has to be deserialized
    s32 mStageNo;
    s32 mStartPosNo;
    // u8 mReviveStock;
    // s32 mFlagNum;
    // nNetMsgData_GameNormal_stFlagData mpFlagData[mFlagNum];
    // u32 mPawnMsgNum;
    // nNetMsgData_GameNormal_stPawnMsg mpPawnMsg[mPawnMsg];
    // u32 mEmDieNum;
    // nNetMsgData_GameNormal_stEmDieData mpEmDieData[mEmDieNum];
    // u32 mDoorNum;
    // nNetMsgData_GameNormal_stDoorData mpDoorData[mDoorNum];
    // u32 mFreeMarkerNum;
    // nNetMsgData_GameNormal_stFreeMarker mpFreeMarker[mFreeMarkerNum];
    // u32 mPawnOrderMemberIndex;
    // u32 mPawnOrderNo;
};

struct nNetMsgData_GameNormal_stMsgGameNormalData_SET_EM_DIE
{
    u32 mEmDieNum;
    nNetMsgData_GameNormal_stEmDieData mpEmDieData[mEmDieNum];
};

struct nNetMsgData_GameNormal_stMsgGameNormalData_STAGE
{
    s32 mStageNo;
    s32 mStartPosNo;
};

struct nNetMsgData_GameBase_stMsgGameBaseData
{
    s32 dummy;
};

struct nNetMsg_cNetMsgGameBase : nNetMsg_cNetMsgBase
{
    nNetMsgData_GameBase_stMsgGameBaseData mpMsgGameBaseData;
};

struct nNetMsg_cNetMsgGameNormal : nNetMsg_cNetMsgGameBase
{
    nNetMsgData_GameNormal_stMsgGameNormalData mpMsgGameNormalData;
};

struct nNetMsg_cNetMsgGameNormal_STAGE : nNetMsg_cNetMsgGameBase
{
    nNetMsgData_GameNormal_stMsgGameNormalData_STAGE mpMsgGameNormalData;
};

struct nNetMsg_cNetMsgGameNormal_SET_EM_DIE : nNetMsg_cNetMsgGameBase
{
    nNetMsgData_GameNormal_stMsgGameNormalData_SET_EM_DIE mpMsgGameNormalData;
};

struct nNetMsgData_CtrlBase_stMsgCtrlBaseData
{
    u32 mUniqueId;
};

struct nNetMsg_cNetMsgCtrlBase : nNetMsg_cNetMsgBase
{
    nNetMsgData_CtrlBase_stMsgCtrlBaseData mpMsgCtrlBaseData;
};

struct nNetMsg_cNetMsgCtrlAction : nNetMsg_cNetMsgCtrlBase
{
    // nNetMsgData_CtrlAction_stMsgCtrlActionData mpMsgCtrlActionData;
};

struct nNetMsgData_stNetPos
{
    f64 x;
    f32 y;
    f64 z;
};

struct nObjCondition_stOcdActiveMsg
{
    u8 mOcdUIDMsg;
    u8 mOcdActiveLvMsg;
    bool mIsStandby;
};

struct nNetMsgData_CtrlAction_stMsgCtrlActionData_ACT_NORMAL
{
    // bool mIsEnemy;
    // bool mIsCharacter;
    // bool mIsHuman;
    // bool mIsEnemyLarge;
    nNetMsgData_stNetPos mPos;
    f32 mMoveSpeed;
    f32 mMoveAngle;
    f32 mAngleY;
    u32 mActNo;
    // u8 mActReqPrio;
    // u16 mActAtkAdjustUniqueId;
    // u32 mActFreeWork;
    // HP_DATATYPE mHp;
    // u16 mUseRegionBit;
    // u64 mRegionRateBit;
    // HP_DATATYPE mHpWhite;
    // u32 mStamina;
    // u16 mCommonWork;
    // u16 mCustomWork;
    // u32 mOcdActiveMsgNum;
};

struct nNetMsg_cNetMsgCtrlAction_ACT_NORMAL : nNetMsg_cNetMsgCtrlBase
{
    nNetMsgData_CtrlAction_stMsgCtrlActionData_ACT_NORMAL mpMsgCtrlActionData;
};

struct CPacket_C2S_SEND_BINARY_MSG_NOTICE : CPacket
{
    MtTypedArray<u32> CharacterIDList;
    u32 netMsgSize;
    u32 unknown1;
    u32 unknown2;
    u32 RpcId;

    NET_MSG_DTI netMsgDTI;
    if (netMsgDTI == NET_MSG_DTI::cNetMsgCtrlAction)
    {
        nNetMsgData_nCtrl_NET_MSG_ID msgId;
        // if (msgId == nNetMsgData_nCtrl_NET_MSG_ID::NET_MSG_ID_ACT_NORMAL)
        //     nNetMsg_cNetMsgCtrlAction_ACT_NORMAL msg;
    }

    if (netMsgDTI == NET_MSG_DTI::cNetMsgToolNormal)
    {
        nNetMsgData_nTool_NET_MSG_ID_TOOL msgId;
    }

    if (netMsgDTI == NET_MSG_DTI::cNetMsgToolEasy)
        nNetMsgData_nTool_NET_MSG_ID_TOOL_EASY msgId;

    if (netMsgDTI == NET_MSG_DTI::cNetMsgSetNormal)
        nNetMsgData_nSetMgr_NET_MSG_ID_SET msgId;

    if (netMsgDTI == NET_MSG_DTI::cNetMsgGameNormal)
    {
        nNetMsgData_nGame_NET_MSG_ID_GAME msgId;
        if (msgId == nNetMsgData_nGame_NET_MSG_ID_GAME::NET_MSG_ID_GAME_STAGE)
            nNetMsg_cNetMsgGameNormal_STAGE msg;
        if (msgId == nNetMsgData_nGame_NET_MSG_ID_GAME::NET_MSG_ID_GAME_SET_EM_DIE)
            nNetMsg_cNetMsgGameNormal_SET_EM_DIE msg;
    }

    if (netMsgDTI == NET_MSG_DTI::cNetMsgGameEasy)
        nNetMsgData_nGame_NET_MSG_ID_GAME_EASY msgId;
};

CPacket_C2S_SEND_BINARY_MSG_NOTICE C2S_SEND_BINARY_MSG_NOTICE @0x00;