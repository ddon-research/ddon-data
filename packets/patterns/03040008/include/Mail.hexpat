// Group 37 MAIL CData of client 03040008 (PC, Season 3), shared by the mail packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T009-mail-stamp-character.md sections 1.1 and 22. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type, whose member names the
// fields carry (m_ and type prefix dropped). Marks: V = read in IDA. None of these types changed in
// Season 3 (PC = PS4, V). The attachment classes are mail's own PS4 classes, not the item storage
// types of Item.hexpat (V).
// Includes Packet.hexpat and Character.hexpat (CDataCommunityCharacterBaseInfo); neither includes
// this file (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"

// CDataMailInfo: PC element reader 0x76e5a0, list reader 0x76e480 (V); PS4 Read_CDataMailInfo_
// 0x19f53b0 / Read_CDataMailInfo__0 0x19f65f0 {u64 m_ullId, u8 m_ucState, u8 m_ucItemState,
// m_BaseInfo, MtString m_wstrSenderName, MtString m_wstrMailText, s64 m_llSenderDate} (V).
// Users: 37.1.2, 37.7.2 (system mail uses the player-mail element), 37.13.16.
struct CDataMailInfo {
    u64 Id;
    u8 State;
    u8 ItemState;
    CDataCommunityCharacterBaseInfo BaseInfo;     // PC 0x75ecf0
    MtString SenderName;
    MtString MailText;
    s64 SenderDate;
};

// CDataMailAttachmentInfo: read inline by each attachment list reader below (V); PS4 {u64
// m_ullAttachmentId, b8 m_bIsReceived} (V).
struct CDataMailAttachmentInfo {
    u64 AttachmentId;
    bool IsReceived;
};

// CDataMailItemInfo: PC list reader 0x76e630 (V); PS4 0x19f5510 {AttachmentInfo, u32 m_unItemId,
// u16 m_usNum} (V).
struct CDataMailItemInfo {
    CDataMailAttachmentInfo AttachmentInfo;
    u32 ItemId;
    u16 Num;
};

// CDataMailGPInfo: PC list reader 0x76e350 (V); PS4 0x19f57b0 {AttachmentInfo, u32 m_unNum,
// u32 m_unType} (V).
struct CDataMailGPInfo {
    CDataMailAttachmentInfo AttachmentInfo;
    u32 Num;
    u32 Type;
};

// CDataMailOptionCourseInfo: PC list reader 0x76e890 (V); PS4 0x19f5a40 {AttachmentInfo,
// u32 m_unOptionCourseId, u32 m_unOptionCourseLineupId, u32 m_unTime} (V).
struct CDataMailOptionCourseInfo {
    CDataMailAttachmentInfo AttachmentInfo;
    u32 OptionCourseId;
    u32 OptionCourseLineupId;
    u32 Time;
};

// CDataMailLegendPawnInfo: PC list reader 0x76e760 (V); PS4 0x19f5d00 {AttachmentInfo,
// u32 m_unPawnId, MtString m_wstrName} (V).
struct CDataMailLegendPawnInfo {
    CDataMailAttachmentInfo AttachmentInfo;
    u32 PawnId;
    MtString Name;
};

// CDataMailAttachmentList: PC reader 0x76e2f0, four lists in this order (V); PS4 {m_ItemList,
// m_GPList, m_OptionCourseList, m_LegendPawnList} (V). Users: 37.9.2 (inside CDataMailTextInfo),
// 37.11.2.
struct CDataMailAttachmentList {
    MtTypedArray<CDataMailItemInfo> ItemList;                   // PC 0x76e630
    MtTypedArray<CDataMailGPInfo> GPList;                       // PC 0x76e350
    MtTypedArray<CDataMailOptionCourseInfo> OptionCourseList;   // PC 0x76e890
    MtTypedArray<CDataMailLegendPawnInfo> LegendPawnList;       // PC 0x76e760
};

// CDataMailTextInfo: PC reader 0x76e9e0 {MtString, CDataMailAttachmentList 0x76e2f0} (V); PS4
// {MtString m_wstrText, CMailAttachmentList m_AttachmentList} (V). User: 37.9.2.
struct CDataMailTextInfo {
    MtString Text;
    CDataMailAttachmentList AttachmentList;
};
