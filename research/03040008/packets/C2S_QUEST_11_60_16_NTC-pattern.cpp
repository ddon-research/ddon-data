// 11.60.16 C2S_QUEST_11_60_16_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 25 (section 44 for the shared types in include/Quest.hexpat).
// Client to server (source 0x00). Code name
// C2S_PRT_READY_SET_RETURN_SESSION (V by behaviour): PC writer 0x8395a0 (11, 60, 16) writes one
// bool, sent by sub_883B30 from cPRTManager::updatePRT, as PS4 cNetGameServer::
// setReturnSessionForPRT 0x350630 -> Send_C2S_PRT_READY_SET_RETURN_SESSION 0x19ba090 {b8
// m_bIsReturnSession}. Walk: 7/7 fit, slack 6.
// Body: bool IsReturnSession (1 byte).
// packet-id: 11.60.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct C2S_QUEST_11_60_16_NTC : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    bool IsReturnSession;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_QUEST_11_60_16_NTC packet @ 0x00;
