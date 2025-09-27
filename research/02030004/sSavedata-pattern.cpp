#define sSavedata_RESULT s32
#define size_t s64
#define f32 float
#define t64 s64

struct MtObject
{
};

struct cSystem : MtObject
{
};

struct cStorageDataBase : MtObject
{
};

struct MtString
{
    char value[];
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


enum DTIId : u32{
    cGamePadInfo=1772587478,
};

enum sSavedata_TYPE : s32
{
  TYPE_UNDEFINED = 0x0,
  TYPE_BOOLEAN = 0x1,
  TYPE_U8 = 0x2,
  TYPE_U16 = 0x3,
  TYPE_U32 = 0x4,
  TYPE_U64 = 0x5,
  TYPE_S8 = 0x6,
  TYPE_S16 = 0x7,
  TYPE_S32 = 0x8,
  TYPE_S64 = 0x9,
  TYPE_F32 = 0xA,
  TYPE_F64 = 0xB,
  TYPE_BINARY = 0xC,
};

enum sSavedata_STATE : u32
{
  STATE_IDLE_1 = 0x0,
  STATE_EXECUTING = 0x1,
  STATE_BASE = 0x2,
};

enum sSavedata_OPMODE : u32
{
  OPMODE_NONE = 0x0,
  OPMODE_DELETE = 0x1,
  OPMODE_SAVE = 0x2,
  OPMODE_LOAD = 0x3,
  OPMODE_BASE = 0x4,
};

enum SAVEDATA_TYPE : s32
{
  SAVEDATA_TYPE_MAIN = 0x0,
  SAVEDATA_TYPE_EDIT = 0x1
};

struct sSavedata_HEADER
{
  u32 systemVersion;
  u32 appVersion;
  u32 labelSize;
  u32 reserved;
};

struct sSavedata_KEYTABLE
{
  //void *buf;
  //size_t size;

  u32 hash;
  sSavedata_TYPE type;
  size_t size;
};

struct sSavedata : cSystem
{
  //sSavedata_OPMODE mOpMode;
  //sSavedata_STATE mState;
  //sSavedata_RESULT mResult;
  //void *mpData;
  size_t mDataSize;
  sSavedata_HEADER mHdr;
  u32 mSavedataVersion;
  
  s32 mKeyTableNum;
  sSavedata_KEYTABLE mKeyTable[mKeyTableNum];//[200];
  
