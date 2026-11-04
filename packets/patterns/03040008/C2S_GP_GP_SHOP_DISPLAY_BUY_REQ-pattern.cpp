// 28.9.1 C2S_GP_GP_SHOP_DISPLAY_BUY_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 8.
// PC writer 0x829f00 (not a function in the PC database, decoded linearly): WritePacket(28, 9, 1),
// Write_u32, Write_u32 (V). PS4 Send_C2S_GP_SHOP_DISPLAY_BUY_REQ 0x19bd170(u32 in_DisplayLineupId)
// writes one u32: Season 3 adds a u32. DisplayLineupId on the first is I (position); the second
// takes the values 1, 3, 5, 7-10 (the value set of the 28.23.1 third u32). The PS4 body fails 9/9.
// Walk: 9/9 fit, slack 15.
// Body: u32 DisplayLineupId (I), u32 unk_u32 (8 bytes).
// packet-id: 28.9.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_GP_GP_SHOP_DISPLAY_BUY_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 DisplayLineupId;        // I: position (PS4 writes only this u32)
    // T014b open (no caller found), kept unk: writer 0x829f00 is not a function and has no code
    // xref, so the caller that supplies the u32 was not found
    u32 unk_u32;                // Season 3
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_GP_GP_SHOP_DISPLAY_BUY_REQ packet @ 0x00;
