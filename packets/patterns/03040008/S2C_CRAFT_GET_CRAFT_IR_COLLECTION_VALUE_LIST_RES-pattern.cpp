// 30.15.2 S2C_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T013-small-groups.md
// section 3 (1 and 16 for the types).
// PC handler 0x7d0850 -> 0x8059b0: header, list 0x7610f0 (CDataCraftSkillRate) (V). PS4 0x3346f0 reads
// inline {m_usError, s32, Read_CDataCraftSkillRate_} into a local array (no member name).
// Walk: 2/2 fit; 10 rates.
// Body: s32 Error [, s32 Result, list CDataCraftSkillRate].
// packet-id: 30.15.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Craft.hexpat"

struct S2C_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataCraftSkillRate> unk_RateList;   // PC 0x7610f0; I: the PS4 reader keeps it in a local
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CRAFT_GET_CRAFT_IR_COLLECTION_VALUE_LIST_RES packet @ 0x00;
