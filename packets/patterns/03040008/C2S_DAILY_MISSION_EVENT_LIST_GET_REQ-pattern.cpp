// 72.3.1 C2S_DAILY_MISSION_EVENT_LIST_GET_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 72.3.1.
// PC writer 0x825fe0 cSeedGameSvConnection::Send_C2S_DAILY_MISSION_EVENT_LIST_GET_REQ (V name):
// WritePacket(0x48, 3, 1), Write_u8 (V; 008 T001). No server structure. PS4 counterpart: none.
// Walk: 4/4 fit, slack 6.
// Body: u8.
// packet-id: 72.3.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_DAILY_MISSION_EVENT_LIST_GET_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u8 unk_u8;      // T004 open, kept unk: captured 7 in 4/4; the 72.3.2 response repeats it (4/4)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_DAILY_MISSION_EVENT_LIST_GET_REQ packet @ 0x00;
