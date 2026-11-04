// 54.0.2 S2C_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 14 (1 and 16 for the types).
// PC handler 0x7d0eb0 (string "...OnPacket_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES") -> 0x805db0: header,
// u8, list 0x76e000 (CDataMDataCraftRecipe, Season 3 material), bool (V). PS4 0x336480 -> 0x19dfb30
// {u8 m_ucCategory, m_RecipeList, b8 m_bIsEnd}: match V; Season 3 adds a bool per material (the PS4
// material fails 3/3). Walk: 3/3 fit; up to 79 recipes.
// Body: s32 Error [, s32 Result, u8 Category, list CDataMDataCraftRecipe, bool IsEnd].
// packet-id: 54.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Craft.hexpat"

struct S2C_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 Category;
        MtTypedArray<CDataMDataCraftRecipe> RecipeList;   // PC 0x76e000
        bool IsEnd;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CRAFT_RECIPE_GET_CRAFT_RECIPE_RES packet @ 0x00;
