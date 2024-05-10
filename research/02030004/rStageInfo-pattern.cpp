#include <std/core.pat>

struct MtVector3
{
  float x;
  float y;
  float z;
};

struct rStageInfo
{
  s32 mStageNo;

  char SchedulerModelType[];
  if (SchedulerModelType[0] > 1)
    char SchedulerModelPath[];

  char SchedulerFilterType[];
  if (SchedulerFilterType[0] > 1)
    char SchedulerFilterPath[];

  char CollisionScrSbcType1[];
  if (CollisionScrSbcType1[0] > 1)
    char CollisionScrSbcPath1[];

  char CollisionEffSbcType1[];
  if (CollisionEffSbcType1[0] > 1)
    char CollisionEffSbcPath1[];

  char CollisionScrSbcType2[];
  if (CollisionScrSbcType2[0] > 1)
    char CollisionScrSbcPath2[];

  char CollisionEffSbcType2[];
  if (CollisionEffSbcType2[0] > 1)
    char CollisionEffSbcPath2[];

  char CollisionScrSbcType3[];
  if (CollisionScrSbcType3[0] > 1)
    char CollisionScrSbcPath3[];

  char CollisionEffSbcType3[];
  if (CollisionEffSbcType3[0] > 1)
    char CollisionEffSbcPath3[];

  char NavigationMeshNaviMeshType[];
  if (NavigationMeshNaviMeshType[0] > 1)
    char NavigationMeshNaviMeshPath[];

  char AIPathConsecutiverWayPointType[];
  if (AIPathConsecutiverWayPointType[0] > 1)
    char AIPathConsecutiverWayPointPath[];

  char OccluderExOCCType[];
  if (OccluderExOCCType[0] > 1)
    char OccluderExOCCPath[];

  char StartPosStartPosType[];
  if (StartPosStartPosType[0] > 1)
    char StartPosStartPosPath[];

  char CameraParamListCmrPrmLstFldType[];
  if (CameraParamListCmrPrmLstFldType[0] > 1)
    char CameraParamListCmrPrmLstFldPath[];

  char CameraParamListCmrPrmLstEvtType[];
  if (CameraParamListCmrPrmLstEvtType[0] > 1)
    char CameraParamListCmrPrmLstEvtPath[];

  MtVector3 mPos;
  float mAng;

  u32 mSceLoadFlag;
  u32 mFlag;

  char WeatherStageInfoResourceType[];
  if (WeatherStageInfoResourceType[0] > 1)
    char WeatherStageInfoResourcePath[];

  char WeatherParamInfoTblType[];
  if (WeatherParamInfoTblType[0] > 1)
    char WeatherParamInfoTblPath[];

  char WeatherParamEfcInfoType[];
  if (WeatherParamEfcInfoType[0] > 1)
    char WeatherParamEfcInfoPath[];

  char WeatherEffectParamType[];
  if (WeatherEffectParamType[0] > 1)
    char WeatherEffectParamPath[];

  char SchedulerStageLightSchdlType[];
  if (SchedulerStageLightSchdlType[0] > 1)
    char SchedulerStageLightSchdlPath[];

  char EffectProviderType[];
  if (EffectProviderType[0] > 1)
    char EffectProviderPath[];

  s32 mEpvIndexAlways;
  s32 mEpvIndexDay;
  s32 mEpvIndexNight;

  char ZoneListType0[];
  if (ZoneListType0[0] > 1)
    char ZoneListPath0[];

  char ZoneListType1[];
  if (ZoneListType1[0] > 1)
    char ZoneListPath1[];

  char ZoneListType2[];
  if (ZoneListType2[0] > 1)
    char ZoneListPath2[];

  char ZoneListType3[];
  if (ZoneListType3[0] > 1)
    char ZoneListPath3[];

  char ZoneIndoorScrType[];
  if (ZoneIndoorScrType[0] > 1)
    char ZoneIndoorScrPath[];

  char ZoneIndoorEfcType[];
  if (ZoneIndoorEfcType[0] > 1)
    char ZoneIndoorEfcPath[];

  float mDayNightLightChgFrame;
  float mDayNightFogChgFrame;

  s32 mSkyInfiniteLightGroupType;

  char ZoneUnitCtrlType0[];
  if (ZoneUnitCtrlType0[0] > 1)
    char ZoneUnitCtrlPath0[];

  char ZoneUnitCtrlType1[];
  if (ZoneUnitCtrlType1[0] > 1)
    char ZoneUnitCtrlPath1[];

  char ZoneUnitCtrlType2[];
  if (ZoneUnitCtrlType2[0] > 1)
    char ZoneUnitCtrlPath2[];

  char ZoneStatusType[];
  if (ZoneStatusType[0] > 1)
    char ZoneStatusPath[];

  char SoundZoneType0[];
  if (SoundZoneType0[0] > 1)
    char SoundZonePath0[];

  char SoundZoneType1[];
  if (SoundZoneType1[0] > 1)
    char SoundZonePath1[];

  char SoundZoneType2[];
  if (SoundZoneType2[0] > 1)
    char SoundZonePath2[];

  float mEqLength[4];

  char SoundAreaInfoSoundInfoType[];
  if (SoundAreaInfoSoundInfoType[0] > 1)
    char SoundAreaInfoSoundInfoPath[];

  char SchedulerEffectSchdlType[];
  if (SchedulerEffectSchdlType[0] > 1)
    char SchedulerEffectSchdlPath[];

  char SchedulerLanternSchdlType[];
  if (SchedulerLanternSchdlType[0] > 1)
    char SchedulerLanternSchdlPath[];

  bool mIsCraftStage;

  char LocationDataLocationType[];
  if (LocationDataLocationType[0] > 1)
    char LocationDataLocationPath[];

  float mGrassVisiblePercentMulValue;
  float mGrassFadeBeginDistance;
  float mGrassFadeEndDistance;

  u16 mPerformanceFlag;
  char mAnotherMapName[];
};

rStageInfo rstageinfo_at_0x08 @0x08;