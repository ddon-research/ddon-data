// 11.117.16 S2C_QUEST_11_117_16_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 38 (section 44 for the shared types in include/Quest.hexpat).
// Code name REWARD_BOX_LIST_NUM_NOTICE (V by behaviour): PC handler 0x7f4e10, reader 0x818760:
// u16, u16, u8 (no header); stores the u8 and adds chat message 0xCA when non-zero under a GUI
// flag, as PS4 OnPacket_S2C_REWARD_BOX_LIST_NUM_NOTICE 0x312390 {u16 m_usError, u8
// m_ucListNum}. Season 3 adds the two u16 and fill-level announcements (0x12C when the first
// >= the second, 0x12D at 80 %). Walk: 47/47 fit, slack 2; the PS4 body (u8 only) fits too, so
// the two u16 rest on the code.
// Body: u16 unk_u16_0, u16 unk_u16_1, u8 ListNum (5 bytes).
// packet-id: 11.117.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_11_117_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u16 unk_u16_0;   // Season 3; compared against unk_u16_1 (>= and >= 80 %): a count, I
    u16 unk_u16_1;   // Season 3; the limit of that comparison: a capacity, I
    u8 ListNum;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_11_117_16_NTC packet @ 0x00;
