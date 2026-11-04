// 12.1.1 C2S_STAGE_AREA_CHANGE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 3.2.
// PC writer 0x83e9f0 (12, 1, 1): u32, u32 (V). PS4 Send_C2S_AREA_CHANGE_REQ 0x19bb320: u32
// in_StageId, u32 in_JumpType (V). No Season 3 change. Walk: 150/150 fit, slack 15.
// Body: u32 StageId, u32 JumpType (8 bytes).
// packet-id: 12.1.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_STAGE_AREA_CHANGE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 StageId;
    u32 JumpType;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_STAGE_AREA_CHANGE_REQ packet @ 0x00;
