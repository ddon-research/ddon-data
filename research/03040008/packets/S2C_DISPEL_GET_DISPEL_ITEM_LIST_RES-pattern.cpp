// 51.0.2 S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 6. PC handler code
// 0x7d23ec-0x7d2471 (not a defined function; string 0x1bd1ff0 pushed at 0x7d248c), inline ctor
// 0x7d2402 (0x33, 0, 2), reader 0x806830 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_DISPEL_ITEM_LIST_RES 0x333820 (CDataDispelBaseItem, LotItem, LotCrest in DWARF).
// Body: s32 Error [, s32 Result, list] (P11a G1). The CrestLot lists are empty in the one capture,
// so CDataDispelLotCrest rests on the PC code only.
// packet-id: 51.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

// PC list 0x7632a0 {u32, u32}; PS4 {u32 ItemID, u8 Num}: the second field is u32 on PC.
struct CDataDispelBaseItemData {
    u32 ItemID;
    u32 Num;
};

// PC list 0x763b30 {u16, u8} (V), Season 3.
struct CDataDispelLotCrestUnk {
    u16 unk_u16;
    u8 unk_u8;
};

// CrestLot element, PC 0x7639e0 {u32, u8, u8, u8, list {u16, u8}} (V); PS4 LotCrest {u32, u8}.
struct CDataDispelLotCrest {
    u32 CrestItemId;
    u8 CrestItemRate;
    u8 unk_u8_0;
    u8 unk_u8_1;
    MtTypedArray<CDataDispelLotCrestUnk> unk_list;
};

// PC list 0x7638f0 {u8, u8}.
struct CDataDispelLotColor {
    u8 Color;
    u8 ColorRate;
};

// PC list 0x763dc0 {u8, u8}.
struct CDataDispelLotPlus {
    u8 Plus;
    u8 PlusRate;
};

// ItemLot, PC 0x763d40 {u32, u8, u8, u16, bool, u8} (V); PS4 LotItem {u32, u8, u8, u32 ItemNum}.
struct CDataDispelLotItem {
    u32 ItemId;
    u8 ItemRate;
    u8 CrestNum;
    u16 ItemNum;
    bool unk_bool;
    u8 unk_u8;
};

// PC list 0x763c20.
struct CDataDispelLotData {
    u32 Id;
    CDataDispelLotItem ItemLot;
    MtTypedArray<CDataDispelLotCrest> CrestLot;
    MtTypedArray<CDataDispelLotColor> ColorLot;
    MtTypedArray<CDataDispelLotPlus> PlusLot;
};

// PC list 0x7630d0, element 0x763190 (V). PS4 CDataDispelBaseItem has no u32 after Id and ends with
// u8 m_ucCategory where PC reads u32, u16, u16.
struct CDataDispelBaseItem {
    u32 Id;
    u32 unk_u32;
    s64 Begin;
    s64 End;
    MtTypedArray<CDataDispelBaseItemData> BaseItemId;
    MtTypedArray<CDataWalletPoint> Cost;                     // PC 0x77c5a0
    bool IsHide;
    MtTypedArray<CDataDispelLotData> LotItemList;
    u32 SortId;
    MtString Label;
    u32 Category;              // name I (PS4 u8 m_ucCategory here)
    u16 unk_u16_0;
    u16 unk_u16_1;
};

struct S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataDispelBaseItem> DispelBaseItemList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_DISPEL_GET_DISPEL_ITEM_LIST_RES packet @ 0x00;
