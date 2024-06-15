#define f32 float

struct MtObject
{
};

struct cResource
{
    char magicString[];
    u32 magicVersion;
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};

struct MtFloat2
{
    float x;
    float y;
};

struct MtVector2
{
    float x;
    float y;
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

struct MtRect
{
    s32 l;
    s32 t;
    s32 r;
    s32 b;
};

struct nZone_ShapeInfoBase
{
    float mDecay;
    bool mIsNativeData;
};

struct nZone_ShapeInfoOBB : nZone_ShapeInfoBase
{

    MtOBB mOBB;
    float pading;
    float mDecayY;
    float mDecayZ;
    bool mIsEnableExtendedDecay;
};

struct nZone_ShapeInfoArea : nZone_ShapeInfoBase
{
    float mHeight;
    float mBottom;
    u32 mConcaveStatus;
    bool mFlgConvex;
    MtVector3 mVertex[4];
    MtVector3 mConcaveCrossPos;
};

struct nZone_ShapeInfoPanel : nZone_ShapeInfoBase
{
    MtVector3 mVertex[4];
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
    s32 type;

    if (type == 9)
        nZone_ShapeInfoOBB shape;
    if (type == 1)
        nZone_ShapeInfoArea shape;
};

struct rGUIMapSetting_cData : MtObject
{
    s32 mShapeType;
    char mShapeName[];

    AreaHitShape mpShape;

    u32 mFloorId;
    // bool mVisible;
};

struct rGUIMapSetting : cResource
{
    MtFloat2 mCenter;
    s32 mFloorBaseId;
    u32 mFloorBaseSizeId;
    u32 mTextureNumX;
    u32 mTextureNumY;
    MtRect mRect;
    f32 mFoundationScale;
    f32 mOffsetPosX;
    f32 mOffsetPosY;
    bool mUseIdTex;
    MtTypedArray<rGUIMapSetting_cData> mArray;
};

rGUIMapSetting rguimapsetting_at_0x00 @0x00;