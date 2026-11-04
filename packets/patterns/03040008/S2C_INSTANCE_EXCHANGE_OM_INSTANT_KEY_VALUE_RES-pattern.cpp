// 13.23.2 S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 13 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7db090, reader 0x80b000: RES header, u32, 0x76fe10 (u64, u32), u32 (V). PS4
// CPacket_S2C_EXCHANGE_OM_INSTANT_KEY_VALUE_RES::ReadPacket 0x19d9910 {u32 m_unStageId, COmData
// m_Value, u32 m_ulValueOld} (V; the recompilation agrees, u32 key). Season 3: Key is u64. Walk:
// 46/46 fit, slack 11.
// Body: s32 Error [, s32 Result, u32 StageId, CDataOmData Value, u32 ValueOld] (28 bytes).
// packet-id: 13.23.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 StageId;
        CDataOmData Value;
        u32 ValueOld;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_RES packet @ 0x00;
