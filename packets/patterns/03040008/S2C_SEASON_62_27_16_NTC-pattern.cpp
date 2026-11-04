// 62.27.16 S2C_SEASON_62_27_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.27.16.
// PC handler 0x7f8a70 (no OnPacket_ string): Read_u32, then sGUIExt::requestAnnounce and sChat::addMessage
// of message 0x250 with the value as a parameter (V). Packet name: the CLI/server name (purpose open).
// PS4 counterpart: none (Season 3 group).
// Walk: 1/1 fit, slack 3.
// Body: u32.
// packet-id: 62.27.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_SEASON_62_27_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T005 open (role V: the handler passes it as a parameter of announce/chat message 0x250; text not
    // resolved), kept unk: 4 in 1/1; no server structure
    u32 unk_u32;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_62_27_16_NTC packet @ 0x00;
