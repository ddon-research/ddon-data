// 13.32.16 S2C_INSTANCE_ENEMY_GROUP_RESET_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 15 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dab00, reader 0x80ac90: u32, u8, u32, no error header (V). Settled V by
// behaviour as PS4 S2C_ENEMY_GROUP_RESET_NOTICE (OnPacket 0x2f43b0 ->
// sSetManager::resetEnemySetList); DWARF {u16 m_usError, CStageLayoutID m_LayoutId}. Walk:
// 130/130 fit, slack 14.
// Body: CDataStageLayoutId LayoutId (9 bytes).
// packet-id: 13.32.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_ENEMY_GROUP_RESET_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_ENEMY_GROUP_RESET_NTC packet @ 0x00;
