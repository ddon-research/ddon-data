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
  // bool mIsEnableExtendedDecay;
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
    u32 mConcaveStatus;
    bool mFlgConvex;
  }
  if (type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_SPHERE || type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_CYLINDER || type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_CONE || type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_OBB)
  {
    float x;
    float y;
    float a;
    float b;
    float c;
  }
  if (type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_AABB)
  {
    float x;
    float y;
    bool mIsEnableExtendedDecay;
  }
};

struct cDayNightColorFogParam
{
  float mHeightStart;
  float mHeightEnd;
  float mHeightDensity;

  MtVector3 mHeightColor;

  float mStart;
  float mEnd;
  float mDensity;

  MtVector3 mColor;

  float mDiffuseBlendFactor;
  // bool mIsEnable;
  // float mSupplementFrame;
  // s32 mId;
  // u32 mKind;
};

struct rStageCustomPartsEx_ColorFog
{
  cDayNightColorFogParam mBase;
  cDayNightColorFogParam mNight;
  // char mComment[];
};

struct rStageCustomPartsEx_HemiSphLight
{
  MtVector3 mLightColor;
  MtVector3 mRevColor;
  MtVector3 mNightColor;
  MtVector3 mNightRevColor;
  // char mComment[];
};

struct rStageCustomPartsEx_InfiLight
{
  MtVector3 mLightColor;
  MtVector3 mNightColor;
  // char mComment[];
};

struct rStageCustomPartsEx_Pattern
{
  s32 mColorFogNo;
  s32 mHemiSphLightNo;
  s32 mInfiLightNo;
  // char mComment[];
};

struct rStageCustomPartsEx_AreaParam
{
  bool mUseAllFilter;
  s32 mFilterNo;
  s32 mPatternNo;
  u32 num;
  AreaHitShape mAreaHitShapeList[num];
  // char mComment[];
};

struct rStageCustom_Area
{
  s8 mAreaNo;
  u8 mFilterNo;
  s32 mGroupNo;
};

struct MtColor
{
  u8 r;
  u8 g;
  u8 b;
  u8 a;
};

struct rStageCustomPartsEx_InfoEx
{
  char mModel[];
  char mScrSbc1[];
  char mEffSbc1[];
  char mScrSbc2[];
  char mEffSbc2[];
  char mScrSbc3[];
  char mEffSbc3[];
  char mLight[];
  char mNaviMesh[];
  char mEpv[];
  char mOccluder[];

  u16 mAreaNo;
  u16 mType;
  u32 mSize;
  float mOffsetZ;
  s32 mEpvIndexAlways;
  s32 mEpvIndexDay;
  s32 mEpvIndexNight;
  MtColor mColor;

  u64 mEfcColorZone;
  u64 mEfcCtrlZone;
  u64 mIndoorZoneScr;
  u64 mIndoorZoneEfc;
  u64 mLightAndFogZone;
  u64 mSoundAreaInfo;
  u64 mZoneUnitCtrl[3];
  u64 mZoneStatus;

  char mComment[];

  u32 mAddVersion;
  if (mAddVersion > 0)
  {
    // u32 num;
    rStageCustomPartsEx_AreaParam mAreaParamList[mAddVersion];
  }
};

struct rStageCustomParts_Filter
{
  char mFilter[];
};

struct rStageCustomParts_Param
{
  float mDelta;
  float mOffsetY;
};

struct rStageCustomPartsEx : cResource
{
  rStageCustomParts_Param mParam;
  u32 mArrayInfoNum;
  rStageCustomPartsEx_InfoEx mpArrayInfo[mArrayInfoNum];
  u32 mArrayFilterNum;
  rStageCustomParts_Filter mpArrayFilter[mArrayFilterNum];

  u32 mArrayColorFogNum;
  rStageCustomPartsEx_ColorFog mpArrayColorFog[mArrayColorFogNum];
  u32 mArrayHemiSphLightNum;
  rStageCustomPartsEx_HemiSphLight mpArrayHemiSphLight[mArrayHemiSphLightNum];
  u32 mArrayInfiLightNum;
  rStageCustomPartsEx_InfiLight mpArrayInfiLight[mArrayInfiLightNum];
  u32 mArrayPatternNum;
  rStageCustomPartsEx_Pattern mpArrayPattern[mArrayPatternNum];
};

rStageCustomPartsEx rstagecustompartsex_at_0x00 @0x00;