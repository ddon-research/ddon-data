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

struct CDataClanServerParam
{
    u32 ID;
    u16 Lv;
    u16 MemberNum;
    CClanMemberInfo MasterInfo;
    b8 IsSystemRestriction;
    b8 IsClanBaseRelease;
    b8 CanClanBaseRelease;
    u32 TotalClanPoint;
    u32 MoneyClanPoint;
    u32 NextClanPoint;
};

struct CDataClanUserParam
{
    MtString Name;
    MtString ShortName;
    u8 EmblemMarkType;
    u8 EmblemBaseType;
    u8 EmblemBaseMainColor;
    u8 EmblemBaseSubColor;
    u32 Motto;
    u32 ActiveDays;
    u32 ActiveTime;
    u32 Characteristic;
    b8 IsPublish;
    MtString Comment;
    MtString BoardMessage;
    s64 Created;
};

struct CDataClanParam
{
    CClanUserParam ClanUserParam;
    CClanServerParam ClanServerParam;
};

struct CPacket_S2C_CLAN_GET_MY_INFO_RES : CPacket
{
    u32 Error;
    s32 Result;
    CClanParam CreateParam;
    s64 LeaveTime;
};

CPacket_S2C_CLAN_GET_MY_INFO_RES S2C_CLAN_GET_MY_INFO_RES @0x00;