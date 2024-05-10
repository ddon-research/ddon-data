struct MtVector3
{
  float x;
  float y;
  float z;
};
struct MtVector4
{
  float x;
  float y;
  float z;
  float w;
};

struct MtFloat3
{
  float x;
  float y;
  float z;
};

struct MtMatrix
{
  MtVector4 m[4];
};

struct MtOBB
{
  MtMatrix coord;
  MtVector3 extent;
};

struct MtString
{
  char string[];
};

struct cSetInfoCoord544
{
  MtString mName;
  s32 mUnitID;
  MtFloat3 mPosition;
  MtFloat3 mAngle;
  MtFloat3 mScale;
  s32 mAreaHitNo;
};

struct cSetInfoCharacter544 : cSetInfoCoord544
{
};

struct cSetInfoGeneralPoint : cSetInfoCoord544
{
  float mRadius;
  s32 mObjectID;
  s32 mGroup;
};

struct cSetInfoNpc
{
  s32 mNpcId;
  MtString mFilePath;
  bool mIsCommunicate;
  u8 mClothType;
  s8 mDefNPCMotCategory;
  s8 mDefNPCMotNo;
  u16 mThinkIndex;
  u16 mJobLv;
  u8 mLantern;
  bool mDisableScrAdj;
  bool mDisableLedgerFinger;
  bool mIsForceListTalk;
  bool mIsAttand;
  bool mDisableTouchAction;
  bool mDispElseQuestTalk;
  s16 unknown1;
  s16 unknown2;
  s16 unknown3;
  s16 unknown4;
  s16 unknown5;
  s16 unknown6;
  cSetInfoCharacter544 prnt;
};

struct rLayoutSetInfo
{
  s32 mID;
  u32 type;
};

struct cSetInfoEnemy
{
  rLayoutSetInfo info;
  s32 mPresetKind;
  s32 mGroup;
  u32 mEmReactNo;
  s32 mSubGroupNo;
  bool mReturnPoint2nd;
  u32 unknown;
  cSetInfoCharacter544 prnt;
};

struct cSetInfoEnemyV2
{
  rLayoutSetInfo info;
  s32 unknown1;
  s32 mPresetKind;
  s32 mGroup;
  u32 mEmReactNo;
  s32 mSubGroupNo;
  bool mReturnPoint2nd;
  u32 unknown;
  cSetInfoCharacter544 prnt;
};

struct cSetInfoOmOld
{
  bool mDisableEffect;
  bool mDisableOnlyEffect;
  bool mOpenFlag;
  bool mEnableSyncLight;
  bool mEnableZone;
  u32 mInitMtnNo;
  u32 mAreaMasterNo;
  u16 mAreaReleaseNo;
  bool mAreaReleaseON;
  bool mAreaReleaseOFF;
  u32 mWarpPointId;
  u32 mKeyNo;
  bool mIsBreakLink;
  bool mIsBreakQuest;
  u16 mBreakKind;
  u16 mBreakGroup;
  u16 mBreakID;
  u32 mQuestFlag;
  bool mIsNoSbc;
  bool mIsMyQuest;
  cSetInfoCoord544 prnt;
};

