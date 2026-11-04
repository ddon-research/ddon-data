// 37.11.2 S2C_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 16.
// PC handler 0x7e3c10, reader 0x80eee0: RES header, u64, CDataMailAttachmentList 0x76e2f0 (V).
// PS4 CPacket_S2C_SYSTEM_MAIL_GET_ALL_ITEM_RES::ReadPacket 0x19ddb50: u64 m_ullId,
// m_AttachmentList (V). Walk: 5/5 fit, slack 8-10, up to 3 items.
// Body: s32 Error [, s32 Result, u64 Id, CDataMailAttachmentList] (variable).
// packet-id: 37.11.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Mail.hexpat"

struct S2C_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u64 Id;
        CDataMailAttachmentList AttachmentList;             // PC 0x76e2f0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_MAIL_SYSTEM_MAIL_GET_ALL_ITEM_RES packet @ 0x00;
