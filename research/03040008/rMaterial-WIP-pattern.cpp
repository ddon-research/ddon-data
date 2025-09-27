#define f32 float
// Shared or Shader Object handle
#define SO_HANDLE u32
#define uintptr u32

struct MtObject
{
};

struct cResource : MtObject
{
};

enum nDraw_Animation_TYPE : s32
{
  TYPE_FLOAT = 0x0,
  TYPE_VECTOR = 0x1,
  TYPE_INT = 0x2,
  TYPE_TEX = 0x3,
  TYPE_LEGACY = 0x4,
  TYPE_SAMPLER = 0x5,
  TYPE_TEXCOORD = 0x6,
  TYPE_TEXCOORD2 = 0x7,
};

enum nDraw_PASS_TYPE : s32
{
  PASS_SUBSCENE = 0x0,
  PASS_BEGIN = 0x1,
  PASS_BACKFACE_ZPASS = 0x2,
  PASS_ZPREPASS = 0x3,
  PASS_GBUFFER = 0x4,
  PASS_GBUFFER_OVERLAP = 0x5,
  PASS_LIGHT_MASK = 0x6,
  PASS_LIGHTING = 0x7,
  PASS_GBUFFER_TRANS = 0x8,
  PASS_LIGHTING_TRANS = 0x9,
  PASS_AMBIENT_MASK = 0xA,
  PASS_TANGENT = 0xB,
  PASS_SOLID = 0xC,
  PASS_ALPHA_MASK = 0xD,
  PASS_FILL = 0xE,
  PASS_OVERLAP = 0xF,
  PASS_WATER = 0x10,
  PASS_TRANSPARENT = 0x11,
  PASS_ZPOSTPASS = 0x12,
  PASS_EFFECT = 0x13,
  PASS_PREFILTER = 0x14,
  PASS_DISTORTION = 0x15,
  PASS_FILTER = 0x16,
  PASS_SCREEN = 0x17,
  PASS_END = 0x18,
  MAX_PASS = 0x19,
};

enum nDraw_FORMAT_TYPE : s32
{
  FORMAT_UNKNOWN = 0x0,
  FORMAT_R32G32B32A32_FLOAT = 0x1,
  FORMAT_R16G16B16A16_FLOAT = 0x2,
  FORMAT_R16G16B16A16_UNORM = 0x3,
  FORMAT_R16G16B16A16_SNORM = 0x4,
  FORMAT_R32G32_FLOAT = 0x5,
  FORMAT_R10G10B10A2_UNORM = 0x6,
  FORMAT_R8G8B8A8_UNORM = 0x7,
  FORMAT_R8G8B8A8_SNORM = 0x8,
  FORMAT_R8G8B8A8_UNORM_SRGB = 0x9,
  FORMAT_B4G4R4A4_UNORM = 0xA,
  FORMAT_R16G16_FLOAT = 0xB,
  FORMAT_R16G16_UNORM = 0xC,
  FORMAT_R16G16_SNORM = 0xD,
  FORMAT_R32_FLOAT = 0xE,
  FORMAT_D24_UNORM_S8_UINT = 0xF,
  FORMAT_R16_FLOAT = 0x10,
  FORMAT_R16_UNORM = 0x11,
  FORMAT_A8_UNORM = 0x12,
  FORMAT_BC1_UNORM = 0x13,
  FORMAT_BC1_UNORM_SRGB = 0x14,
  FORMAT_BC2_UNORM = 0x15,
  FORMAT_BC2_UNORM_SRGB = 0x16,
  FORMAT_BC3_UNORM = 0x17,
  FORMAT_BC3_UNORM_SRGB = 0x18,
  FORMAT_BCX_GRAYSCALE = 0x19,
  FORMAT_BCX_ALPHA = 0x1A,
  FORMAT_BC5_SNORM = 0x1B,
  FORMAT_B5G6R5_UNORM = 0x1C,
  FORMAT_B5G5R5A1_UNORM = 0x1D,
  FORMAT_BCX_NM1 = 0x1E,
  FORMAT_BCX_NM2 = 0x1F,
  FORMAT_BCX_RGBI = 0x20,
  FORMAT_BCX_RGBY = 0x21,
  FORMAT_B8G8R8X8_UNORM = 0x22,
  FORMAT_BCX_RGBI_SRGB = 0x23,
  FORMAT_BCX_RGBY_SRGB = 0x24,
  FORMAT_BCX_NH = 0x25,
  FORMAT_R11G11B10_FLOAT = 0x26,
  FORMAT_B8G8R8A8_UNORM = 0x27,
  FORMAT_B8G8R8A8_UNORM_SRGB = 0x28,
  FORMAT_BCX_RGBNL = 0x29,
  FORMAT_BCX_YCCA = 0x2A,
  FORMAT_BCX_YCCA_SRGB = 0x2B,
  FORMAT_R8_UNORM = 0x2C,
  FORMAT_B8G8R8A8_UNORM_LE = 0x2D,
  FORMAT_B10G10R10A2_UNORM_LE = 0x2E,
  FORMAT_BCX_SRGBA = 0x2F,
  FORMAT_BC7_UNORM = 0x30,
  FORMAT_BC7_UNORM_SRGB = 0x31,
  FORMAT_SE5M9M9M9 = 0x32,
  FORMAT_R10G10B10A2_FLOAT = 0x33,
  FORMAT_YVU420P2_CSC1 = 0x34,
  FORMAT_R8A8_UNORM = 0x35,
  FORMAT_A8_UNORM_WHITE = 0x36,
};

