// 29.23.16 S2C_EQUIP_29_23_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 29.23.16.
// PC handler 0x7d5730 is `mov eax, 1; retn 4`: the client ignores the body (V; spec 006 T012 § 15). No
// PC reader exists, so the layout is the capture shape only (G (capture shape)); no server structure.
// Walk: 2/2 fit, slack 7 (two identical bodies, stream85 tcp-stream-11).
// Body: u32, count, 18-byte elements (8 + 18n).
// packet-id: 29.23.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Capture-shape element (G (capture shape); no PC reader, the handler ignores the body). Struct name
// neutral.
struct CDataEquip_29_23_16_unk {
    u32 unk_u32_0;      // T005 G (capture shape): 0, then three PawnIds of the stream (I, 006 T012 § 15)
    u32 unk_u32_1;      // T005 G (capture shape): 2 in 8/8
    u32 unk_u32_2;      // T005 G (capture shape): 0 in 8/8
    u8 unk_u8_0;        // T005 G (capture shape): 1 in 8/8
    u32 unk_u32_3;      // T005 G (capture shape): 0 in 8/8
    u8 unk_u8_1;        // T005 G (capture shape): 2 in 8/8
};

struct S2C_EQUIP_29_23_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T005 G (capture shape), kept unk: 2184603 in 2/2, a CharacterId elsewhere in the stream (I, 006 T012 § 15)
    u32 unk_u32;
    MtTypedArray<CDataEquip_29_23_16_unk> unk_list;   // T005 G (capture shape): count 4 in 2/2
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_EQUIP_29_23_16_NTC packet @ 0x00;
