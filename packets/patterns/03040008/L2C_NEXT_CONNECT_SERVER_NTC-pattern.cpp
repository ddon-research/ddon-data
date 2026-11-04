// 2.3.16 L2C_NEXT_CONNECT_SERVER_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T002-login.md section 7.
// PC reader 0x889df0 via handler 0x886ec0 (key 0x100003): Read_s32, CDataGameServerListInfo
// 0x768ae0, Read_u8, all unconditional (V). The s32 is an error: on non-zero the handler stores it
// into mErrorCode[14], sets mStatus[14] = 4 and raises the error dialog (V); the name Error is I.
// Login NTCs read no error header on PC except this one (T002 section 0.2). PS4 reads u16 Error +
// s32 Result here, PC one s32 (Season 3 difference, V). PS4 DWARF {u16 m_usError,
// s32 m_nResult, CGameServerListInfo m_GameServer, u8 m_ucCounter}; slot 14 (V).
// Walk: 42/42 fit, slack 0-15.
// Body: s32 Error (I), CDataGameServerListInfo GameServer, u8 Counter (no Error guard: read
// unconditionally).
// packet-id: 2.3.16
// packet-select: L2C_NEXT_CONNECT_SERVER_NTC
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Login.hexpat"

struct L2C_NEXT_CONNECT_SERVER_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;                  // I (name); read unconditionally
    CDataGameServerListInfo GameServer;
    u8 Counter;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

L2C_NEXT_CONNECT_SERVER_NTC packet @ 0x00;
