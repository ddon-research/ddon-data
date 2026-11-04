// 13.5.2 S2C_INSTANCE_GET_ITEM_SET_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 5 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dbb60, reader 0x80b710: RES header, LayoutId, list 0x76cb40 {u8, bool x4} (V).
// PS4 CPacket_S2C_GET_ITEM_SET_LIST_RES::ReadPacket 0x19d7270 (V). Season 3: none. Walk: 258/258
// fit, slack 0-15, list up to 24.
// Body: s32 Error [, s32 Result, LayoutId, MtTypedArray<CDataLayoutItemData> SetList] (21 + 5n
// bytes).
// packet-id: 13.5.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_GET_ITEM_SET_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataStageLayoutId LayoutId;
        MtTypedArray<CDataLayoutItemData> SetList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_GET_ITEM_SET_LIST_RES packet @ 0x00;
