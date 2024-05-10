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
  s16 mIndex[6];
  u32 mIndexNum;
};

struct rStageConnect_Data
{
  u32 mType;
  MtVector3 mPos;
  u32 mPartsNo;
  u32 mMapGroup;
};

struct rStageConnect
{
  u32 mConnectorNum;
  rStageConnect_Data mpConnectorArray[mConnectorNum];

  u32 mConnectionNum;
  rStageConnect_Connect mpConnectionArray[mConnectionNum];
};