// Loading-screen info CData of client 03040008 (PC, Season 3) for the group 43 LOADING_INFO pattern.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T012-achievement-equip-skill.md sections 1, 17 and 19. "PC 0x..." is the reader VA in the PC
// 03040008 database (image base 0x400000); "PS4" names the PS4 02020005 reader and DWARF type, whose
// member names the fields carry (m_ and type prefix dropped). The recompilation's PacketData/Loading.h
// declares the same members. Marks: V = read in IDA.
// Includes Packet.hexpat only. User: 43.0.2.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// CDataLoadingInfoSchedule: PC list reader 0x76d550 (loc) {MtString, u32, u32, s64, s64} (V); PS4
// 0x19ee8a0 {MtString m_wstrText, u32 m_unImageId, u32 m_unPriority, s64 m_llBeginDateTime, s64
// m_llEndDateTime}: same (V).
struct CDataLoadingInfoSchedule {
    MtString Text;
    u32 ImageId;
    u32 Priority;
    s64 BeginDateTime;
    s64 EndDateTime;
};
