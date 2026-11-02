// GP course CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/T002-login.md
// sections 10, 11 and 15. "PC 0x..." is the reader VA in the PC 03040008 database (image base
// 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the fields carry. Marks:
// V = read in IDA, I = inferred. Users: 4.0.2 L2C_GP_COURSE_GET_INFO_RES and, through
// Login.hexpat, 5.0.2 L2C_GET_CHARACTER_LIST_RES.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataGPCourseInfo: PC reader 0x767440 (list 0x767340) {u32, MtString, bool, u8, u8, u8, list
// 0x75e8e0 of CDataCommonU32} (V); PS4 CDataGPCourseInfo {u32 m_unCourseID, MtString
// m_wstrCourseName, b8 m_bDoubleCourseTarget, u8 m_ucPrioGroup, u8 m_ucPrioSameTime,
// u8 m_ucAnnounceType, MtTypedArray<CDataCommonU32> m_EffectUIDList}: same order and widths (V).
struct CDataGPCourseInfo {
    u32 CourseID;
    MtString CourseName;
    bool DoubleCourseTarget;
    u8 PrioGroup;
    u8 PrioSameTime;
    u8 AnnounceType;
    MtTypedArray<CDataCommonU32> EffectUIDList;
};

// CDataGPCourseEffectParam: PC list reader 0x767220 {u32 x4} (V); PS4 CDataGPCourseEffectParam
// {u32 m_unEffectUID, u32 m_unEffectID, u32 m_unParam0, u32 m_unParam1} (V).
struct CDataGPCourseEffectParam {
    u32 EffectUID;
    u32 EffectID;
    u32 Param0;
    u32 Param1;
};

// CDataGPCourseValid: PC reader 0x7675d0 (list 0x7674d0) {u32, u32, MtString, MtString, u64, u64}
// (V). PS4 Read_CDataGPCourseValid_ 0x1a10d20 reads u32 m_unID, u32 m_unCourseID, MtString
// m_wstrName, u32 m_unIconID, u64 m_ullStartTime, u64 m_ullEndTime: PC reads a second MtString
// where PS4 has the u32 IconID (Season 3; carrying the PS4 layout is contradicted, C). Not
// capture-tested: every GpCourseValid list in the 03040008 captures is empty (T002 section 11).
struct CDataGPCourseValid {
    u32 ID;
    u32 CourseID;
    MtString Name;
    MtString unk_MtString;      // Season 3 (PS4: u32 m_unIconID); server: NameB (lead)
    u64 StartTime;
    u64 EndTime;
};

// --- Since spec 006 T010b: the group 28 GP types of
// specs/006-packet-pattern-coverage/research/T010-gp-clan.md sections 1.1 and 25 (field names: the
// PS4 DWARF member, m_ and type prefix dropped, V; Season 3 fields with no PS4 member are `unk_*`).
// Users: 28.2.2, 28.7.2, 28.8.2, 28.17.2, 28.22.2.

// CDataGPPeriod: PC list reader 0x7678e0 {u32, bool, u64} (V); PS4 CDataGPPeriod {u32 m_unGP,
// b8 m_bIsFreeGP, u64 m_ullPeriod}: same (V).
struct CDataGPPeriod {
    u32 GP;
    bool IsFreeGP;
    u64 Period;
};

// CDataGPShopDisplayType: PC list reader 0x767d00 (not a function in the PC database, decoded
// linearly) {u32, MtString, u32} (V); PS4 0x1a0fc00 CDataGPShopDisplayType {u32 m_unID,
// MtString m_wstrName, u32 m_unInGameUrlID}: same (V).
struct CDataGPShopDisplayType {
    u32 ID;
    MtString Name;
    u32 InGameUrlID;
};

// CDataGPShopDisplayLineup (Season 3): PC list reader 0x767b20, element 0x767be0: 14 reads {u32,
// u32, u8, u32, u32, u32, MtString, MtString, u32, MtString, u32 x4} (V). PS4 0x1a0f8e0 reads 12:
// {u32 m_unID, m_unCategory, u8 m_ucIconId, u32 m_unGP, m_unDiscountType, m_unDiscountGP, MtString
// m_wstrName, m_wstrComment, u32 m_unLineupID, m_unBackIconID, m_unFrameIconID,
// m_unBehaviorAfterBuyingType}. The first nine match (V); Season 3 adds an MtString after LineupID
// and has four u32 where PS4 has three. Which PS4 u32 survive and where the new one sits is not
// settled, so all four are `unk_u32_0..3` (T010 1.1, 27). The PS4 element fails 38/38 captures.
struct CDataGPShopDisplayLineup {
    u32 ID;
    u32 Category;
    u8 IconId;
    u32 GP;
    u32 DiscountType;
    u32 DiscountGP;
    MtString Name;
    MtString Comment;
    u32 LineupID;
    MtString unk_MtString;      // Season 3
    u32 unk_u32_0;              // PS4 has BackIconID, FrameIconID, BehaviorAfterBuyingType here (3 u32)
    u32 unk_u32_1;
    u32 unk_u32_2;
    u32 unk_u32_3;
};

// CDataGPCourseAvailable (Season 3): PC list reader 0x7670a0, element 0x7671a0 {u32, MtString,
// u64, u32, u32, MtString} (V). PS4 0x1a113c0 {u32 m_unID, MtString m_wstrName, u64
// m_ullUseLimitTime, u32 m_unCourseID, u32 m_unLineupID, u32 m_unBackIconID, u32 m_unFrameIconID}:
// PC reads one MtString where PS4 has the two icon u32 (the same change as CDataGPCourseValid
// above). CourseID and LineupID are I by position. Code-only: every captured list is empty (T010 9).
struct CDataGPCourseAvailable {
    u32 ID;
    MtString Name;
    u64 UseLimitTime;
    u32 CourseID;
    u32 LineupID;
    MtString unk_MtString;      // Season 3 (PS4: u32 m_unBackIconID, u32 m_unFrameIconID)
};

// CDataEditParamPalette: PS4 {u32 m_unParamTypeId, u32 m_unUID} (V), read inline by CDataEditParam.
struct CDataEditParamPalette {
    u32 ParamTypeId;
    u32 UID;
};

// CDataEditParam: PC list reader 0x764b20 {u32, u32, bool, bool, bool} (V); PS4 0x1a10090
// CDataEditParam {CEditParamPalette m_EditParamPalette, b8 m_bIsValid, b8 m_bIsGp,
// b8 m_bIsPitchEnable}: same (V).
struct CDataEditParam {
    CDataEditParamPalette EditParamPalette;
    bool IsValid;
    bool IsGp;
    bool IsPitchEnable;
};
