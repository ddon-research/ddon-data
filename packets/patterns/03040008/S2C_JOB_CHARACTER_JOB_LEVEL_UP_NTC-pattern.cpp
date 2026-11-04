// 33.12.16 S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 1.3 (section 6 for the shared types).
// PC handler 0x7dfa50, reader 0x80d3a0: u8, u32, u32, u32, 0x75cb00 (10 x u16) (V). PS4
// CPacket_S2C_CHARACTER_JOB_LEVEL_UP_NOTICE::ReadPacket 0x19d8080: u8 m_ucJob, u32 m_unLevel,
// u32 m_unAddJobPoint, u32 m_unTotalJobPoint, CDataCharacterLevelParam (V).
// No error header: the PC reader reads none (V); PS4 framing (u16 error first) also fits, not
// discriminating (slack 6). Walk: 1/1 fit, slack 6.
// Body: u8 Job, u32 Level, u32 AddJobPoint, u32 TotalJobPoint, CDataCharacterLevelParam (33 bytes).
// packet-id: 33.12.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Character.hexpat"

struct S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u8 Job;
    u32 Level;
    u32 AddJobPoint;
    u32 TotalJobPoint;
    CDataCharacterLevelParam CharacterLevelParam;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_JOB_CHARACTER_JOB_LEVEL_UP_NTC packet @ 0x00;
