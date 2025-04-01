#define f32 float

struct MtObject
{
};

struct cResource : MtObject
{
};

struct MtVector2
{
  f32 x;
  f32 y;
};

struct MtVector3
{
  f32 x;
  f32 y;
  f32 z;
  f32 pad_;
};

struct MtVector4
{
  f32 x;
  f32 y;
  f32 z;
  f32 w;
};

struct MtHermiteCurve
{
  f32 x[8];
  f32 y[8];
};

struct MtMatrix
{
  MtVector4 m[4];
};

enum MtProperty_TYPE : s32
{
  TYPE_UNDEFINED = 0x0,
  TYPE_CLASS = 0x1,
  TYPE_CLASSREF = 0x2,
  TYPE_BOOL = 0x3,
  TYPE_U8 = 0x4,
  TYPE_U16 = 0x5,
  TYPE_U32 = 0x6,
  TYPE_U64 = 0x7,
  TYPE_S8 = 0x8,
  TYPE_S16 = 0x9,
  TYPE_S32 = 0xA,
  TYPE_S64 = 0xB,
  TYPE_F32 = 0xC,
  TYPE_F64 = 0xD,
  TYPE_STRING = 0xE,
  TYPE_COLOR = 0xF,
  TYPE_POINT = 0x10,
  TYPE_SIZE = 0x11,
  TYPE_RECT = 0x12,
  TYPE_MATRIX = 0x13,
  TYPE_VECTOR3 = 0x14,
  TYPE_VECTOR4 = 0x15,
  TYPE_QUATERNION = 0x16,
  TYPE_PROPERTY = 0x17,
  TYPE_EVENT = 0x18,
  TYPE_GROUP = 0x19,
  TYPE_PAGE_BEGIN = 0x1A,
  TYPE_PAGE_END = 0x1B,
  TYPE_EVENT32 = 0x1C,
  TYPE_ARRAY = 0x1D,
  TYPE_PROPERTYLIST = 0x1E,
  TYPE_GROUP_END = 0x1F,
  TYPE_CSTRING = 0x20,
  TYPE_TIME = 0x21,
  TYPE_FLOAT2 = 0x22,
  TYPE_FLOAT3 = 0x23,
  TYPE_FLOAT4 = 0x24,
  TYPE_FLOAT3x3 = 0x25,
  TYPE_FLOAT4x3 = 0x26,
  TYPE_FLOAT4x4 = 0x27,
  TYPE_EASECURVE = 0x28,
  TYPE_LINE = 0x29,
  TYPE_LINESEGMENT = 0x2A,
  TYPE_RAY = 0x2B,
  TYPE_PLANE = 0x2C,
  TYPE_SPHERE = 0x2D,
  TYPE_CAPSULE = 0x2E,
  TYPE_AABB = 0x2F,
  TYPE_OBB = 0x30,
  TYPE_CYLINDER = 0x31,
  TYPE_TRIANGLE = 0x32,
  TYPE_CONE = 0x33,
  TYPE_TORUS = 0x34,
  TYPE_ELLIPSOID = 0x35,
  TYPE_RANGE = 0x36,
  TYPE_RANGEF = 0x37,
  TYPE_RANGEU16 = 0x38,
  TYPE_HERMITECURVE = 0x39,
  TYPE_ENUMLIST = 0x3A,
  TYPE_FLOAT3x4 = 0x3B,
  TYPE_LINESEGMENT4 = 0x3C,
  TYPE_AABB4 = 0x3D,
  TYPE_OSCILLATOR = 0x3E,
  TYPE_VARIABLE = 0x3F,
  TYPE_VECTOR2 = 0x40,
  TYPE_MATRIX33 = 0x41,
  TYPE_RECT3D_XZ = 0x42,
  TYPE_RECT3D = 0x43,
  TYPE_RECT3D_COLLISION = 0x44,
  TYPE_PLANE_XZ = 0x45,
  TYPE_RAY_Y = 0x46,
  TYPE_POINTF = 0x47,
  TYPE_SIZEF = 0x48,
  TYPE_RECTF = 0x49,
  TYPE_EVENT64 = 0x4A,
  TYPE_ENUM_RESOURCE_QUALITY = 0x106,
  TYPE_CUSTOM = 0x80,
};

