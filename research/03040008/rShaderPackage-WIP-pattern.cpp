#define uintptr u32
#define SO_HANDLE u32

struct MtObject
{
};

struct cResource : MtObject
{
};

struct nDraw_SHADER_INPUT
{
  SO_HANDLE layouts[4];
  // u32 crc;
  // u32 padding1;
  // void *playout;
};

bitfield nDraw_SHADER_CODE_bits
{
reserved:
  1;
compiled:
  1;
regcount:
  8;
codesize:
  22;
};

struct nDraw_SHADER_CODE
{
  nDraw_SHADER_CODE_bits bits;
  u32 crc;
  u32 pcode_offset;
  u8 pcode[bits.codesize] @mHeader.body_offset + pcode_offset;
};

bitfield rShaderPackage_SHADER_TABLE_bits
{
index:
  31;
conflict:
  1;
};

struct rShaderPackage_SHADER_TABLE2
{
  //u64 id;
  //u32 next;
  rShaderPackage_SHADER_TABLE_bits bits;
};

struct rShaderPackage_SHADER_TABLE
{
  // u64 id;
  // u32 next;
  rShaderPackage_SHADER_TABLE_bits bits;
};

bitfield nDraw_SHADER_PARAM_bits
{
slot:
  6;
index:
  10;
size:
  16;
};

struct nDraw_SHADER_PARAM
{
  nDraw_SHADER_PARAM_bits constantoOrSampleOrTexture;
};

struct rShaderPackage_CORE
{
  u32 params_offset;
  u32 resources_offset;
  u32 tables_offset;
  u32 vs_list_offset;
  u32 ps_list_offset;
  u32 gs_list_offset;
  u32 ia_list_offset;
  rShaderPackage_SHADER_TABLE2 ptable[(params_offset-28)/4]; //* probably not entirely correct? works as a lookup table for shaders


  nDraw_SHADER_PARAM params[(resources_offset - params_offset) / 4] @ sizeof(mHeader) + params_offset; //* unsure where to get param count from

  SO_HANDLE resources[mHeader.resource_num] @ sizeof(mHeader) + resources_offset; //*

  rShaderPackage_SHADER_TABLE tables[(vs_list_offset - tables_offset) / 4] @ sizeof(mHeader) + tables_offset; //* table num does not work

  nDraw_SHADER_CODE vs_list[mHeader.vs_num] @ sizeof(mHeader) + vs_list_offset; //*

  nDraw_SHADER_CODE ps_list[mHeader.ps_num] @ sizeof(mHeader) + ps_list_offset; //*

  nDraw_SHADER_CODE gs_list[mHeader.gs_num] @ sizeof(mHeader) + gs_list_offset; //*

  nDraw_SHADER_INPUT ia_list[mHeader.table_num] @(sizeof(mHeader) + ia_list_offset); //*


  // nDraw::SHADER shaders[1];
};

struct rShaderPackage_HEADER
{
  u32 magic;
  u32 shader_version; // HLSL Shader Compiler 9.29.952.3111
  u16 version;
  u16 shader_num;
  u16 vs_num; // Vertex Shader, vs_3_0
  u16 ps_num; // Pixel Shader, ps_3_0
  u16 gs_num; // Geometry Shader, unused
  u16 ia_num;
  u32 table_num;
  u32 resource_num;
  u32 body_size;
  uintptr body_offset;
};

struct rShaderPackage : cResource
{
  rShaderPackage_CORE mpCore; //*
  // u8 mpBody[mHeader.body_size] @ mHeader.body_offset;//*
};

rShaderPackage_HEADER mHeader @0x00;
rShaderPackage rshaderpackage_at_0x00 @ sizeof(mHeader);
