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
#include "Pawn.hexpat"         // CDataCharacterEquipData; Pawn -> Login -> Character, Context, GP (T010b)
#include "Furniture.hexpat"    // CDataFurnitureLayout (T010b)

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

// --- Since spec 006 T010b: the group 31 CLAN types of
// specs/006-packet-pattern-coverage/research/T010-gp-clan.md sections 1.2 and 25 (field names: the
// PS4 DWARF member, m_ and type prefix dropped, V, unless marked). None of Pawn, Login, Character,
// Context, GP or Furniture includes this file (no include cycle).

// CDataClanJoinRequest: PC list reader 0x75d430 (not a function in the PC database, decoded
// linearly), element at 0x75d4e2 {u32, MtString, CDataCommunityCharacterBaseInfo 0x75ecf0, s64}
// (V); PS4 Read_CDataClanJoinRequest__0, CDataClanJoinRequest {u32 m_unClanID, MtString
// m_wstrClanName, CCommunityCharacterBaseInfo m_CommunityCharacterBaseInfo, s64 m_llCreated}: same
// (V). Code-only: every captured 31.9.2 list is empty. User: 31.9.2.
struct CDataClanJoinRequest {
    u32 ClanID;
    MtString ClanName;
    CDataCommunityCharacterBaseInfo CommunityCharacterBaseInfo;
    s64 Created;
};

// CDataClanHistoryElement: PC list reader 0x75d280, element 0x75d390 {s64, u8, MtString x2, u32 x3,
// MtString} (V); PS4 {s64 m_llDate, u8 m_ucType, CCharacterName m_CharacterName, u32 m_unValue1,
// m_unValue2, m_unValue3, MtString m_wstrFreeText}: same (V). User: 31.30.2.
struct CDataClanHistoryElement {
    s64 Date;
    u8 Type;
    CDataCharacterName CharacterName;
    u32 Value1;
    u32 Value2;
    u32 Value3;
    MtString FreeText;
};

// CDataClanFunctionInfo / CDataClanDungeonInfo: PS4 {MtTypedArray<CDataCommonU32> m_ReleaseIdList}
// each (V); PC reads one list 0x75e8e0 for each, inline in the 31.31.2 reader 0x802de0 (V).
struct CDataClanFunctionInfo {
    MtTypedArray<CDataCommonU32> ReleaseIdList;
};

struct CDataClanDungeonInfo {
    MtTypedArray<CDataCommonU32> ReleaseIdList;
};

// CDataPawnExpeditionInformation (the report's CDataClanPawnExpeditionInfo): PC 0x771e80 {u8 x3}
// (V); PS4 CDataPawnExpeditionInformation {u8 m_ucSallyStatus, m_ucGoldenSallyPrice,
// m_ucChargeSallyPrice}: same (V).
struct CDataPawnExpeditionInformation {
    u8 SallyStatus;
    u8 GoldenSallyPrice;
    u8 ChargeSallyPrice;
};

// CDataClanPartnerPawnInfo: PC 0x75d770 {list 0x75e8e0, list 0x75e8e0} (V); PS4
// {MtTypedArray<CDataCommonU32> m_MyPartnerPawnList, m_MemberPartnerPawnList} (V).
struct CDataClanPartnerPawnInfo {
    MtTypedArray<CDataCommonU32> MyPartnerPawnList;
    MtTypedArray<CDataCommonU32> MemberPartnerPawnList;
};

// CDataClanConciergeNpc: PC list reader 0x75d160 {u32, u32, bool, u32} (V); PS4 {u32 m_unNpcId,
// u32 m_unPrice, b8 m_bIsInit, u32 m_unSortId} (V).
struct CDataClanConciergeNpc {
    u32 NpcId;
    u32 Price;
    bool IsInit;
    u32 SortId;
};

// CDataClanConciergeInfo: PC 0x75d120 {u32, list 0x75d160} (V); PS4 {u32 m_unNpcId,
// MtTypedArray<CDataClanConciergeNpc> m_ClanConciergeNpcList} (V).
struct CDataClanConciergeInfo {
    u32 NpcId;
    MtTypedArray<CDataClanConciergeNpc> ClanConciergeNpcList;
};

// CDataClanShopLineupName: PC list reader 0x75e2f0 {u32, MtString} (V); PS4 {u32 m_unLineupID,
// MtString m_wstrName} (V).
struct CDataClanShopLineupName {
    u32 LineupID;
    MtString Name;
};

// CDataClanValueInfo: PC list reader 0x75e500 {u8, u32} (V); PS4 {u8 m_ucType, u32 m_unValue} (V).
struct CDataClanValueInfo {
    u8 Type;
    u32 Value;
};

// CDataClanShopBuffInfo: PC list reader 0x75dd30 {u32, u8} (V); PS4 {u32 m_unBuffID,
// u8 m_ucBuffType} (V).
struct CDataClanShopBuffInfo {
    u32 BuffID;
    u8 BuffType;
};

// CDataClanShopBuffItem: PC list reader 0x75de20, element 0x75dee0 {u32, u32, u8, u32, MtString,
// list 0x75dd30, list 0x75e8e0} (V); PS4 {u32 m_unLineupId, m_unRequireClanPoint, u8
// m_ucRequiredLevel, u32 m_unIconID, MtString m_wstrName, MtTypedArray<CDataClanShopBuffInfo>
// m_BuffInfo, MtTypedArray<CDataCommonU32> m_RequireLineupId}: same (V). User: 31.34.2.
struct CDataClanShopBuffItem {
    u32 LineupId;
    u32 RequireClanPoint;
    u8 RequiredLevel;
    u32 IconID;
    MtString Name;
    MtTypedArray<CDataClanShopBuffInfo> BuffInfo;
    MtTypedArray<CDataCommonU32> RequireLineupId;
};

// CDataClanShopInfo: PC 0x75e2a0 (not a function in the PC database; called as loc_75E29C+4)
// {u32, list 0x75e8e0, list 0x75e8e0} (V); PS4 {u32 m_unClanPoint, MtTypedArray<CDataCommonU32>
// m_CurrentFunctionList, m_CurrentBuffList} (V). User: 31.34.2.
struct CDataClanShopInfo {
    u32 ClanPoint;
    MtTypedArray<CDataCommonU32> CurrentFunctionList;
    MtTypedArray<CDataCommonU32> CurrentBuffList;
};

// CDataNoraPawnInfo (Season 3): PC 0x76f790 {u32, MtString, CDataEditInfo 0x764550 (122 B), u8,
// list 0x75c190, list 0x75c190} (V). PS4 CDataNoraPawnInfo (alias CNoraPawnInfo) {u32 m_unVersion,
// MtString m_wstrName, CEditInfo m_EditInfo, u8 m_ucJob, MtTypedArray<CDataCharacterEquipData>
// m_CharacterEquipDataList}: the first five match (V); Season 3 adds a second equip list, named
// CharacterEquipViewDataList (I: the same list pair as in CDataPawnInfo and CDataCharacterInfo).
// The PS4 body fails 22/28 31.40.2 captures. User: 31.40.2.
struct CDataNoraPawnInfo {
    u32 Version;
    MtString Name;
    CDataEditInfo EditInfo;                                           // PC 0x764550
    u8 Job;
    MtTypedArray<CDataCharacterEquipData> CharacterEquipDataList;      // PC 0x75c190
    MtTypedArray<CDataCharacterEquipData> CharacterEquipViewDataList;  // Season 3, PC 0x75c190; name I
};
