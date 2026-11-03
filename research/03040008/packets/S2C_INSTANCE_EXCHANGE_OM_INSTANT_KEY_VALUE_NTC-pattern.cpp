// 13.23.16 S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC (client 03040008).
// Evidence: specs/008-remaining-packets/research/T005-batches-B3-B7-B6.md § 13.23.16.
// PC handler 0x7db000 (no OnPacket_ string; name G (lead)), reader 0x80af70: Read_u32, Read_u64,
// Read_u32, Read_u32 (V): the body of the 13.23.2 RES after its header.
// PS4 counterpart: none matched (spec 006 T004 § 13).
// Walk: 46/46 fit, slack 3.
// Body: u32, CDataOmData, u32.
// packet-id: 13.23.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Instance.hexpat"

struct S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    // T005 I (same structure: 13.23.2's StageId; value, 5 distinct, chance 0.28: 46/46 a stage_list.slt StageId, e.g. 655, 347
    // "Clan Hall"); server: StageId (lead agrees)
    u32 StageId;
    CDataOmData Value;  // T005 I (same structure: 13.23.2's CDataOmData {u64 Key, u32 Value}); server: Key, Value (lead agrees)
    // T005 I (same structure: 13.23.2's ValueOld; value, 25 distinct: 25/35 equal the Value the previous 13.23.16 of the
    // stream set for the same (StageId, Key)); server: OldValue (lead agrees)
    u32 ValueOld;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_NTC packet @ 0x00;
