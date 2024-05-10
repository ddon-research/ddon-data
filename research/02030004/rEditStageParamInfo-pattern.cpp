struct MtVector3
{
    float x;
    float y;
    float z;
};
struct rEditStageParamInfoWeatherData
{
    u32 mWeatherID;
    u32 mHour;
    u32 mMinite;
};

struct rEditStageParamInfo
{
    char mModelSdl[];
    char mFilterSdl[];
    char mLightSdl[];
    char mOmListSdl[];
    u32 mReverb;
    MtVector3 mPlPos;
    float mPlRotY;
    char mWeatherStageInfo[];
    char mWeatherParamInfo[];
    rEditStageParamInfoWeatherData mWeatherData[2];
    u64 cResPathExmpSkyWep;
    u64 cResPathExmpRoomWep;
    u64 cResPathExmpEpv;
    s32 mEpvIndexAlways;
    s32 mEpvIndexDay;
    s32 mEpvIndexNight;
    u32 mFlag;
};

struct rEditStageParamList
{
    s8 mListTbl[8];
};

struct rEditStageParam
{
    u32 mArrayInfoNum;
    rEditStageParamInfo mpArrayInfo[mArrayInfoNum];
    u32 mArrayListNum;
    rEditStageParamList mpArrayList[mArrayListNum];
};
rEditStageParam reditstageparam_at_0x08 @0x08;