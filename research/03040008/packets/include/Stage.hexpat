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
    // T014b V (consumer); I (name): handler 0x7fd690 -> 0x7fd490 -> 0x416a20 (sArea stage object,
    // list +52, max 64): element +12 goes through 0x84a200, the same table lookup (conn +40516,
    // 40-byte entries, key +4 -> +8) that 0x7fd490 applies to the RES StageNo (...)
    u32 StageNo;
    // T014b open (not read), kept unk: 0x416a20 copies +12, +20, +24, +28 of the element but not
    // +16; no other consumer of the list
    u8 unk_u8_0;
    // T014b V (consumer); I (name): 0x416a20 stores (mapped stage u16 | element +20 << 16) as one
    // key; 0xbfec20 passes +20 (as u16 1..511, 0x5df810) to sSetManager type 2: add 0xbf8250 or
    // remove 0xbfabb0 (...)
    u32 GroupId;
    // T014b V (consumer); I (role: second key): stored at the stage-object slot +4 (0x416a20);
    // 0x40c5a0 matches it against the caller's second key (layout object +84) together with the
    // stage/group key
    u32 unk_u32_2;
    // T014b V (consumer); I (role: state): 0xbfec20: value 1 removes the sSetManager type-2 entry,
    // any other value adds it; 0x40c5a0 returns it and 0x5bd670 keeps it when it is in 63..76
    u8 unk_u8_1;
};

// 12.1.2 second Season 3 list: PC list reader 0x766540, element {u32, bool, bool} (V). server:
// CDataStageAreaChangeResUnk1 {Unk0, Unk1, Unk2} (lead).
struct CDataAreaChangeUnk1 {
    // T014b V (consumer); I (role: object id key): 0x4169b0 stores the element at sArea stage
    // object +1508 (+4/+8/+9); 0x40c530 finds it by this u32, called from 0x752f50 with the
    // object's +60 id (0x753280 filters ids 6000..6007 / 6100..6107)
    u32 unk_u32;
    // T014b V (consumer); I (role: suppress flag): 0x752f50 creates the object (0xbf90d0(16, ...))
    // only when no entry is found or bool +8 is 0
    bool unk_bool_0;
    // T014b open (no reader), kept unk: 0x40c530 copies +9 out, but its only caller 0x752f50 reads
    // only +8
    bool unk_bool_1;
};
