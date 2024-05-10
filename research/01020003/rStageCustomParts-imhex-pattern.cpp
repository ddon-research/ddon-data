struct MtVector3
{
  float x;
  float y;
  float z;
};

struct MtColor
{
  u8 r;
  u8 g;
  u8 b;
  u8 a;
};

struct rStageCustom_Area
{
  s8 mAreaNo;
  u8 mFilterNo;
  s32 mGroupNo;
};

struct rStageCustomParts_Info
{
  char mModel[];
  char mScrSbc1[];
  char mEffSbc1[];
  char mScrSbc2[];
  char mEffSbc2[];
  char mScrSbc3[];
  char mEffSbc3[];
  char mLight[];
  char mNaviMesh[];
  char mEpv[];
  char mOccluder[];

  u16 mAreaNo;
  u16 mType;
  u32 mSize;
  float mOffsetZ;
  s32 mEpvIndexAlways;
  s32 mEpvIndexDay;
  s32 mEpvIndexNight;
  MtColor mColor;

  u64 mEfcColorZone;
  u64 mEfcCtrlZone;
  u64 mIndoorZoneScr;
  u64 mIndoorZoneEfc;
  u64 mLightAndFogZone;
  u64 mSoundAreaInfo;
  u64 mZoneUnitCtrl[3];
  u64 mZoneStatus;

  char mComment[];
};

struct rStageCustomParts_Filter
{
  char mFilter[];
};

struct rStageCustomParts_Param
{
  float mDelta;
  float mOffsetY;
};

struct rStageCustomParts
{
  rStageCustomParts_Param mParam;
  u32 mArrayInfoNum;
  rStageCustomParts_Info mpArrayInfo[mArrayInfoNum]; //*
  u32 mArrayFilterNum;
  rStageCustomParts_Filter mpArrayFilter[mArrayFilterNum]; //*
};

rStageCustomParts rstagecustomparts_at_0x08 @0x08;