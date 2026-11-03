// 28.23.1 C2S_GP_GP_SHOP_CAN_BUY_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 28.23.1.
// 006 T010 § 11. PC writer 0x829df0 cSeedGameSvConnection::Send_C2S_GP_GP_SHOP_CAN_BUY_REQ (V name):
// WritePacket(28, 23, 1), Write_u32 x3 (V). PS4 counterpart: none (V; PS4 has only GP_SHOP_CAN_BUY_PAWN and
// _PAWN_VOICE).
// Walk: 9/9 fit, slack 11.
// Body: u32, u32, u32.
// packet-id: 28.23.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_GP_GP_SHOP_CAN_BUY_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T003 I (value: 9/9 echoed as the second u32 of the 28.23.2 response; values 23-463; PS4
    // GP_SHOP_CAN_BUY_PAWN carries u32 m_unLineupId); no lead
    u32 LineupId;
    // T003 open, kept unk: values 2 x4, 3, 7, 9, 19, 21; no lead
    u32 unk_u32_1;
    // T003 open, kept unk: echoed 9/9 as the response's third u32; values 1, 3, 5, 7-10 (the value set
    // of the 28.9.1 second u32); no lead
    u32 unk_u32_2;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_GP_GP_SHOP_CAN_BUY_REQ packet @ 0x00;
