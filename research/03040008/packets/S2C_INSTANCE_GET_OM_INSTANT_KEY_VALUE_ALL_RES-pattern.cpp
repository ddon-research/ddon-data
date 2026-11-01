// 13.22.2 S2C_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 12 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dbc50, reader 0x80b7a0: RES header, u32, list 0x76fd10 = {u64, u32} (V). PS4
// OnPacket_S2C_Get_OM_INSTANT_KEY_VALUE_ALL_RES 0x2f67a0; DWARF {u32 m_unStageId,
// MtTypedArray<CDataOmData> m_Values} (V). Season 3: Key is u64. Walk: 150/150 fit, slack 7-15,
// list up to 6; the u32 key fits 147/150.
// Body: s32 Error [, s32 Result, u32 StageId, MtTypedArray<CDataOmData> Values] (16 + 12n
// bytes).
// packet-id: 13.22.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 StageId;
        MtTypedArray<CDataOmData> Values;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_GET_OM_INSTANT_KEY_VALUE_ALL_RES packet @ 0x00;
