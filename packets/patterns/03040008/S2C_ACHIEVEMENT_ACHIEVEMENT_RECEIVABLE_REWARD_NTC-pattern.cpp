// 27.9.16 S2C_ACHIEVEMENT_ACHIEVEMENT_RECEIVABLE_REWARD_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 11 (1, 19 for the types).
// PC handler 0x7c35b0 (table entry tagged 27, 9, 16): list 0x7584b0 (CDataAchieveRewardCommon); on
// success sets [dword_21C08C4+0x30] = 1 (V). PS4 OnPacket_S2C_ACHIEVEMENT_RECEIVABLE_REWARD_NTC 0x309a10:
// u16 error, m_RewardList, on success mIsAvailableAchieve = true: match V by list type and behaviour.
// No error header: the PC reader reads none (V); the PS4 framing fails 3/3.
// Walk: 3/3 fit, slack 14; one element each.
// Body: list CDataAchieveRewardCommon.
// packet-id: 27.9.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Achievement.hexpat"

struct S2C_ACHIEVEMENT_ACHIEVEMENT_RECEIVABLE_REWARD_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataAchieveRewardCommon> RewardList;   // PC 0x7584b0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ACHIEVEMENT_ACHIEVEMENT_RECEIVABLE_REWARD_NTC packet @ 0x00;
