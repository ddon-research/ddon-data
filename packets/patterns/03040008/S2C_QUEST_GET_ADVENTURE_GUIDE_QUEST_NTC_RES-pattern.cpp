// 11.123.2 S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.123.2.
// 006 T005 § 42. PC handler 0x7f0880
// cSeedGameSvConnection::OnPacket_QUEST_GET_ADVENTURE_GUIDE_QUEST_NOTICE_RES (V name; the raw name's NTC is
// the CLI's spelling of NOTICE, as 11.95.16), reader 0x815aa0: RES header, bool (V). The handler keeps the
// packet object in a connection slot (consumer not traced). PS4 counterpart: none (V).
// Walk: 155/155 fit, slack 14; the bool is 0 in 109, 1 in 46.
// Body: s32 Error [, s32 Result, bool].
// packet-id: 11.123.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T003 G (context: the adventure-guide "notice" query answers whether there is something to
        // notify); server: Unk0 (lead)
        bool HasNotice;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_ADVENTURE_GUIDE_QUEST_NTC_RES packet @ 0x00;
