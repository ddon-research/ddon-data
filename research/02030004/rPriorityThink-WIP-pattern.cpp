#define f32 float
#define cAIPawnOrderFlag nDDOUtility_cBitSet
#define cAIPawnOrderTypeFlag nDDOUtility_cBitSet
#define cPrioThkRetActFlag nDDOUtility_cBitSet
#define cPrioThkCmdRetHealAct_cFlag nDDOUtility_cBitSet

struct MtVector3
{
  float x;
  float y;
  float z;
};

struct MtObject
{
};

struct cAIResource : MtObject
{
};

struct MtArray
{
  u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
  T arr[mLength];
};

struct rTbl2Base
{
  u32 version;
  u32;
};

struct nDDOUtility_cBitSet
{
  u32 mLength;
  if (mLength > 0)
    u32 mBit[mLength];
};

struct cPawnEnableArea : MtObject
{
  f32 mMinXZ;
  f32 mMaxXZ;
  f32 mMinY;
  f32 mMaxY;
  f32 mRadius;
};

struct cPrioThkCmd : cAIResource
{
};

struct cPrioThkCmdIsBase : cPrioThkCmd
{
  bool mIs;
};

struct cPrioThkCmdConFollowArea : cPrioThkCmd
{
  u32 mAreaType;
  cPawnEnableArea mAreaEnable;
  u32 mAreaPosType;
  f32 mAreaPosOfsZ;
  bool mNoContinue;
};

struct cPrioThkCmdConSpotExt : cPrioThkCmd
{
  u32 mShlId;
  f32 mLength;
  f32 mThroughLength;
  f32 mFollowRange;
};

struct cPrioThkCmdConSpot : cPrioThkCmd
{
  u32 mShlId;
  f32 mLength;
  f32 mFollowRange;
};

struct cPrioThkCmdConCureSpot : cPrioThkCmd
{
};

struct cPrioThkCmdConHealSpot : cPrioThkCmd
{
};

struct cPrioThkCmdConHealFountain : cPrioThkCmd
{
};

struct cPrioThkCmdConEventOmElf : cPrioThkCmd
{
};

struct cPrioThkCmdRetActGoldBurst : cPrioThkCmd
{
  cPrioThkRetActFlag mRetActFlag;
};

struct cPrioThkCmdRetFreeParam : cPrioThkCmd
{
  // TODO: Verify
  // nDDOUtility::cArray<f32,4> mFreeParamF32;
  u32 length;
  if (length)
    f32 mFreeParamF32[4];
};

struct cPrioThkCmdRetStaminaHealAct : cPrioThkCmd
{
};

struct cPrioThkCmdRetCureAct : cPrioThkCmd
{
};

struct cPrioThkCmdRetHealAct : cPrioThkCmd
{
  cPrioThkCmdRetHealAct_cFlag mPrioThkHealActFlag;
};

struct cPrioThkCmdRetDispersion : cPrioThkCmd
{
};

struct cPrioThkCmdRetFollow : cPrioThkCmd
{
  u32 mReqMoveType;
};

struct cPrioThkCmdRetOrder : cPrioThkCmd
{
  u32 mOrderGroup;
};

struct cPrioThkCmdRetNoMoveJump : cPrioThkCmd
{
};

struct cPrioThkCmdRetRouteInfo : cPrioThkCmd
{
};

struct cPrioThkCmdRetGoto : cPrioThkCmd
{
  u32 mReqTargetType;
  MtVector3 mReqTargetRealPos;
  f32 mReqTargetRange;
  u32 mReqMoveType;
};

struct cPrioThkCmdRetActGroup : cPrioThkCmd
{
  u32 mActionInterfaceGroup;
  u32 mReqTargetType;
  u32 mReqTargetFrameType;
  f32 mReqTargetFrame;
  MtVector3 mReqTargetRealPos;
  cPrioThkRetActFlag mRetActFlag;
  bool mReqUseEmChecker;
};

struct cPrioThkCmdRetActInterTarget : cPrioThkCmd
{
  u32 mActionInterfaceID;
  cPrioThkRetActFlag mRetActFlag;
};

struct cPrioThkCmdRetActInter : cPrioThkCmd
{
  u32 mActionInterfaceID;
  u32 mReqTargetType;
  u32 mReqTargetFrameType;
  f32 mReqTargetFrame;
  MtVector3 mReqTargetRealPos;
  cPrioThkRetActFlag mRetActFlag;
};

struct cPrioThkCmdRetSupport : cPrioThkCmd
{
};

struct cPrioThkCmdIsBattle : cPrioThkCmdIsBase
{
};

struct cPrioThkCmdIsAutoSituation : cPrioThkCmdIsBase
{
  u32 mAutoSituation;
};

struct cPrioThkCmdPointer : cAIResource
{
  u32 dtiID;

  match(dtiID)
  {
    (738809866) : cPrioThkCmdIsBattle PrioThkCmdIsBattle;
    (1682618329) : cPrioThkCmdIsAutoSituation PrioThkCmdIsAutoSituation;
    (204687719) : cPrioThkCmdRetActInter PrioThkCmdRetActInter;
  }
};

struct cPrioThkCode : cAIResource
{
  MtTypedArray<cPrioThkCmdPointer> mCommands;
  s32 mPrio;
  u32 mID;
  cAIPawnOrderFlag mDisableOrder;
  cAIPawnOrderTypeFlag mDisableTypeFlag;
  u32 mCodeFlag;
};

struct rTbl2<cPrioThkCode> : rTbl2Base
{
  u32 mDataNum;
  cPrioThkCode mpData[2];
};

struct rPriorityThink : rTbl2<cPrioThkCode>
{
};

rPriorityThink rprioritythink_at_0x00 @0x00;