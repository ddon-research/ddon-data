// 30.12.2 S2C_CRAFT_RESET_CRAFTPOINT_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 3 (1 and 16 for the types).
// PC handler 0x7d1080 -> reader 0x805ed0: header, u32, list 0x771c80 (CDataPawnCraftSkill), u32 (V).
// PS4 0x333e30 -> 0x19df770 {m_unPawnID, m_CraftSkillList, m_unCraftPoint} (V).
// Walk: 1/1 fit; PawnID 0x00db3bcf (the 30.0.2 pawn), 5 skills, CraftPoint 7.
// Body: s32 Error [, s32 Result, u32 PawnID, list CDataPawnCraftSkill, u32 CraftPoint].
// packet-id: 30.12.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Pawn.hexpat"

struct S2C_CRAFT_RESET_CRAFTPOINT_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 PawnID;
        MtTypedArray<CDataPawnCraftSkill> CraftSkillList;   // PC 0x771c80
        u32 CraftPoint;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CRAFT_RESET_CRAFTPOINT_RES packet @ 0x00;
