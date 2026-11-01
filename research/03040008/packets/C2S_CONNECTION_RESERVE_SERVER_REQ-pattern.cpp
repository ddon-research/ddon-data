// 0.7.1 C2S_CONNECTION_RESERVE_SERVER_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T003-connection-server-cert.md
// section 8.
// PC writer 0x840930: WritePacket(p, 0, 7, 1, -1), Write_u16, Write_u8, Write_u8, list writer
// 0x77df90 (u32 count + u32 per element) (V). PS4 CPacket_C2S_RESERVE_SERVER_REQ::WritePacket
// 0x1a3a730; DWARF {u16 m_usGameServerUniqueID, u8 m_ucType, u8 m_ucRotationServerID,
// MtTypedArray<CDataCommonU32> m_ReserveInfoList} (V).
// Walk: 41/41 fit, slack 11.
// Body: u16 GameServerUniqueID, u8 Type, u8 RotationServerID, MtTypedArray<CDataCommonU32>
// ReserveInfoList (the character id in the captures).
// packet-id: 0.7.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_CONNECTION_RESERVE_SERVER_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u16 GameServerUniqueID;
    u8 Type;
    u8 RotationServerID;
    MtTypedArray<CDataCommonU32> ReserveInfoList;       // PC 0x77df90
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_CONNECTION_RESERVE_SERVER_REQ packet @ 0x00;
