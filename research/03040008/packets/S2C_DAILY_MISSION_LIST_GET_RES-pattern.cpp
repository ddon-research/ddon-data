// 72.0.2 S2C_DAILY_MISSION_LIST_GET_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 72.0.2.
// PC handler 0x7d1950 cSeedGameSvConnection::OnPacket_DAILY_MISSION_LIST_GET_RES (V name), reader
// 0x8064e0: RES header, list 0x762460 (+24), list 0x762460 (+44), list 0x7626e0 (+64) (V); the handler
// passes the packet to 0x580b90, which copies the lists into the mission manager (V flow). No server
// structure (lead: PacketId only). PS4 counterpart: none (Season 3 group).
// Walk: 117/117 fit, slack 4; 15 missions and 14 special rewards in 117/117, the third list empty.
// Body: s32 Error [, s32 Result, list CDataDailyMission, list CDataDailyMission, list].
// packet-id: 72.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Mail.hexpat"
#include "DailyMission.hexpat"

struct S2C_DAILY_MISSION_LIST_GET_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        // T004 G (context: purposes 1-6, the quest/dungeon/battle content/craft tasks of the gmd tab
        // "Mission List")
        MtTypedArray<CDataDailyMission> MissionList;              // PC 0x762460
        // T004 G (context: purposes 7-9, texts "Mission List: achieve <VAL>", the gmd tab "Special Reward")
        MtTypedArray<CDataDailyMission> SpecialRewardList;        // PC 0x762460
        MtTypedArray<CDataDailyMissionUnkCourseList> unk_list;    // PC 0x7626e0; T004 open (empty 117/117)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_DAILY_MISSION_LIST_GET_RES packet @ 0x00;
