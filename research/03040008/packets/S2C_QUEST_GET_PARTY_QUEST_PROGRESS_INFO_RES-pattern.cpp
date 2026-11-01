// 11.71.2 S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 4. PC handler 0x7f1c60
// (string 0x1bc9470), inline ctor (11, 71, 2), reader 0x8168c0 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_PARTY_QUEST_PROGRESS_INFO_RES 0x313220, same body.
// Body: s32 Error [, s32 Result, CDataPartyQuestProgressInfo] (P11a G1: the PC reader stops after a
// non-zero Error). DeliveredItemRecord and KeyItemPointRecord are empty in every capture.
// packet-id: 11.71.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma pattern_limit 3200000
#pragma array_limit 3200000
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Quest.hexpat"

struct S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataPartyQuestProgressInfo PartyQuestProgressInfo;   // PC 0x771aa0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_GET_PARTY_QUEST_PROGRESS_INFO_RES packet @ 0x00;
