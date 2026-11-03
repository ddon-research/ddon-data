// 63.5.16 C2S_CHAIN_DUNGEON_END_CHAIN_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 63.5.16.
// PC sender 0x826330 cSeedGameSvConnection::Send_S2C_63_5_16_NTC: WritePacket(63, 5, 16), no body writes
// (V). Name: the CLI name (upstream Arrowgene, G (lead)); the PC symbol keeps the S2C_63_5_16 spelling.
// PS4 counterpart: none (Season 3 group).
// Walk: 1/1 fit, slack 7.
// Body: none.
// packet-id: 63.5.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CHAIN_DUNGEON_END_CHAIN_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CHAIN_DUNGEON_END_CHAIN_NTC packet @ 0x00;
