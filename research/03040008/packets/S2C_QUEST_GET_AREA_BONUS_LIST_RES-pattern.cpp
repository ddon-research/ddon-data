// 11.19.2 S2C_QUEST_GET_AREA_BONUS_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 9. PC handler 0x7f0960
// (string 0x1bc6adc), ctor 0x78b230 (11, 19, 2), reader 0x815b20 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_AREA_BONUS_LIST_RES 0x2ec110; its CDataAreaBonus has 4 u16, PC reads 5.
// Body: s32 Error [, s32 Result, list] (P11a G1).
// packet-id: 11.19.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// PC list 0x758f30, element 0x759010 {u32, u16 x5}.
struct CDataAreaBonus {
    u32 AreaId;
    u16 GoldRatio;
    u16 ExpRatio;
    u16 RimRatio;
    u16 AreaPointRatio;
    // T014b V (position: the Season 3 u16 is the fifth); name open: consumer 0xbd4e40 takes the
    // maximum of element +8/+10/+12/+14 (the four PS4 ratios, Gold/Exp/Rim/AreaPoint) and never
    // reads +16, so the new u16 is the last one, as the pattern places it; no reader of it found;
    // constant 100
    u16 unk_u16;               // Season 3; position I: PC reads 5 u16s, PS4 4 (R2 F5)
};

struct S2C_QUEST_GET_AREA_BONUS_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataAreaBonus> AreaBonusList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_AREA_BONUS_LIST_RES packet @ 0x00;
