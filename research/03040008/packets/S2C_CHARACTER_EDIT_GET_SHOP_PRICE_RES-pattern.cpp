// 41.8.2 S2C_CHARACTER_EDIT_GET_SHOP_PRICE_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 41.8.2.
// PC handler 0x7c81e0 cSeedGameSvConnection::OnPacket_CHARACTER_EDIT_GET_SHOP_PRICE_RES (V name), reader
// 0x802130: RES header, list 0x764d70 {u8, list 0x77c5a0 CDataWalletPoint} (V).
// PS4 counterpart: none matched (spec 006 T013 § 9).
// Walk: 4/4 fit, slack 2; UpdateType 1 -> (5, 5), (4, 200); UpdateType 2 -> (5, 20).
// Body: s32 Error [, s32 Result, list CDataCharacterEditPriceInfo].
// packet-id: 41.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"

// Element of PC list reader 0x764d70 {u8 +4, list 0x77c5a0 +8} (V). Struct name: server (lead).
struct CDataCharacterEditPriceInfo {
    u8 UpdateType;      // T005 G (lead): server UpdateType; 1, 2
    // T005 V (same reader 0x77c5a0: Character.hexpat CDataWalletPoint); name G (lead: server Prices)
    MtTypedArray<CDataWalletPoint> PriceList;
};

struct S2C_CHARACTER_EDIT_GET_SHOP_PRICE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCharacterEditPriceInfo> PriceInfoList;   // PC 0x764d70; T005 G (lead: server PriceInfo)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CHARACTER_EDIT_GET_SHOP_PRICE_RES packet @ 0x00;
