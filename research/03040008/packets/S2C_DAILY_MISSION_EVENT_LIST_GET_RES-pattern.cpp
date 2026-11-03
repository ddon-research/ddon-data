// 72.3.2 S2C_DAILY_MISSION_EVENT_LIST_GET_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 72.3.2.
// PC handler 0x7d18b0 cSeedGameSvConnection::OnPacket_DAILY_MISSION_EVENT_LIST_GET_RES (V name), reader
// 0x806440: RES header, Read_u8, list 0x762460, list 0x7626e0 (V); the handler passes it to 0x580f90
// of the mission manager (V flow). No server structure. PS4 counterpart: none (Season 3 group).
// Walk: 4/4 fit, slack 3-6; the mission list holds 1 event mission in 2 files, else 0.
// Body: s32 Error [, s32 Result, u8, list CDataDailyMission, list].
// packet-id: 72.3.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Mail.hexpat"
#include "DailyMission.hexpat"

struct S2C_DAILY_MISSION_EVENT_LIST_GET_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 unk_u8;      // T004 open, kept unk: captured 7, the request's u8 (4/4)
        // T004 G (context: packet name EVENT_LIST, gmd "Time Event"; the one mission is a 4th-anniversary
        // furniture event ("defeat 4 goblins", items 23502-23505) with MissionId 19080101)
        MtTypedArray<CDataDailyMission> EventMissionList;         // PC 0x762460
        MtTypedArray<CDataDailyMissionUnkCourseList> unk_list;    // PC 0x7626e0; T004 open (empty 4/4)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_DAILY_MISSION_EVENT_LIST_GET_RES packet @ 0x00;
