struct MtObject
{
};

struct cResource
{
    u32 version;
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};

struct cEvidence : MtObject
{
    u16 mUnknown;
    u32 mIdx;
    u32 mQuestId;
    u32 mFlag;
};

struct rEvidenceList : cResource
{
    MtTypedArray<cEvidence> Array;
};

rEvidenceList revidencelist_at_0x00 @ 0x00;