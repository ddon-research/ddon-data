// 27.4.2 S2C_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 9 (1, 19 for the types).
// PC handler 0x7c3690 (decoded linearly; misaligned at the IDA function boundary), reader 0x7ff8d0:
// header, list 0x7584b0 twice (V). PS4 0x309b80 {m_RecievedRewardList, m_RewardList}: same (V).
// Walk: 1/1 fit, slack 7; both lists empty (non-empty lists code-only).
// Body: s32 Error [, s32 Result, 2 x list CDataAchieveRewardCommon].
// packet-id: 27.4.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Achievement.hexpat"

struct S2C_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataAchieveRewardCommon> RecievedRewardList;   // PC 0x7584b0; DWARF spelling
        MtTypedArray<CDataAchieveRewardCommon> RewardList;           // PC 0x7584b0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_RES packet @ 0x00;
