// 30.13.2 S2C_CRAFT_GET_CRAFT_SETTING_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 4 (1 and 16 for the types).
// PC handler 0x7d0bf0 (not a function, read linearly; string "...OnPacket_CRAFT_GET_CRAFT_SETTING_RES")
// -> 0x805be0: header, 0x760f20: list 0x75e8e0 {u32}, list 0x7611f0 (CDataCraftTimeSaveCost), u32,
// u32, u8, list 0x77abd0, u32, u32, list 0x760db0 (V). PS4 0x334070 -> 0x19df830
// {m_ColorRegulateItemList, m_TimeSaveCostList, m_unReasonableCraftLv, m_unCraftItemLv,
// m_ucCreateCountMax}: match V; Season 3 adds four fields (the PS4 body fails 2/2).
// Season 3 tail names are unk_ (server leads: RegisteredLegendPawnInfo list, Unk1, Unk2,
// RefiningMaterialInfo list). Walk: 2/2 fit; ColorRegulateItemList 993 entries, 2 pawn records,
// unk_u32_0 49, unk_u32_1 30, 7 tail elements.
// Body: s32 Error [, s32 Result, list u32, list CDataCraftTimeSaveCost, u32, u32, u8, Season 3 tail].
// packet-id: 30.13.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Craft.hexpat"

struct S2C_CRAFT_GET_CRAFT_SETTING_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCommonU32> ColorRegulateItemList;          // PC 0x75e8e0
        MtTypedArray<CDataCraftTimeSaveCost> TimeSaveCostList;        // PC 0x7611f0
        u32 ReasonableCraftLv;
        u32 CraftItemLv;
        u8 CreateCountMax;
        MtTypedArray<CDataCraftSettingUnkPawn> unk_PawnList;          // Season 3, PC 0x77abd0
        // T014b open (no reader), kept unk: packet +100: none of the 22 callers of the getter
        // 0x86a2c0 nor the undefined caller 0x53243f reads +100; the handler 0x7d0bf0 only passes
        // +80 (pawn list) to 0x87f610
        u32 unk_u32_0;                                                // Season 3
        // T014b open (no reader), kept unk: packet +104: no reader among the getter 0x86a2c0
        // callers or the handler
        u32 unk_u32_1;                                                // Season 3
        MtTypedArray<CDataCraftSettingUnkElement> unk_List;           // Season 3, PC 0x760db0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CRAFT_GET_CRAFT_SETTING_RES packet @ 0x00;
