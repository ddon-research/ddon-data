// 23.13.16 S2C_AREA_POINT_UP_NTC (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 7. PC handler
// sub_7c38c0 (group-23 handler table, key 16/13; 23, 13, 16), reader 0x7ffa60: u32 x5, bool (V).
// PS4 match by code: CPacket_S2C_AREA_POINT_UP_NTC::ReadPacket 0x19da9f0 reads u16 + 5 x u32 +
// bool; DWARF names m_unAreaID, m_unAddPoint, m_unAddPointByCharge, m_unTotalPoint, m_unWeekPoint,
// m_bCanRankUp (V PS4). The PC handler looks the area up by AreaID, prints AddPoint and
// AddPointByCharge into message 0xB6 and stores the rest (V). The PS4 recompilation has no class
// for it. The earlier pattern (S2C_AREA_23_13_16_NTC) read only AreaId and AreaPoints (= AddPoint)
// and still "fit" (P11b G7: 13 bytes short, inside the slack).
// Body (NTC, no error field): u32 AreaID, u32 AddPoint, u32 AddPointByCharge, u32 TotalPoint,
// u32 WeekPoint, bool CanRankUp.
// packet-id: 23.13.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_AREA_POINT_UP_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 AreaID;
    u32 AddPoint;
    u32 AddPointByCharge;
    u32 TotalPoint;
    u32 WeekPoint;
    bool CanRankUp;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_AREA_POINT_UP_NTC packet @ 0x00;
