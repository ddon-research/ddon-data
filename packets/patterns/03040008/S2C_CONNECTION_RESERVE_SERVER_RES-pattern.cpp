// 0.7.2 S2C_CONNECTION_RESERVE_SERVER_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 8.
// PC reader 0x804d10 via handler 0x7cead0: RES header, Read_u16 (+24), list 0x75e8e0
// (CDataCommonU32) (V). PS4 0x2df750 u16, s32, u16, CommonU32 list; DWARF {..., u16
// m_usGameServerUniqueID, MtTypedArray<CDataCommonU32> m_ReserveInfoList} (V).
// Walk: 41/41 fit, slack 5; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, u16 GameServerUniqueID, MtTypedArray<CDataCommonU32>
// ReserveInfoList].
// packet-id: 0.7.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CONNECTION_RESERVE_SERVER_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u16 GameServerUniqueID;
        MtTypedArray<CDataCommonU32> ReserveInfoList;       // PC 0x75e8e0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONNECTION_RESERVE_SERVER_RES packet @ 0x00;
