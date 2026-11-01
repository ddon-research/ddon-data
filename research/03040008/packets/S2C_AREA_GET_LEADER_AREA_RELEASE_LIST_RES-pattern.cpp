// 23.8.2 S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11a-old-patterns.md section 15. PC handler 0x7c4600
// (string 0x1bcda00), ctor 0x785dd0 (23, 8, 2), reader 0x8000b0 (V). PS4 counterpart by code:
// OnPacket_S2C_GET_LEADER_AREA_RELEASE_LIST_RES 0x3030a0, which reads only the first list
// (CDataReleaseAreaInfoSet); the two trailing lists are Season 3.
// Body: s32 Error [, s32 Result, three lists] (P11a G1).
// packet-id: 23.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Area.hexpat"

struct S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataReleaseAreaInfoSet> ReleaseAreaInfoSetList;   // PC 0x776890
        MtTypedArray<CDataAreaUnkU32U32S64> unk_list_0;                // PC 0x7696e0, Season 3
        MtTypedArray<CDataAreaUnkU32BoolS64> unk_list_1;               // PC 0x76d440, Season 3
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_AREA_GET_LEADER_AREA_RELEASE_LIST_RES packet @ 0x00;
