// 52.1.2 S2C_MY_ROOM_FURNITURE_LIST_GET_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 10. PC handler 0x7e5a90
// (string 0x1bd2478), ctor 0x78a3d0 (52, 1, 2), reader 0x80fa00 (V). PS4 counterpart by code:
// OnPacket_S2C_FURNITURE_LIST_GET_RES 0x334ba0 / ReadPacket 0x19df920; its CDataMyRoomOption is
// {list, u32}, PC reads one more u32.
// Body: s32 Error [, s32 Result, body] (P11a G1).
// packet-id: 52.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x766f90 {u32, u32, u8}.
struct CDataFurnitureLayout {
    u32 ItemID;
    u32 unOmID;
    u8 LayoutID;
};

// PC 0x76f300: list CDataCommonU32 (0x75e8e0), u32, u32.
struct CDataMyRoomOption {
    MtTypedArray<CDataCommonU32> BgmAcquirementNoList;
    u32 BgmAcquirementNo;
    u32 unk_u32;               // Season 3
};

struct S2C_MY_ROOM_FURNITURE_LIST_GET_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataFurnitureLayout> FurnitureList;
        CDataMyRoomOption MyRoomOption;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_MY_ROOM_FURNITURE_LIST_GET_RES packet @ 0x00;
