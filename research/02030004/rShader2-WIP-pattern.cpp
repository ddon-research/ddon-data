#define _stringPoolOffset 1222512
import std.io;

enum nDraw_TEXTURE_TYPE : s32
{
  TT_UNDEFINED = 0x0,
  TT_1D = 0x1,
  TT_2D = 0x2,
  TT_3D = 0x3,
  TT_1DARRAY = 0x4,
  TT_2DARRAY = 0x5,
  TT_CUBE = 0x6,
  TT_CUBEARRAY = 0x7,
  TT_2DMS = 0x8,
  TT_2DMSARRAY = 0x9,
};

enum nDraw_SHADER_TYPE : s32
{
  SHADER_VS = 0x0,
  SHADER_PS = 0x1,
  SHADER_GS = 0x2,
  SHADER_HS = 0x3,
  SHADER_DS = 0x4,
  SHADER_CS = 0x5,
  SHADER_ES = 0x6,
};

enum nDraw_CLASS_TYPE : s32
{
  CT_UNDEFINED = 0x0,
  CT_VOID = 0x1,
  CT_SCALAR = 0x2,
  CT_VECTOR = 0x3,
  CT_MATRIX = 0x4,
  CT_STRUCT = 0x5,
  CT_OBJECT = 0x6,
};

enum nDraw_DATA_TYPE : s32
{
  DT_UNDEFINED = 0x0,
  DT_FLOAT = 0x1,
  DT_HALF = 0x2,
  DT_BOOL = 0x3,
  DT_INT = 0x4,
  DT_UINT = 0x5,
  DT_DOUBLE = 0x6,
  DT_STRING = 0x7,
  DT_VOID = 0x8,
};

enum nDraw_OBJECT_TYPE : s32
{
  OT_CBUFFER = 0x0,
  OT_TEXTURE = 0x1,
  OT_FUNCTION = 0x2,
  OT_SAMPLER = 0x3,
  OT_BLEND = 0x4,
  OT_DEPTHSTENCIL = 0x5,
  OT_RASTERIZER = 0x6,
  OT_TECHNIQUE = 0x7,
  OT_STRUCT = 0x8,
  OT_INPUTLAYOUT = 0x9,
  OT_SAMPLERCMP = 0xA,
  OT_POINTSTREAM = 0xB,
  OT_LINESTREAM = 0xC,
  OT_TRIANGLESTREAM = 0xD,
  OT_INPUTPATCH = 0xE,
  OT_OUTPUTPATCH = 0xF,
};

enum nDraw_VARIABLE_ATTRIBUTE : s32
{
  VA_EXTERN = 0x1,
  VA_CONST = 0x2,
  VA_NOINTERPOLATION = 0x4,
  VA_SHARED = 0x8,
  VA_UNIFORM = 0x10,
  VA_VOLATILE = 0x20,
  VA_STATIC = 0x40,
  VA_UNORM = 0x80,
  VA_SNORM = 0x100,
  VA_IN = 0x200,
  VA_OUT = 0x400,
  VA_INOUT = 0x800,
  VA_INLINE = 0x1000,
  VA_ROW_MAJOR = 0x2000,
  VA_COLUMN_MAJOR = 0x4000,
  VA_PACKED = 0x8000,
  VA_POINT = 0x10000,
  VA_LINE = 0x20000,
  VA_TRIANGLE = 0x30000,
  VA_LINEADJ = 0x40000,
  VA_TRIANGLEADJ = 0x50000,
  VA_INSENSITIVENAME = 0x200000,
  VA_TARGET = 0x400000,
};

enum nDraw_INPUT_ELEMENT_FORMAT : s32
{
  IEF_UNDEFINED = 0x0,
  IEF_F32 = 0x1,
  IEF_F16 = 0x2,
  IEF_S16 = 0x3,
  IEF_U16 = 0x4,
  IEF_S16N = 0x5,
  IEF_U16N = 0x6,
  IEF_S8 = 0x7,
  IEF_U8 = 0x8,
  IEF_S8N = 0x9,
  IEF_U8N = 0xA,
  IEF_SCMP3N = 0xB,
  IEF_UCMP3N = 0xC,
  IEF_U8NL = 0xD,
  IEF_COLOR4N = 0xE,
  IEF_MAX = 0xF,
};

struct cResource
{
};

struct MT_CHAR
{
  char val[];
};

bitfield nDraw_OBJECT_attributes
{
  nDraw_OBJECT_TYPE type : 6;
attr:
  16;
annotation_num:
  10;
sindex:
  16;
index:
  16;
};

bitfield nDraw_INPUT_ELEMENT_attributes
{
sindex:
  6;
  nDraw_INPUT_ELEMENT_FORMAT format : 5;
count:
  7;
start:
  4;
offset:
  9;
instance:
  1;
};

