// 51.2.2 S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 10 (1 and 16 for the types).
// PC handler 0x7d24b0 (string "...DISPEL_GET_DISPEL_ITEM_SETTING_RES" at 0x7d2587) -> 0x8068b0: header,
// list 0x763390 {u32, MtString}, bool (V). PS4 0x337ac0: header, m_DispelCategoryInfo
// (CDataDispelCategoryInfo {u8, MtString}): match V; Season 3 widens Category to u32 and adds a bool
// (the PS4 body fails 1/1). Walk: 1/1 fit; 5 categories (152-156).
// Body: s32 Error [, s32 Result, list CDataDispelCategoryInfo, bool].
// packet-id: 51.2.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Dispel.hexpat"

struct S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataDispelCategoryInfo> DispelCategoryInfo;   // PC 0x763390
        bool unk_bool;   // Season 3, 0 in the capture; server: Unk1 (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_DISPEL_GET_DISPEL_ITEM_SETTING_RES packet @ 0x00;
