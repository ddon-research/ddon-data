// 20.0.2 S2C_SHOP_GET_SHOP_GOODS_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 6 (1, 19 for the types).
// PC handler 0x7fa010, reader 0x81adc0: header, then 0x778710: u32, u8, u8, list 0x769330 (goods,
// element 0x769450 with requirement list 0x778770) (V widths and order). PS4
// OnPacket_S2C_GET_SHOP_GOODS_LIST_RES 0x301ac0: header + m_GoodsParamList of CDataGoodsParam {u32 x6}
// (match V by symbol pair and string). Season 3 body: the PS4 body fails 18/18. No field consumer
// traced: names I (basis stated) or unk_ (include/Shop.hexpat).
// Walk: 18/18 fit, slack 5-9; up to 44 goods, requirement lists 0 or 1 entries.
// Body: s32 Error [, s32 Result, u32 ShopID (I), u8, u8, list CDataGoodsParam (Season 3)].
// packet-id: 20.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Shop.hexpat"

struct S2C_SHOP_GET_SHOP_GOODS_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 ShopID;         // I: echoes the 20.0.1 ShopID in 18/18 pairs
        u8 unk_u8_0;        // always 0
        u8 unk_u8_1;        // 11 (17), 10 (1); 11 is the 20.1.2 PointType value; server: WalletType (lead)
        MtTypedArray<CDataGoodsParam> GoodsParamList;   // PC 0x769330 (Season 3 element)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SHOP_GET_SHOP_GOODS_LIST_RES packet @ 0x00;
