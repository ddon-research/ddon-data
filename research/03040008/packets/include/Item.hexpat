// Item CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11b-old-patterns.md
// section 13 and the shared-structure table (the two storage types), and since T008b
// specs/006-packet-pattern-coverage/research/T008-warp-item.md sections 1 and 6 (the group 10 and
// 50 types). "PC 0x..." is the reader VA in the PC 03040008 database (image base 0x400000); "PS4"
// names the PS4 02020005 DWARF type, whose member names the fields carry (m_ and type prefix
// dropped) unless marked. Marks: V = read in IDA, I = inferred. A Season 3 field without a PS4
// member is `unk_*`; server C# (Arrowgene) names are leads only ("server: <name> (lead)").
// Includes Packet.hexpat, Character.hexpat (CDataWalletPoint) and Context.hexpat (EquipElementParam,
// CDataContextEquipData_unk_0, CDataContextBase_unk_0); none of them includes this file (no include cycle).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Context.hexpat"

// CDataGameItemStorage: PS4 CDataGameItemStorage {u8 m_ucStorageType}; read inline by PC 0x7688e0.
struct CDataGameItemStorage {
    u8 StorageType;
};

// CDataGameItemStorageInfo: PC list reader 0x7688e0 (mid-function) {u8, u16, u16} (P11b 13, V);
// PS4 CDataGameItemStorageInfo {CDataGameItemStorage, u16 m_usUsedSlotNum, u16 m_usMaxSlotNum}.
struct CDataGameItemStorageInfo {
    CDataGameItemStorage GameItemStorage;
    u16 UsedSlotNum;
    u16 MaxSlotNum;
};

// CDataItemList (Season 3): PC element reader 0x76aca0, list 0x76abe0 (T008 1.1, V widths and
// order). PS4 Read_CDataItemList__0 0x19fe070 reads {u8 m_ucStorageType, u16 m_usSlotNo, MtString
// m_wstrUID, u32 m_unItemID, u32 m_unItemNum, u32 m_unEquipCharacterID, u32 m_unEquipPawnID, u32
// m_unEquipPoint, u8 m_ucColor, list CDataEquipElementParam {u8, u32}, u8 m_ucPlusValue, b8
// m_bBind}: Season 3 reorders the whole element and adds a u8, a u16 per element-param entry and
// two lists, so no PS4 name carries over by position. ItemUId is V by type (the only string); the
// other names are I with the basis given. The PS4 element fails 130/136 (10.3.2), 3/3 (10.6.2) and
// 245/390 (10.12.16) captures; every PS4 fit has an empty list (T008 1.1).
struct CDataItemList {
    MtString ItemUId;            // PS4 m_wstrUID (V by type)
    u32 ItemId;                  // I: PS4 m_unItemID, first of the u32 run
    u32 ItemNum;                 // I: PS4 m_unItemNum, second of the u32 run
    // T014b open, kept unk: PC 0x880cf0 copies +16 to item +16; addItemNotice 0xb941e0 does not
    // read it; no PS4 member
    u8 unk_u8;                   // Season 3, new (server: SafetySetting, lead)
    u8 StorageType;              // I: capture values 1-6, 13, 14 are storage types
    u16 SlotNo;                  // I: PS4 m_usSlotNo is the only u16 member
    u8 Color;                    // I: PS4 m_ucColor, u8 pair before the bool
    u8 PlusValue;                // I: PS4 m_ucPlusValue
    bool Bind;                   // I: PS4 b8 m_bBind, the only bool
    // T014b I (consumer; lead agrees): PC 0xb941e0 reads item+24 where PS4 0x7cee20 reads
    // m_unEquipPoint and stores it (u16, sub-object +76); the other two u32 are V, so EquipPoint by
    // elimination; server lead EquipPoint agrees
    u32 EquipPoint;               // PS4 has three u32 here (m_unEquipCharacterID, m_unEquipPawnID,
    // T014b V: PC 0xb941e0: item+28 != 0 -> equip owner = it, owner type 1; PS4 0x7cee20 the same
    // with m_unEquipCharacterID
    u32 EquipCharacterId;               // m_unEquipPoint); which is which has no code basis. server:
    // T014b V: PC 0xb941e0: else item+32 -> owner, owner type 2; PS4 0x7cee20: else
    // m_unEquipPawnID, mEquipCharType = 2*(id != 0)
    u32 EquipPawnId;               // EquipPoint, EquipCharacterID, EquipPawnID in this order (lead)
    MtTypedArray<EquipElementParam> unk_ElementList;     // PC 0x765a90 {u8, u32, u16} (Season 3 u16)
    MtTypedArray<CDataContextEquipData_unk_0> unk_List_0;   // PC 0x765ba0, Season 3
    MtTypedArray<CDataContextBase_unk_0> unk_List_1;        // PC 0x766210, shape {u8, u16}, Season 3
};

// CDataItemUpdateResult: PC list 0x76aec0 element {CDataItemList, s32} (V); PS4 {CItemList
// m_ItemInfo, s32 m_nUpdateItemNum} (V).
struct CDataItemUpdateResult {
    CDataItemList ItemInfo;
    s32 UpdateItemNum;
};

// CDataUpdateWalletPoint: PC list 0x77c1c0 element {u8, u32, s32, u32} (V; the first two read
// inline, the shape of Character.hexpat's CDataWalletPoint); PS4 {CWalletPoint m_PointParam {u8
// m_ucType, u32 m_unValue}, s32 m_nAddPoint, u32 m_unExtraBonusPoint} (same, V).
struct CDataUpdateWalletPoint {
    CDataWalletPoint PointParam;
    s32 AddPoint;
    u32 ExtraBonusPoint;
};

// CDataSwitchStorage (Season 3 width): PC list 0x75c570 element {u8, u16} (V); PS4 {u8
// m_ucTargetStorageType, u8 m_ucChangeStorageType}. Season 3 widens the second field to u16 (V
// width; name I by position). The PS4 u8 element fits the 2 captures too (the byte is inside the
// slack): the width rests on the PC reader. The same PC list reader serves Server.hexpat's
// CDataCharacterItemSlotInfo {u8, u16}.
struct CDataSwitchStorage {
    u8 TargetStorageType;
    u16 ChangeStorageType;       // I (server: Num, lead)
};

// CDataMoveItemUIDFromTo: PC writer 0x780090 element {MtString, u32, u8, u8, u16} (V); PS4
// {m_wstrUID, u32 m_unNum, u8 m_ucSrcStorageType, u8 m_ucDstStorageType, u16 m_usSlotNo} (same, V).
struct CDataMoveItemUIDFromTo {
    MtString UID;
    u32 Num;
    u8 SrcStorageType;
    u8 DstStorageType;
    u16 SlotNo;
};

// CDataItemSort: PC list 0x75e6e0 element (read linearly) {u8, u8[0x400]} (V); PS4 {u8
// m_ucStorageType, u8 m_ucBin[1024]} (same, V). The bin is fixed-size: no count on the wire.
struct CDataItemSort {
    u8 StorageType;
    u8 Bin[1024];
};
