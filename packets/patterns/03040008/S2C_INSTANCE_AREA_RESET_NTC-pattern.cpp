// 13.42.16 S2C_INSTANCE_AREA_RESET_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 18 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dbe00 reads nothing (V): it sets the connection's reset flag and calls the quest
// manager. Settled V by behaviour as PS4 S2C_INSTANCE_AREA_RESET_NTC (OnPacket 0x30a350 ->
// sQuestManagerExt::callbackInstanceAreaReset); DWARF {u16 m_usError}, PS4 NTC framing only.
// Walk: 120/120 fit, slack 7 (a 16-byte raw fits any body of 0-7 bytes, so the emptiness rests
// on the handler).
// Body: none.
// packet-id: 13.42.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_INSTANCE_AREA_RESET_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_AREA_RESET_NTC packet @ 0x00;
