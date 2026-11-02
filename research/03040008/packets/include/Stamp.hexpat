// Group 45 STAMP CData of client 03040008 (PC, Season 3), shared by the stamp packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T009-mail-stamp-character.md sections 1.2, 18, 19 and 22. "PC 0x..." is the reader VA in the PC
// 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type. Marks: V = read
// in IDA, I = inferred. Season 3 changed every stamp shape: CDataStampBonus has three u32 (PS4 two),
// the daily list is wrapped in a group, and the check response carries a list of pairs. Season 3
// fields with no PS4 member are `unk_*`; server C# names appear only as "server: <name> (lead)".
// Capture link (I, T009 1.2): in every walked capture the u32 pair of the daily group, of the
// 45.1.2 list and of the (Season 3-exclusive) 45.3.1 request is (1, 77).
// Includes nothing but Packet.hexpat (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataStampBonus: PC list reader 0x77a380, element {u32, u32, u32} (V widths). PS4 CDataStampBonus
// {u32 m_unBonusType, u32 m_unBonusValue}: Season 3 adds one u32. Which u32 is new is I: the PS4
// pair is placed last (server lead: Unk0, BonusType, BonusValue, the new one first).
struct CDataStampBonus {
    u32 unk_u32;                // Season 3; server: Unk0 (lead)
    u32 BonusType;              // I (PS4 member, position)
    u32 BonusValue;             // I (PS4 member, position)
};

// CDataStampBonusDaily: PC list reader 0x77a6b0, element {list 0x77a380, u16, u8} (V order); PS4
// CDataStampBonusDaily {MtTypedArray<CDataStampBonus> m_StampBonus, u16 m_usStampNum,
// u8 m_ucRecieveState} (names V by matching shape). PS4 CDataStampBonusTotal has the identical
// members, and Season 3 reads the daily and the total lists with this one reader (0x77a6b0, V):
// CDataStampBonusTotal is an alias. server: CDataStampBonusAsset (lead).
struct CDataStampBonusDaily {
    MtTypedArray<CDataStampBonus> StampBonus;                   // PC 0x77a380
    u16 StampNum;
    u8 RecieveState;            // PS4 DWARF spelling (m_ucRecieveState)
};

using CDataStampBonusTotal = CDataStampBonusDaily;

// CDataStampBonusDailyGroup (Season 3, name I: it wraps the daily list of PS4's
// m_StampBonusDaily, and its pair is what 45.3.1 RECIEVE_DAILY sends): PC list reader 0x77a490,
// element {u32, u32, list 0x77a6b0} (V shape); no PS4 type. User: 45.0.2.
// server: CDataStampBonusDaily {Unk0, Unk1, AssetList} (lead; not the PS4 class of that name).
struct CDataStampBonusDailyGroup {
    u32 unk_u32_0;              // server: Unk0 (lead)
    u32 unk_u32_1;              // server: Unk1 (lead)
    MtTypedArray<CDataStampBonusDaily> StampBonusDaily;         // PC 0x77a6b0
};

// Season 3 element of 45.1.2 (it replaces PS4's u16 m_usTotalStampNum): PC list reader 0x77a5c0,
// element {u32, u32} (V shape); no PS4 type, name unk. server: CDataStampCheck (lead).
struct CDataStampBonusCheckRes_unk_0 {
    u32 unk_u32_0;              // server: Unk0 (lead)
    u32 unk_u32_1;              // server: Unk1 (lead)
};
