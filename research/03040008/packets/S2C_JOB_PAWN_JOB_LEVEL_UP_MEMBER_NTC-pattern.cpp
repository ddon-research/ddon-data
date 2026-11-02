// 33.17.16 S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 1.7 (section 6 for the shared types).
// PC handler 0x7e17b0, reader 0x80e250: u32, u32, u8, u32, 0x75cb00 (V). PS4 0x19d8360:
// u32 m_unCharacterID, u32 m_unPawnID, u8 m_ucJob, u32 m_unLevel, CDataCharacterLevelParam (V).
// No error header: the PC reader reads none (V). Walk: 3/3 fit, slack 6.
// Body: u32 CharacterID, u32 PawnID, u8 Job, u32 Level, CDataCharacterLevelParam (33 bytes).
// packet-id: 33.17.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Character.hexpat"

struct S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterID;
    u32 PawnID;
    u8 Job;
    u32 Level;
    CDataCharacterLevelParam CharacterLevelParam;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_JOB_PAWN_JOB_LEVEL_UP_MEMBER_NTC packet @ 0x00;
