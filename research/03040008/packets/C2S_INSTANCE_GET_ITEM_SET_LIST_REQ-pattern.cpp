// 13.5.1 C2S_INSTANCE_GET_ITEM_SET_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 5 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x841790 (13, 5, 1): LayoutId (V). PS4
// CPacket_C2S_GET_ITEM_SET_LIST_REQ::WritePacket 0x1a36c20 (V). Walk: 118/118 fit, slack 14; the
// padding holds plain text of an uncleared send buffer, not body.
// Body: CDataStageLayoutId LayoutId (9 bytes).
// packet-id: 13.5.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_GET_ITEM_SET_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_GET_ITEM_SET_LIST_REQ packet @ 0x00;
