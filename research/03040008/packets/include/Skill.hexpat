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
