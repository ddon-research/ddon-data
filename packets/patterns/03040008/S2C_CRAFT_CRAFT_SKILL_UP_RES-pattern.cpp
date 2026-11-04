// 30.10.2 S2C_CRAFT_CRAFT_SKILL_UP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 3.
// PC handler 0x7d03d0 -> reader 0x805740: header, u32 x5 (V). PS4 0x315330 -> ReadPacket 0x19d96e0
// {m_unPawnID, m_unSkillType, m_unSkillLevel, m_unUseCraftPoint, m_unRemainCraftPoint} (V; the PS4
// recompilation implements the same ReadPacket).
// Walk: 1/1 fit.
// Body: s32 Error [, s32 Result, u32 x5].
// packet-id: 30.10.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_CRAFT_CRAFT_SKILL_UP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 PawnID;
        u32 SkillType;
        u32 SkillLevel;
        u32 UseCraftPoint;
        u32 RemainCraftPoint;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CRAFT_CRAFT_SKILL_UP_RES packet @ 0x00;
