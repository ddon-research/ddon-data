// 37.13.16 S2C_MAIL_SYSTEM_MAIL_SEND_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T009-mail-stamp-character.md
// section 17.
// Code name: SYSTEM_MAIL_SEND_NTC (V by behaviour: the system-mail list).
// PC handler 0x7e4180, no error header: CDataMailInfo element reader 0x76e5a0, then sub_7E4120 adds
// it to the system-mail list (manager +41452, the list of 37.7.2) (V). PS4
// OnPacket_S2C_SYSTEM_MAIL_SEND_NTC 0x32d8e0: u16 error, Read_CDataMailInfo_,
// addMailInfo(&mAddSysMailList) (V).
// The PS4 u16 framing also fits (the window cannot tell): the framing rests on the PC handler.
// Walk: 5/5 fit, slack 7.
// Body: CDataMailInfo (variable).
// packet-id: 37.13.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Mail.hexpat"

struct S2C_MAIL_SYSTEM_MAIL_SEND_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataMailInfo MailInfo;                             // PC 0x76e5a0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_MAIL_SYSTEM_MAIL_SEND_NTC packet @ 0x00;
