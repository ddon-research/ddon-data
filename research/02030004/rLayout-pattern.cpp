struct MtFloat3
{
  float x;
  float y;
  float z;
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
  cSetInfoCharacter544 prnt;
};

struct cSetInfoEnemy
{
  s32 mPresetKind;
  s32 mGroup;
  u32 mEmReactNo;
  s32 mSubGroupNo;
  bool mReturnPoint2nd;
  cSetInfoCharacter544 prnt;
};

struct rLayoutSetInfo
{
  s32 mID;
  u32 type;
};

struct cSetInfoOm
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
  cSetInfoOm InfoOm;
};

struct cSetInfoOmBlock
{
  u32 QuestID;
  cSetInfoOm prnt;
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
  cSetInfoOm InfoOm;
};
struct cSetInfoOmWarp
{
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
  cSetInfoOm InfoOm;
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
  cSetInfoOmCtrl ctrl;
};

struct rLayoutHeader
{
  u32 magicNumber;
  u32 version;
  rLayout layout;
};

rLayoutHeader rlayoutheader_at_0x00 @0x00;