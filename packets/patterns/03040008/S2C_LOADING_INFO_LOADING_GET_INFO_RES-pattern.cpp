// 43.0.2 S2C_LOADING_INFO_LOADING_GET_INFO_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 17 (1, 19 for the types).
// PC handler 0x7e28d0, reader 0x80e7c0: header, list 0x76d550 (V). PS4 0x330180:
// Read_CDataLoadingInfoSchedule_ into m_Info.m_LoadingInfoScheduleList: same (V); the
// CDataLoadingInfoSchedules wrapper is only the list on the wire.
// Walk: 42/42 fit, slack 3-15; 34, 35 or 100 entries.
// Body: s32 Error [, s32 Result, list CDataLoadingInfoSchedule].
// packet-id: 43.0.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Loading.hexpat"

struct S2C_LOADING_INFO_LOADING_GET_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataLoadingInfoSchedule> LoadingInfoScheduleList;   // PC 0x76d550
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_LOADING_INFO_LOADING_GET_INFO_RES packet @ 0x00;
