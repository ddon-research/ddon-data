// 13.20.1 C2S_INSTANCE_SET_OM_INSTANT_KEY_VALUE_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 11 (section 20 for the shared types in include/Instance.hexpat).
// PC writer 0x82c460 (13, 20, 1): Write_u64, Write_u32 (V). PS4
// Send_C2S_SET_OM_INSTANT_KEY_VALUE_REQ 0x19bb710 {u32 m_ulKey, u32 m_ulValue} (V). Season 3:
// Key is u64 (V). Walk: 542/542 fit, slack 11.
// Body: CDataOmData Data = u64 Key, u32 Value (12 bytes).
// packet-id: 13.20.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_INSTANCE_SET_OM_INSTANT_KEY_VALUE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    CDataOmData Data;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_INSTANCE_SET_OM_INSTANT_KEY_VALUE_REQ packet @ 0x00;
