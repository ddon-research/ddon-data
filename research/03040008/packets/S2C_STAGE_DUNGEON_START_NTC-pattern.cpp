// 12.9.16 S2C_STAGE_DUNGEON_START_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 12.9.16.
// PC handler 0x7fdff0 (no OnPacket_ string; name G (lead)), reader 0x81d070: 0x779a90 {u32, MtString,
// u32, u32, Read_bool, list 0x779b10 {u32, u16}} (V).
// PS4 counterpart: none matched (spec 006 T006 § 3).
// Walk: 3/3 fit, slack 4; EntryCostList empty in 3/3.
// Body: CDataStageDungeonStart.
// packet-id: 12.9.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

// Element of PC list reader 0x779b10 {u32 +4, u16 +8} (V); never captured non-empty. Struct name G
// (context); server: CDataBattleContentUnk5 {Unk0, Unk1} (lead).
struct CDataStageDungeonEntryCost {
    u32 unk_u32;        // T005 open: code only; server: Unk0 (lead)
    u16 unk_u16;        // T005 open: code only; server: Unk1 (lead)
};

// PC reader 0x779a90 {u32 +4, MtString +8, u32 +12, u32 +16, bool +20, list 0x779b10 +24} (V). Struct
// name G (context); the server writes the fields flat.
struct CDataStageDungeonStart {
    // T005 I (value: 3/3 = the ContentId of the preceding 12.5.1; 19); server: Unk0 (lead)
    u32 ContentId;
    MtString unk_str;   // T005 open: empty in 3/3; server: Unk1 (lead)
    // T005 I (value: 559 in 3/3 = stage_list.slt StageId "Memory of Megadosys", the 62.1.2 dungeon
    // name); server: StageId (lead agrees)
    u32 StageId;
    u32 StartPos;       // T005 G (lead): server StartPos; 5 in 3/3
    bool unk_bool;      // T005 open: true in 3/3; server: Unk4 (lead)
    MtTypedArray<CDataStageDungeonEntryCost> EntryCostList;  // T005 G (lead)
};

struct S2C_STAGE_DUNGEON_START_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    CDataStageDungeonStart DungeonStart;    // PC 0x779a90; T005 G (context)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_STAGE_DUNGEON_START_NTC packet @ 0x00;
