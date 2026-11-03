// 62.1.2 S2C_SEASON_DUNGEON_GET_INFO_RES (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 62.1.2.
// PC handler 0x7f7990 cSeedGameSvConnection::OnPacket_SEASON_DUNGEON_GET_INFO_RES (V name), reader
// 0x819c80: RES header, 0x777b00 {u32, MtString, u32}, list 0x777d70 (element 0x777e80), u8 (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 4/4 fit, slack 2; one dungeon with 4 sections.
// Body: s32 Error [, s32 Result, CDataSeasonDungeonInfo, list CDataSeasonDungeonSection, u8].
// packet-id: 62.1.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "SeasonDungeon.hexpat"

struct S2C_SEASON_DUNGEON_GET_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataSeasonDungeonInfo DungeonInfo;     // PC 0x777b00; T005 G (lead)
        MtTypedArray<CDataSeasonDungeonSection> SectionList;  // PC 0x777d70; T005 G (lead: server DungeonSections)
        u8 unk_u8;          // T005 open: 0 in 4/4; server: Unk0 (lead)
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_SEASON_DUNGEON_GET_INFO_RES packet @ 0x00;
