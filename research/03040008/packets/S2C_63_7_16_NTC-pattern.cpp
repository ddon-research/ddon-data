// 63.7.16 S2C_63_7_16_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 63.7.16.
// PC handler 0x7d2000 (no OnPacket_ string): list reader 0x762c50 {u32, u8, u32, u32} (V). Packet name:
// the CLI/server name (purpose open).
// PS4 counterpart: none (Season 3 group).
// Walk: 8/8 fit, slack 6; one element each (StageId 655, GroupId 109).
// Body: list CDataChainDungeonLayoutInfo.
// packet-id: 63.7.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"
#include "ChainDungeon.hexpat"

struct S2C_63_7_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataChainDungeonLayoutInfo> LayoutInfoList;   // PC 0x762c50; T005 G (lead: upstream CDataStageLayoutInfo)
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_63_7_16_NTC packet @ 0x00;
