#define f32 float

struct MtVector3
{
    f32 x;
    f32 y;
    f32 z;
};

struct MtObject
{
};

struct rTbl2Base
{
    u32 version;
};

struct rTbl2<T> : rTbl2Base
{
    u32 mDataNum;
    T mpData[mDataNum];
};

struct cMyRoomActParam : MtObject
{
    MtVector3 mPos;
    f32 mAngleY;
    u16 mWaypoint;
    u16 mNpcMotNo;
    u16 mStartIdx;
    u32 mNeedOM;
    u32 mNeedOM2;
    u32 mNeedOM3;
    u32 mNeedOM4;
    u32 mNeedOM5;
    s16 mMessage;
    u16 mCondition;
    s16 mLinkActNo;
    u16 mLinkActLv;
    s16 mChangeEquip;
    bool mIsGriffin;
    bool mIsNotAvoid;
    bool mIsSingle;
};

struct rMyRoomActParam : rTbl2<cMyRoomActParam>
{
};

rMyRoomActParam rmyroomactparam_at_0x00 @0x00;