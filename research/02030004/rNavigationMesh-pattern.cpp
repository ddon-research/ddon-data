#pragma pattern_limit 1310720
#define f32 float

struct MtObject
{
};

struct cAIObject : MtObject
{
};

struct cResource : MtObject
{
};

struct MtVector3
{
    f32 x;
    f32 y;
    f32 z;
    // f32 pad_;
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

struct MtAABBPadded
{
    MtVector3Padded minpos;
    MtVector3Padded maxpos;
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

enum rNavigationMesh_TYPE : s32
{
    TYPE_MESH = 0x0,
    TYPE_POINT_2 = 0x1,
};

enum MtGeometry_Type : s32
{
    TYPE_NULL = 0x0,
    TYPE_LINE = 0x1,
    TYPE_LINE_SEGMENT = 0x2,
    TYPE_RAY = 0x3,
    TYPE_PLANE = 0x4,
    TYPE_SPHERE = 0x5,
    TYPE_CAPSULE = 0x6,
    TYPE_AABB = 0x7,
    TYPE_OBB = 0x8,
    TYPE_CYLINDER = 0x9,
    TYPE_CONVEX_HULL = 0xA,
    TYPE_TRIANGLE = 0xB,
    TYPE_CONE = 0xC,
    TYPE_TORUS = 0xD,
    TYPE_ELLIPSOID = 0xE,
    TYPE_MINCOWSKI_SUM = 0xF,
    TYPE_MINCOWSKI_DIFF = 0x10,
    TYPE_LINE_SEGMENT4 = 0x11,
    TYPE_AABB4 = 0x12,
    TYPE_LINESWEPTSPHERE = 0x13,
    TYPE_PLANE_XZ = 0x14,
    TYPE_RAY_Y = 0x15
};

struct rNavigationMesh_nodeInfo : MtObject
{
    u32 mNodeOffset;
    MtAABB mAABB;
};

struct rNavigationMesh_nodeData_LinkInfo
{
    s32 mLinkNodeIndex;
    u32 mAttribute;
    u32 mPortalNumber;
    f32 mLinkCost;
    f32 mSize;
    f32 mHeight;
};

struct rNavigationMesh_nodeData_PolygonArea
{
    u32 mNumberOfIndex;
    s32 mpVertexIndex[mNumberOfIndex]; //*
};

struct rNavigationMesh_nodeData : MtObject
{
    bool mNoMemFree = 1 [[export]];
    s32 mIndex;
    u32 mNumberOfAttribute;
    u32 mpAttribute[mNumberOfAttribute]; //*
    bool mConnect;
    MtVector3 mDir;
    f32 mLength;
    u8 mSeekPt;
    if (mSeekPt)
    {
        u32 mNumberOfCAttribute;
        u32 mpCAttribute[mNumberOfCAttribute]; //*
    }
    rNavigationMesh_nodeData_PolygonArea mPolygonArea;
    u32 mNumberOfLink;
    rNavigationMesh_nodeData_LinkInfo mpLinkInformation[mNumberOfLink]; //*
};

struct cAITreeBase_Node_ObjectList
{
    u32 mParam;
    u32 mpObj; // MtObject mpObj; //*
};

struct cAITreeBase_Node : MtObject
{
    u32 mNumberOfObject;
    cAITreeBase_Node_ObjectList mpObjectList[mNumberOfObject]; //*
};

struct cAITreeBase //: cAITask
{
    u8 mNest;
    // u8 mAxisPartition;
    u32 mNumberOfNode;
    // MtAABBPadded region;
    // cAITreeBase_Node mpNode[mNumberOfNode]; //*
    // bool mDelete;
};

struct cAIQuadTree
{
    // bool mMultiple;
    // MtVector3 mPos;
    // MtVector3 mXZ;
    cAITreeBase base;
    MtAABBPadded mpTempRegion;                   //* // Reused for all nodes/quad trees
    cAITreeBase_Node mpNode[base.mNumberOfNode]; //* // based on the node data in the initial section of file
};

struct MtGeometry : MtObject
{
    // MtGeometry_Type mType;
};

struct MtGeomConvex : MtGeometry
{
    f32 mMargin;
};

struct MtGeomAABB : MtGeomConvex
{
    MtAABB mAABB;
};

struct MtGeomOBB : MtGeomConvex
{
    MtOBB mOBB;
};

struct MtGeomSphere : MtGeomConvex
{
    MtSphere mSphere;
};

struct rAIPathBase_HierarchyArea : MtObject
{
    u16 mID;
    u32 mNameSize;
    char mName[mNameSize + 1];
    u32 mAttribute;
    u8 mNumberOfGeometry;
    // MtGeometry mpGeometryList; //**
    u8 mType;
    $ -= 1;
    //$+=3;
    match(mType)
    {
        (0) : MtGeomAABB Geometry;
        (1) : MtGeomOBB Geometry;
        (2) : MtGeomSphere Geometry;
    }
    u16 mFirstIndex;
    u16 mLastIndex;
    s16 mParentID;
    u8 mNumberOfChild;
    u8 mpChild[mNumberOfChild]; //*
    u8 mNumberOfLink;
    u8 mpLink[mNumberOfLink]; //*
};

struct rAIPathBase : cResource
{
    u16 mNumberOfArea;
    rAIPathBase_HierarchyArea mpHierarchyArea[mNumberOfArea]; //**

    u16 mNumberOfTotalAreaChild;
    u16 mNumberOfTotalAreaLink;
};

struct rNavigationMesh_VertexObject
{
    MtVector3 mpPolygonVertex; //*
    bool mpNearWall;           //*
    u16 mpWallDistance;        //*
};

struct rNavigationMesh_HEADER
{
    u32 magic;
    u32 version;
    rNavigationMesh_TYPE type;
    u32 attributeBuffer;
};

struct rNavigationMesh //: rAIPathBase
{
    rNavigationMesh_HEADER mCoreHeader;
    u32 mNameSize;
    char mName[mNameSize + 1];
    u32 mNumberOfVertex;
    u32 mNumberOfNode;
    u32 mNumberOfNodeInfo;
    bool mpNearWall; //*
    if (mpNearWall)
    {
        rNavigationMesh_VertexObject anonObj[mNumberOfVertex];
    }
    rNavigationMesh_nodeData mpNode[mNumberOfNode]; // Fills node data in QuadTree
    rAIPathBase aiPathBase;
    u32 mNumberOfTotalLink;
    u32 mNumberOfTotalAttribute;
    u32 mNumberOfTotalIndex;
    rNavigationMesh_nodeInfo mpNodeInfo[mNumberOfNodeInfo]; //[mNumberOfNodeInfo];//*
    u8 mSeekPt;
    $ -= 1;
    cAIQuadTree mpQuadTree; //*
};

rNavigationMesh rnavigationmesh_at_0x00 @0x00;