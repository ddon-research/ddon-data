// 28.24.16 S2C_GP_28_24_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 28.24.16.
// 006 T010 § 12. PC handler 0x7d6fd0 (no name string) reads one u32 inline (no RES header, no reader
// object) and passes it to 0xb86860 (store at +0x34c of the object at n3_0 + 0x4ad0; reset to 0 by
// 0x419ee0) (V). No notice class, no name: the raw name stays. PS4 counterpart: none found (I).
// Walk: 84/84 fit, slack 3.
// Body: u32.
// packet-id: 28.24.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_28_24_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T003 open, kept unk: values 3 (83 files), 4 (1); stored by 0xb86860 (role not traced); no lead
    u32 unk_u32;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_28_24_16_NTC packet @ 0x00;
