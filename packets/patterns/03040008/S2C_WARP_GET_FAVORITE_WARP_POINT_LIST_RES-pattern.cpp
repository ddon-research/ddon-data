// 14.4.2 S2C_WARP_GET_FAVORITE_WARP_POINT_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 2.4.
// PC handler 0x7feb30, reader 0x81d750: RES header, list 0x766af0 (CDataFavoriteWarpPoint, read
// linearly), u32 (V). PS4 OnPacket_S2C_GET_FAVORITE_WARP_POINT_LIST_RES 0x2f72d0:
// m_FavoriteWarpPointList, u32 m_unSlotIDMax (V). Walk: 104/104 fit, slack 3-15.
// Body: s32 Error [, s32 Result, list CDataFavoriteWarpPoint, u32 SlotIDMax] (16 + 12n bytes).
// packet-id: 14.4.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Warp.hexpat"

struct S2C_WARP_GET_FAVORITE_WARP_POINT_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataFavoriteWarpPoint> FavoriteWarpPointList;   // PC 0x766af0
        u32 SlotIDMax;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_WARP_GET_FAVORITE_WARP_POINT_LIST_RES packet @ 0x00;
