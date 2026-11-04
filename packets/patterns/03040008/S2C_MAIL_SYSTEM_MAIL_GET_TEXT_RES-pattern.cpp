// 37.9.2 S2C_MAIL_SYSTEM_MAIL_GET_TEXT_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 15.
// PC handler 0x7e4050 (not a function in the database; read linearly), reader 0x80f190: RES
// header, u64, CDataMailTextInfo 0x76e9e0 (MtString + CDataMailAttachmentList 0x76e2f0) (V). PS4
// 0x32cdc0: u64 m_ullId, m_MailTextInfo (V). Walk: 7/7 fit, slack 6-15, up to 3 items; the GP,
// option course and legend pawn lists are empty in every capture.
// Body: s32 Error [, s32 Result, u64 Id, CDataMailTextInfo] (variable).
// packet-id: 37.9.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Mail.hexpat"

struct S2C_MAIL_SYSTEM_MAIL_GET_TEXT_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u64 Id;
        CDataMailTextInfo MailTextInfo;                     // PC 0x76e9e0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_MAIL_SYSTEM_MAIL_GET_TEXT_RES packet @ 0x00;