  //bool mThroughRunning;
  //bool mOverWrite;
  //bool mIsEncrypt;
  //u8 mCipherKey[64];
  //sSavedata_cStorageThread mStorageThread;
  //SceUserServiceUserId mUserId;
  //SceSaveDataTitleId mTitleId;//*
  //MtString mNewItemIconPath;
  //MtString mIconPath;
  //MtString mSaveDataDirName;
  //MtString mSaveDataFileName;
  //MtString mParamTitle;
  //MtString mParamSubTitle;
  //MtString mParamDetail;
  //MtString mNewItemTitle;
  //SceSaveDataIcon mIcon;
  //SceSaveDataIcon mNewItemIcon;
  //u32 mRequireBlocks;
  //SceSaveDataFingerprint mFingerprint;//*
  //bool mUseSearchCond;
  //MtString mSaveDataDirSearchCond;
  //SceSaveDataSortKey mSortKey;
  //SceSaveDataSortOrder mSortOrder;
  //u32 mListSaveCanCreateNum;
};

struct cStorageData_stTitle
{
  u8 mLookOpMovie;
  bool mIsFirstOption;
};

struct cStorageData_stOptionDataSystem
{
  u8 mGamma;
  u8 mVolChatRcv;
  u8 mVolSysSE;
  u8 mVolVoiceNpc;
  u8 mVolVoicePawn;
  u8 mVolVoicePl;
  u8 mVolVoicePt;
  u8 mVolVoiceEm;
  u8 mVolVoiceSCC;
  u8 mVolBGMBattle;
  u8 mVolBGMOther;
  u8 mVolSEEnv;
  u8 mVolSEEm;
  u8 mVolSEPl;
  u8 mVolSEPt;
  u8 mVolSEOther;
  bool mPadVibration;
  u8 mActPltType;
  bool mIsDirectChat;
  bool mIsCamVRevPad;
  bool mIsCamHRevPad;
  bool mIsCamVRevKeyboard;
  bool mIsCamHRevKeyboard;
  u8 mCamSpdPad;
  u8 mCamSpdMouse;
  u8 mMouseCursorSpd;
  u8 mOthersEffTrans;
  u8 mFrameRate;
  u8 mTexResolution;
  u8 mAntiAliasing;
  u8 mLightHardwareMode;
  u8 mShadowQuality;
  u8 mShadowResolution;
  u8 mShadowDistance;
  u8 mShadow00;
  u8 mShadow01;
  u8 mShadow02;
  u8 mShadowVtxSmoother;
  u8 mShadowLantern;
  u8 mGrassVolume;
  u8 mGrassQuality;
  u8 mGrassDistance;
  u8 mOmDistance;
  u8 mOmLOD;
  u8 mChrDispNum;
  u8 mChrDispDistance;
  u8 mEftBGQuality;
  u8 mEftBattleTarget;
  u8 mEftResponse;
  bool mUILarge;
  u8 mKeyJobLinksSize;
  u8 mKeyJobLinks[10];
};

struct cStorageData_stTutorialGuide
{
  u32 mFinishTutorial[16];
  u32 mLatestTutorial[5];
};

struct cStorageData_stAreaMasterTalk
{
  u32 mIsFirstTalkEnd[1];
};

struct cStorageData : cStorageDataBase
{
  u8 mDataU8;
  u16 mDataU16;
  u32 mDataU32;
  cStorageData_stOptionDataSystem mOptionSys;
  cStorageData_stTitle mTitle;
  cStorageData_stTutorialGuide mTutorialGuide;
  cStorageData_stAreaMasterTalk mAreaMasterTalk;
};

struct cStorageDataBase_UserHeader
{
  char playerName[64];
  char comment[128];
  t64 createTime;
  u8 bodyType;
};


struct cStorageDataEdit : cStorageDataBase
{
  cStorageDataBase_UserHeader mUserHeader;
  char mPlayerName[64];
  char mComment[64];
  char mSexStr[32];
  u8 mBodyType;
  s32 mHair;
  s32 mBeard;
  s32 mMakeup;
  s32 mScar;
  f32 mWrinkleValue;
  s32 mEyePresetNo;
  s32 mEyebrowTexNo;
  s32 mNosePresetNo;
  s32 mMouthPresetNo;
  f32 mSokutoubuValue;
  f32 mHitaiValue;
  f32 mMimijyougeValue;
  f32 mMabisasijyougeValue;
  f32 mHitomiookisaValue;
  f32 mMeookisaValue;
  f32 mMekaitenValue;
  f32 mKannkakuValue;
  f32 mEyebrowUVOffsetYValue;
  f32 mEyebrowUVOffsetXValue;
  f32 mMayukaitenValue;
  f32 mMikentakasaValue;
  f32 mMikenhabaValue;
  f32 mHanajyougeValue;
  f32 mHanahabaValue;
  f32 mHanatakasaValue;
  f32 mHanakakudoValue;
  f32 mHohobonejyougeValue;
  f32 mHohoboneryouValue;
  f32 mMimiookisaValue;
  f32 mMimimukiValue;
  f32 mElfmimi;
  f32 mHanakuchijyougeValue;
  f32 mAgozengoValue;
  f32 mKuchihabaValue;
  f32 mKuchiatsusaValue;
  f32 mHohonikuValue;
  f32 mAgosakijyougeValue;
  f32 mAgosakihabaValue;
  f32 mErahonejyougeValue;
  f32 mErahonehabaValue;
  f32 mHeightValue;
  f32 mHeadSizeValue;
  f32 mNeckOffsetValue;
  f32 mNeckScaleValue;
  f32 mUpperBodyScaleXValue;
  f32 mBellySizeValue;
  f32 mTeatScaleValue;
  f32 mTekubiSizeValue;
  f32 mKoshiOffsetValue;
  f32 mKoshiSizeValue;
  f32 mAnkleOffsetValue;
  f32 mFatValue;
  f32 mMuscleValue;
  f32 mMotionFilterValue;
  s32 mColorSkin;
  s32 mColorHair;
  s32 mColorBeard;
  s32 mColorEyebrow;
  s32 mColorREye;
  s32 mColorLEye;
  s32 mColorMakeup;
};

struct sSavedataExt //: sSavedata
{
  //void *mpSaveBuff;  
  
  u32 mSaveVersion;
  
  //void *mpSaveUserHeaderBuff;  
  u32 mLoadVersion;
  u32 mCurrentVersion;
  cStorageData mStorageData;
  cStorageDataEdit mStorageDataEdit;


  u32 mLauncherSaveVersion;
  u32 mLauncherLoadVersion;
  u32 mLauncherCurrentVersion;
  //void *mpLauncherSaveBuff;
  bool mIsCheckTrophySize;
  u32 mNeedHddSizeKB;
};

struct binaryData{
  DTIId id;
};

struct BinaryString{
  u8 pointerOffset;
  char string[];
};

struct BinaryValue{
  u8 bufferSize;
  s8 offset;
  s16 count1;
  s8 count3;
  u32 data[(bufferSize-4)/4];
};

struct KeyConfigWrapper{
  DTIId id;
  u32 unknown1;
  u32 bufferSizeTotalMaybe;
  u8 unknown2;
  u32 bufferSizeWrapperData;
  u32 arraySize;
  
  BinaryString string1;
  u8 arraySize1;
  BinaryValue values1[arraySize1];
  
    
  BinaryString string2;
  u8 arraySize2;
  BinaryValue values2[arraySize2];
  
  BinaryString string3;
  u8 arraySize3;
  BinaryValue values3[arraySize3];
};

u32 unkownOffset1 @ 0x20;
sSavedata_KEYTABLE unknownValue1 @ unkownOffset1;


u32 saveVersionOffset @ 0x48; // DATA_VERSION
sSavedata_KEYTABLE saveVersion @ saveVersionOffset;

u32 saveUserHeaderBuffOffset @ 0x4C; // _UserHeader_
sSavedata_KEYTABLE saveUserHeader @ saveUserHeaderBuffOffset;

u32 saveBuffOffset @0x44;  //DATA_BODY
sSavedata_KEYTABLE saveBuff @ saveBuffOffset;

cStorageData cstoragedata_at_0x6B @ 0x64;

KeyConfigWrapper wrapper @ 0x102;