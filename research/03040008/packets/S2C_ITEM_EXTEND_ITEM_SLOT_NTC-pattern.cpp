// 10.10.16 S2C_ITEM_EXTEND_ITEM_SLOT_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.7.
// Code name: EXTEND_ITEM_SLOT_NTC (V by behaviour and unique shape).
// PC handler 0x7dcad0, reader 0x80c1a0: u8, u16, u16, no error header (V). PS4
// OnPacket_S2C_EXTEND_ITEM_SLOT_NTC 0x305830 is the only PS4 notice reading u16 + u8, u16, u16, and
// both handlers look the storage up by the u8, store the second u16 and announce a GUI message
// (PC 0x1BA, PS4 0x1BC); members u8 m_ucCategory, u16 m_usAddNum, u16 m_usTotalNum. The PS4 u16
// framing also fits: the framing rests on the PC reader. Walk: 43/43 fit, slack 2.
// Body: u8 Category, u16 AddNum, u16 TotalNum (5 bytes).
// packet-id: 10.10.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_ITEM_EXTEND_ITEM_SLOT_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u8 Category;
    u16 AddNum;
    u16 TotalNum;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_EXTEND_ITEM_SLOT_NTC packet @ 0x00;
