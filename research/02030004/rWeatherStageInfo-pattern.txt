struct MtVector3
{
  float x;
  float y;
  float z;
};

struct TypedResourcePointer {
    char Type[];
    if(Type[0]>1)
    char Path[];
};

struct rWeatherStageInfo
{
  TypedResourcePointer SkyRes;
  TypedResourcePointer RefSkyRes;
  TypedResourcePointer ModelScheduler;
  TypedResourcePointer StarModel;
  TypedResourcePointer StarTex;
  TypedResourcePointer StarCatalog;
  float StarSize;
  float StarrySkyIntensity;
  float StarTwinkleAmplitude;
  MtVector3 EnvMapBaseColor[2];
  float EnvMapBlendColorScale[2];
};
rWeatherStageInfo rweatherstageinfo_at_0x08 @ 0x08;