// Game-server connection setup CData of client 03040008 (PC, Season 3), shared by the packet
// patterns of groups 0 CONNECTION and 1 SERVER (C2S_/S2C_).
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T003-connection-server-cert.md sections 2, 11, 13, 14 and 18. "PC 0x..." is the reader or writer
// VA in the PC 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type,
// whose member names the fields carry unless marked. Marks: V = read in IDA, I = inferred.
// Server C# (Arrowgene) names are leads only.
// Includes Packet.hexpat and Login.hexpat (CDataURLInfo, CDataGameServerListInfo); neither includes
// this file (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Login.hexpat"

// CDataCheatInfo: PC writer 0x77db60 (u32 count, then Write_u8, Write_u8, Write_u32 x3 per element)
// (V); PS4 CDataCheatInfo {u8 m_ucId, u8 m_ucCount, u32 m_unParam1, u32 m_unParam2,
// u32 m_unParam3} (V).
struct CDataCheatInfo {
    u8 Id;
    u8 Count;
    u32 Param1;
    u32 Param2;
    u32 Param3;
};

// CDataCharacterItemSlotInfo: PC list reader 0x75c570 {u8, u16} (V); PS4 {u8 m_ucStorageType,
// u16 m_usSlotMax} (V).
struct CDataCharacterItemSlotInfo {
    u8 StorageType;
    u16 SlotMax;
};

// CDataPartyMemberMaxNum: PC list reader 0x7717e0 {u32, u32} (V); PS4 {u32 m_unContentType,
// u32 m_unNum} (V).
struct CDataPartyMemberMaxNum {
    u32 ContentType;
    u32 Num;
};

// CDataJewelryEquipLimit: PC list reader 0x76afb0 {u8, u8} (V); PS4 {u8 m_ucJewelryType,
// u8 m_ucEquipNumMax} (V).
struct CDataJewelryEquipLimit {
    u8 JewelryType;
    u8 EquipNumMax;
};

// CDataWalletLimit (name I, server lead): PC list reader 0x77c4b0 {u32, u32} (V widths). Season 3,
// no PS4 counterpart; no PS4 or PC field name (unk_*). Captures: 16 pairs, ids 1-16.
struct CDataWalletLimit {
    u32 unk_u32_0;            // Season 3, no PS4 member; server: WalletType (lead)
    u32 unk_u32_1;            // Season 3, no PS4 member; server: MaxValue (lead)
};

// CDataExpRequirement (name I, server lead): PC list reader 0x766910 {u8, u32} (V widths). Season 3,
// no PS4 counterpart. Captures: (1, 0), (2, 300), ... read as (level, exp), I.
struct CDataExpRequirement {
    u8 unk_u8;                // level (I)
    u32 unk_u32;              // exp (I)
};

// CDataExpSetting (name I, server lead): PC list reader 0x766800 {u8, list 0x766910} (V widths).
// Season 3, no PS4 counterpart. Captures: two entries (1, 2) with 120 and 55 rows.
struct CDataExpSetting {
    u8 unk_u8;                // Season 3, no PS4 member; server: Type (lead)
    MtTypedArray<CDataExpRequirement> unk_ExpRequirementList;
};

