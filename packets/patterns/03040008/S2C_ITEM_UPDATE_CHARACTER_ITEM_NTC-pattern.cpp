// 10.12.16 S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 3.8 (1.1, 1.2 for the types).
// PC handler 0x7ddd80, reader 0x80cb90: u16, list 0x76aec0 (CDataItemUpdateResult), list 0x77c1c0
// (CDataUpdateWalletPoint), no error header (V). PS4 OnPacket_S2C_UPDATE_CHARACTER_ITEM_NOTICE
// 0x315b80 (unique shape): u16 m_usUpdateType, m_UpdateItemList, CWallet m_UpdateWallet (V; the
// PS4 CDataItemList element fails 245/390, the PS4 framing 388/390). Walk: 390/390 fit, slack 0-14,
// up to 16 items and 2 wallet entries.
// Body: u16 UpdateType, list CDataItemUpdateResult, list CDataUpdateWalletPoint (variable).
// packet-id: 10.12.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u16 UpdateType;
    MtTypedArray<CDataItemUpdateResult> UpdateItemList;    // PC 0x76aec0
    MtTypedArray<CDataUpdateWalletPoint> UpdateWallet;     // PC 0x77c1c0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_UPDATE_CHARACTER_ITEM_NTC packet @ 0x00;
