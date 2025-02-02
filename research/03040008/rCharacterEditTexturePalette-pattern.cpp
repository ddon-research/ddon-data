struct MtObject
{
};

struct rTexture
{
};

struct rTbl2Base
{
	u32 version;
};

struct cResPathBase
{
	u64 mId;
};

struct cResPath<rTexture> : cResPathBase
{
};

struct cCharacterEditPaletteBase : MtObject
{
	u32 mIconNo;
	u32 mReleaseVersion;
	u32 mFlag;
};

struct cCharacterEditTexturePalette : cCharacterEditPaletteBase
{
	u32 mUID;
	cResPath<rTexture> mPath;
	u32 mRandom;
};
struct rTbl2<cCharacterEditTexturePalette> : rTbl2Base
{
	u32 mDataNum;
	cCharacterEditTexturePalette mpData[mDataNum];
};

struct rCharacterEditTexturePalette : rTbl2<cCharacterEditTexturePalette>
{
};

rCharacterEditTexturePalette rcharacteredittexturepalette_at_0x00 @0x00;