// 53.8.1 C2S_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 3.3.
// PC writer 0x831610 (53, 8, 1): list writer 0x77fd30 {Write_MtString, Write_u32} (V). PS4
// Send_C2S_PRESENT_FOR_PARTNER_PAWN_REQ 0x19ce290: MtTypedArray<CDataItemUIDList> m_ItemUIDList (V).
// Walk: 20/20 fit, slack 5.
// Body: list CDataItemUIDList (Quest.hexpat, same PC writer).
// packet-id: 53.8.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct C2S_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataItemUIDList> ItemUIDList;            // PC 0x77fd30
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PARTNER_PAWN_PRESENT_FOR_PARTNER_PAWN_REQ packet @ 0x00;
