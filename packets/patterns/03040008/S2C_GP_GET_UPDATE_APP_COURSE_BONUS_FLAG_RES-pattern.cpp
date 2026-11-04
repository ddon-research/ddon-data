// 28.34.2 S2C_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 28.34.2.
// 006 T010 § 15. PC handler 0x7d74c0
// cSeedGameSvConnection::OnPacket_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES (V name), reader 0x809020: RES
// header, bool (V); when Result == 0 the handler stores the bool in a byte of sGame (sGame[3709] + 1) (V).
// Walk: 42/42 fit, slack 14; the bool is 0 in 42/42.
// Body: s32 Error [, s32 Result, bool].
// packet-id: 28.34.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 V (role: the handler stores it in an sGame byte); G (name: the "flag" of the packet name);
        // always 0 in 42 captures; no lead (the server has no structure)
        bool UpdateAppCourseBonusFlag;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GET_UPDATE_APP_COURSE_BONUS_FLAG_RES packet @ 0x00;
