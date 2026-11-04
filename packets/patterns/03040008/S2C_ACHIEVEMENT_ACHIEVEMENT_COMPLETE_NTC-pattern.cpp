// 27.8.16 S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 10 (1, 19 for the types).
// PC handler 0x7c2f80 (table entry tagged 27, 8, 16): list 0x758720, elements {Read_u32, Read_u8}; per
// element name lookup, chat line, banner, sub_B67C50(6, id, 1) if the u8 == 6, then
// sQuestManagerExt (V). PS4 OnPacket_S2C_ACHIEVEMENT_COMPLETE_NTC 0x3091a0: u16 error,
// m_AchievementIdList (CDataCommonU32), the same flow with mCategory == 6 from its own table: match V
// by behaviour. Season 3 element {u32, u8}. No error header: the PC reader reads none (V); PS4 NTCs
// start with u16 m_usError (the PS4 framing fails 8/8; the PS4 u32 element fits, slack: the PC reader
// decides).
// Walk: 8/8 fit, slack 14; one element each, Category 1-4.
// Body: list CDataAchievementCompleteElement {u32 AchievementId, u8 Category}.
// packet-id: 27.8.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Achievement.hexpat"

struct S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataAchievementCompleteElement> AchievementIdList;   // PC 0x758720 (Season 3 element)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ACHIEVEMENT_ACHIEVEMENT_COMPLETE_NTC packet @ 0x00;
