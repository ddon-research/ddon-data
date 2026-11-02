// 33.20.16 S2C_JOB_PLAY_POINT_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T006-job-lobby-area-stage.md
// section 1.8.
// Code-backed name: UPDATE_PLAY_POINT_NOTICE (V by behaviour, T006 1.8); the file and pattern keep
// the name the raws carry. PC handler 0x7e2770 (packet object 33/20/16), reader 0x80e740: u8, u32,
// u32, u32, u8 (V). PS4 cSeedGameSvConnection::OnPacket_S2C_UPDATE_PLAY_POINT_NOTICE 0x30ec00 /
// CPacket_S2C_UPDATE_PLAY_POINT_NOTICE::ReadPacket 0x19d8560: same body, same gain-info type 7, same
// messages 0xF6/0xF8, same final cPlayPointInfo update (V). Season 3: Type values 5 and 6 added
// (values only). No error header (V). Walk: 14/14 fit, slack 9.
// Body: u8 Job, u32 UpdatePoint, u32 ExtraBonusPoint, u32 TotalPoint, u8 Type (14 bytes).
// packet-id: 33.20.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_JOB_PLAY_POINT_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u8 Job;
    u32 UpdatePoint;
    u32 ExtraBonusPoint;
    u32 TotalPoint;
    u8 Type;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_JOB_PLAY_POINT_NTC packet @ 0x00;
