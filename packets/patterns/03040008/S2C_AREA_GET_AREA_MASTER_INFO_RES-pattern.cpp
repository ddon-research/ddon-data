// 23.0.2 S2C_AREA_GET_AREA_MASTER_INFO_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 17. PC handler at
// 0x7c4180 (group-23 table key 2/0; pushes string 0x1bcd7d4 at 0x7c4208), ctor 0x785c90
// (0x17, 0, 2), reader 0x7ffcc0 (V). PS4 counterpart by code:
// CPacket_S2C_GET_AREA_MASTER_INFO_RES::ReadPacket 0x19da7a0, identical field for field.
// Body: s32 Error [, s32 Result, body] (P11a G1).
// packet-id: 23.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x77a9f0 {u32, u16}.
struct CDataSupplyItem {
    u32 ItemID;
    u16 ItemNum;
};

// PC list 0x75a860 {u32, list}.
struct CDataBorderSupplyItem {
    u32 MinAreaPoint;
    MtTypedArray<CDataSupplyItem> SupplyItemList;
};

// PC list 0x7593c0 {u32, u32}.
struct CDataAreaRankUpQuestInfo {
    u32 Rank;
    u32 QuestID;
};

struct S2C_AREA_GET_AREA_MASTER_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 AreaId;
        u32 Rank;
        u32 Point;
        u32 WeekPoint;
        u32 LastWeekPoint;
        u32 ToNextPoint;
        MtTypedArray<CDataCommonU32> ReleaseList;   // PC 0x75e8e0
        bool CanReciveSupply;
        bool CanRankUp;
        MtTypedArray<CDataBorderSupplyItem> SupplyItemInfoList;
        MtTypedArray<CDataAreaRankUpQuestInfo> AreaRankUpQuestInfoList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_AREA_GET_AREA_MASTER_INFO_RES packet @ 0x00;
