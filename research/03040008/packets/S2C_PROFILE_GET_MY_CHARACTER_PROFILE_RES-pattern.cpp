// 26.1.2 S2C_PROFILE_GET_MY_CHARACTER_PROFILE_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T011-party-profile-friend.md
// section 14 (1, 18 for the types).
// PC handler 0x7eec80, reader 0x814620: header, list 0x7698c0 (CDataHistoryElement), MtString, u32,
// list 0x7583b0 (CDataAchieveCategoryStatus), list 0x7702d0 (CDataOrbPageStatus), list 0x76c270
// (CDataJobOrbTreeStatus), list 0x76c270 again (V). PS4
// CPacket_S2C_GET_MY_CHARACTER_PROFILE_RES::ReadPacket 0x19de980 {m_HistoryElementList,
// m_wstrOnlineId, m_unAbilityCostMax, m_AchieveCategoryStatusList, m_OrbStatusList,
// m_JobOrbTreeStatusList} (V). Season 3: the second CDataJobOrbTreeStatus list (V shape; the PS4 body
// fails 4/4); consumer 0x84d1f0 fills a second 11-job table from it, so its name is I. The same list
// pair as 8.36.16.
// Walk: 4/4 fit, slack 0; History 20, Achieve 5, OrbPage 4 (empty inner lists), 11 + 11 job entries.
// Body: s32 Error [, s32 Result, list CDataHistoryElement, MtString OnlineId, u32 AbilityCostMax, list
// CDataAchieveCategoryStatus, list CDataOrbPageStatus, 2 x list CDataJobOrbTreeStatus].
// packet-id: 26.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Character.hexpat"
#include "Pawn.hexpat"

struct S2C_PROFILE_GET_MY_CHARACTER_PROFILE_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataHistoryElement> HistoryElementList;  // PC 0x7698c0
        MtString OnlineId;
        u32 AbilityCostMax;
        MtTypedArray<CDataAchieveCategoryStatus> AchieveCategoryStatusList;  // PC 0x7583b0
        MtTypedArray<CDataOrbPageStatus> OrbStatusList;  // PC 0x7702d0
        MtTypedArray<CDataJobOrbTreeStatus> JobOrbTreeStatusList;  // PC 0x76c270
        MtTypedArray<CDataJobOrbTreeStatus> unk_JobOrbTreeStatusList;  // Season 3, PC 0x76c270 (name I: element type); server: JobOrbHiBOStatusList (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PROFILE_GET_MY_CHARACTER_PROFILE_RES packet @ 0x00;
