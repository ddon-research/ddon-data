// 0.0.1 C2S_CONNECTION_PING_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 2.
// PC writer 0x824750: WritePacket(p, 0, 0, 1, -1), list writer 0x77db60 (u32 count, per element
// Write_u8, Write_u8, Write_u32 x3) (V). PS4 Send_C2S_PING_REQ 0x19c3110, Write_CDataCheatInfo_;
// DWARF CPacket_C2S_PING_REQ {u16 m_usError, MtTypedArray<CDataCheatInfo> m_Info} (V).
// The login server's C2L_PING_REQ shares the id 0.0.1: `// packet-select:` below.
// Walk: 2134/2134 fit, slack 3-5; count 0 in 2026 files, 1 in 108 (the list beyond one element is
// code-only).
// Body: MtTypedArray<CDataCheatInfo> Info.
// packet-id: 0.0.1
// packet-select: C2S_CONNECTION_PING_REQ
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Server.hexpat"

struct C2S_CONNECTION_PING_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtTypedArray<CDataCheatInfo> Info;                  // PC 0x77db60 (Server.hexpat)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONNECTION_PING_REQ packet @ 0x00;
