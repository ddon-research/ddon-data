// 28.26.16 S2C_GP_COURSE_EXTEND_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 14.
// Code name: GP_COURSE_EXTEND_NTC (V by behaviour). PC handler 0x7d78f0, reader 0x809310: u32, u64,
// no error header; then 0xb60b50(sGame, u32, 1, u64, 0, 1, 0) (V). PS4
// OnPacket_S2C_GP_COURSE_EXTEND_NTC 0x30c1c0: setChargeCourse(sGame, id, true, endTime, false,
// true, 0); DWARF {u32 m_unCourseID, u64 m_ullFinishDateTime} (V).
// The PS4 u16 framing also fits (the window cannot tell): the framing rests on the PC handler.
// Walk: 21/21 fit, slack 11.
// Body: u32 CourseID, u64 FinishDateTime (12 bytes).
// packet-id: 28.26.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_COURSE_EXTEND_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CourseID;
    u64 FinishDateTime;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_COURSE_EXTEND_NTC packet @ 0x00;
