// 1.0.2 S2C_SERVER_GET_SERVER_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 10.
// PC reader 0x81a880 via handler 0x7f9740 ("OnPacket_SERVER_GET_SERVER_LIST_RES"): RES header,
// list 0x7689f0 of 0x768ae0 = CDataGameServerListInfo (V). PS4 OnPacket_S2C_GET_SERVER_LIST_RES
// 0x2dda40; DWARF {..., MtTypedArray<CDataGameServerListInfo> m_ServerList} (V).
// The login server's L2C_CLIENT_CHALLENGE_RES shares the id 1.0.2: `// packet-select:` below.
// Walk: 43/43 fit, slack 0-13, 24-25 servers; no captured RES has Error != 0, so the error branch is code-only.
// Body: s32 Error [, s32 Result, MtTypedArray<CDataGameServerListInfo> ServerList].
// packet-id: 1.0.2
// packet-select: S2C_SERVER_GET_SERVER_LIST_RES
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Server.hexpat"

struct S2C_SERVER_GET_SERVER_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataGameServerListInfo> ServerList;  // PC 0x7689f0 (Login.hexpat)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SERVER_GET_SERVER_LIST_RES packet @ 0x00;
