// Group 31 CLAN CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11b-old-patterns.md
// sections 4 and 6 and the shared-structure table. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type; the member order also
// matches the PS4 recompilation (D:/ddon-data-s2/recompilation, PacketData/Clan.h). Marks: V = read
// in IDA, I = inferred. Field names without the m_ prefix are the earlier patterns' names (they
// mirror the PS4 DWARF names). Server C# names are leads only.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"

// CDataClanMemberInfo: PC element reader 0x75d640, list reader 0x75d580 {u32, s64 x3, u32,
// CDataCharacterListElement} (V); PS4 CDataClanMemberInfo, same order. Users: 31.4.2,
// CDataClanServerParam.
struct CDataClanMemberInfo {
    u32 Rank;
    s64 Created;
    s64 LastLoginTime;
    s64 LeaveTime;
    u32 Permission;
    CDataCharacterListElement CharacterListElement;
};

// CDataClanUserParam: PC reader 0x75e3e0 {MtString x2, u8 x4, u32 x4, bool, MtString x2, s64} (V);
// PS4 CDataClanUserParam, same order.
struct CDataClanUserParam {
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
    bool IsPublish;
    MtString Comment;
    MtString BoardMessage;
    s64 Created;
};

// CDataClanServerParam: PC reader 0x75dc60 {u32, u16, u16, CDataClanMemberInfo, bool x3, u32 x3}
// (V); PS4 CDataClanServerParam, same order.
struct CDataClanServerParam {
    u32 ID;
    u16 Lv;
    u16 MemberNum;
    CDataClanMemberInfo MasterInfo;
    bool IsSystemRestriction;
    bool IsClanBaseRelease;
    bool CanClanBaseRelease;
    u32 TotalClanPoint;
    u32 MoneyClanPoint;
    u32 NextClanPoint;
};

// CDataClanParam: PC reader 0x75d730 = CDataClanUserParam + CDataClanServerParam (V); PS4
// CDataClanParam {m_ClanUserParam, m_ClanServerParam}. User: 31.29.2.
struct CDataClanParam {
    CDataClanUserParam ClanUserParam;
    CDataClanServerParam ClanServerParam;
};
