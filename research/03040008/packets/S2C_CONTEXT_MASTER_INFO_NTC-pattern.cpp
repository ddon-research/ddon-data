// 35.15.16 S2C_CONTEXT_MASTER_INFO_NTC (client 03040008).
// Body: u32 count, CDataMasterInfo[count]. P4 2.3 (PC handler 0x7cfc80, reader 0x76ec20).
// packet-id: 35.15.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
#pragma endian big

import std.mem;

#include "Context.hexpat"

struct S2C_CONTEXT_MASTER_INFO_NTC : CPacket {
    MasterInfoList m_MasterInfoList;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_CONTEXT_MASTER_INFO_NTC packet @ 0x00;
