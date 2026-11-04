// 11.5.1 C2S_QUEST_GET_PACKAGE_QUEST_LIST_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T003-batches-B5-B2.md § 11.5.1.
// 006 T005 § 7. PC writer 0x837fc0: WritePacket(11, 5, 1), Write_u32 (V). PS4 counterpart: none (V: no
// PACKAGE_QUEST symbol, string or type).
// Walk: 146/146 fit, slack 3.
// Body: u32.
// packet-id: 11.5.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_QUEST_GET_PACKAGE_QUEST_LIST_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T003 open, kept unk: echoed in 146/146 responses (11.5.2 unk_u32); 27 distinct values (200 x52,
    // 210 x27, 211 x20, ...); not the package ids of package_quest_info.pqi (1-3) and not the NpcID of
    // the preceding 60.0.1 (0/105); server: Unk0 (lead)
    u32 unk_u32;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_QUEST_GET_PACKAGE_QUEST_LIST_REQ packet @ 0x00;
