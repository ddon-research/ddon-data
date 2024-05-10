struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct cEmSoundTable : MtObject
{
    u32 mIdx;
    u32 mSoundResNo;
    u32 mSoundNo;
    bool mAttachFlag;
    u32 mRequestType;
    s32 mBoneNo;
    MtVector3 mOffsetPos;
    bool mDieIsNoCall;
};

struct rTbl2<cEmSoundTable> : rTbl2Base
{
    u32 mDataNum;
    cEmSoundTable mpData[mDataNum];
};

struct rEmSoundTable : rTbl2<cEmSoundTable>
{
};

rEmSoundTable remsoundtable_at_0x00 @0x00;