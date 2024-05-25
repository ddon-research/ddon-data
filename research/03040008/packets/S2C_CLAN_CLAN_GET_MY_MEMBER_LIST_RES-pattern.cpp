#pragma endian big

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

struct MtTypedArray<CDataClanMemberInfo>
{
    u32 num;
    CDataClanMemberInfo array[num];
};

struct CPacket_S2C_CLAN_GET_MY_MEMBER_LIST_RES : CPacket
{
    u32 m_usError;
    s32 m_nResult;
    MtTypedArray<CDataClanMemberInfo> m_MemberList;
    u8 pad[14];
};

CPacket_S2C_CLAN_GET_MY_MEMBER_LIST_RES cpacket_s2c_clan_get_my_member_list_res_at_0x00 @0x00;