#define f32 float
#define SO_HANDLE u32

struct MtObject
{
};

struct cAIObject : MtObject
{
};

struct cResource : MtObject
{
    u32 magicNumber;
    u32 version;
};

struct MtVector3
{
    f32 x;
    f32 y;
    f32 z;
};

struct MtVector3Padded
{
    f32 x;
    f32 y;
    f32 z;
    f32 pad_;
};

struct MtVector4
{
    f32 x;
    f32 y;
    f32 z;
    f32 w;
};

struct MtMatrix
{
    MtVector4 m[4];
};

struct MtAABB
{
    MtVector3 minpos;
    MtVector3 maxpos;
};

struct MtOBB
{
    MtMatrix coord;
    MtVector3 extent;
};

struct MtSphere
{
    MtVector3 pos;
    f32 r;
};

enum nDraw_USAGE_TYPE : s32
{
    USAGE_DEFAULT = 0x0,
    USAGE_DYNAMIC = 0x1,
    USAGE_RENDERTARGET = 0x2,
    USAGE_STAGING = 0x3,
    USAGE_MANAGED = 0x4,
    USAGE_DEPTHSTENCIL = 0x5,
    USAGE_DISPLAYBUFFER = 0x6,
};

struct rModel_MATERIAL_NAME
{
    char name[128];
};

struct nDraw_Resource : MtObject
{
    s32 mRefFrame;
    s32 mRefCount;
    u32 mCRC;
};

bitfield nDraw_Material_BITS_1
{
mStencilRef:
    8;
mAlphaTestEnable:
    1;
mAlphaTestCmpFunc:
    4;
mAlphaTestRopTest:
    1;
mAlphaTestRef:
    8;
mSelect:
    1;
mLayerID:
    2;
mDeferredShadowEnable:
    1;
mDrawPass:
    5;
mFogEnable:
    1;
};

bitfield nDraw_Material_BITS_2
{
mStateNum:
    9;
mAnimationNum:
    9;
mProceduralTextureNum:
    4;
mReserve_fId:
    6;
mDeferredLighting:
    1;
mAlbedoAlpha:
    1;
mTangent:
    1;
mHalfLambert:
    1;
};

struct nDraw_Material : nDraw_Resource
{
    SO_HANDLE mTechnique;

    nDraw_Material_BITS_1 bits1;

    nDraw_Material_BITS_2 bits2;

    u16 mID;
    f32 mAnimationSpeed;
    // nDraw_BlendState *mpBlendState;
    // nDraw_RasterizerState *mpRasterizerState;
    // nDraw_DepthStencilState *mpDepthStencilState;
    SO_HANDLE mBlendStateHandle;
    // nDraw_Material_STATE *mStates;
    //MtColorF mBlendFactor;
    //nDraw_Material_ANIMATION_STATE mAnimationState[4];
    // nDraw_Material_PROCEDURAL_TEXTURE *mProceduralTexture;
    // nDraw_Animation *mpAnimation;
    // nDraw_CBufferSystem *mpCBuffer;
    bool mLegacyAnimation;
    u32 mpStateAccessTablePointer[4]; //
    u32 mStateAccessTableNum[4];
};

struct rModel_MODEL_INFO//info
{
    s32 middist;
    s32 lowdist;
    u32 light_group;
    u16 memory;
    u16 reserved;
};

struct nDraw_Buffer : nDraw_Resource
{
    nDraw_USAGE_TYPE mUsageType;
    u32 mBufSize;
    //void *mpBufferPointer;//*
    bool mDirty;
    bool mSuspend;
};

struct nDraw_VertexBuffer : nDraw_Buffer
{
    // nDraw_HVertexBuffer mpVertexBuffer;//void*
};

struct nDraw_IndexBuffer : nDraw_Buffer
{
    // nDraw_HIndexBuffer mpIndexBuffer;//void*
};

struct rModel_RECALCNORMAL_INFO
{
    u16 width;
    u16 height;
    u32 map_vertex_basePointer; //*
    u32 triangle_num;
    nDraw_VertexBuffer trianglePointer;        //*
    nDraw_VertexBuffer vertex_to_indexPointer; //*
};

