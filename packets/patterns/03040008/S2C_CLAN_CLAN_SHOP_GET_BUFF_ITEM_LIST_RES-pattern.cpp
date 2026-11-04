// 31.34.2 S2C_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 20.
// PC handler 0x7cd8f0, reader 0x8046f0: list CDataClanShopBuffItem 0x75de20, u32, CDataClanShopInfo
// 0x75e2a0 (V). PS4 ReadPacket 0x19dc020 {m_BuffItemList, u32 m_unClanPoint, m_ShopInfo}: same (V).
// Walk: 25/25 fit, slack 12 (buff items up to 8, CurrentFunctionList up to 26).
// Body: s32 Error [, s32 Result, list CDataClanShopBuffItem, u32 ClanPoint, CDataClanShopInfo].
// packet-id: 31.34.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Clan.hexpat"

struct S2C_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataClanShopBuffItem> BuffItemList;     // PC 0x75de20
        u32 ClanPoint;
        CDataClanShopInfo ShopInfo;                            // PC 0x75e2a0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CLAN_CLAN_SHOP_GET_BUFF_ITEM_LIST_RES packet @ 0x00;
