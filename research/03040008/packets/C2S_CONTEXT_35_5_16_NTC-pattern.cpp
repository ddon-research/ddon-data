// 35.5.16 C2S_CONTEXT_35_5_16_NTC (client 03040008).
// Body: one u32. P4 2.3, P5 7 (PC writer 0x824900, caller 0x87d350). Client name by caller code
// match with PS4 cNetGameServer::sendBadStatusNotice: C2S_CHARACTER_START_BAD_STATUS_NOTICE
// (PS4 m_unStatusID); the raw-file name is the server's.
// packet-id: 35.5.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CONTEXT_35_5_16_NTC : CPacket {
    u32 m_unStatusID;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONTEXT_35_5_16_NTC packet @ 0x00;
