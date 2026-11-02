// 10.0.16 S2C_ITEM_USE_BAG_ITEM_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.2.
// Code name: USE_BAG_ITEM_NOTICE (V by behaviour).
// PC handler 0x7de3b0, reader 0x80cd10: u32 x3, no error header (V); the handler only stores the
// three values into the network manager at +0x8dd4/+0x8dd8/+0x8ddc. PS4
// OnPacket_S2C_USE_BAG_ITEM_NOTICE 0x2e9280 stores them the same way (mUsedItemCharacterId,
// mUsedItemId, mUsedItemNum); members u32 m_unCharacterID, m_unItemID, m_unItemNum. The PS4 u16
// framing also fits (2 bytes inside the slack): the framing rests on the PC reader. Walk: 18/18 fit,
// slack 11.
// Body: u32 CharacterID, u32 ItemID, u32 ItemNum (12 bytes).
// packet-id: 10.0.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_ITEM_USE_BAG_ITEM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterID;
    u32 ItemID;
    u32 ItemNum;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_USE_BAG_ITEM_NTC packet @ 0x00;
