// 20.1.1 C2S_SHOP_BUY_SHOP_GOODS_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 5.
// PC writer 0x842670 (20, 1, 1): u32, u32, u8, u32 (V). PS4 CPacket_C2S_BUY_SHOP_GOODS_REQ::WritePacket
// 0x1a34e30 {u32 m_unGoodsIndex, u32 m_unNum, u8 m_ucStorageType, u32 m_unPrice}: same (V); the
// recompilation's C2S.cpp has the signature only (DDON_STUB).
// Walk: 17/17 fit, slack 10; StorageType 19 always; Price = unit Price of goods GoodsIndex x Num (17/17).
// Body: u32 GoodsIndex, u32 Num, u8 StorageType, u32 Price (13 bytes).
// packet-id: 20.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_SHOP_BUY_SHOP_GOODS_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 GoodsIndex;
    u32 Num;
    u8 StorageType;
    u32 Price;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_SHOP_BUY_SHOP_GOODS_REQ packet @ 0x00;
