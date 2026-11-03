// 28.23.2 S2C_GP_GP_SHOP_CAN_BUY_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 28.23.2.
// 006 T010 § 11. PC handler 0x7d84e0 cSeedGameSvConnection::OnPacket_GP_GP_SHOP_CAN_BUY_RES (V name),
// reader 0x809810: RES header, bool, u32 x4 (V). PS4 counterpart: none (V; the PS4 PAWN analogue's RES is
// {b8 m_bCanBuy, u32 m_unLineupId}).
// Walk: 9/9 fit, slack 14.
// Body: s32 Error [, s32 Result, bool, u32 x4].
// packet-id: 28.23.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_GP_SHOP_CAN_BUY_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 I (PS4 GP_SHOP_CAN_BUY_PAWN RES leads with b8 m_bCanBuy; packet name; 1 in 9/9)
        bool CanBuy;
        // T003 I (value: 9/9 equal the first u32 of the preceding 28.23.1 request; PS4 analogue's
        // m_unLineupId follows m_bCanBuy)
        u32 LineupId;
        // T003 open, kept unk: 9/9 equal the third u32 of the preceding 28.23.1 request (an echo)
        u32 unk_u32_2;
        u32 unk_u32_3;   // T003 open, kept unk: 0 in 9/9
        u32 unk_u32_4;   // T003 open, kept unk: 0 in 9/9
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GP_SHOP_CAN_BUY_RES packet @ 0x00;
