struct MtObject
{
};

struct cResource
{
  u32 magicNumber;
  u32 version;
};

struct MtArray
{
  u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
  T arr[mLength];
};

enum cGroupParam_KILL_AREA_TYPE : s32
{
  KILL_AREA_ALL = 0x0,
  KILL_AREA_SHAPE = 0x1,
};

enum AREAHIT_SHAPE_TYPE : s32
{
  AREAHIT_SHAPE_TYPE_NONE = 0x0,
  AREAHIT_SHAPE_TYPE_BOX = 0x1,
  AREAHIT_SHAPE_TYPE_SPHERE = 0x2,
  AREAHIT_SHAPE_TYPE_CYLINDER = 0x3,
  AREAHIT_SHAPE_TYPE_DUMMY_04 = 0x4,
  AREAHIT_SHAPE_TYPE_DUMMY_05 = 0x5,
  AREAHIT_SHAPE_TYPE_CONE = 0x6,
  AREAHIT_SHAPE_TYPE_DUMMY_07 = 0x7,
  AREAHIT_SHAPE_TYPE_AABB = 0x8,
  AREAHIT_SHAPE_TYPE_OBB = 0x9,
  AREAHIT_SHAPE_TYPE_MAX = 0xA,
};

bitfield cGroupParam_stLoadCondition_Bits
{
mLotFlag:
  1;
mLayoutFlag:
  1;
mRandomOnly:
  1;
mStage:
  1;
mVersion:
  1;
mOmit:
  1;
};

union cGroupParam_stLoadCondition
{
  cGroupParam_stLoadCondition_Bits bits;
  u32 mLoadCondition;
};

bitfield cGroupParam_stSetCondition_Bits
{
mAreaHit:
  1;
mSimpleEv:
  1;
mSetMax:
  8;
};

union cGroupParam_stSetCondition
{
  cGroupParam_stSetCondition_Bits bits;
  u32 mSetCondition;
};

bitfield cGroupParam_stDeleteCondition_Bits
{
mLotFlag:
  1;
mLayoutFlag:
  1;
};

union cGroupParam_stDeleteCondition
{
  cGroupParam_stDeleteCondition_Bits bits;
  u32 mDeleteCondition;
};

bitfield cGroupParam_DataCommon_Bits
{
mGroup:
  9;
mPriority:
  18;
mIsDisableSplit:
  1;
mIsParts:
  1;
mHasMarkerPos:
  1;
};

union cGroupParam_DataCommon
{
  cGroupParam_DataCommon_Bits bits;
  u32 mDataCommon;
};

bitfield cGroupParam_DataLotFlag_Bits
{
mLotFlagNo:
  16;
};

union cGroupParam_DataLotFlag
{
  cGroupParam_DataLotFlag_Bits bits;
  u32 mDataLotFlag;
};

struct cGroupParam_GuardData
{
  u32 mQuestNo;
  u32 mLayoutFlagNo;
};

bitfield nLayout_stLayoutID_Bits
{
mArea:
  10;
mGroup:
  22;
};

union nLayout_stLayoutID
{
  nLayout_stLayoutID_Bits bits;
  u64 mLayoutID;
};

bitfield nLayout_stSplitID_Bits
{
mSplitX:
  32;
mSplitZ:
  32;
};

union nLayout_stSplitID
{
  nLayout_stSplitID_Bits bits;
  u64 mSplitID;
};

struct cGroupParam_cID : MtObject
{
  nLayout_stLayoutID mLayoutID;
  nLayout_stSplitID mSplitID;
};

struct MtVector3
{
  float x;
  float y;
  float z;
};

struct MtVector4
{
  float x;
  float y;
  float z;
  float w;
};

struct nZone_ShapeInfoBase
{
  float mDecay;
  bool mIsNativeData;
};

struct MtAABB
{
  MtVector3 minpos;
  MtVector3 maxpos;
};

struct MtMatrix
{
  MtVector4 m[4];
};

struct MtOBB
{
  MtMatrix coord;
  MtVector3 extent;
};

struct MtSphere
{
  MtVector3 pos;
  float r;
};

struct MtCylinder
{
  MtVector3 p0;
  MtVector3 p1;
  float r;
};

struct nZone_ShapeInfoSphere : nZone_ShapeInfoBase
{
  MtSphere mSphere;
};