bitfield nDraw_INPUTLAYOUT_attributes
{
element_num:
  16;
stride:
  16;
};

bitfield nDraw_STRUCT_attributes
{
size:
  10;
member_num:
  12;
rcount:
  10;
};

bitfield nDraw_VARIABLE_ClassInfo
{
attr:
  19;
  nDraw_CLASS_TYPE ctype : 3;
size:
  10;
};

bitfield nDraw_VARIABLE_AnnotationInfo
{
sindex:
  8;
offset:
  10;
svalue:
  6;
annotation_num:
  8;
};

bitfield nDraw_VARIABLE_DataTypeAndNum
{
  nDraw_DATA_TYPE dtype : 4;
col_num:
  4;
row_num:
  4;
reserved:
  8;
element_num:
  12;
};

bitfield nDraw_VARIABLE_HStruct
{
hstruct:
  12;
bitfieldPadding3:
  8;
bitfieldPadding4:
  12;
};

bitfield nDraw_VARIABLE_ObjectAndTextureType
{
bitfieldPadding1:
  12;
  nDraw_OBJECT_TYPE otype : 4;
  nDraw_TEXTURE_TYPE ttype : 4;
bitfieldPadding2:
  12;
};

union nDraw_VARIABLE_TypeInfo
{
  nDraw_VARIABLE_DataTypeAndNum type1;
  nDraw_VARIABLE_HStruct type2;
  nDraw_VARIABLE_ObjectAndTextureType type3;
};

struct nDraw_VARIABLE_STRING
{
  u32 stOffset;
  char sttringValue[] @_stringPoolOffset + stOffset;
};

struct nDraw_VARIABLE_INT
{
  u32 intValue;
};

struct nDraw_VARIABLE_FLOAT
{
  float floatValue;
};

struct nDraw_VARIABLE
{
  u32 nameOffset;
  // char name[] @_stringPoolOffset + nameOffset;
  nDraw_VARIABLE_ClassInfo classInfo;
  nDraw_VARIABLE_TypeInfo typeInfo;
  u32 snameOffset;
  char sname[] @_stringPoolOffset + snameOffset;
  nDraw_VARIABLE_AnnotationInfo annotationInfo;

  if (annotationInfo.annotation_num > 1)
  {
    u32 annotationsPointer;
    nDraw_VARIABLE annotations[annotationInfo.annotation_num] @annotationsPointer;
  }
  else if (annotationInfo.svalue > 0 || annotationInfo.offset > 0)
  {
    u32 padding1;
  }
  else if (annotationInfo.annotation_num == 0 && typeInfo.type1.dtype == nDraw_DATA_TYPE::DT_FLOAT)
  {
    u32 padding2; // maybe this is also simply the value of the float?
  }
  else if (annotationInfo.annotation_num == 0 && typeInfo.type1.dtype == nDraw_DATA_TYPE::DT_BOOL)
  {
    u32 padding3; // maybe this is also simply the value of the bool?
  }

  u32 pinitvaluesPointer;
  if (pinitvaluesPointer > 0)
  {
    u32 initValue @pinitvaluesPointer; // TODO: does this depend on the previous DT Type?
  }

  if (typeInfo.type1.dtype == nDraw_DATA_TYPE::DT_STRING)
  {
    u32 stPointer;
    nDraw_VARIABLE_STRING STRING @stPointer;
  }
  if (typeInfo.type1.dtype == nDraw_DATA_TYPE::DT_INT) // TODO: broken condition on newest object
  {
    u32 intPointer;
    nDraw_VARIABLE_INT INT @intPointer;
  }
};

struct nDraw_STRUCT
{
  nDraw_STRUCT_attributes attrs;

  u32 membersPointer;
  nDraw_VARIABLE members[attrs.member_num];
};

struct nDraw_INPUT_ELEMENT
{
  u32 snameOffset;
  char sname[] @_stringPoolOffset + snameOffset;
  nDraw_INPUT_ELEMENT_attributes attrs;
};

struct nDraw_INPUTLAYOUT
{
  nDraw_INPUTLAYOUT_attributes attrs;
  u32 padding1;
  nDraw_INPUT_ELEMENT elements[attrs.element_num];
};

struct nDraw_OBJECT
{
  u32 nameOffset;
  char name[] @_stringPoolOffset + nameOffset;
  u32 snameOffset;
  char sname[] @_stringPoolOffset + snameOffset;
  nDraw_OBJECT_attributes attributes;
  u32 hash;
  u32 padding1;
  if (attributes.type == nDraw_OBJECT_TYPE::OT_INPUTLAYOUT)
  { // case 9
    nDraw_INPUTLAYOUT INPUTLAYOUT;
  }
  else if (attributes.type == nDraw_OBJECT_TYPE::OT_STRUCT)
  { // case 8
    nDraw_STRUCT STRUCT;
  }
  else
  {
    break;
  }
};

