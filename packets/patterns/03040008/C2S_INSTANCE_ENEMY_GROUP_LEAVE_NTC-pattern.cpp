// 13.2.16 C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 3 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x841370 (13, 2, 0x10): LayoutId only (V). Settled V by behaviour as PS4
// CPacket_C2S_ENEMY_GROUP_LEAVE_NOTICE (WritePacket 0x1a36da0): the same PC 0xaa78b0 sends it
// when the kill-area state leaves 1, as PS4 cGroupParam::update calls
// cNetGameServer::enemyGroupLeave. Walk: 184/184 fit, slack 14 (the 9-byte body rests on the
// code).
// Body: CDataStageLayoutId LayoutId (9 bytes).
// packet-id: 13.2.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataStageLayoutId LayoutId;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_ENEMY_GROUP_LEAVE_NTC packet @ 0x00;
