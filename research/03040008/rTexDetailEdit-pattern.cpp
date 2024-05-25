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

struct rTexDetailEdit_Param
{
	u16 index1;
	u16 propertyIndex;
	u32 bufferSize;
	u32 propertyCount1;
	char mPath[];
	u32 propertyCount2;
	u32 mForm;
	u32 propertyCount3;
	u32 mType;
};

struct rTexDetailEdit
{
	u16 index1;
	u16 propertyIndex;
	u32 bufferSize;

	u32 propertySet;
	MtArray mEditList;
	rTexDetailEdit_Param ListData[mEditList.mLength];
};

struct Body
{
	u32 bufferSize;

	u32 propertySet1;
	u32 mQuality;

	u32 propertySet2;
	rTexDetailEdit deserializedResource;
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
