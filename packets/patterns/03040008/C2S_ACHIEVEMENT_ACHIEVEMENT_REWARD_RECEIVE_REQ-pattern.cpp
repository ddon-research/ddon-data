// 27.4.1 C2S_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 9 (1, 19 for the types).
// PC writer 0x81e070 (27, 4, 1): writer 0x77d160, count + {u8, u32} (V). PS4
// Send_C2S_ACHIEVEMENT_REWARD_RECEIVE_REQ 0x19cb5b0(MtTypedArray<CDataAchieveRewardCommon>* in_RewardList)
// (V).
// Walk: 1/1 fit, slack 14; 1 entry.
// Body: list CDataAchieveRewardCommon (4 + 5n bytes).
// packet-id: 27.4.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Achievement.hexpat"

struct C2S_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataAchieveRewardCommon> RewardList;   // PC writer 0x77d160
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_ACHIEVEMENT_ACHIEVEMENT_REWARD_RECEIVE_REQ packet @ 0x00;
