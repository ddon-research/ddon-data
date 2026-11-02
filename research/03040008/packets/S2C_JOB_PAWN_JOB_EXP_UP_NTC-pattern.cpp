// 33.15.16 S2C_JOB_PAWN_JOB_EXP_UP_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 1.5.
// PC handler 0x7e15b0, reader 0x80e1c0: u32, u8, u32, u32, u32, u8 (V). PS4 0x19d81e0:
// u32 m_unPawnID, u8 m_ucJob, u32 m_unAddExp, u32 m_unExtraBonusExp, u32 m_unTotalExp, u8 m_ucType
// (V). No error header: the PC reader reads none (V). Walk: 1245/1245 fit, slack 5.
// Body: u32 PawnID, u8 Job, u32 AddExp, u32 ExtraBonusExp, u32 TotalExp, u8 Type (18 bytes).
// packet-id: 33.15.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_JOB_PAWN_JOB_EXP_UP_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 PawnID;
    u8 Job;
    u32 AddExp;
    u32 ExtraBonusExp;
    u32 TotalExp;
    u8 Type;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_JOB_PAWN_JOB_EXP_UP_NTC packet @ 0x00;
