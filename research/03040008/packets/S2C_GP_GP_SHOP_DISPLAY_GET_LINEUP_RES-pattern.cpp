// 28.8.2 S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 7.
// PC handler 0x7d8650, reader 0x809980: list CDataGPShopDisplayLineup (list 0x767b20, element
// 0x767be0; Season 3 element, include/GP.hexpat) (V). PS4 0x30b000 reads m_Items (12-field
// element); the PS4 element fails 38/38 captures.
// Walk: 38/38 fit (lists up to 24).
// Body: s32 Error [, s32 Result, list CDataGPShopDisplayLineup].
// packet-id: 28.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "GP.hexpat"

struct S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataGPShopDisplayLineup> Items;   // PC 0x767b20
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GP_SHOP_DISPLAY_GET_LINEUP_RES packet @ 0x00;
