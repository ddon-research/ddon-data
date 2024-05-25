#pragma endian big
#define b8 bool
#define CDataClanParam CClanParam
#define CDataClanUserParam CClanUserParam
#define CDataClanServerParam CClanServerParam
#define CDataClanMemberInfo CClanMemberInfo
#define CDataCharacterListElement CCharacterListElement
#define CDataJobBaseInfo CJobBaseInfo
#define CDataCommunityCharacterBaseInfo CCommunityCharacterBaseInfo
#define CDataCharacterName CCharacterName

struct MtString
{
    u16 strLen;
    char string[strLen];
};

struct CPacket
{
    u8 group;
    u16 id;
    u8 subId;
    u8 source;
    u32 packetcounter;
};

struct CDataJobBaseInfo
{
    u8 m_ucJob;
    u8 m_ucLv;
};

struct CDataCharacterName
{
    MtString m_wstrFirstName;
    MtString m_wstrLastName;
};

struct CDataCommunityCharacterBaseInfo
{
    u32 m_unCharacterID;
    CCharacterName m_CharacterName;
    MtString m_wstrClanName;
};

struct CDataCharacterListElement
{
    CCommunityCharacterBaseInfo m_BaseInfo;
    u16 m_usServerID;
    u8 m_ucOnlineStatus;
    CJobBaseInfo m_CurrentJobInfo;
    CJobBaseInfo m_EntryJobInfo;
    MtString m_wstrMatchingPlofile;
    u8 unknown;
};

struct CDataClanMemberInfo
{
    u32 m_unRank;
    s64 m_llCreated;
    s64 m_llLastLoginTime;
    s64 m_llLeaveTime;
    u32 m_unPermission;
    CCharacterListElement m_CharacterListElement;
};

struct CDataClanServerParam
{
    u32 m_unID;
    u16 m_usLv;
    u16 m_usMemberNum;
    CClanMemberInfo m_MasterInfo;
    b8 m_bIsSystemRestriction;
    b8 m_bIsClanBaseRelease;
    b8 m_bCanClanBaseRelease;
    u32 m_unTotalClanPoint;
    u32 m_unMoneyClanPoint;
    u32 m_unNextClanPoint;
};

struct CDataClanUserParam
{
    MtString m_wstrName;
    MtString m_wstrShortName;
    u8 m_ucEmblemMarkType;
    u8 m_ucEmblemBaseType;
    u8 m_ucEmblemBaseMainColor;
    u8 m_ucEmblemBaseSubColor;
    u32 m_unMotto;
    u32 m_unActiveDays;
    u32 m_unActiveTime;
    u32 m_unCharacteristic;
    b8 m_bIsPublish;
    MtString m_wstrComment;
    MtString m_wstrBoardMessage;
    s64 m_llCreated;
};

struct CDataClanParam
{
    CClanUserParam m_ClanUserParam;
    CClanServerParam m_ClanServerParam;
};

struct CPacket_S2C_CLAN_GET_MY_INFO_RES : CPacket
{
    u32 m_usError;
    s32 m_nResult;
    CClanParam m_CreateParam;
    s64 m_llLeaveTime;
    u8 pad[11];
};
CPacket_S2C_CLAN_GET_MY_INFO_RES cpacket_s2c_clan_get_my_info_res_at_0x00 @0x00;