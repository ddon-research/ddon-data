#define f32 float

struct MtObject
{
};

struct cResource
{
	u32 version;
};

struct MtVector3
{
	f32 x;
	f32 y;
	f32 z;
};

struct MtArray
{
	u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
	T arr[mLength];
};

struct cMandraActionParam : MtObject
{
	MtVector3 Pos;
	f32 AngleY;
	u16 Waypoint;
	u16 NpcMotNo;
	u16 StartIdx;
	s16 Message;
	u16 Condition;
	s16 LinkActNo;
	u16 LinkActLv;
	s16 ChangeEquip;
	bool IsGriffin;
	bool IsNotAvoid;
	bool IsSingle;
};

struct rMandraActionParam : cResource
{
	MtTypedArray<cMandraActionParam> Array;
};

rMandraActionParam rmandraactionparam_at_0x00 @0x00;