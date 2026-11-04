// 11.68.16 S2C_QUEST_QUEST_BOARD_RELOAD_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.68.16.
// 006 T005 § 28. PC handler 0x7f2be0 (no name string): packet object (11, 68, 16), reader 0x8175d0: bool,
// bool, u32 (V), no RES header. If the first bool is set it adds chat message 0x132; if the second is set,
// chat message 0x133 with %d of the u32 (V). PS4 counterpart: none found (I). Name: the raw name (server
// lead), G (lead).
// Walk: 1/1 fit, slack 1: {1, 1, 1}.
// Body: bool, bool, u32.
// packet-id: 11.68.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_QUEST_QUEST_BOARD_RELOAD_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T003 V (role: set -> chat message 0x132); name open, kept unk; server: Unk0 (lead)
    bool unk_bool_0;
    // T003 V (role: set -> chat message 0x133 with %d of Count); name open, kept unk; server: Unk1 (lead)
    bool unk_bool_1;
    // T003 V (role: the %d of chat message 0x133); I (name; lead Count agrees)
    u32 Count;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_QUEST_BOARD_RELOAD_NTC packet @ 0x00;
