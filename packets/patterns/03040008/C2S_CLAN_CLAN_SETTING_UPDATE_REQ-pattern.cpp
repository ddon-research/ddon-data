// 31.17.1 C2S_CLAN_CLAN_SETTING_UPDATE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T010-gp-clan.md section 16.
// PC writer 0x823a80: bool (V); PS4 0x19c5af0(in_IsMemberNotice) (V).
// Walk: 42/42 fit, slack 6 (0 x22, 1 x20).
// Body: bool IsMemberNotice (1 byte).
// packet-id: 31.17.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CLAN_CLAN_SETTING_UPDATE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    bool IsMemberNotice;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CLAN_CLAN_SETTING_UPDATE_REQ packet @ 0x00;
