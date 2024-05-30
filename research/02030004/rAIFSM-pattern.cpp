#define f32 float

struct MtVector3
{
	f32 x;
	f32 y;
	f32 z;
	f32 pad;
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
	MtString fieldNames[57]; // adjust as needed
	padding[2];				 // adjust as needed
};

struct cResource
{
	u16 classIndex; // cResource == 1
	u16 objIndex;
	u32 bufferSize;

	u32;
	u32 mQuality;
};

bitfield cAIFSMNode_UIPos_bits
{
mUIPosX:
	16;
mUIPosY:
	16;
};

union cAIFSMNode_UIPos
{
	u32 mUIPos;
	cAIFSMNode_UIPos_bits mUIPosXY;
};

struct cAIFSMLink
{
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;

	u32;
	MtString mName;
	u32;
	u32 mDestinationNodeId;
	u32;
	bool mExistCondition;
	u32;
	u32 mConditionId;
};

struct cAIUserProcessReference
{
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;

	u32;
	MtString mContainerName;
	u32;
	MtString mCategoryName;
};

struct cAICopiableParameter
{
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;
};

struct cFSMOrderParamIsMyQuestFlag : cAICopiableParameter
{
	u32;
	u32 mQuestId;
	u32;
	u32 mFlagNo;
	u32;
	u32 mArrayIdx;
};

struct cFSMUnit_cParamSetDisableTouchAction : cAICopiableParameter
{
	u32;
	bool mIsDisableTouch;
};

struct cFSMUnit_cParamSetChangeThink : cAICopiableParameter
{
	u32;
	u32 mThink;
	u32;
	bool mIsInvincible;
};

struct cFSMUnit_cParamSetGoto : cAICopiableParameter
{
	u32;
	MtVector3 mTargetPos;
	u32;
	u8 mRunType;
	u32;
	f32 mStopBorder;
	u32;
	bool mIsSetDir;
	u32;
	bool mIsPathFinding;
	u32;
	MtVector3 mDir;
	u32;
	f32 mSpeed;
};

struct cAIFSMNodeProcess : cAIUserProcessReference
{
	u32;

	if (mContainerName.value == "checkMyQuestFlag\0")
		cFSMOrderParamIsMyQuestFlag mpParameter;

	if (mContainerName.value == "SetDisableTouchAction\0")
		cFSMUnit_cParamSetDisableTouchAction mpParameter;

	if (mContainerName.value == "SetChangeThink\0")
		cFSMUnit_cParamSetChangeThink mpParameter;

	if (mContainerName.value == "SetGoto\0")
		cFSMUnit_cParamSetGoto mpParameter;
};

struct cAIFSMNode
{
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;

	u32;
	MtString mName;
	u32;
	u32 mId;
	u32;
	u32 mUniqueId;
	u32;
	u32 mOwnerId;
	u32;
	u32 mpSubCluster;
	u32 mLinkNum;
	cAIFSMLink mpLinkList[mLinkNum];
	u32 mProcessNum;
	cAIFSMNodeProcess mpProcessList[mProcessNum];
	u32;
	cAIFSMNode_UIPos mUIPos;
	u32;
	u8 mColorType;
	u32;
	u32 mSetting;
	u32;
	u32 mUserAttribute;
	u32;
	bool mExistConditionTrainsitionFromAll;
	u32;
	u32 mConditionTrainsitionFromAllId;
};

struct cAIFSMCluster
{
		u16 classIndex;
	u16 objIndex;
	u32 bufferSize;

	u32;
	u32 mId;
	u32;
	u32 mOwnerNodeUniqueId;
	u32;
	u32 mInitialStateId;
	u32 mNodeNum;
	cAIFSMNode mpNodeList[mNodeNum];
};

struct cAIDEnum
{
	// MtString mElementName;
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;
	u32;
	u32 mId;
};

struct rAIConditionTree_OperationNode
{
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;
	u32;

	// mpChildList

	u32 mOperator;
};

struct rAIConditionTreeNode
{
	u16 classIndex2;
	u16 objIndex2;
	u32 bufferSize2;

	u32 mChildNum;

	if (classIndex2 == 25)
		rAIConditionTree_OperationNode;
};

struct rAIConditionTree_TreeInfo
{
	u16 classIndex;
	u16 objIndex;
	u32 bufferSize;

	u32;
	cAIDEnum mName;
	u32;
	rAIConditionTreeNode mpRootNode;
};

struct rAIConditionTree : cResource
{
	u32 mTreeNum;
	rAIConditionTree_TreeInfo mpTreeList[1];
};

struct rAIFSM : cResource
{
	u32;
	MtString ownerObjectName;

	u32;
	cAIFSMCluster mpRootCluster;
	u32;
	rAIConditionTree mpConditionTree;
	// u32 mFSMAttribute;
	// u32 mLastEditType;
};

struct File
{
	u32 magicNumber;
	u16 serializerVersion;
	u16 classVersion;
	u32 objectDataNum;

	u16 classIndex;
	u16 objIndex;
	Header header;

	rAIFSM resource;
};

File file_at_0x00 @0x00;