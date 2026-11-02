// 8.36.16 S2C_PAWN_GET_PAWN_ORB_DEVOTE_INFO_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 2.11 (1.3 for the types).
// PC handler 0x7eb2c0, reader 0x8127a0: u32, u32, list 0x7702d0 (CDataOrbPageStatus), list 0x76c270
// (CDataJobOrbTreeStatus), list 0x76c270 again (V). PS4 CPacket_S2C_GET_PAWN_ORB_DEVOTE_INFO_NTC::
// ReadPacket 0x19d5890: u16, u32 m_unCharacterId, u32 m_unPawnId, m_OrbStatusList, m_JobOrbStatusList
// (V). Season 3: the second CDataJobOrbTreeStatus list (V; the PS4 body fails 72/74). No error header: the PC reader reads none (V); PS4 NTCs start with u16 m_usError.
// Walk: 74/74 fit, slack 3-11; PS4 framing fails 74/74.
// Body: u32 CharacterId, u32 PawnId, list CDataOrbPageStatus, 2 x list CDataJobOrbTreeStatus.
// packet-id: 8.36.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Pawn.hexpat"

struct S2C_PAWN_GET_PAWN_ORB_DEVOTE_INFO_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterId;
    u32 PawnId;
    MtTypedArray<CDataOrbPageStatus> OrbStatusList;        // PC 0x7702d0
    MtTypedArray<CDataJobOrbTreeStatus> JobOrbStatusList;  // PC 0x76c270
    MtTypedArray<CDataJobOrbTreeStatus> unk_JobOrbStatusList;  // Season 3, PC 0x76c270; server: JobOrbHiBOStatusList (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_GET_PAWN_ORB_DEVOTE_INFO_NTC packet @ 0x00;
