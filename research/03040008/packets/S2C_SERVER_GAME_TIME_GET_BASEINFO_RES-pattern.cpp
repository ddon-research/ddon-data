// 1.8.2 S2C_SERVER_GAME_TIME_GET_BASEINFO_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 14.
// PC reader 0x81a620 via handler 0x7f8f30: RES header, 0x769030 (CDataGameTimeBaseInfo), list
// 0x77ca30 {u8, u32}, list 0x77cb20 {u8, s64, s64}, Read_u32 (+120), list 0x76f0f0 {u8, s64, s64}
// (V). PS4 OnPacket_S2C_GAME_TIME_GET_BASEINFO_RES 0x332380, the same sequence; DWARF member
// names (V); no Season 3 change.
// Walk: 41/41 fit, slack 7 (WeatherLoop 11, WeatherSchedule 1, MoonSchedule 0 in all: the
// MoonSchedule element is code-only); no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, CDataGameTimeBaseInfo GameTimeBaseInfo, MtTypedArray<
// CDataWeatherLoop> WeatherLoop, MtTypedArray<CDataWeatherSchedule> WeatherSchedule,
// u32 MoonAgeLoopSec, MtTypedArray<CDataMoonSchedule> MoonSchedule].
// packet-id: 1.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Server.hexpat"

struct S2C_SERVER_GAME_TIME_GET_BASEINFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataGameTimeBaseInfo GameTimeBaseInfo;             // PC 0x769030 (Server.hexpat)
        MtTypedArray<CDataWeatherLoop> WeatherLoop;         // PC 0x77ca30
        MtTypedArray<CDataWeatherSchedule> WeatherSchedule; // PC 0x77cb20
        u32 MoonAgeLoopSec;
        MtTypedArray<CDataMoonSchedule> MoonSchedule;       // PC 0x76f0f0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SERVER_GAME_TIME_GET_BASEINFO_RES packet @ 0x00;
