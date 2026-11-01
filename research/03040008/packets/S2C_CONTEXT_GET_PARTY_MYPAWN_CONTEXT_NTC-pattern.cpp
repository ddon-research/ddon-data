// 35.3.16 S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC (client 03040008).
// Body: u32 PawnID, ContextBase, PlayerInfo, PawnInfo, Resist, EditInfo. P4 2.2-2.3 (PC handler
// 0x7cf330, reader 0x805040 -> 0x771200).
// packet-id: 35.3.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 m_unPawnID;
    CDataContextBase m_Base;
    CDataContextPlayerInfo m_PlayerInfo;
    CDataContextPawnInfo m_PawnInfo;
    CDataContextResist m_ResistInfo;
    CDataEditInfo m_EditInfo;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_GET_PARTY_MYPAWN_CONTEXT_NTC packet @ 0x00;