struct rShader2_HEADER
{
  u32 magic;
  u16 majorVersion;
  u16 minorVersion;
  u32 shaderVersion;
  u32 objectNum;
  u32 stringPoolOffset;
};

struct rShader2 : cResource
{
  rShader2_HEADER Header;
  u32 ObjectsOffsets[Header.objectNum];
  nDraw_OBJECT Objects1[119]; // 119 is the first non-INPUTLAYOUT variant, STRUCT
};

rShader2 rshader2_at_0x00 @0x00;
// MT_CHAR string_pool[5692] @rshader2_.Header.stringPoolOffset;
nDraw_OBJECT ndraw_object_at_0x55C8 @0x55C8;
nDraw_OBJECT ndraw_object_at_0x56A0 @0x56A0;
nDraw_OBJECT ndraw_object_at_0x5768 @0x5768;
nDraw_OBJECT ndraw_object_at_0x57C0 @0x57C0;
nDraw_OBJECT ndraw_object_at_0x5818 @0x5818;
nDraw_OBJECT ndraw_object_at_0x588C @0x588C;
nDraw_OBJECT ndraw_object_at_0x591C @0x591C;
nDraw_OBJECT ndraw_object_at_0x5974 @0x5974;
nDraw_OBJECT ndraw_object_at_0x5AA8 @0x5AA8;
nDraw_OBJECT ndraw_object_at_0x5BDC @0x5BDC;
nDraw_OBJECT ndraw_object_at_0x5C50 @0x5C50;
nDraw_OBJECT ndraw_object_at_0x5D28 @0x5D28;

nDraw_OBJECT ndraw_object_at_0x5D80 @0x5D80;
nDraw_OBJECT ndraw_object_at_0x60E8 @0x60E8;
nDraw_OBJECT ndraw_object_at_0x6278 @0x6278;
nDraw_OBJECT ndraw_object_at_0x6350 @0x6350;
nDraw_OBJECT ndraw_object_at_0x6484 @0x6484;

nDraw_OBJECT ndraw_object_at_0x655C @0x655C;
nDraw_OBJECT ndraw_object_at_0x6608 @0x6608;
nDraw_OBJECT ndraw_object_at_0x6740 @0x6740;
nDraw_OBJECT ndraw_object_at_0x685C @0x685C;
nDraw_OBJECT ndraw_object_at_0x68D0 @0x68D0;
nDraw_OBJECT ndraw_object_at_0x6928 @0x6928;

nDraw_OBJECT ndraw_object_at_0x6A60 @0x6A60;

nDraw_OBJECT ndraw_object_at_0x6B44 @0x6B44;
nDraw_OBJECT ndraw_object_at_0x6BB8 @0x6BB8;
nDraw_OBJECT ndraw_object_at_0x6D28 @0x6D28;
nDraw_OBJECT ndraw_object_at_0x6E28 @0x6E28;
nDraw_OBJECT ndraw_object_at_0x6F7C @0x6F7C;
nDraw_OBJECT ndraw_object_at_0x707C @0x707C;
nDraw_OBJECT ndraw_object_at_0x710C @0x710C;
nDraw_OBJECT ndraw_object_at_0x7164 @0x7164;
nDraw_OBJECT ndraw_object_at_0x71A0 @0x71A0;
nDraw_OBJECT ndraw_object_at_0x7310 @0x7310;
nDraw_OBJECT ndraw_object_at_0x7464 @0x7464;
nDraw_OBJECT ndraw_object_at_0x759C @0x759C;
nDraw_OBJECT ndraw_object_at_0x7728 @0x7728;
nDraw_OBJECT ndraw_object_at_0x7800 @0x7800;
nDraw_OBJECT ndraw_object_at_0x78D8 @0x78D8;
nDraw_OBJECT ndraw_object_at_0x79B0 @0x79B0;
nDraw_OBJECT ndraw_object_at_0x7A88 @0x7A88;
nDraw_OBJECT ndraw_object_at_0x7AE0 @0x7AE0;

nDraw_OBJECT ndraw_object_at_0x7B7C @0x7B7C;
nDraw_OBJECT ndraw_object_at_0x7C94 @0x7C94;
nDraw_OBJECT ndraw_object_at_0x7F94 @0x7F94;
nDraw_OBJECT ndraw_object_at_0x8124 @0x8124;
nDraw_OBJECT ndraw_object_at_0x836C @0x836C;