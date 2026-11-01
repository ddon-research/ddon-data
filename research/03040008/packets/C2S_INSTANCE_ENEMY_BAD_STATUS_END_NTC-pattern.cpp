// 13.47.16 C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC (client 03040008).
// Body: u32, u8, u32, u32, u32, u32. P4 4, P5 7 (PC writer 0x841170 / 0x82b650; sent for a player character).
// The client name is unresolved (P5 7); the raw-file name is the server's. Server names
// (StageId, LayerNo, GroupId, PosId, Unk4, Unk5) are leads only; the last u32 looks like a
// status id (captures: 0x100c, I).
// packet-id: 13.47.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 unk_u32_0;  // server: StageId (lead)
    u8 unk_u8;      // server: LayerNo (lead)
    u32 unk_u32_1;  // server: GroupId (lead)
    u32 unk_u32_2;
    u32 unk_u32_3;
    u32 unk_u32_4;  // status id (inferred)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_ENEMY_BAD_STATUS_END_NTC packet @ 0x00;