struct cSetInfoOmWall
{
  u32 WallType;
  MtOBB NavOBB;
  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown49
{
  u32 unknown1;
  u32 unknown2;
  u32 unknown3;
  u32 unknown4;
  u32 unknown5;
  bool unknown6;
  MtFloat3 unknown7;
  float unknown8;
  bool unknown9;
  s32 unknown10[3];
  u32 unknown11;
  u8 unknown12;
};

struct cSetInfoOmUnknown30
{
  u32 unknownStageNo;
  u32 unknown1;
  u32 QuestId;
  u32 unknown2;

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown46
{
  u32 unknownStageNo;
  u32 QuestId;
  u32 unknown1;
  u32 unknown2;

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown28
{
  u16 unknown1;
  u16 unknown2;

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown31
{
  float unknown[4];

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown33
{
  u32 unknown1;
  u32 unknown2;
  u32 unknown3;
  u32 unknown4;

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown34
{
  u32 unknown1;
  u32 unknown2;

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown45
{
  u32 unknown[2];
  s32 unknown2;
  bool unknown3;
  float unknown4[4];

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown47
{
  u32 unknown1;
  bool unknown2;
  s32 unknown3;
  bool unknown4;
  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown48
{
  u32 unknown;
  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown51
{
  u32 unknown[3];
  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown52
{
  float unknown[8];
  u32 unknown2[2];
  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmUnknown55
{
  u32 unknown[9];
  bool unknown5;
  float unknown6;
  bool unknown7;
  u32 unknown8;
  s32 unknown9;
  bool unknown10;
  u32 unknown11;
  u32 unknown12;
  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmOldData
{
  rLayoutSetInfo info;
  cSetInfoOmOld setInfoOmOld;
};

struct cSetInfoOmNew
{
  bool mDisableEffect;
  bool mDisableOnlyEffect;
  bool mOpenFlag;
  bool mEnableSyncLight;
  bool unknown1;
  bool mEnableZone;
  u32 mInitMtnNo;
  u32 mAreaMasterNo;
  u16 mAreaReleaseNo;
  bool mAreaReleaseON;
  bool mAreaReleaseOFF;
  u32 mWarpPointId;
  u32 mKeyNo;
  bool mIsBreakLink;
  bool mIsBreakQuest;
  u16 mBreakKind;
  u16 mBreakGroup;
  u16 mBreakID;
  u32 mQuestFlag;
  bool mIsNoSbc;
  bool mIsMyQuest;
  cSetInfoCoord544 prnt;
};

struct cSetInfoOmCtrlcLinkParam
{
  u16 mKind;
  u16 mGroup;
  u16 mID;
  u32 mTransition;
  u32 mState;
  s32 mCamEvNo;
  u64 cResPathrAIFSMmrFSMCam;
};

struct cSetInfoOmCtrl
{
  u32 mKeyItemNo;
  cSetInfoOmCtrlcLinkParam mLinkParam[4];
  bool mIsQuest;
  u32 mQuestId;
  s32 mAddGroupNo;
  s32 mAddSubGroupNo;
  u32 unknown1;

  cSetInfoOmOld InfoOm;
};

struct cSetInfoOmBlock
{
  u32 QuestID;
  cSetInfoOmOld prnt;
};

struct cSetInfoOmEx
{
  u32 QuestID;
  cSetInfoOmOld prnt;
};

struct cSetInfoOmDoor
{
  bool mbPRT;
  float mPRTPos[3];
  float mPRTScale;
  u32 mTextType;
  u32 mTextQuestNo;
  u32 mTextNo;
  u32 mQuestID;
  u32 mQuestFlag;
  cSetInfoOmOld InfoOm;
};
struct cSetInfoOmWarp
{
  rLayoutSetInfo setInfoHeader;
  u32 numStageNo;
  u32 mStageNo[numStageNo];
  u32 numStartPosNo;
  u32 mStartPosNo[numStartPosNo];
  u32 numQuestNo;
  u32 mQuestNo[numQuestNo];
  u32 numFlagNo;
  u32 mFlagNo[numFlagNo];
  u32 numSpotId;
  u32 mSpotId[numSpotId];
  u32 mTextType;
  u32 mTextQuestNo;
  u32 mTextNo;
  cSetInfoOmNew InfoOm;
};
struct cSetInfoOmOldDoor
{
  bool mIsQuest;
  u32 mQuestId;
  u16 mKind1;
  u16 mGroup1;
  u16 mID1;

  u16 mKind2;
  u16 mGroup2;
  u16 mID2;

  u16 mKind3;
  u16 mGroup3;
  u16 mID3;
  cSetInfoOmOld InfoOm;
};
struct cSetInfoUnknown32
{
  bool mIsQuest;
  u32 mQuestId;
  u16 mKind1;
  u16 mGroup1;
  u16 mID1;

  u16 mKind2;
  u16 mGroup2;
  u16 mID2;

  u16 mKind3;
  u16 mGroup3;
  u16 mID3;

  float Unknown1;
  float Unknown2;
  u32 Unknown3;
  cSetInfoOmOld InfoOm;
};
struct cSetInfoOmWarpNew
{
  u32 unknown;
  u32 numStageNo;
  u32 mStageNo[numStageNo];
  u32 numStartPosNo;
  u32 mStartPosNo[numStartPosNo];
  u32 numQuestNo;
  u32 mQuestNo[numQuestNo];
  u32 numFlagNo;
  u32 mFlagNo[numFlagNo];
  u32 numSpotId;
  u32 mSpotId[numSpotId];
  u32 mTextType;
  u32 mTextQuestNo;
  u32 mTextNo;
  cSetInfoOmNew InfoOm;
};

struct cSetInfoOmWarpNewV3
{
  bool unknown1;
  u16 unknown3;
  u16 unknown4;
  s32 unknown2;
  u32 numStageNo;
  u32 mStageNo[numStageNo];
  u32 numStartPosNo;
  u32 mStartPosNo[numStartPosNo];
  u32 numQuestNo;
  u32 mQuestNo[numQuestNo];
  u32 numFlagNo;
  u32 mFlagNo[numFlagNo];
  u32 numSpotId;
  u32 mSpotId[numSpotId];
  u32 mTextType;
  u32 mTextQuestNo;
  u32 mTextNo;
  cSetInfoOmNew InfoOm;
};

struct SetInfoNum
{
  u32 numSetInfoEnemy;        // e
  u32 numSetInfoNpc;          // n
  u32 numSetInfoGeneralPoint; // t
  u32 numSetInfoOm;           // s
  u32 numSetInfoOmBoard;
  u32 numSetInfoOmBowlOfLife;
  u32 numSetInfoOmCtrl;
  u32 numSetInfoOmDoor;
  u32 numSetInfoOmElfSW;
  u32 numSetInfoOmFall;
  u32 numSetInfoOmGather;
  u32 numSetInfoOmTreasureBox;
  u32 numSetInfoOmHakuryuu;
  u32 numSetInfoOmHeal;
  u32 numSetInfoOmLadder;
  u32 numSetInfoOmLever;
  u32 numSetInfoOmNav;
  u32 numSetInfoOmRange;
  u32 numSetInfoOmText;
  u32 numSetInfoOmWall;
  u32 numSetInfoOmWarp;
  u32 numSetInfoOmBadStatus;
};

struct rLayout
{
  SetInfoNum mSetInfoNeedNums;

  u32 arrayNum;

  rLayoutSetInfo h1;
};

struct rLayoutHeader
{
  u32 magicNumber;
  u32 version;
  rLayout layout;
};

rLayoutHeader rlayoutheader_at_0x00 @0x00;

cSetInfoOmOld csetinfoomold_at_0x75 @0x75;