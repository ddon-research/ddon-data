// 23.3.2 S2C_AREA_GET_AREA_SUPPLY_INFO_RES (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 10. PC handler code
// 0x7c44c0 (group-23 table key 2/3) calls ctor 0x785d70 (23, 3, 2) and reader 0x7fff90 (V). PS4
// OnPacket_S2C_GET_AREA_SUPPLY_INFO_RES 0x302af0: u16, s32, u8, Read_CDataRewardItemInfo_ (V PS4);
// PS4 recompilation (UserSession/S2C.h) {u16 m_usError, s32 m_nResult, u8 m_ucSupplyGrade,
// MtTypedArray<CDataRewardItemInfo>}.
// Body: s32 Error [, s32 Result, u8 SupplyGrade, list CDataRewardItemInfo] (P11a G1).
// packet-id: 23.3.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Area.hexpat"

struct S2C_AREA_GET_AREA_SUPPLY_INFO_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u8 SupplyGrade;
        MtTypedArray<CDataRewardItemInfo> RewardItemInfoList;   // PC 0x7773b0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_AREA_GET_AREA_SUPPLY_INFO_RES packet @ 0x00;
