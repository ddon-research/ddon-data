// 24.6.16 S2C_JOB_MASTER_MARK_TARGETS_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 24.6.16.
// 006 T011 § 13. PC handler 0x7e0b70 (no name string): packet object (0x18, 6, 0x10), list reader 0x76c500
// of element reader 0x76c5f0 {Read_u8 +8, Read_u32 +0xc, Read_u8 +0x10, Read_u8 +0x14, Read_u32 +0x18,
// Read_u32 +0x1c} (V), no RES header; when sAreaExt::isStage, the list goes to 0x416bb0 (sArea +0x3834).
// PS4 counterpart: none (V by code; a list of PS4 CDataJobOrderProgress fails 117/150).
// Name: the raw name (server lead S2C_JOB_MASTER_MARK_TARGETS_NTC), G (lead); group 24 is JOB_MASTER (V by
// its RES strings).
// Walk: 150/150 fit, lists of 0, 12, 35 or 45 elements.
// Body: u32 count + count x 15 bytes.
// packet-id: 24.6.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list 0x76c500, reader 0x76c5f0 {u8, u32, u8, u8, u32, u32} (V widths). No PS4 type.
// Names I (006 T011 § 13: width parallel): the head of PS4 CDataActiveJobOrder {u8 m_ucReleaseType,
// u32 m_unReleaseID, u8 m_ucReleaseLv} followed by the head of PS4 CDataJobOrderProgress {u8
// m_ucConditionType, u32 m_unTargetID, u32 m_unTargetRank}; the server's CDataJobMasterTargetData
// writes the same widths with the same names (lead agrees). Struct name: server (lead).
struct CDataJobMasterTargetData {
    u8 ReleaseType;     // T003 I (width parallel, PS4 m_ucReleaseType; lead agrees): values 1, 2
    u32 ReleaseId;      // T003 I (width parallel, PS4 m_unReleaseID; lead agrees): 63 distinct
    u8 ReleaseLv;       // T003 I (width parallel, PS4 m_ucReleaseLv; lead agrees): values 5-10
    u8 ConditionType;   // T003 I (width parallel, PS4 m_ucConditionType; lead Condition agrees): always 1
    u32 TargetId;       // T003 I (width parallel, PS4 m_unTargetID; lead agrees): 53 distinct
    u32 TargetRank;     // T003 I (width parallel, PS4 m_unTargetRank; lead agrees): 10-80
};

struct S2C_JOB_MASTER_MARK_TARGETS_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T003 G (lead): server TargetList
    MtTypedArray<CDataJobMasterTargetData> TargetList;   // PC 0x76c500 (V)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_JOB_MASTER_MARK_TARGETS_NTC packet @ 0x00;
