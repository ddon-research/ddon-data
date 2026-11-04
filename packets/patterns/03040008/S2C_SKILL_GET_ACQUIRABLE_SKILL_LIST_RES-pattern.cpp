// 19.1.2 S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 16. PC handler 0x7fab30
// (string 0x1bcc438), ctor 0x78cfa0, reader 0x81b220; list 0x778d30 of CDataSkillParam with sublist
// 0x778c10 (V). PS4 OnPacket_S2C_GET_ACQUIRABLE_SKILL_LIST_RES 0x2fbea0 + DWARF
// CDataSkillParam/CDataSkillLevelParam: identical (V PS4); PS4 recompilation (UserSession/S2C.h,
// PacketData/Skill.h) agrees. All 4 captures are Error 0x3a9d (PS4 nError
// CHARACTER_PARAM_NOT_FOUND) with nothing after it (P11b G2b): the body has no capture.
// Body: s32 Error [, s32 Result, list CDataSkillParam] (P11a G1).
// packet-id: 19.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Skill.hexpat"

struct S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataSkillParam> SkillParamList;   // PC 0x778d30
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SKILL_GET_ACQUIRABLE_SKILL_LIST_RES packet @ 0x00;
