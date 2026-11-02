// 5.1.1 C2L_DECIDE_CHARACTER_ID_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 12.
// PC writer 0x88a980 (caller 0x88a110): WritePacket(p, 5, 1, 1, -1), Write_u32, Write_u32,
// Write_u8, Write_u8, Write_u32, Write_u8 (V, pushes). PS4
// CPacket_C2L_DECIDE_CHARACTER_ID_REQ::WritePacket 0x1a408d0 (u32 in_CharacterID,
// u32 in_ClientVersion, u8 in_Type, u8 in_RotationServerID, u32 in_WaitNum, u8 in_Counter), same
// writes (V).
// Walk: 42/42 fit, slack 8.
// Body: u32 CharacterID, u32 ClientVersion, u8 Type, u8 RotationServerID, u32 WaitNum, u8 Counter
// (15 B; T002 section 12 says 14 B, see its Errata R1).
// packet-id: 5.1.1
// packet-select: C2L_DECIDE_CHARACTER_ID_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2L_DECIDE_CHARACTER_ID_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 CharacterID;
    u32 ClientVersion;
    u8 Type;
    u8 RotationServerID;
    u32 WaitNum;
    u8 Counter;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2L_DECIDE_CHARACTER_ID_REQ packet @ 0x00;
