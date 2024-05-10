struct MtFloat4
{
  float x;
  float y;
  float z;
  float w;
};

struct rMaterialLUT_INFO
{
  u32 type;
  u32 format;
  u32 width;
  u32 height;
  float min_value;
  float max_value;
  float param1;
  float param2;
  u16 hermite_x[8];
  u16 hermite_y[8];
};

struct rTextureSHFACTOR
{
  float r[9];
  float g[9];
  float b[9];
};

bitfield nDrawOBJECT_BITS
{
type:
  6;
attr:
  16;
annotation_num:
  10;
sindex:
  16;
index:
  16;
};

struct nDrawOBJECT
{
  char name[];
  char sname[];
  nDrawOBJECT_BITS bits;
  u32 hash;
  // u32 padding1;
  nDrawVARIABLE *annotations;
};

bitfield nDrawTEXTURE_BITS
{
ttype:
  8;
dtype:
  8;
row_num:
  4;
col_num:
  4;
reserved:
  8;
};

struct nDrawTEXTURE : nDrawOBJECT
{
  nDrawTEXTURE_BITS bits;
  MtFloat4 null_value;
};

struct rTexture
{
  rTextureSHFACTOR mSHFactor;
  nDrawTexture *mpTexture; //*
  float mOrgInvWidth;
  float mOrgInvHeight;
  u32 mOrgWidth;
  u32 mOrgHeight;
  u32 mOrgDepth;
  u32 mDetailBias;
  bool mbStream;
  u32 mStreamLv;
};

union rMaterialTEXTURE_INFO_LUT
{
  char rpath[64];
  rMaterialLUT_INFO lutinfo;
};

struct rMaterialTEXTURE_INFO
{
  u32 dti;
  // u32 padding1;
  // rTexture *ptex;
  // nDraw::Texture *plut;
  rMaterialTEXTURE_INFO_LUT _anon_0;
};

union nDrawSHADER_STATE_UNION_PTR
{
  u64 ivalue;
  // u64 *pvalue;
};

struct nDrawSHADER_STATE
{
  nDrawSHADER_STATE_UNION_PTR _anon_0;
  u32 crc;
  // u32 padding1;
};

bitfield nDrawMaterialSTATE_BITS
{
type:
  4;
group:
  16;
index:
  12;
};

struct nDrawMaterialSTATE
{
  nDrawMaterialSTATE_BITS bits;
  // u32 padding1;
  nDrawSHADER_STATE state;
};

bitfield nDrawAnimationPARAM_BITS
{
type:
  4;
interpolate:
  4;
key_num:
  24;
};

struct nDrawAnimationPARAM
{
  u32 handle;
  nDrawAnimationPARAM_BITS bits;
};

bitfield nDrawAnimationANIMATION_BITS
{
repeat:
  1;
run:
  1;
param_num:
  16;
cbuffer_num:
  14;
};
struct nDrawAnimationANIMATION
{
  u32 length;
  nDrawAnimationANIMATION_BITS bits;
  u32 cbuffers; //*
  u32 crc;
  // u32 padding1;
  nDrawAnimationPARAM params[1]; //*
};

struct nDrawAnimationANIMATION_LIST
{
  u32 animation_num;
  // u32 padding1;
  nDrawAnimationANIMATION animations[1]; //*
};
bitfield rMaterialMATERIAL_INFO_BITS
{
state_num:
  12;
reserved1:
  1;
id:
  16;
fog:
  1;
tangent:
  1;
half_lambert:
  1;
stencil_ref:
  8;
alphatest_ref:
  8;
polygon_offset:
  4;
alphatest:
  1;
alphatest_func:
  3;
draw_pass:
  5;
layer_id:
  2;
deferred_lighting:
  1;
};
struct rMaterialMATERIAL_INFO
{
  u32 dti; // offset into file for JamCRC of DTI
  // u32 padding1;
  u32 state_bufsize;
  u32 name;

  u32 bsstate;
  u32 dsstate;
  u32 rsstate;
  rMaterialMATERIAL_INFO_BITS bits;
  MtFloat4 blend_factor;
  u32 animation_bufsize;
  nDrawMaterialSTATE states[bits.state_num];   //*
  nDrawAnimationANIMATION_LIST animation_list; //*
};

struct rMaterialHEADER
{
  u32 magic;
  u32 version;
  u32 material_num;
  u32 texture_num;
  u32 shader_version;
  // u32 padding1;
  rMaterialTEXTURE_INFO textures[texture_num]; //*
  // rMaterialMATERIAL_INFO materials[material_num];//*
};

rMaterialHEADER rmaterialheader_at_0x00 @0x00;
