struct MtObject
{
};

struct cResource
{
    char magicString[4];
    u32 magicVersion;
};

struct MtVector3
{
  float x;
  float y;
  float z;
};

struct rStageConnect_Connect
{
  s16 mStart;
  s16 mGoal;
  u32 mIndexNum;
  s16 mIndex[6];
};

struct rStageConnect_Data
{
  u32 mType;
  MtVector3 mPos;
  u32 mPartsNo;
  u32 mMapGroup;
};

struct rStageConnect : cResource
{
  u32 mConnectorNum;
  rStageConnect_Data mpConnectorArray[mConnectorNum];

  u32 mConnectionNum;
  rStageConnect_Connect mpConnectionArray[mConnectionNum];
};

rStageConnect rstageconnect_at_0x00 @ 0x00;
