// 11.83.16 S2C_QUEST_11_83_16_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T005-quest.md
// section 31 (section 44 for the shared types in include/Quest.hexpat).
// Code name SET_QUEST_UNRELEASED_AREA_NOTICE (V): PC handler 0x7f56d0, reader 0x818c90 = list
// u32 0x75e8e0 (no header), pushes cQuestSvNotSetQuestUnreleasedArea (dti__1524); PS4's only
// user of that class is OnPacket_S2C_SET_QUEST_UNRELEASED_AREA_NOTICE 0x2ea270 {u16 m_usError,
// MtTypedArray<CDataCommonU32> m_AreaIdList}. Walk: 20/20 fit, slack 15; PS4 framing 0/20.
// Body: MtTypedArray<CDataCommonU32> AreaIdList (4 + 4n bytes).
// packet-id: 11.83.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Quest.hexpat"

struct S2C_QUEST_11_83_16_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    MtTypedArray<CDataCommonU32> AreaIdList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_QUEST_11_83_16_NTC packet @ 0x00;
