#define DWORD u32

enum dwCaps_ENUM : s32
{

    DDSCAPS_COMPLEX = 0x8,
    DDSCAPS_MIPMAP = 0x400000,
    DDSCAPS_TEXTURE = 0x1000

};

enum DDS_PIXELFORMAT_FLAGS : s32
{
    DDPF_ALPHAPIXELS = 0x1,
    DDPF_ALPHA = 0x2,
    DDPF_FOURCC = 0x4,
    DDPF_RGB = 0x40,         // 7
    DDPF_YUV = 0x200,        // 10
    DDPF_LUMINANCE = 0x20000 // 18
};

struct DDS_PIXELFORMAT
{
    DWORD dwSize;
    DWORD dwFlags;
    DWORD dwFourCC;
    DWORD dwRGBBitCount;
    DWORD dwRBitMask;
    DWORD dwGBitMask;
    DWORD dwBBitMask;
    DWORD dwABitMask;
};

enum DDS_FLAGS : s32
{
    DDSD_CAPS = 0x1,
    DDSD_HEIGHT = 0x2,
    DDSD_WIDTH = 0x4,
    DDSD_PITCH = 0x8,

    DDSD_PIXELFORMAT = 0x1000,  // 13
    DDSD_MIPMAPCOUNT = 0x20000, // 18

    DDSD_LINEARSIZE = 0x80000, // 20

    DDSD_DEPTH = 0x800000 // 24
};

bitfield DDS_FLAG_BITS
{
DDSD_CAPS:
    1;
DDSD_HEIGHT:
    1;
DDSD_WIDTH:
    1;
DDSD_PITCH:
    1;
reserved1:
    8;
DDSD_PIXELFORMAT:
    1; // 13
reserved2:
    4;
DDSD_MIPMAPCOUNT:
    1; // 18
reserved3:
    1;
DDSD_LINEARSIZE:
    1; // 20
reserved4:
    3;
DDSD_DEPTH:
    1; // 24
reserved5:
    8;
};

struct DDS_HEADER
{
    DWORD magic;
    DWORD dwSize;
    DDS_FLAG_BITS dwFlags;
    DWORD dwHeight;
    DWORD dwWidth;
    DWORD dwPitchOrLinearSize;
    DWORD dwDepth;
    DWORD dwMipMapCount;
    DWORD dwReserved1[11];
    DDS_PIXELFORMAT ddspf;
    DWORD dwCaps;
    DWORD dwCaps2;
    DWORD dwCaps3;
    DWORD dwCaps4;
    DWORD dwReserved2;
};
DDS_HEADER dds_header_at_0x00 @0x00;