// Equip CData structures of client 03040008 (PC, Season 3) shared by the group 29 EQUIP patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T012-achievement-equip-skill.md sections 1, 13 and 19. The report proposes Item.hexpat for these
// types; they live here instead so that Item.hexpat (and its group 10/50 users) need not include
// Pawn.hexpat. "PC 0x..." is the reader VA in the PC 03040008 database (image base 0x400000);
// "PS4" names the PS4 02020005 reader and DWARF type, whose member names the fields carry (m_ and
// type prefix dropped) unless marked. Marks: V = read in IDA, I = inferred. A Season 3 field without
// a PS4 member is `unk_*`; server C# (Arrowgene) names are leads only ("server: <name> (lead)").
// Includes Packet.hexpat and Pawn.hexpat (CDataEquipJobItem; Pawn -> Login -> Character, Context
// (EquipElementParam, CDataContextBase_unk_0), GP); none of them includes this file (no include cycle).
// Users: 29.0.2, 29.1.1, 29.1.2, 29.2.1, 29.2.2, 29.15.2.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Pawn.hexpat"

// CDataS2CCharacterEquipInfo: PC list reader 0x7776e0, C2S writer 0x77d2d0 {MtString, u8, u8} (V);
// PS4 0x19fdbc0 {MtString m_wstrEquipItemUID, u8 m_ucEquipCategory, u8 m_ucEquipType}: same (V).
// Also the C2S element of 29.1.1/29.2.1: PS4 CDataC2SChangeCharacterEquipInfo (Write_ 0x1a37960),
// same members (V).
struct CDataS2CCharacterEquipInfo {
    MtString EquipItemUID;
    u8 EquipCategory;
    u8 EquipType;
};

// CDataPawnEquipInfo: PC list reader 0x7777e0 {u32, list 0x7776e0, list 0x766120} (V); PS4
// CDataS2CPawnEquipInfo 0x1a0ea50 {u32 m_unPawnID, m_CharacterEquipList, m_EquipJobItemList}: same (V).
struct CDataPawnEquipInfo {
    u32 PawnID;
    MtTypedArray<CDataS2CCharacterEquipInfo> CharacterEquipList;
    MtTypedArray<CDataEquipJobItem> EquipJobItemList;            // PC 0x766120 (Pawn.hexpat)
};

// CDataItemEquipElement: PC list reader 0x76aad0 {MtString, list 0x765a90} (V); PS4 0x19e4070
// {MtString m_wstrItemUID, list CDataEquipElementParam {u8, u32}}. Season 3 through the element:
// EquipElementParam (Context.hexpat) carries the Season 3 u16 (V).
struct CDataItemEquipElement {
    MtString ItemUID;
    MtTypedArray<EquipElementParam> EquipElementList;            // PC 0x765a90 {u8, u32, u16}
};

// CDataEquipChangeUnk (struct name I): the Season 3 tail read by PC 0x765f70 {Read_u8, list
// 0x766210 {u8, u16}} (V shape). 0x765f70 has 12 callers, among them 29.1.2, 29.2.2, 29.1.16, 29.4.2, 29.4.16,
// 29.5.2 and four group-7 readers (T012 1, 13); this is the one type for all of them. No PS4
// counterpart. Consumer 0x7d4760 compares the u8 with the current job (sGamePointer[3142]) and passes
// u8 and list to sub_B9E8C0 (I: a job id; captures 10). The list has the shape of CDataContextBase_unk_0
// (Context.hexpat). Server: CDataJobChangeJobResUnk0 {Unk0, List<CDataCharacterItemSlotInfo>} (lead).
struct CDataEquipChangeUnk {
    u8 Job;                                                      // Season 3; I: compared with the current job
    MtTypedArray<CDataContextBase_unk_0> unk_List;                       // PC 0x766210 {u8, u16}
};
