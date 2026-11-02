// 30.0.2 S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 2 (1 and 16 for the types).
// PC handler 0x7d0b40 (string "...OnPacket_CRAFT_GET_CRAFT_PROGRESS_LIST_RES") -> reader 0x805b40:
// header, list 0x760b60 (CDataCraftProgress, Season 3), list 0x760960 (CDataCraftPawnList), list
// 0x75e8e0 {u32} (V). PS4 OnPacket_S2C_GET_CRAFT_PROGRESS_LIST_RES 0x313ec0 -> ReadPacket 0x19d8e80
// {m_CraftProgressList, m_CraftMyPawnList, m_CreatedReicpeList}: match V, Season 3 via the progress
// element (include/Craft.hexpat). Code-only element: the progress list is empty in every capture.
// Walk: 10/10 fit; pawn list 1, created recipes 3.
// Body: s32 Error [, s32 Result, list CDataCraftProgress, list CDataCraftPawnList, list u32].
// packet-id: 30.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Craft.hexpat"

struct S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCraftProgress> CraftProgressList;   // PC 0x760b60
        MtTypedArray<CDataCraftPawnList> CraftMyPawnList;     // PC 0x760960
        MtTypedArray<CDataCommonU32> CreatedReicpeList;       // PC 0x75e8e0; PS4 DWARF spelling (m_CreatedReicpeList)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CRAFT_GET_CRAFT_PROGRESS_LIST_RES packet @ 0x00;
