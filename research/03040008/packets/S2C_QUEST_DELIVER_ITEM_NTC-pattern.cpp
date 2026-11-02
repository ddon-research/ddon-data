// 11.69.16 S2C_QUEST_DELIVER_ITEM_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 29 (section 44 for the shared types in include/Quest.hexpat).
// PC handler 0x7f0260, reader 0x8156c0: no header, u32, u32, u16, list 0x762d80 {u32, u16, u16}
// (V). PS4 0x312de0 {u16 m_usError, CDeliveredItemRecord} (V). Walk: 1/1 fit, slack 1; PS4
// framing 0/1.
// Body: CDataDeliveredItemRecord DeliveredItemRecord (14 + 8n bytes).
// packet-id: 11.69.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_DELIVER_ITEM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataDeliveredItemRecord DeliveredItemRecord;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_DELIVER_ITEM_NTC packet @ 0x00;
