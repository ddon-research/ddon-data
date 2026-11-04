// 14.11.16 C2S_WARP_14_11_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 14.11.16.
// 006 T008 § 2.8. PC writer 0x840080: WritePacket(14, 11, 0x10), Write_u32 (V); caller 0x885a90 <-
// 0xb61ab0, an sGame setter that sends only when the value changes (sGame[0x3994]) (V). PS4 counterpart:
// none (I by absence). Name: the raw name (TC2 renamed it from C2S_WARP_WARP_END_NTC, which belongs to
// 14.10.16).
// Walk: 57/57 fit, slack 3.
// Body: u32.
// packet-id: 14.11.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_WARP_14_11_16_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T003 G (value: 51/57 values are in the 14.14.2 StartPointIdList of the same capture (1 x48 and
    // 87 x3); 20, 21, 72, 97 are not, and 1 dominates, so a coincidence is not ruled out); no lead
    u32 StartPointId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_WARP_14_11_16_NTC packet @ 0x00;
