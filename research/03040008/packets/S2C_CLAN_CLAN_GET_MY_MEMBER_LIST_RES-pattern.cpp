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
    u8 Job;
    u8 Lv;
};

struct CDataCharacterName
{
    MtString FirstName;
    MtString LastName;
};

struct CDataCommunityCharacterBaseInfo
{
    u32 CharacterID;
    CCharacterName CharacterName;
    MtString ClanName;
};

struct CDataCharacterListElement
{
    CCommunityCharacterBaseInfo BaseInfo;
    u16 ServerID;
    u8 OnlineStatus;
    CJobBaseInfo CurrentJobInfo;
    CJobBaseInfo EntryJobInfo;
    MtString MatchingPlofile;
    u8 unknown;
};

struct CDataClanMemberInfo
{
    u32 Rank;
    s64 Created;
    s64 LastLoginTime;
    s64 LeaveTime;
    u32 Permission;
    CCharacterListElement CharacterListElement;
};

struct MtTypedArray<CDataClanMemberInfo>
{
    u32 num;
    CDataClanMemberInfo array[num];
};

struct CPacket_S2C_CLAN_GET_MY_MEMBER_LIST_RES : CPacket
{
    u32 Error;
    s32 Result;
    MtTypedArray<CDataClanMemberInfo> MemberList;
};

CPacket_S2C_CLAN_GET_MY_MEMBER_LIST_RES S2C_CLAN_GET_MY_MEMBER_LIST_RES @0x00;