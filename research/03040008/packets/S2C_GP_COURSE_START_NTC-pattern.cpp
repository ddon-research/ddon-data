// 28.25.16 S2C_GP_COURSE_START_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 13.
// Code name: GP_COURSE_START_NTC (V by behaviour). PC handler 0x7d8010, reader 0x8095a0: u32, u64,
// u32, no error header; then 0xb60b50(sGame, u32, 1, u64, isChargeAnnounce(u32), 0, 0) (V). PS4
// OnPacket_S2C_GP_COURSE_START_NTC 0x30c0a0: u16 Error, u32, u64, u32, then
// sGame::setChargeCourse(sGame, id, true, time, isChargeAnnounce(type), false, 0); DWARF {u32
// m_unCourseID, u64 m_ullFinishDateTime, u32 m_unannounceType} (V).
// The PS4 u16 framing also fits (the window cannot tell): the framing rests on the PC handler.
// Walk: 22/22 fit, slack 7 (CourseID 1 x21, 15 x1; AnnounceType always 1).
// Body: u32 CourseID, u64 FinishDateTime, u32 AnnounceType (16 bytes).
// packet-id: 28.25.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_COURSE_START_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CourseID;
    u64 FinishDateTime;
    u32 AnnounceType;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_COURSE_START_NTC packet @ 0x00;
