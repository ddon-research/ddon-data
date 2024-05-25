#define f32 float

struct MtVector3
{
	f32 x;
	f32 y;
	f32 z;
	f32 pad;
};

struct MtString
{
	char value[];
};

struct MtArray
{
	bool mAutoDelete;
	u32 mLength;
};

bitfield FieldFlag
{
type:
	8;
attr:
	8;
bytes:
	15;
disable:
	1;
};

bitfield ObjectFlag
{
prop_num:
	15;
init:
	1;
reserved:
	16;
};

struct PROPERTYDATA
{
	u32 ownerOffset; // fieldNameOffsetFromBase;
	FieldFlag param32;
	u32 unk2;
	u32 unk3;
	u32 unk4;
	u32 unk5;
};

struct OBJECTDATA
{
	u32 mClassID; // jamCRC
	ObjectFlag param32;
	PROPERTYDATA fields[param32.prop_num];
};

struct ClassHeader
{
	u32 numClasses;
	u32 bufferSizeForHeader;
	u32 classOffsets[numClasses];
	// <- this is now the new base offset
	OBJECTDATA classHeaders[numClasses];
};

fn getClassPropTotal(ClassHeader classHeader)
{
	u32 total = 0;
	for (u8 i = 0, i < classHeader.numClasses, i = i + 1)
	{
		total += classHeader.classHeaders[i].param32.prop_num;
	}
	return total;
};

struct Header
{
	ClassHeader classHeader;
	MtString fieldNames[getClassPropTotal(classHeader)];
	padding[3]; // adjust as needed
};

struct rOmKey_cOmKey
{
	u16 index1;
	u16 propertyIndex;
	u32 bufferSize;

	u32 propertySet1;
	s32 mOmID;

	u32 propertySet2;
	u32 mKeyType;

	u32 propertySet3;
	MtVector3 mPos;

	u32 propertySet4;
	bool mbHorizontal;
};

struct rOmKey_cItem
{
	u16 index1;
	u16 propertyIndex;
	u32 bufferSize;

	u32 propertySet1;
	s32 mItemIndex;

	u32 propertySet2;
	u32 mColor;
};

struct rOmKey
{
	u32 propertySet0;
	u16 index1;
	u16 propertyIndex;
	u32 bufferSize;

	u32 propertySet1;
	MtArray mEditList1;
	rOmKey_cOmKey ListData1[mEditList1.mLength];

	u32 propertySet2;
	u16 index2;
	u16 propertyIndex2;
	u32 bufferSize2;

	u32 propertySet3;
	MtArray mEditList2;
	rOmKey_cItem ListData2[mEditList2.mLength];
};

struct Body
{
	u32 bufferSize;

	u32 propertySet1;
	u32 mQuality;

	rOmKey deserializedResource;
};

struct File
{
	u32 magicNumber;
	u16 serializerVersion;
	u16 classVersion;
	u32 objectDataNum;

	u32 headerIndex;
	Header header;

	u32 bodyIndex;
	Body body;
};

File file_at_0x00 @0x00;