enum nDraw_Material_STATE_TYPE : s32
{
  STATE_FUNCTION = 0x0,
  STATE_CBUFFER = 0x1,
  STATE_SAMPLER = 0x2,
  STATE_TEXTURE = 0x3,
  STATE_PROCEDURAL = 0x4,
};

struct MtFloat4
{
  float x;
  float y;
  float z;
  float w;
};

enum MtDTI : u32
{
  rTexture = 606035435,
  nDraw_DDMrlStdEstScr = 2047959896,
  nDraw_DDMrlStdEstObj = 1700434011,
  rRenderTargetTexture = 2013850128,
};

bitfield nDraw_Animation_PARAM_bits
{
  nDraw_Animation_TYPE type : 4;
interpolate:
  4;
key_num:
  24;
};

struct nDraw_Animation_PARAM
{
  SO_HANDLE handle;
  nDraw_Animation_PARAM_bits bits;
};

bitfield nDraw_Animation_ANIMATION_bits
{
  bool repeat : 1;
  bool run : 1;
param_num:
  16;
cbuffer_num:
  14;
};

struct nDraw_Animation_ANIMATION
{
  u32 length;
  nDraw_Animation_ANIMATION_bits bits;
  SO_HANDLE cbuffers[bits.cbuffer_num]; //*
  u32 crc;
  // u32 padding;
  nDraw_Animation_PARAM params[bits.param_num]; //*
};

struct nDraw_Animation_ANIMATION_LIST
{
  u32 animation_num;
  // u32 padding;
  nDraw_Animation_ANIMATION animations[animation_num]; //*
};

union nDraw_SHADER_STATE_union
{
  // There are SO_HANDLE arrays defined in the client, e.g. qword_1C1BCD0
  uintptr ivalue;
  // void *pvalue;//*
};

struct nDraw_SHADER_STATE
{
  nDraw_SHADER_STATE_union value;
  u32 crc;
  // u32 padding;
};

bitfield nDraw_Material_STATE_bits
{
  nDraw_Material_STATE_TYPE type : 4;
group:
  16;
index:
  12;
};

struct nDraw_Material_STATE
{
  nDraw_Material_STATE_bits bits;
  // u32 padding;
  nDraw_SHADER_STATE state;
};

bitfield rMaterial_MATERIAL_INFO_bits1
{
state_num:
  12;
reserved1:
  1;
id:
  16;
  bool fog : 1;
  bool tangent : 1;
  bool half_lambert : 1;
};

bitfield rMaterial_MATERIAL_INFO_bits2
{
stencil_ref:
  8;
alphatest_ref:
  8;
polygon_offset:
  4;
  bool alphatest : 1;
alphatest_func:
  3;
  nDraw_PASS_TYPE draw_pass : 5;
layer_id:
  2;
  bool deferred_lighting : 1;
};

struct rMaterial_MATERIAL_INFO
{
  MtDTI dti;
  // u32 padding1;
  u32 name;
  u32 state_bufsize;

  SO_HANDLE bsstate; // BlendState
  SO_HANDLE dsstate; // DepthStencilState
  SO_HANDLE rsstate; // RasterizerState

  rMaterial_MATERIAL_INFO_bits1 bits1;
  rMaterial_MATERIAL_INFO_bits2 bits2;

  MtFloat4 blend_factor;
  u32 animation_bufsize;
  u32 states_offset;
  if (states_offset > 0)
  {
    nDraw_Material_STATE states[bits1.state_num] @states_offset; //*
    f32 Unknown[(state_bufsize - sizeof(states)) / 4] @(states_offset + sizeof(states));
  }
  u32 animation_list_offset;
  if (animation_list_offset > 0)
  {
    nDraw_Animation_ANIMATION_LIST animation_list[bits1.state_num] @animation_list_offset; //*
  }
};

struct rMaterial_LUT_INFO
{
  u32 type;
  nDraw_FORMAT_TYPE format;
  u32 width;
  u32 height;
  f32 min_value;
  f32 max_value;
  f32 param1;
  f32 param2;

  u16 hermite_x[8];
  u16 hermite_y[8];
};

union rMaterial_TEXTURE_INFO_pathinfo
{
  char rpath[]; // 64
  rMaterial_LUT_INFO lutinfo;
};

struct rMaterial_TEXTURE_INFO
{
  MtDTI dti; // As long as a valid DTI is supplied, there is no LUT
  // u32 padding1;
  u32 ptex_num;
  // rTexture ptex;//* This is essentially constructed via the reference in pathinfo->rpath
  u32 plut_num;
  // nDraw_Texture plut;//*

  // random heuristic because it's a bit hard in ImHex to define a fallback case for enums
  if (dti > 1000000)
  {
    char rpath[];
    padding[64 - sizeof(rpath)];
  }
  else
  {
    rMaterial_LUT_INFO lutinfo;
  }
};

struct rMaterial_HEADER
{
  char magic[];
  u32 version;
  u32 material_num;
  u32 texture_num;
  u32 shader_version;
  u32 textures_offset;
  u32 materials_offset;
  rMaterial_TEXTURE_INFO textures[texture_num] @textures_offset;     //*
  rMaterial_MATERIAL_INFO materials[material_num] @materials_offset; //*
};

struct rMaterial : cResource
{
  rMaterial_HEADER mpHeader; //*
  // nDraw_Material mpMaterials;//**
};

rMaterial_HEADER mpHeader @0x00;