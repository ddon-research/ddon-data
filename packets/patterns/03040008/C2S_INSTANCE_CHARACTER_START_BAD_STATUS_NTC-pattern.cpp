// 13.44.16 C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC (client 03040008).
// Body: one u32, the OCD (status) uid. P4 4, P5 7, T001c 3 (PC writer 0x82c2b0, sender 0x604ee0
// from 0x96d610). Status start: sent from cOcdBase::init (PC 0x8a2670 = PS4 0x399c40, matched by
// code) for the master player character (isMaster && mIsPlayer, 0x41dbd0), when the uid satisfies
// (uid & 0xF000) == 0x1000 (V). This corrects P5 7 ("non-player character", C). The client name is
// unresolved (no PC string, no PS4 sender); the raw-file name is the server's.
// packet-id: 13.44.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 m_unOcdUID;  // PS4 cOcdBase::mOcdUID (PC this+288; T001c 3, V)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_CHARACTER_START_BAD_STATUS_NTC packet @ 0x00;
