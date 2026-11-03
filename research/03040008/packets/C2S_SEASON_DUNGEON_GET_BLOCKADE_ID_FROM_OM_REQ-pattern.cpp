// 62.8.1 C2S_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.8.1.
// PC writer 0x842150: WritePacket(0x3e, 8, 1), Write_u32 +4, Write_u8 +8, Write_u32 +12 (layout id),
// Write_u32 (V). Name: CLI/server (G (lead)).
// PS4 counterpart: none (Season 3 group).
// Walk: 7/7 fit, slack 10.
// Body: CDataStageLayoutId, u32.
// packet-id: 62.8.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct C2S_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T005 I (same structure: the writer's inline {Write_u32 +4, Write_u8 +8, Write_u32 +12} is the
    // CDataStageLayoutId triplet; value: StageId 560 in 7/7 = stage_list.slt "Memory of Megadosys Old
    // Road", GroupId 131-136); server: LayoutId (lead agrees)
    CDataStageLayoutId LayoutId;
    u32 PosId;          // T005 G (lead): server PosId; 0 in 7/7
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_SEASON_DUNGEON_GET_BLOCKADE_ID_FROM_OM_REQ packet @ 0x00;
