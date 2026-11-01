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