struct rModel_PARTS_INFO
{
    u32 no;
    u32 reserved[3];
    MtSphere boundary;
};

struct rModel_BOUNDARY_INFO//MOD_Boundary_Info
{
    u32 joint;
    u32 reserved[3];
    MtSphere sphere;
    MtAABB aabb;
    MtOBB obb;
};

bitfield rModel_PRIMITIVE_INFO_BITS_1
{
draw_mode:
    16;
vertex_num:
    16;
};

bitfield rModel_PRIMITIVE_INFO_BITS_2
{
parts_no:
    12;
material_no:
    12;
lod:
    8;
};

bitfield rModel_PRIMITIVE_INFO_BITS_3
{
disp:
    1;
shape:
    1;
sort:
    1;
weight_num:
    5;
alphapri:
    8;
vertex_stride:
    8;
topology:
    6;
binormal_flip:
    1;
bridge:
    1;
};

bitfield rModel_PRIMITIVE_INFO_BITS_4
{
envelope:
    8;
boundary_num:
    8;
connect_id:
    16;
};

bitfield rModel_PRIMITIVE_INFO_BITS_5
{
min_index:
    16;
max_index:
    16;
};

struct rModel_PRIMITIVE_INFO//MOD_Mesh_Info
{
    rModel_PRIMITIVE_INFO_BITS_1 bits1;

    rModel_PRIMITIVE_INFO_BITS_2 bits2;

    rModel_PRIMITIVE_INFO_BITS_3 bits3;

    u32 vertex_ofs;
    u32 vertex_base;
    SO_HANDLE inputlayout;
    u32 index_ofs;
    u32 index_num;
    u32 index_base;

    rModel_PRIMITIVE_INFO_BITS_4 bits4;

    rModel_PRIMITIVE_INFO_BITS_5 bits5;

    rModel_BOUNDARY_INFO boundaryPointer; //*
};

bitfield rModel_JOINT_INFO_BITS
{
no:
    8;
Parent:
    8;
symmetry:
    8;
reserved:
    8;
};

struct rModel_JOINT_INFO//MODE_Bone_Info
{
    rModel_JOINT_INFO_BITS bits;
    f32 radius;
    f32 length;
    MtVector3 offset;
};

struct rModel : cResource
{

    u32 mJointNum;
    //rModel_PRIMITIVE_INFO mPrimitiveInfoPointer; //*
    u32 mPrimitiveNum;
    u32 mMaterialNum;
    u32 mVertexNum;

    u32 mLmatNum;
    u32 mImatNum;
    //MtMatrix mLmatPointer;                       //*
    //MtMatrix mImatPointer;                       //*

    u32 mJointInfoOffset;
    rModel_JOINT_INFO mJointInfoPointer @ mJointInfoOffset; //*

    u32 mEnvelopeNum;
    
    u32 mPolygonNum;
    
    u32 mIndexNum;
    u32 mPartsNum;
    //rModel_PARTS_INFO mPartsInfoPointer; //*
    u32 mVertexBufsize;
    //nDraw_IndexBuffer mpIndexBufferPointer;   //*
    //nDraw_VertexBuffer mpVertexBufferPointer; //*
    //f32 mQuantPosScale;
 

    //nDraw_Material mpMaterialsStackPointer[4]; //*
    //MtVector3 mQuantPosOffset;
    //u8 mJointTable[256];
    //rMaterial mpMaterialPointer;               //*
    //nDraw_Material mpMaterialsPointerArray;    //**
    //rModel_MATERIAL_NAME mMaterialNamePointer; //*
    //rModel_RECALCNORMAL_INFO mRCNInfo;

    MtSphere mBoundingSphere;
    MtAABB mBoundingBox;
    rModel_MODEL_INFO mModelInfo;
    u32 mBoundaryNum;
    //rModel_BOUNDARY_INFO mBoundaryInfoPointer; //*
};

rModel rmodel_at_0x00 @ 0x00;
rModel_MATERIAL_NAME rmodel_material_name_at_0xA3 @ 0xA3;
// TODO: https://github.com/chrispurnell/ddmod-tool/blob/main/modeleditor.h