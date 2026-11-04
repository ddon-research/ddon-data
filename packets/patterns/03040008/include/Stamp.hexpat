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
// {u32 m_unBonusType, u32 m_unBonusValue}: Season 3 adds one u32. T014b part 7 (stamp UI 0xebcaf0)
// rejects the PS4-position names BonusType (+8) / BonusValue (+12) that T009b gave the last two:
// +4 is the bonus kind, +8 an id (mapped by 0xebb610 when +4 == 1), +12 the amount. Which u32 is
// the PS4 pair stays open, so all three are `unk_*` with their roles (server lead: Unk0,
// BonusType, BonusValue).
struct CDataStampBonus {
    // T014b V (role): STAMP_BONUS_GET_LIST_RES handler 0x7fe140 (not a function, read by
    // instruction) keeps the packet at conn sub +0x478 (getter 0x871bd0, one caller) (...)
    u32 unk_u32;                // Season 3; server: Unk0 (lead). Role (V): bonus kind
    // T014b V (role), kept unk: the bonus id; 0xebcaf0 maps it by 0xebb610 (1..5 -> 7789, 7792,
    // 7795, 10682, 10664) when unk_u32 == 1, else shows it as is. Was BonusType (PS4 position, I),
    // rejected; server: BonusType (lead)
    u32 unk_u32_1;
    // T014b V (role), kept unk: the amount (multiplied by the u16 of a 0xebcaf0 switch). Was
    // BonusValue (PS4 position, I), rejected; server: BonusValue (lead)
    u32 unk_u32_2;
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
    // T014b V (role): 0xebcaf0 selects the daily group whose +4 (this field) equals stamp UI
    // +0x25A8 (...)
    u32 unk_u32_0;              // server: Unk0 (lead)
    // T014b open (not read), kept unk: group +8: 0xebcaf0, the only caller of the GET_LIST getter
    // 0x871bd0, reads group +4 and the daily list (+12/+16) only. Captures give 77, the value of
    // CHECK_RES element +8 that the UI keeps at +0x25AC (I)
    u32 unk_u32_1;              // server: Unk1 (lead)
    MtTypedArray<CDataStampBonusDaily> StampBonusDaily;         // PC 0x77a6b0
};

// Season 3 element of 45.1.2 (it replaces PS4's u16 m_usTotalStampNum): PC list reader 0x77a5c0,
// element {u32, u32} (V shape); no PS4 type, name unk. server: CDataStampCheck (lead).
struct CDataStampBonusCheckRes_unk_0 {
    // T014b V (role): 0x65cbd0 (getter 0x871bc0, list +28/+40) takes the element whose +4 == 1 and
    // stores +4 / +8 in the stamp talk UI (dti__4246) at +0x25A8 / +0x25AC (...)
    u32 unk_u32_0;              // server: Unk0 (lead)
    // T014b V (flow); role open: stored with unk_u32_0 by 0x65cbd0 at UI +0x25AC and pushed with
    // +0x25A8 to 0x8785c0 (request 561, whose send body is not visible in the decompiled function);
    // no other reader
    u32 unk_u32_1;              // server: Unk1 (lead)
};
