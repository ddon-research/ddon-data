// 13.20.16 S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T004-instance.md
// section 11 (section 20 for the shared types in include/Instance.hexpat).
// PC handler 0x7dc160, reader 0x80bb10: u32, u64, u32, no error header (V); then one COmData
// callback (sub_BBF470, a protected thunk). Settled V by behaviour as PS4
// S2C_SET_OM_INSTANT_KEY_VALUE_NOTICE (OnPacket 0x2f65b0 -> sOmManager::callBackInsSync); DWARF
// {u16 m_usError, u32 m_unStageId, COmData m_Value}, the u16 is PS4 NTC framing. The triage
// candidate GP_COURSE_START_NTC is rejected (C). Walk: 571/571 fit, slack 7; the u32 key fits
// too (slack 11): the u64 rests on the PC reader and the RES.
// Body: u32 StageId, CDataOmData Value (16 bytes).
// packet-id: 13.20.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 StageId;
    CDataOmData Value;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_INSTANCE_SET_OM_INSTANT_KEY_VALUE_NTC packet @ 0x00;
