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
