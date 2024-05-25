#define f32 float

struct MtVector3
{
	f32 x;
	f32 y;
	f32 z;
	f32 pad;
};

struct MtFloat3
{
	f32 x;
	f32 y;
	f32 z;
	f32 pad;
};

struct MtVector4
{
	f32 x;
	f32 y;
	f32 z;
	f32 w;
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
	char value[];
};

struct MtArray
{
	bool mAutoDelete;
	u32 mLength;
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

struct ClassHeader
{
	u32 numClasses;
	u32 bufferSizeForHeader;
	u32 classOffsets[numClasses];
	// <- this is now the new base offset
	OBJECTDATA classHeaders[numClasses];
};

// doesn't work for shared fields when inheritance plays a role
fn getClassPropTotal(ClassHeader classHeader)
{
	u32 total = 0;
	for (u8 i = 0, i < classHeader.numClasses, i += 1)
	{
		total += classHeader.classHeaders[i].param32.prop_num;
	}
	return total;
};

struct Header
{
	ClassHeader classHeader;
	MtString fieldNames[62]; // adjust as needed
	padding[2];				 // adjust as needed
};

struct cSetInfoCoord544
{
	u32;
	MtString mName;

	u32;
	s32 mUnitID;

	u32;
	MtFloat3 mPosition;

	u32;
	MtFloat3 mAngle;

	u32;
	MtFloat3 mScale;

	u32;
	s32 mAreaHitNo;

	u32;
	u32 mVersion;
};

struct cFSMRelate
{
	u32;
	MtString mFSMName;
	u32;
	u8 mFSMType;
};

struct cSetInfoNpc : cSetInfoCoord544
{

	u32;
	s32 mNpcId;
	cFSMRelate mFsmResource;
	u32;
	bool mIsCommunicate;
	u32;
	u8 mClothType;
	u32;
	s8 mDefNPCMotCategory;
	u32;
	s8 mDefNPCMotNo;
	u32;
	u16 mThinkIndex;
	u32;
	u16 mJobLv;
	u32;
	u8 mLantern;
	u32;
	bool mDisableScrAdj;
	u32;
	bool mDisableLedgerFinger;
	u32;
	bool mIsForceListTalk;
	u32;
	bool mIsAttand;
	u32;
	bool mDisableTouchAction;
	u32;
	bool mDispElseQuestTalk;
};

struct cSetInfoOm : cSetInfoCoord544
{
	u32;
	bool mDisableEffect;
	u32;
	bool mDisableOnlyEffect;
	u32;
	bool mOpenFlag;
	u32;
	bool mEnableSyncLight;
	u32;
	bool mEnableZone;
	u32;
	u32 mInitMtnNo;
	u32;
	u32 mAreaMasterNo;
	u32;
	u16 mAreaReleaseNo;
	u32;
	bool mAreaReleaseON;
	u32;
	bool mAreaReleaseOFF;
	u32;
	u32 mWarpPointId;
	u32;
	u32 mKeyNo;
	u32;
	bool mIsBreakLink;
	u32;
	bool mIsBreakQuest;
	u32;
	u16 mBreakKind;
	u32;
	u16 mBreakGroup;
	u32;
	u16 mBreakID;
	u32;
	u32 mQuestFlag;
	u32;
	bool mIsNoSbc;
	u32;
	bool mIsMyQuest;
};

struct cSetInfoOmWall : cSetInfoOm
{
	u32;
	u32 WallType;
	u32;
	MtOBB NavOBB;
};

struct cSetInfoOmWarp : cSetInfoOm
{
	u32 mStageNoNum;
	u32 mStageNo[3];
	u32 mStartPosNoNum;
	u32 mStartPosNo[3];
	u32 mQuestNoNum;
	u32 mQuestNo[3];
	u32 mFlagNoNum;
	u32 mFlagNo[3];
	u32 mSpotIdNum;
	u32 mSpotId[3];
	u32;
	u32 mTextType;
	u32;
	u32 mTextQuestNo;
	u32;
	u32 mTextNo;
};

struct cSetInfoOmBowlOfLife : cSetInfoOm
{
	u32 mStageNoNum;
	u32 mStageNo[3];
	u32 mStartPosNoNum;
	u32 mStartPosNo[3];
	u32 mQuestNoNum;
	u32 mQuestNo[3];
	u32 mFlagNoNum;
	u32 mFlagNo[3];
	u32 mSpotIdNum;
	u32 mSpotId[3];
	u32;
	u32 mTextType;
	u32;
	u32 mTextQuestNo;
	u32;
	u32 mTextNo;
};

struct cSetInfoOmDoor : cSetInfoOm
{
	u32;
	bool mbPRT;
	u32;
	MtVector3 mPRTPos;
	u32;
	f32 mPRTScale;
	u32;
	u32 mTextType;
	u32;
	u32 mTextQuestNo;
	u32;
	u32 mTextNo;
	u32;
	u32 mQuestID;
	u32;
	u32 mQuestFlag;
};

struct cSetInfoOmText : cSetInfoOm
{
	u32;
	u32 mTextNo;
	u32;
	u32 mTextQuestNo;
	u32;
	u32 mTextType;
};

struct cSetInfoOmLever : cSetInfoOm
{
	u32;
	bool mbReqLever;
	u32;
	s32 mCamEvNo;
	u32;
	// cResPath<rAIFSM> mFSMCamEv;
	MtString FSM;
};

struct cSetInfoOmCtrl_cLinkParam
{
	u16 classIndex1; // cQuestSet == 9
	u16 objIndex1;
	u32 bufferSize1;

