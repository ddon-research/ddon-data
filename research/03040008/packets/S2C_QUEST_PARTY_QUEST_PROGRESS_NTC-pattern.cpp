// 11.120.16 S2C_QUEST_PARTY_QUEST_PROGRESS_NTC (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 3. PC handler 0x7f30f0
// (group-11 table key 16/120; inline ctor 0x0B, 0x78, 0x10; notice class
// "cQuestSvNotPartyQuestProgress" 0x1a13d6d), reader 0x817940 (V). PS4 counterpart by code:
// OnPacket_S2C_PARTY_QUEST_PROGRESS_NOTICE 0x313510 (u32 m_unProgressCharacterId +
// CPartyQuestProgressInfo). No error field on PC (P11a G3). No capture: not validated on data.
// Raw name from packets/all_packets_v03040008.txt.
// packet-id: 11.120.16
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

struct S2C_QUEST_PARTY_QUEST_PROGRESS_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 ProgressCharacterId;                       // PS4 m_unProgressCharacterId
    CDataPartyQuestProgressInfo PartyQuestProgressInfo;   // PC 0x771aa0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_PARTY_QUEST_PROGRESS_NTC packet @ 0x00;
