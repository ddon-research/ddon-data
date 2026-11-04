// 13.0.1 C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 2 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x8415f0: WritePacket(p, 13, 0, 1), LayoutId, Write_u8 (V). PS4
// CPacket_C2S_GET_ENEMY_SET_LIST_REQ::WritePacket 0x1a37040 {m_LayoutId, u8 m_ucSubGroupId} (V).
// Walk: 563/563 fit, slack 13.
// Body: CDataStageLayoutId LayoutId, u8 SubGroupId (10 bytes).
// packet-id: 13.0.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    u8 SubGroupId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_GET_ENEMY_SET_LIST_REQ packet @ 0x00;
