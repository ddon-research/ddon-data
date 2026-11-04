// 13.10.2 S2C_INSTANCE_GET_DROP_ITEM_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 8 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7db2a0, reader 0x80b130: RES header, LayoutId, u32, list 0x769100 (the 17-byte
// Season 3 CDataGatheringItemElement) (V). PS4 CPacket_S2C_GET_DROP_ITEM_LIST_RES::ReadPacket
// 0x19d76f0 (12-byte element, V). Walk: 88/88 fit, slack 11-14, list up to 3; the PS4 element
// fits 44/88 (only the empty lists).
// Body: s32 Error [, s32 Result, LayoutId, u32 Id, MtTypedArray<CDataGatheringItemElement>
// ItemList] (25 + 17n bytes).
// packet-id: 13.10.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_GET_DROP_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataStageLayoutId LayoutId;
        u32 Id;
        MtTypedArray<CDataGatheringItemElement> ItemList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_GET_DROP_ITEM_LIST_RES packet @ 0x00;