struct nZone_ShapeInfoOBB : nZone_ShapeInfoBase
{
  MtOBB mOBB;
  float mDecayY;
  float mDecayZ;
  bool mIsEnableExtendedDecay;
};

struct nZone_ShapeInfoAABB : nZone_ShapeInfoBase
{
  MtAABB AABB;
  float mDecayY;
  float mDecayZ;
  bool mIsEnableExtendedDecay;
};

struct nZone_ShapeInfoCone : nZone_ShapeInfoBase
{
  float mHeight;
  float mTopRadius;
  MtVector3 mPos;
  float mBottomRadius;
};

struct nZone_ShapeInfoCylinder : nZone_ShapeInfoBase
{
  MtCylinder mCylinder;
};

struct nZone_ShapeInfoArea : nZone_ShapeInfoBase
{
  float mHeight;
  // float mBottom;
  // u32 mConcaveStatus;
  // bool mFlgConvex;
  MtVector3 mVertex[4];
  MtVector3 mConcaveCrossPos;
};

struct AreaHitShape
{
  char mName[];
  float mCheckAngle;
  float mCheckRange;
  float mCheckToward;
  bool mAngleFlag;
  bool mTowardFlag;
  // bool mIsDeleteZone;

  AREAHIT_SHAPE_TYPE type;
  match(type)
  {
    (AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_BOX) : nZone_ShapeInfoArea mpZone;
    (AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_SPHERE) : nZone_ShapeInfoSphere mpZone;
    (AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_CYLINDER) : nZone_ShapeInfoCylinder mpZone;
    (AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_CONE) : nZone_ShapeInfoCone mpZone;
    (AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_AABB) : nZone_ShapeInfoAABB mpZone;
    (AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_OBB) : nZone_ShapeInfoOBB mpZone;
    (_) : nZone_ShapeInfoBase mpZone;
  }

  if (type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_BOX)
  {
    MtAABB mZoneBoundingBox;
    u32 unk1;
    bool unk2;
  }
  if (type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_CYLINDER)
  {
    float x;
    float y;
    float a;
    float b;
    float c;
  }
};

struct cGroupParam_cLifeArea
{
  MtTypedArray<AreaHitShape> mShapeList;
};

struct cGroupParam
{
  cGroupParam_DataCommon mDataCommon;
  MtTypedArray<cGroupParam_cID> mLayoutIDArray;
  cGroupParam_stLoadCondition mLoadCondition1;
  cGroupParam_DataLotFlag mDataLotFlag;
  cGroupParam_stLoadCondition mLoadCondition2;
  cGroupParam_GuardData mGuardData;
  cGroupParam_stLoadCondition mLoadCondition3;
  cGroupParam_stLoadCondition mLoadCondition4;
  u32 mLoadStageNo;

  u8 Unknown1;
  u32 Unknown2;
  u32 Unknown3;

  cGroupParam_stSetCondition mSetCondition1;
  MtTypedArray<AreaHitShape> mAreaHitShapeList;
  cGroupParam_stSetCondition mSetCondition2;
  cGroupParam_stSetCondition mSetCondition3;
  cGroupParam_stDeleteCondition mDeleteCondition1;
  cGroupParam_stDeleteCondition mDeleteCondition2;
  cGroupParam_stDeleteCondition mDeleteCondition3;
  MtTypedArray<cGroupParam_cLifeArea> mLifeAreaArray;
  cGroupParam_KILL_AREA_TYPE mKillAreaType;
  MtTypedArray<AreaHitShape> mKillAreaList;
};

struct AreaHitShape_NativeAllocInfo
{
  u32 pShapeBoxArray;
  u32 pShapeSphereArray;
  u32 pShapeCylinderArray;
  u32 pShapeConeArray;
  u32 pShapeAABBArray;
  u32 pShapeOBBArray;
};

struct nLayoutGroupParam_NativeAllocInfo
{
  u32 pIdArray;
  u32 pLifeAreaArray;
  u32 pAreaHitShapeArray;
  AreaHitShape_NativeAllocInfo ShapeAllocInfo;
};

struct rLayoutGroupParamList : cResource
{
  u32 mGroupNum;
  u32 mGroupList[mGroupNum];
  u32 mpGroupParamBuffSize;
  nLayoutGroupParam_NativeAllocInfo mAllocInfo;
  cGroupParam mpGroupParamBuff[mpGroupParamBuffSize];
};
rLayoutGroupParamList rlayoutgroupparamlist_at_0x00 @0x00;