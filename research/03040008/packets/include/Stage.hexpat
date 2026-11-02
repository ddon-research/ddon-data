// Group 12 STAGE CData structures of client 03040008 (PC, Season 3) shared by the packet patterns.
//
// Source (transcribed, not re-derived): specs/006-packet-pattern-coverage/research/
// T006-job-lobby-area-stage.md sections 3.2 and 6. "PC 0x..." is the reader VA in the PC 03040008
// database (image base 0x400000). Marks: V = read in IDA, I = inferred. Both structures are Season 3
// (no PS4 02020005 counterpart: PS4 S2C_AREA_CHANGE_RES ends with m_StageFeatureList), so their
// names and fields are unk; server C# names are leads only and appear as "server: <name>".
// CDataStageInfo stays local to S2C_STAGE_GET_STAGE_LIST_RES-pattern.cpp (one user; T006 6).
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"

// 12.1.2 first Season 3 list: PC list reader 0x766640, element {u32, u8, u32, u32, u8} (V). In the
// captures the first u32 equals the RES StageNo (T006 3.2 sample: 560). server:
// CDataStageAreaChangeResUnk0 {Unk0..Unk4} (lead).
struct CDataAreaChangeUnk0 {
    u32 unk_u32_0;
    u8 unk_u8_0;
    u32 unk_u32_1;
    u32 unk_u32_2;
    u8 unk_u8_1;
};

// 12.1.2 second Season 3 list: PC list reader 0x766540, element {u32, bool, bool} (V). server:
// CDataStageAreaChangeResUnk1 {Unk0, Unk1, Unk2} (lead).
struct CDataAreaChangeUnk1 {
    u32 unk_u32;
    bool unk_bool_0;
    bool unk_bool_1;
};
