// 13.6.2 S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 6 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7db750, reader 0x80b480: RES header, LayoutId, u32, MtString, bool, bool, list
// 0x773060, list 0x769100 (V). PS4 CPacket_S2C_GET_GATHERING_ITEM_LIST_RES::ReadPacket 0x19d7330
// {m_LayoutId, u32 m_unPosId, MtString m_wstrGatheringItemUID, b8 m_bIsGatheringItemBreak,
// MtTypedArray<CDataGatheringItemElement> m_ItemList} (V). Season 3 (V widths): a second bool,
// the restriction list, and the 17-byte item element (include/Instance.hexpat). Walk: 155/155
// fit, slack 3-14; the PS4 layout fits 66/155; the restriction list is never non-empty
// (code-only).
// Body: s32 Error [, s32 Result, LayoutId, u32 PosId, MtString GatheringItemUID, bool
// IsGatheringItemBreak, bool unk_bool, MtTypedArray<GatheringItemListRes_unk_0>
// unk_List, MtTypedArray<CDataGatheringItemElement> ItemList].
// packet-id: 13.6.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataStageLayoutId LayoutId;
        u32 PosId;
        MtString GatheringItemUID;
        bool IsGatheringItemBreak;   // PS4 member; that it is the first of the two bools is I (position)
        bool unk_bool;               // Season 3, no PS4 member (PC reader 0x80b480, V width); server: Unk0 (lead)
        MtTypedArray<GatheringItemListRes_unk_0> unk_List;  // Season 3 (V width); server: RestrictionList (lead); never non-empty in captures
        MtTypedArray<CDataGatheringItemElement> ItemList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_GET_GATHERING_ITEM_LIST_RES packet @ 0x00;
