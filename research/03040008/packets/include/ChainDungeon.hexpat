// Group 63 CData of client 03040008 (PC, Season 3), shared by the group 63 packet patterns (server:
// CHAIN_DUNGEON / situation data, lead).
//
// Source: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 3 and § 4. "PC 0x..." is the
// reader VA in the PC 03040008 database (image base 0x400000). No PS4 02020005 type exists (Season 3
// group). Marks (spec 008): V = read in the PC code, I (basis) = inferred, G (basis) = guess; server C#
// (Arrowgene) names are leads, "server: <name> (lead)". Comments read `// T005 <mark>: <basis>`.
// Includes Packet.hexpat and Instance.hexpat (CDataStageLayoutId); neither includes this file.
// Every multi-byte value is big-endian: include this file after `#pragma endian big`.

#pragma once

#include "Packet.hexpat"
#include "Instance.hexpat"

// CDataChainDungeonLayoutInfo: PC list reader 0x762c50 element {u32 +8, u8 +12, u32 +16, u32 +20} (V).
// Users: 63.7.16 (handler 0x7d2000), 63.6.16 (handler 0x7d2150). Struct name G (lead: upstream
// Arrowgene CDataStageLayoutInfo; fork: CDataS2C_63_7_16).
struct CDataChainDungeonLayoutInfo {
    // T005 I (same structure: the element's first {u32, u8, u32} is the CDataStageLayoutId triplet; value:
    // StageId 655 in 9/9 = stage_list.slt "Darkness Cloaked Shadolean Great Temple"); server: LayoutId
    // (lead agrees)
    CDataStageLayoutId LayoutId;
    u32 unk_u32;        // T005 open: 0-7 (63.7.16), 0 (63.6.16); server: Unk0 (lead)
};

// CDataSituationObjective: PC list reader 0x762b40 element {u8 +4, u32 +8, MtString +12} (V). User:
// 63.2.16 (reader 0x806610). Struct name: server (lead).
struct CDataSituationObjective {
    u8 unk_u8;          // T005 open: 63-69, 0; server: Unk0 (lead)
    u32 unk_u32;        // T005 open: 0x000d0003-0x000d0008, 0x00030001/2, 0x00060009; server: Unk1 (lead)
    // T005 I (value: objective texts, e.g. "敵を全滅せよ" / "敵を全滅せよ：成功" (annihilate the enemies /
    // success), "暗黒の竜晶を破壊せよ"); server: Message (lead agrees)
    MtString Message;
};
