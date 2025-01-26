#define f32 float

struct MtObject
{
};

struct MtArray
{
};

struct TypedResourcePointer
{
  char Type[];
  if (Type[0])
    char Path[];
};

struct MtTypedArray<T> : MtArray
{
  u32 mLength;
  T arr[mLength];
};

struct cWeatherObjectRes
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

struct cWeatherCloudModel : cWeatherObjectRes
{
  TypedResourcePointer res_ptr_rModel_mpModel;
  u32 mColorType;
  f32 mSunColorScale;
  f32 mSaturationScale;
  f32 mIntensityScale;
  f32 mFogMulRate;
  f32 mFogAddRate;
  u32 mViewType;
};

struct cWeatherParam : cWeatherObjectRes
{
  MtVector3 mSunColor;
  MtVector3 mMieScattering;
  f32 mMieDensity;
  f32 mCloudHeight;
  f32 mCloudiness;
  f32 mCloudThickness;
  f32 mCloudScattering;
  f32 mCloudEccentricity;
  f32 mMoonLRate;
  f32 mSunIntensityRate;
  f32 mEnvMapBaseScale;
  f32 mFogDensity;
};

struct cWeatherParamInfo : MtObject
{
  cWeatherParam mWeatherParam;
  s32 mWeatherID;
  f32 mWeatherSoundVolume;
  f32 mWeatherStarIntensity;
  f32 mLightMainIntensityScale;
  f32 mLightMainSatuationScale;
  MtVector3 mLightSubDayColor;
  MtVector3 mLightHemiDayColor;
  MtVector3 mLightHemiDayRevColor;
  TypedResourcePointer res_ptr_rWeatherFogInfo_mpFogParam;
  TypedResourcePointer res_ptr_rSoundRequest_mpSoundReq;
  MtTypedArray<cWeatherCloudModel> mClouds;
};
struct rTbl2<cWeatherParamInfo> : rTbl2Base
{
  u32 mDataNum;
  cWeatherParamInfo mpData[mDataNum];
};

struct rWeatherParamInfoTbl : rTbl2<cWeatherParamInfo>
{
};

rWeatherParamInfoTbl rweatherparaminfotbl_at_0x00 @0x00;