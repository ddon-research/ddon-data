// Skill and ability CData structures of client 03040008 (PC, Season 3) shared by the packet
// patterns.
//
// Source (transcribed, not re-derived): specs/005-netmsg-patterns/research/P11b-old-patterns.md
// sections 16-17 and the shared-structure table. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000); "PS4" names the PS4 02020005 DWARF type; the member order also
// matches the PS4 recompilation (PacketData/Skill.h). No capture holds these bodies (all 19.1.2 and
// 19.2.2 captures are errors): the layouts rest on the PC code only. Marks: V = read in IDA.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataSkillLevelParam: PC list reader 0x778c10 {u8, u32, u32, bool} (V); PS4 CDataSkillLevelParam.
struct CDataSkillLevelParam {
    u8 Lv;
    u32 RequireJobLevel;
    u32 RequireJobPoint;
    bool IsRelease;
};

// CDataSkillParam: PC list reader 0x778d30 {u32, u8, u8, list CDataSkillLevelParam} (V); PS4
// CDataSkillParam {m_unSkillNo, m_ucJob, m_ucType, m_Param}.
struct CDataSkillParam {
    u32 SkillNo;
    u8 Job;
    u8 Type;
    MtTypedArray<CDataSkillLevelParam> Param;
};

// CDataAbilityLevelParam: PC list reader 0x758100 {u8, u32, u32, bool} (V); same shape as
// CDataSkillLevelParam but a separate reader and DWARF type.
struct CDataAbilityLevelParam {
    u8 Lv;
    u32 RequireJobLevel;
    u32 RequireJobPoint;
    bool IsRelease;
};

// CDataAbilityParam: PC list reader loc_758220 (not a function), element 0x758320 {u32, u8 x4,
// u32, list CDataAbilityLevelParam} (V); PS4 CDataAbilityParam, same order.
struct CDataAbilityParam {
    u32 AbilityNo;
    u8 Job;
    u8 Category;
    u8 SortCategory;
    u8 Type;
    u32 Cost;
    MtTypedArray<CDataAbilityLevelParam> Param;
};

// Since spec 006 T012b (specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// sections 1, 3 and 19; field names: the PS4 DWARF member, m_ and type prefix dropped, V). User: 19.28.2.

// CDataNormalSkillParam: PC list reader 0x76f820 {u8, u32, u32, u32} (V); PS4 0x19f1cc0 {u8 m_ucJob,
// u32 m_unSkillNo, u32 m_unIndex, u32 m_unPreSkillNo}; the PS4 reader stores +0xc, +0x10, +0x14 in
// that order and the recompilation's PacketData/Skill.h agrees (V). Server: writes Index before
// SkillNo (lead; the two u32 names are swapped there, T012 20).
struct CDataNormalSkillParam {
    u8 Job;
    u32 SkillNo;
    u32 Index;
    u32 PreSkillNo;
};

// CDataSetAcquirementParam: PC list reader 0x777f10 {u8, u8, u8, u32, u8} (V); PS4 0x19f1f40 {u8
// m_ucJob, u8 m_ucType, u8 m_ucSlotNo, u32 m_unAcquirementNo, u8 m_ucAcquirementLv}: same (V).
struct CDataSetAcquirementParam {
    u8 Job;
    u8 Type;
    u8 SlotNo;
    u32 AcquirementNo;
    u8 AcquirementLv;
};
