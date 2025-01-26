#define f32 float

struct MtObject
{
};

struct MtVector3
{
    float x;
    float y;
    float z;
};

struct rTbl2Base
{
    u32 version;
};

struct cWeatherFogInfo : MtObject
{
    u32 mTime;
    f32 mStart;
    f32 mEnd;
    f32 mExponentDensity;
    // u32 mChgMode;
    MtVector3 mColor;
};
struct rTbl2<cWeatherFogInfo> : rTbl2Base
{
    u32 mDataNum;
    cWeatherFogInfo mpData[mDataNum];
};

struct rWeatherFogInfo : rTbl2<cWeatherFogInfo>
{
};

rWeatherFogInfo rweatherfoginfo_at_0x00 @0x00;