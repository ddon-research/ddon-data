// 0.5.1 C2S_CONNECTION_MOVE_IN_SERVER_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 6.
// PC writer 0x824580: WritePacket(p, 0, 5, 1, -1), Write_cstr, Write_u8, Write_u32 (V). PS4
// CPacket_C2S_MOVE_IN_SERVER_REQ::WritePacket 0x1a3a990 MT_CSTR, u8, u32; DWARF {MtString
// m_wstrSessionKey, u8 m_ucPlatform, u32 m_unClientVersion} (V); recompilation stub signature agrees.
// Server lead misplacement: C2SConnectionMoveInServerReq reads only SessionKey (T003 19).
// The SessionKey is the one 0.6.2 returned on the previous connection (T003 6).
// Walk: 41/41 fit, slack 1.
// Body: MtString SessionKey, u8 Platform, u32 ClientVersion.
// packet-id: 0.5.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CONNECTION_MOVE_IN_SERVER_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    MtString SessionKey;
    u8 Platform;
    u32 ClientVersion;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONNECTION_MOVE_IN_SERVER_REQ packet @ 0x00;
