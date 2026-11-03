// 63.2.16 S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 63.2.16.
// Raw/CLI name S2C_63_2_16_NTC; pattern name G (lead: server class S2CSituationDataUpdateObjectivesNtc;
// context: the list carries objective texts). No OnPacket_ string.
// PC handler 0x7d1be0 (no function in the dump) calls reader 0x806610: Read_bool, Read_u8, Read_u32 x4,
// list 0x762b40 {u8, u32, MtString} (V; 008 T001 § 4).
// PS4 counterpart: none (Season 3 group).
// Walk: 21/21 fit, slack 2-13; 4 objectives in 21/21.
// Body: bool, u8, u32 x4, list CDataSituationObjective.
// packet-id: 63.2.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "ChainDungeon.hexpat"

struct S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    bool unk_bool;      // T005 open: true in 3/21; server: Unk0 (lead)
    u8 unk_u8;          // T005 open: 0, 1; server: Unk1 (lead)
    u32 unk_u32_0;      // T005 open: 0-6; server: Unk2 (lead)
    u32 unk_u32_1;      // T005 open: 15 in 21/21; server: Unk3 (lead)
    u32 unk_u32_2;      // T005 open: 0, 1; server: Unk4 (lead)
    u32 unk_u32_3;      // T005 open: 3 in 21/21; server: Unk5 (lead)
    MtTypedArray<CDataSituationObjective> ObjectiveList;   // PC 0x762b40; T005 G (lead)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SITUATION_DATA_UPDATE_OBJECTIVES_NTC packet @ 0x00;