enum rScheduler_KEY_MODE : s32
{
  MODE_CONSTANT = 0x0,
  MODE_OFFSET = 0x1,
  MODE_TRIGGER = 0x2,
  MODE_LINEAR = 0x3,
  MODE_OFFSET_F = 0x4,
  MODE_HERMITE = 0x5,
};

enum rScheduler_TRACK_TYPE : s32
{
  TYPE_UNKNOWN = 0x0,
  TYPE_ROOT = 0x1,
  TYPE_UNIT = 0x2,
  TYPE_SYSTEM = 0x3,
  TYPE_SCHEDULER = 0x4,
  TYPE_OBJECT = 0x5,
  TYPE_INT = 0x6,
  TYPE_INT64 = 0x7,
  TYPE_VECTOR = 0x8,
  TYPE_FLOAT = 0x9,
  TYPE_FLOAT64 = 0xA,
  TYPE_BOOL = 0xB,
  TYPE_REF = 0xC,
  TYPE_RESOURCE = 0xD,
  TYPE_STRING = 0xE,
  TYPE_EVENT = 0xF,
  TYPE_MATRIX = 0x10,
};

enum MtDTI : s32
{
  None = 0,
  sEffectExt = 1338348278,
  uScrBaseModel = 517287601,
  sWeatherManager = 23040018,
  uOfsMotionCamera = 1721483090,
  sCameraExt = 240824064,
  uImagePlaneFilter = 346344521,
  uDDOActorModelPl = 1202664442,
};

bitfield rScheduler_KEY
{
frame:
  24;
  rScheduler_KEY_MODE mode : 8;
};

bitfield TrackBits
{
  rScheduler_TRACK_TYPE track_type : 8;
  MtProperty_TYPE prop_type : 8;
key_num:
  16;
};

struct rScheduler_TRACK
{
  TrackBits trackBits;

  u32 parent_index;
  u32 track_name_offset;
  char track_name[] @Header.meta_data_offset + track_name_offset;
  MtDTI dti_id;
  u64 unit_group;

  u32 key_frame_offset;
  rScheduler_KEY key_frame[trackBits.key_num] @key_frame_offset; //*

  u32 key_value_offset;
  match(trackBits.prop_type)
  {
    (MtProperty_TYPE::TYPE_U32) : u32 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_U16) : u16 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_S32) : s32 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_S16) : s16 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_BOOL) : bool key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_F32) : f32 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_HERMITECURVE) : MtHermiteCurve key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_MATRIX) : MtMatrix key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_FLOAT2) : MtVector2 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_VECTOR3) : MtVector3 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_VECTOR4) : MtVector4 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_QUATERNION) : MtVector4 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_CLASSREF) : u32 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_EVENT) : u32 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_EVENT32) : u32 key_value[trackBits.key_num] @key_value_offset;
    (MtProperty_TYPE::TYPE_CUSTOM) :
    {
      u32 key_value[trackBits.key_num] @key_value_offset;
      char key_value_name[] @(Header.meta_data_offset + key_value[0]); // NOTE: won't work if there are more than one, but imhex doesn't easily work with loops
    }
  }
};

bitfield FrameBits
{
frame_max:
  24;
floor_frame:
  1;
reserved:
  7;
};

struct rScheduler_HEADER
{
  u32 magic;
  u16 version;
  u16 track_num;
  u32 crc;
  FrameBits frameBits;
  u32 base_track;
  u32 meta_data_offset;
};

struct rScheduler : cResource
{
  rScheduler_HEADER Header; //*
};

rScheduler_HEADER Header @0x00;
rScheduler_TRACK track[Header.track_num] @ sizeof(Header);