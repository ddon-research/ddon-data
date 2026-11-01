// 10.9.2 S2C_ITEM_GET_ITEM_STORAGE_INFO_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 13. PC handler 0x7dd070
// (string 0x1bd1f24), ctor 0x789240, reader 0x80c420; list reader 0x7688e0 {u8, u16, u16} (V). PS4
// OnPacket_S2C_GET_ITEM_STORAGE_INFO_RES 0x3336a0: u16, s32, Read_CDataGameItemStorageInfo_ (V
// PS4); PS4 recompilation (UserSession/S2C.h) {u16 m_usError, s32 m_nResult,
// MtTypedArray<CDataGameItemStorageInfo>}.
// Body: s32 Error [, s32 Result, list CDataGameItemStorageInfo] (P11a G1).
// packet-id: 10.9.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Item.hexpat"

struct S2C_ITEM_GET_ITEM_STORAGE_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataGameItemStorageInfo> GameItemStorageInfoList;   // PC 0x7688e0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_ITEM_GET_ITEM_STORAGE_INFO_RES packet @ 0x00;
