struct MtObject
{
};

struct cResource
{
    char magicString[4];
    u16 magicVersion;
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};

struct rMsgSet_cMsgData : MtObject
{
    u8 mBuffer;

    u32 mMsgSerial;
    u32 mGmdIndex;
    u32 mMsgType;
    u32 mJumpGroupSerial;
    u32 mDispType;
    u32 mDispTime;
    u32 mSetMotion;
    s32 mVoiceReqNo;
    u8 mTalkFaceType;
};

struct rMsgSet_cMsgGroup : MtObject
{
    u8 mBuffer;

    u32 mGroupSerial;
    u32 mNpcId;
    u32 mGroupNameSerial;
    u32 mGroupType;
    bool mNameDispOff;

    MtTypedArray<rMsgSet_cMsgData> mMsgData;
};

struct rMsgSet : cResource
{
    u32 mNativeMsgGroupArrayNum;

    u32 mNativeMsgDataArrayNum;

    rMsgSet_cMsgGroup mpNativeMsgGroupArray[mNativeMsgGroupArrayNum];
};

rMsgSet rmsgset_at_0x00 @0x00;