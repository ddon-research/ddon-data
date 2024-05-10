#pragma pattern_limit 231072

struct MtVector3
{
  float x;
  float y;
  float z;
};

struct cOmParam
{
  s32 mOmID;
  u64 cResPath_rModel_mrModel;
  u64 cResPath_rObjCollision_mrObjCollision;
  u64 cResPath_rMotionList_mrMotionList;
  u64 cResPath_rSoundMotionSe_mrSoundMotionSe;
  u32 mUnitDTIID;
  u32 mUseComponent;
  u32 mOmSetType;
  u64 cResPath_rEffectProvider_mrEffectProvider;
  u64 cResPath_rSoundRequest_mrSoundRequest;
  u32 mReqSeFlag;
  s32 mFxIndex0;
  s32 mSeIndex0;
  s32 mFxIndex1;
  s32 mSeIndex1;
  s32 mFxIndex2;
  s32 mSeIndex2;
  s32 mFxIndex3;
  s32 mSeIndex3;
  u64 cResPath_rSwingModel_mrSwingModel;
  u64 cResPath_rDeformWeightMap_mrSoftBody;
  u64 cResPath_rRigidBody_mrRigidBody;
  u64 cResPath_rRigidBody_mrBrRigidBody;
  u64 cResPath_rModel_mrBrModel;
  u64 cResPath_rDeformWeightMap_mrBrSoftBody;
  u64 cResPath_rCaughtInfoParam_mrCaught;
  u64 cResPath_rZone_mrZone;
  u64 cResPath_rZone_mrOmZone;
  u64 cResPath_rJointInfo_mrJointInfo;
  u32 mDetailBehavior;
  u32 mMapIcon;

  float mKillLength;
  bool mbUseNightColor;
  MtVector3 mNightColor;

  float mRigidTime;
  float mRigidForce;
  float mRigidOfsY;
  float mRigidVelocity;
  float mThrowVelocity;
  float mThrowVectorY;
  float mRigidWorldOfsY;
  MtVector3 mTargetOfs;
  bool mbNav;
  MtVector3 mNavOBBPos;
  MtVector3 mNavOBBExtent;
  bool mbAtk;
  u32 mShotGroup;
  s32 mWepType;

  u32 mArcTagID;
  s32 mTargetJntNo;
  float mOffSeLength;
  s32 mJointNum;
  MtVector3 mKeyOfs;
  u32 mColliOffFrame;
  u32 mBlinkType;
  u64 cResPath_rCollision_mrCollision[4];
  u32 mVersion;
};

struct rOmParam
{
  u32 mArrayNum;
  cOmParam mArray[1747];
};

rOmParam romparam_at_0x08 @0x08;