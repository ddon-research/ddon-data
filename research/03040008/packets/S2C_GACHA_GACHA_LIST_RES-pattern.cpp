// 39.0.2 S2C_GACHA_GACHA_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 16 (1, 19 for the types).
// PC handler 0x7d6cf0 (not a function in the database), reader 0x808bd0: header, list 0x768430
// (CDataGachaInfo) (V). PS4 OnPacket_S2C_GACHA_LIST_RES 0x32f1b0 m_GachaList: match V; Season 3
// through the settlement's ninth u32 (the PS4 settlement fails 26/26).
// Walk: 26/26 fit, slack 9; 5 gachas, up to 146 items per draw; settlement unk_u32 0 in 520/520.
// Body: s32 Error [, s32 Result, list CDataGachaInfo].
// packet-id: 39.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Gacha.hexpat"

struct S2C_GACHA_GACHA_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataGachaInfo> GachaList;   // PC 0x768430
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GACHA_GACHA_LIST_RES packet @ 0x00;
