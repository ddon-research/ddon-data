// 1.1.2 S2C_SERVER_GET_GAME_SETTING_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 11.
// PC reader 0x81a6f0 via handler 0x7f9070 ("OnPacket_SERVER_GET_GAME_SETTING_RES"): RES header,
// CDataGameSetting 0x768bb0 (V). PS4 Read_CDataGameSetting_ via OnPacket_S2C_GET_GAME_SETTING_RES
// 0x2ddbc0 (V up to MailCacheExpireTime). Season 3 differences (V code, names I): the two PS4
// CapLink MtStrings are gone and a tail follows MailCacheExpireTime (include/Server.hexpat).
// Walk: 42/42 fit, slack 1 in all (no room for the two PS4 strings); no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, CDataGameSetting GameSetting].
// packet-id: 1.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Server.hexpat"

struct S2C_SERVER_GET_GAME_SETTING_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataGameSetting GameSetting;                       // PC 0x768bb0 (Server.hexpat)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SERVER_GET_GAME_SETTING_RES packet @ 0x00;
