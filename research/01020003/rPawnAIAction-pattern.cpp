#define f32 float
#define cPawnAIActComCtrlFlag nDDOUtility_cBitSet
#define cAIPawnActionGroupFlag nDDOUtility_cBitSet
#define cPawnAIActCancelFlag nDDOUtility_cBitSet
#define cPawnAIActComCheckFlag nDDOUtility_cBitSet
#define cAIPawnActSupportFlag nDDOUtility_cBitSet
#define cPawnActInterActNo_cOptFlag nDDOUtility_cBitSet
#define cPawnActInterGuard_cOptFlag nDDOUtility_cBitSet
#define cPawnActInterEnemyClimbMove_cOptFlag nDDOUtility_cBitSet
#define cPawnActInterSearchCorePoint_cOptFlag nDDOUtility_cBitSet
#define cPawnActInterMove_cOptFlag nDDOUtility_cBitSet

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
    u32;
};

struct nDDOUtility_cBitSet
{
    u32 mLength;
    if(mLength>0)
        u32 mBit[mLength];
};

struct cPawnActInterBase : MtObject
{
    f32 mLifeFrame;
    u32 mDisableNotice;
};

struct cPawnActInterCommon : cPawnActInterBase
{
  cPawnAIActCancelFlag mCancelFlag;
};

struct cPawnActInterBreak : cPawnActInterBase
{
  cPawnAIActComCtrlFlag mComFlag;
  u32 mComOrderID;
};

struct cPawnActInterWaitFootwork : cPawnActInterBase
{
};

struct cPawnActInterTalkToPl : cPawnActInterBase
{
};

struct cPawnActInterActNo : cPawnActInterBase
{
  u32 mDoActType;
  u32 mDoActNo;
  u32 mDoAutoSituation;
  f32 mDoEndMinFrame;
  cPawnActInterActNo_cOptFlag mOptFlag;
};

struct cPawnActInterMoveEnergySpot : cPawnActInterBase
{
};

struct cPawnActInterLantern : cPawnActInterBase
{
  bool mOnLantern;
};

struct cPawnActInterRecover : cPawnActInterBase
{
  bool mIsTargetErosion;
};

struct cPawnActInterWait : cPawnActInterBase
{
  bool mOrderClear;
  f32 mWaitTime;
};

struct cPawnActInterReload : cPawnActInterBase
{
  u32 mReloadType;
};

struct cPawnActInterWarp : cPawnActInterBase
{
};

struct cPawnActInterAtkHerald : cPawnActInterBase
{
  u32 mDoActNo;
};

struct cPawnActInterAutoMotion : cPawnActInterBase
{
  u32 mAutoMotSituation;
  bool mSetEmotion;
};

struct cPawnActInterCliffClimb : cPawnActInterBase
{
};

struct cPawnActInterClimbBegin : cPawnActInterBase
{
};

struct cPawnActInterEscape : cPawnActInterBase
{
  f32 mAngle;
};

struct cPawnActInterGuardCancel : cPawnActInterBase
{
};

struct cPawnActInterGuard : cPawnActInterBase
{
  cPawnActInterGuard_cOptFlag mOptFlag;
  f32 mMinGuardTime;
};

struct cPawnActInterMoveJump : cPawnActInterBase
{
  u32 mJumpFlag;
  f32 mHeightCheckLow;
  f32 mHeightCheckHigh;
};

struct cPawnActInterEscapeNotice : cPawnActInterBase
{
  u32 mNoticeFlag;
};

struct cPawnActInterDamage : cPawnActInterBase
{
};

struct cPawnActInterEnemyClimbAttack : cPawnActInterBase
{
  u32 mType;
  u32 mTrgType;
  bool mClimbTargetOnly;
  bool mIsUseUpGradeSkill;
};

struct cPawnActInterEnemyClimbMove : cPawnActInterBase
{
  cPawnActInterEnemyClimbMove_cOptFlag mOptFlag;
};

struct cPawnActInterEnemyClimb : cPawnActInterBase
{
  u32 mEnemyStatus;
};

struct cPawnActInterHoldWait : cPawnActInterBase
{
};

struct cPawnActInterHold : cPawnActInterBase
{
};

struct cPawnActInterStandOffHmEm : cPawnActInterBase
{
  bool mRoateR;
  f32 mStandOffFrame;
};

struct cPawnActInterStandOff : cPawnActInterBase
{
  f32 mStandOffFrame;
};

struct cPawnEnableArea : MtObject
{
  f32 mMinXZ;
  f32 mMaxXZ;
  f32 mMinY;
  f32 mMaxY;
  f32 mRadius;
};

struct cPawnActInterIfLen : cPawnActInterBase
{
  cPawnEnableArea mEnableArea;
};

struct cPawnActInterSearchCorePoint : cPawnActInterBase
{
  cPawnActInterSearchCorePoint_cOptFlag mOptFlag;
};

struct cPawnActInterActArrowChange : cPawnActInterBase
{
  u32 mArrowActGroup;
};

struct cPawnActInterRot : cPawnActInterBase
{
};

struct cPawnActInterMove : cPawnActInterBase
{
  u32 mMovePosType;
  s32 mEnableRangeActNo;
  f32 mNearRange;
  cPawnActInterMove_cOptFlag mOptFlag;
};

struct cPawnActInterFree : cPawnActInterBase
{
};

struct cPawnAIActInter : cAIResource
{
    u32 mNameID;
    u32 mpCmdInterDTIID;
    if(mpCmdInterDTIID==1272092900){
      cPawnActInterWait PawnAIActInter;
    }
};

struct cPawnAIAction : MtObject
{
  u32 mPawnActID;
  cAIPawnActionGroupFlag mGroup;
  f32 mLifeFrame;
  f32 mStandOffFrame;
  cPawnAIActComCtrlFlag mPawnAIActComCtrlFlag;
  u32 mPawnAIActComCtrlOrderID;
  cPawnAIActCancelFlag mPawnAIActCancelFlag;
  MtTypedArray<cPawnAIActInter> mpActInters;
  cPawnAIActComCheckFlag mPawnAIActComEnableFlag;
  cPawnAIActComCheckFlag mPawnAIActComDisableFlag;
  u32 mProperTargetType;
  f32 mStaminaRateMin;
  f32 mStaminaRateMax;
  f32 mSupportHpRateMin;
  f32 mSupportHpRateMax;
  cAIPawnActSupportFlag mSupportPawnActFlag;
  u32 mEnableJobFlag;    
  s32 mUseRate;
  f32 mUseRangeMin;
  f32 mUseRangeMax;
  u32 mEnableJobCharge;
  s32 mJustRangeActNo;
  s32 mJustRangeJob;
  u32 mAIPawnGroupThinkID;
};

struct rTbl2<cPawnAIAction> : rTbl2Base
{
    u32 mDataNum;
    cPawnAIAction mpData[2];
};

struct rPawnAIAction : rTbl2<cPawnAIAction>
{
};

rPawnAIAction rpawnaiaction_at_0x00 @ 0x00;