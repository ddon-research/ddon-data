// 28.17.2 S2C_GP_GP_COURSE_GET_AVAILABLE_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 9.
// PC handler 0x7d7980 and reader 0x809380 (both not functions in the PC database, decoded
// linearly): list CDataGPCourseAvailable (list 0x7670a0, element 0x7671a0; Season 3 element,
// include/GP.hexpat) (V). PS4 0x30bc70 reads m_Items. Code-only: every captured list is empty.
// Walk: 10/10 fit, slack 11.
// Body: s32 Error [, s32 Result, list CDataGPCourseAvailable].
// packet-id: 28.17.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "GP.hexpat"

struct S2C_GP_GP_COURSE_GET_AVAILABLE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataGPCourseAvailable> Items;     // PC 0x7670a0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GP_COURSE_GET_AVAILABLE_LIST_RES packet @ 0x00;
