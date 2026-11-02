// 53.6.2 S2C_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 3.1 (1.3 for the type).
// PC handler 0x7e6a80, reader 0x810510: RES header, list 0x7710f0 (CDataPartnerPawnReward) (V). PS4
// OnPacket_S2C_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES 0x335e80: m_ReleasedRewardList (V). No
// Season 3 change. Walk: 41/41 fit, slack 0-11.
// Body: s32 Error [, s32 Result, list CDataPartnerPawnReward] (12 + 9n bytes).
// packet-id: 53.6.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataPartnerPawnReward> ReleasedRewardList;  // PC 0x7710f0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PARTNER_PAWN_PAWN_LIKABILITY_RELEASED_REWARD_LIST_GET_RES packet @ 0x00;
