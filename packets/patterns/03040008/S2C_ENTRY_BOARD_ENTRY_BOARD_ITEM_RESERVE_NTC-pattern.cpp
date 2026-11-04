// 34.16.16 S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_RESERVE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 8.
// PC handler 0x7d3cf0 (object tagged 34, 16, 16) -> 0x807530: Read_u32, Read_u32, no header; the
// handler keeps nothing (V). PS4 OnPacket_S2C_ENTRY_BOARD_ITEM_RESERVE_NOTICE 0x323ca0 {u16 error,
// u32 m_unNowMember, u32 m_unMaxMember}: match I (among the 22 PS4 entry-board packets only
// RESERVE_NOTICE has the body {u32, u32}; no behaviour to compare). Names I by that match.
// The PS4 framing fits 1/1 too (slack 15): the PC reader decides. Walk: 1/1 fit; (1, 1).
// Body: u32 NowMember, u32 MaxMember (8 bytes, no RES header).
// packet-id: 34.16.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_RESERVE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // Notice: the PC reader reads no RES header (T013 0).
    u32 NowMember;   // I: unique {u32, u32} shape in the PS4 group (T013 8)
    u32 MaxMember;   // I: as NowMember
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ENTRY_BOARD_ENTRY_BOARD_ITEM_RESERVE_NTC packet @ 0x00;
