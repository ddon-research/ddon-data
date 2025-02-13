#define f32 float

struct MtObject
{
};

struct cResource
{
  char magicString[4];
  u32 magicVersion;
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
    u32 unk1;
    bool unk2;
  }
  if (type == AREAHIT_SHAPE_TYPE::AREAHIT_SHAPE_TYPE_AABB)
  {
    float x;
    float y;
    bool mIsEnableExtendedDecay;
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

struct CustomMarkerGroupShape
{
  u32 DTI;

  AreaHitShape mpZone;
  // MtAABB mZoneBoundingBox;
  u32 MapGroup;
};

struct rStageConnect_Connection
{
  u32 mType;
  MtVector3 mPos;
  u32 mPartsNo;
  u32 mMapGroup;
  u32 Unknown1;
  u32 Unknown2;
  u32 mIndex;
};

struct rStageConnect : cResource
{
  u32 mConnectorNum;
  rStageConnect_Connection mpConnectorArray[mConnectorNum];

  u32 mConnectionNum;
  CustomMarkerGroupShape mCustomMarkerGroupShapesArray[mConnectionNum];
};
rStageConnect rstageconnect_at_0x00 @0x00;
