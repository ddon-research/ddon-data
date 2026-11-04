// 13.23.1 C2S_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 13 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x82bb40 (13, 23, 1): u64, u32 (V). PS4 Send_C2S_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ
// 0x19bb9a0 {COmData m_Data} (V). Season 3: Key is u64. Walk: 44/44 fit, slack 11.
// Body: CDataOmData Data (12 bytes).
// packet-id: 13.23.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataOmData Data;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_EXCHANGE_OM_INSTANT_KEY_VALUE_REQ packet @ 0x00;