// CDataGameSetting: PC reader 0x768bb0 (V, T003 section 11): u32 x9, u8, list 0x75c570, u32, u8,
// bool, u8, u32 x7, list 0x77bbd0, list 0x7717e0, u32 x4, u8, list 0x76afb0, u32 x6, list 0x75e8e0,
// u32, bool, u32 x3, list 0x77c4b0, u16, list 0x766800. PS4 CDataGameSetting member names
// (V up to MailCacheExpireTime) with two Season 3 differences (V code, names I):
// - PS4's MtString m_wstrCapLinkServerVerion and m_wstrCapLinkApiVerion are gone: PC reads
//   u32 x4, u8 where PS4 has u32 x3, MtString, MtString, u32, u8; PawnPresentItemID/Num keep
//   their PS4 names by width alignment (I position; the capture's 4th u32 equals PawnCreateItemID).
// - New tail after MailCacheExpireTime: bool, u32 x3, list {u32, u32}, u16, list {u8, list
//   {u8, u32}}: no PS4 or PC name (unk_*; element names are server leads, I).
// BazaarSerch* keeps the PS4 DWARF spelling.
struct CDataGameSetting {
    u32 MainPawnMax;
    u32 SupportPawnMax;
    u32 JobLevelMax;
    u32 CraftLevelMax;
    u32 CraftSkillLevelMax;
    u32 UserListMax;
    u32 ClanLvMax;
    u32 ClanMemberMax;
    u32 ClanLeaveIntervalTime;
    u8 CharacterNumMax;
    MtTypedArray<CDataCharacterItemSlotInfo> GlobalItemSlotNumMaxList;   // PC 0x75c570
    u32 PawnCreateItemID;
    u8 PawnCreateItemNum;
    bool EnableVisualEquip;
    u8 EquipColorChangeGrade;
    u32 FriendListMax;
    u32 RecentPlayerMax;
    u32 BlackListMax;
    u32 HistoryListMax;
    u32 CharacterReviveGP;
    u32 PawnReviveGP;
    u32 LostPawnReviveGP;
    MtTypedArray<CDataURLInfo> UrlInfoList;                              // PC 0x77bbd0 (Login.hexpat)
    MtTypedArray<CDataPartyMemberMaxNum> PartyMemberMaxNumList;          // PC 0x7717e0
    u32 GroupChatMemberMax;
    u32 EventCodeInputLockFailNum;
    u32 EventCodeLockTime;
    u32 PawnPresentItemID;    // I position (Season 3 dropped the two CapLink MtStrings before it)
    u8 PawnPresentItemNum;    // I position
    MtTypedArray<CDataJewelryEquipLimit> JewelryEquipLimitList;          // PC 0x76afb0
    u32 JobPointMax;
    u32 PlayPointMax;
    u32 PlayPointLevelMin;
    u32 BazaarSerchTime;
    u32 BazaarSerchCautionTime;
    u32 BazaarSerchCautionCount;
    MtTypedArray<CDataCommonU32> ClanBaseStageList;                      // PC 0x75e8e0
    u32 MailCacheExpireTime;
    // Season 3 tail (V widths, no names).
    bool unk_bool;
    u32 unk_u32_0;
    u32 unk_u32_1;
    u32 unk_u32_2;
    MtTypedArray<CDataWalletLimit> unk_WalletLimitList;                  // PC 0x77c4b0 (name I)
    u16 unk_u16;
    MtTypedArray<CDataExpSetting> unk_ExpSettingList;                    // PC 0x766800 (name I)
};

// CDataWeatherForecast: PC list reader 0x77c960 {u32} (V); PS4 {u32 m_unWeather} (V).
struct CDataWeatherForecast {
    u32 Weather;
};

// CDataGameTimeBaseInfo: PC reader 0x769030 {u32 x6, s64, s64, u32, u32} (V); PS4
// CDataGameTimeBaseInfo, same order and widths, no Season 3 change (V).
struct CDataGameTimeBaseInfo {
    u32 GameTimeOneDayMin;
    u32 GameTimeYearMonth;
    u32 GameTimeMonthDay;
    u32 GameTimeDayHour;
    u32 GameTimeWeekDay;
    u32 GameTimeMoonAge;
    s64 OriginalRealTimeSec;
    s64 OriginalGameTimeSec;
    u32 OriginalWeek;
    u32 OriginalMoonAge;
};

// CDataWeatherLoop: PC list reader 0x77ca30 {u8, u32} (V); PS4 {u8 m_ucWeatherId, u32 m_unTimeSec} (V).
struct CDataWeatherLoop {
    u8 WeatherId;
    u32 TimeSec;
};

// CDataWeatherSchedule: PC list reader 0x77cb20 {u8, s64, s64} (V); PS4 {u8 m_ucWeatherId,
// s64 m_llBeginTimeSec, s64 m_llEndTimeSec} (V).
struct CDataWeatherSchedule {
    u8 WeatherId;
    s64 BeginTimeSec;
    s64 EndTimeSec;
};

// CDataMoonSchedule: PC list reader 0x76f0f0 {u8, s64, s64} (V); PS4 {u8 m_ucMoonAge,
// s64 m_llBeginTimeSec, s64 m_llEndTimeSec} (V). Not capture-tested: every captured list is empty.
struct CDataMoonSchedule {
    u8 MoonAge;
    s64 BeginTimeSec;
    s64 EndTimeSec;
};