	u32;
	u16 mKind;
	u32;
	u16 mGroup;
	u32;
	u16 mID;
	u32;
	u32 mTransition;
	u32;
	u32 mState;
	u32;
	s32 mCamEvNo;
	u32;
	// cResPath<rAIFSM> mrFSMCam;
	MtString FSM;
};

struct cSetInfoOmCtrl : cSetInfoOm
{
	u32;
	u32 mKeyItemNo;
	u32;
	bool mIsQuest;
	u32;
	u32 mQuestId;
	u32 mLinkParamNum;
	cSetInfoOmCtrl_cLinkParam mLinkParam[mLinkParamNum];
	u32;
	s32 mAddGroupNo;
	u32;
	s32 mAddSubGroupNo;
};

struct cQuestSet
{
	u16 classIndex1; // cQuestSet == 9
	u16 objIndex1;
	u32 bufferSize1;

	u32;
	u32 mOmID;
	u32;
	u32 mUnitNo;
	u32;
	MtString mComment;
	u32;
	u32 mKind;

	u32;
	// q9/st0100 => cSetInfoOmWall == 11, cSetInfoOm == 13, cSetInfoOmWarp == 15
	// q5/st0576 => cSetInfoOm == 11, cSetInfoNpc == 13
	// q70000001/st0408 =>
	//  cSetInfoOmDoor 11, cSetInfoOm 13, cSetInfoOmText 15,
	//  cSetInfoOmCtrl 17, cSetInfoOmCtrl::cLinkParam 19, cSetInfoOmLever 21
	u16 classIndex2;
	u16 objIndex2;
	u32 bufferSize2;
	if (mKind == 3)
		if (classIndex2 == 11)
			cSetInfoOmDoor cSetInfoOmDoor;
		else if (classIndex2 == 13)
			cSetInfoOm cSetInfoOm;
		else if (classIndex2 == 15)
			cSetInfoOmText cSetInfoOmText;
		else if (classIndex2 == 17)
			cSetInfoOmCtrl cSetInfoOmCtrl;
		else if (classIndex2 == 21)
			cSetInfoOmLever cSetInfoOmLever;
		else
			cSetInfoOm UNDEFINED;
	if (mKind == 5)
		cSetInfoNpc cSetInfoNpc;
};

struct cQuestGroup
{
	u16 classIndex1; // cQuestGroup == 7
	u16 objIndex1;
	u32 bufferSize1;

	u32;
	u32 mGroupNo;

	u32;
	char mComment[];

	u32;
	s32 mCondition;

	u32;
	s32 mEraseCondition;

	u32;
	u16 classIndex2; // MtArray == 3
	u16 objIndex2;
	u32 bufferSize2;

	u32;
	MtArray mQusetSetArr;
	cQuestSet mQusetSet[mQusetSetArr.mLength];
};

struct cQuestStage
{
	u16 classIndex1; // cQuestStage == 5
	u16 objIndex1;
	u32 bufferSize1;

	u32;
	s32 mStageNo;

	u32;
	u16 classIndex2; // MtArray == 3
	u16 objIndex2;
	u32 bufferSize2;

	u32;
	MtArray mQuestGrpArr;
	cQuestGroup mQuestGrp[6];
};

struct cResource
{
	u16 classIndex2; // cResource == 1
	u16 objIndex2;
	u32 bufferSize;

	u32;
	u32 mQuality;
};

struct rQuestList : cResource
{
	u32;
	u16 classIndex; // MtArray == 3
	u16 objIndex;
	u32 bufferSize;

	u32;
	MtArray QuestStageListArr;
	cQuestStage QuestStageList[QuestStageListArr.mLength];
};

struct File
{
	u32 magicNumber;
	u16 serializerVersion;
	u16 classVersion;
	u32 objectDataNum;

	u16 classIndex1;
	u16 objIndex1;
	Header header;

	rQuestList resource;
};

File file_at_0x00 @0x00;