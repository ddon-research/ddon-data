// 27.10.2 S2C_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 27.10.2.
// PC handler 0x7c31d0 cSeedGameSvConnection::OnPacket_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES
// (V name), reader 0x7ff650: RES header, nPacket::Read_CDataAchievementProgress_ 0x758810 (V).
// PS4 counterpart: none matched (spec 006 T012 § 12).
// Walk: 19/19 fit, slack 3; 19 achievements per list.
// Body: s32 Error [, s32 Result, list CDataAchievementProgress].
// packet-id: 27.10.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Pawn.hexpat"
#include "Achievement.hexpat"

struct S2C_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T005 V (same reader 0x758810 as 27.0.2: Achievement.hexpat CDataAchievementProgress); list
        // name G (lead: server AchievementProgressList)
        MtTypedArray<CDataAchievementProgress> AchievementProgressList;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ACHIEVEMENT_ACHIEVEMENT_GET_CATEGORY_PROGRESS_LIST_RES packet @ 0x00;
