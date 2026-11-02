// 19.28.2 S2C_SKILL_GET_CURRENT_SET_SKILL_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 3 (1, 19 for the types).
// PC handler 0x7fae10, reader 0x81b3b0: header, list 0x76f820 (CDataNormalSkillParam), list 0x777f10,
// list 0x777f10 (CDataSetAcquirementParam) (V). PS4 CPacket_S2C_GET_CURRENT_SET_SKILL_LIST_RES::
// ReadPacket 0x19da530 {m_NormalSkillList, m_SetCustomSkillList, m_SetAbilityList}: same (V).
// Walk: 41/41 fit, slack 7-12; lists up to 4/8/10.
// Body: s32 Error [, s32 Result, list CDataNormalSkillParam, 2 x list CDataSetAcquirementParam].
// packet-id: 19.28.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Skill.hexpat"

struct S2C_SKILL_GET_CURRENT_SET_SKILL_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataNormalSkillParam> NormalSkillList;        // PC 0x76f820
        MtTypedArray<CDataSetAcquirementParam> SetCustomSkillList;  // PC 0x777f10
        MtTypedArray<CDataSetAcquirementParam> SetAbilityList;      // PC 0x777f10
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SKILL_GET_CURRENT_SET_SKILL_LIST_RES packet @ 0x00;
