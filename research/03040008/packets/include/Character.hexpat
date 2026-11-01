// Character-side CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11a-old-patterns.md
// (shared-structure table, G6) and P11b-old-patterns.md (its extension). "PC 0x..." is the reader VA
// in the PC 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type.
// Marks: V = read in IDA, I = inferred. Enums come from PS4 DWARF only; values without a DWARF
// name are UNK_<value>. Server C# names are leads only and appear only as "server: <name>".
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// nCharacter::E_WALLET_POINT_TYPE (PS4 DWARF, __int32; values 1-8 named there). Read as u8 on the
// wire. Values 9-16 are not in PS4 DWARF (server lead: HighOrbs, DominionPoints,
// AdventurePassPoints, UnknownTickets, BitterBlackMazeResetTicket / CustomMadeServiceTickets,
// GoldenDragonMark, SilverDragonMark, RedDragonMark).
enum E_WALLET_POINT_TYPE : u8 {
    WALLET_POINT_TYPE_INVALID = 0x0,
    WALLET_POINT_TYPE_GOLD = 0x1,
    WALLET_POINT_TYPE_RIM = 0x2,
    WALLET_POINT_TYPE_ORB = 0x3,
    WALLET_POINT_TYPE_TICKET = 0x4,
    WALLET_POINT_TYPE_GP = 0x5,
    WALLET_POINT_TYPE_SUPPORT = 0x6,
    WALLET_POINT_TYPE_JP_RESET = 0x7,
    WALLET_POINT_TYPE_CP_RESET = 0x8,
    UNK_9 = 0x9,
    UNK_10 = 0xA,
    UNK_11 = 0xB,
    UNK_12 = 0xC,
    UNK_13 = 0xD,
    UNK_14 = 0xE,
    UNK_15 = 0xF,
    UNK_16 = 0x10
};

// CDataWalletPoint: PC list reader 0x77c5a0 {u8, u32} (V); PS4 CDataWalletPoint {u8 m_ucType,
// u32 m_unValue}. Users: CDataQuestOrderList, CDataSetQuestDetail, CDataDispelBaseItem.
struct CDataWalletPoint {
    E_WALLET_POINT_TYPE Type;
    u32 Value;
};

// CDataJobBaseInfo: PC reader 0x76b190 {u8, u8} (P11b shared table, V); PS4 CDataJobBaseInfo
// {u8 m_ucJob, u8 m_ucLv}.
struct CDataJobBaseInfo {
    u8 Job;
    u8 Lv;
};

// CDataCharacterName: read inline by PC 0x75ccf0 as two MtStrings (P11b 4, V); PS4
// CDataCharacterName {MtString m_wstrFirstName, MtString m_wstrLastName}.
struct CDataCharacterName {
    MtString FirstName;
    MtString LastName;
};

// CDataCommunityCharacterBaseInfo: read inline by PC 0x75ccf0 {u32, MtString x3} (V); PS4
// CDataCommunityCharacterBaseInfo {u32 m_unCharacterID, CDataCharacterName m_CharacterName,
// MtString m_wstrClanName}.
struct CDataCommunityCharacterBaseInfo {
    u32 CharacterID;
    CDataCharacterName CharacterName;
    MtString ClanName;
};

// CDataCharacterListElement: PC reader 0x75ccf0 (nPacket::Read_CDataCharacterListElement_), list
// reader 0x75cbd0 {u32, MtString x3, u16, u8, JobBaseInfo x2, MtString, u8} (P11b shared table, V).
// PS4 CDataCharacterListElement (and the PS4 recompilation, PacketData/Community.h) has the same
// members up to m_wstrMatchingPlofile and no trailing u8: the u8 is Season 3, name open. Users:
// CDataClanMemberInfo (31.29.2, 31.4.2), 18.0.2.
struct CDataCharacterListElement {
    CDataCommunityCharacterBaseInfo BaseInfo;
    u16 ServerID;
    u8 OnlineStatus;
    CDataJobBaseInfo CurrentJobInfo;
    CDataJobBaseInfo EntryJobInfo;
    MtString MatchingPlofile;   // PS4 DWARF spelling (m_wstrMatchingPlofile)
    u8 unk_u8;                  // Season 3 (PC 0x75ccf0), no PS4 member
};
