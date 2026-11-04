// 28.22.2 S2C_GP_GP_EDIT_GET_VOICE_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 10.
// PC handler 0x7d8230, reader 0x809710: list CDataEditParam 0x764b20 (V). PS4
// CPacket_S2C_GP_EDIT_GET_VOICE_LIST_RES {m_VoiceList}: same (V).
// Walk: 2/2 fit (lists up to 22).
// Body: s32 Error [, s32 Result, list CDataEditParam].
// packet-id: 28.22.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "GP.hexpat"

struct S2C_GP_GP_EDIT_GET_VOICE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataEditParam> VoiceList;     // PC 0x764b20
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_GP_GP_EDIT_GET_VOICE_LIST_RES packet @ 0x00;
