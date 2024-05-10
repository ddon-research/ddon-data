struct MtString
{
	char value[];
};

struct MtArray
{
	bool mAutoDelete;
	//  MtObject **mpArray;
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
	// <- this is now the new base offset, i.e. 24 for this file
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
	MtString fieldNames[getClassPropTotal(classHeader) - 1];
	padding[2]; // adjust as needed
};

struct Body
{
	u32 bufferSizeForBody;
	u8 dataBlock[bufferSizeForBody - 4];
};

struct File
{
	u32 magicNumber;
	u16 serializerVersion;
	u16 classVersion;
	u32 objectDataNum;

	u32 headerIndex;
	Header header[1];
	u32 bodyIndex;
	Body body[1];
};

File file_at_0x00 @0x00;
