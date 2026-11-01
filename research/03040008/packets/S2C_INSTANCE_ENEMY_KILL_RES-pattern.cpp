// 13.3.2 S2C_INSTANCE_ENEMY_KILL_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 15. PC handler 0x7dac80
// (string 0x1bc9b9c; 13, 3, 2), reader 0x80ad10: s32 Error; if 0: s32 Result, u32 EnemyID, u32
// KillNum (V). PS4 OnPacket_S2C_ENEMY_KILL_RES 0x2f3f10 reads u16, u32 m_unResult, u32, u32 (V
// PS4); the PS4 recompilation (UserSession/S2C.h) also declares u32 m_unResult. PC reads Result as
// s32: kept s32 (P11b), see "Recompilation disagreements". Two captures carry Error 0x3e90 (PS4
// nError INSTANCE_AREA_ENEMY_NOT_CREATED) and nothing after it (P11b G2b).
// Body: s32 Error [, s32 Result, u32 EnemyID, u32 KillNum] (P11a G1).
// packet-id: 13.3.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_INSTANCE_ENEMY_KILL_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 EnemyID;
        u32 KillNum;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_ENEMY_KILL_RES packet @ 0x00;
