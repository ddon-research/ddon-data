// 62.24.1 C2S_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 62.24.1.
// PC writer 0x8420e0: WritePacket(0x3e, 24, 1), Write_u32, list writer 0x77fd30 {Write_MtString +4,
// Write_u32 +8}, 0x781020 {Write_u32 +4, Write_u8 +8, Write_u32 +12}, Write_u32 (V; 008 T002).
// Packet name G (lead), the request of the V-named 62.24.2. PS4 counterpart: none (Season 3 group).
// Walk: 28/28 fit, slack 2; TrialCost empty in 28/28 (element layout code only).
// Body: u32, list {MtString, u32}, CDataStageLayoutId, u32.
// packet-id: 62.24.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

// Element of PC list writer 0x77fd30 {Write_MtString +4, Write_u32 +8} (V, 008 T002); never captured
// non-empty here (62.10.1 uses the same writer). Struct name: server CDataSoulOrdealItemInfo (lead).
struct CDataSoulOrdealItemInfo {
    MtString ItemUId;   // T004 G (lead): server ItemUId (62.10.1 carries 8-hex-digit strings, item UIDs)
    u32 Num;            // T004 G (lead): server Num
};

struct C2S_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T004 I (value: 28/28 name a TrialId of the preceding 62.18.2); server: TrialId (lead agrees)
    u32 TrialId;
    MtTypedArray<CDataSoulOrdealItemInfo> TrialCost;      // PC 0x77fd30; T004 G (lead)
    // T004 I (same structure: the writer's inline {Write_u32 +4, Write_u8 +8, Write_u32 +12} is the
    // CDataStageLayoutId triplet; value: a LayoutId that 62.26.16 sets in the same stream); server: LayoutId (lead agrees)
    CDataStageLayoutId LayoutId;
    u32 PosId;          // T004 G (lead): server PosId; captured 0 everywhere
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_SEASON_DUNGEON_EXECUTE_SOUL_ORDEAL_REQ packet @ 0x00;
