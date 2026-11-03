// 72.1.16 S2C_DAILY_MISSION_ACHIEVE_NTC (client 03040008).
// Raw and JSON files keep the CLI name S2C_DAILY_72_1_16_NTC; this pattern carries the better name (G (context; value: every listed mission goes from State 1 to State 2 in the 72.0.2 lists around it, 113/113)).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 72.1.16.
// PC handler 0x7d1760 (no OnPacket_ string): Read_CDataCommonU32_ list; sets an sGUI flag, requests
// information 35, passes the first element to 0x581230 and adds GUI message 0x3e to the chat (V).
// PS4 counterpart: none (Season 3 group).
// Walk: 64/64 fit, slack 3-15; 1-4 ids.
// Body: list CDataCommonU32.
// packet-id: 72.1.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_DAILY_MISSION_ACHIEVE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T004 I (value, 10 distinct: 113/113 are MissionIds of 72.0.2 whose State is 1 in the list before and 2 in the
    // list after (or no later list))
    MtTypedArray<CDataCommonU32> MissionIdList;     // PC 0x75e8e0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_DAILY_MISSION_ACHIEVE_NTC packet @ 0x00;
