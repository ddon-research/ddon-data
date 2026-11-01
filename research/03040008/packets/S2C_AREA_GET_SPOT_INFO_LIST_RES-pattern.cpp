// 23.11.2 S2C_AREA_GET_SPOT_INFO_LIST_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 11. PC handler 0x7c46b0
// (string 0x1bcdb28), ctor 0x785e70, reader 0x800150: RES, list CDataSpotInfo (0x779cf0), list
// {u32, u32, s64} (0x7696e0), list {u32, bool, s64} (0x76d440), list u32 (0x75e8e0) (V). PS4
// OnPacket_S2C_GET_SPOT_INFO_LIST_RES 0x303540 (and the PS4 recompilation, UserSession/S2C.h) has
// only the first list: the three trailing lists are Season 3, the same readers as 23.8.2 lists 2
// and 3 (P11a 15). Fixed: the earlier `u32 Unknown1` is the count of list 0x7696e0; its {u32, bool,
// u64} list is s64; the trailing u32 list was missing (P11b G7: lists 2 and 4 are empty in every
// capture).
// Body: s32 Error [, s32 Result, four lists] (P11a G1).
// packet-id: 23.11.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Area.hexpat"

struct S2C_AREA_GET_SPOT_INFO_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        MtTypedArray<CDataSpotInfo> SpotInfoList;             // PC 0x779cf0
        MtTypedArray<CDataAreaUnkU32U32S64> unk_list_0;      // PC 0x7696e0, Season 3
        MtTypedArray<CDataAreaUnkU32BoolS64> unk_list_1;     // PC 0x76d440, Season 3
        MtTypedArray<CDataCommonU32> unk_list_2;             // PC 0x75e8e0, Season 3
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_AREA_GET_SPOT_INFO_LIST_RES packet @ 0x00;
