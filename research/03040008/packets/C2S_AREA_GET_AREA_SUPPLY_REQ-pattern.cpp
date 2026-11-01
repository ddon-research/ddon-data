// 23.4.1 C2S_AREA_GET_AREA_SUPPLY_REQ (client 03040008).
// Evidence: specs/005-netmsg-patterns/research/P11b-old-patterns.md section 9. PC writer 0x81e760:
// WritePacket(0x17, 4, 1, -1), Write_u32, Write_u8, list writer 0x780ea0 (u32 count, {u32, u8})
// (V). PS4 CPacket_C2S_GET_AREA_SUPPLY_REQ::WritePacket 0x1a34990: u32, u8, u32 count, {u32, u8} (V
// PS4).
// Body: u32 AreaID, u8 StorageType, list CDataSelectItemInfo.
// packet-id: 23.4.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Area.hexpat"

struct C2S_AREA_GET_AREA_SUPPLY_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 AreaID;
    u8 StorageType;
    MtTypedArray<CDataSelectItemInfo> SelectItemInfoList;   // PC 0x780ea0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_AREA_GET_AREA_SUPPLY_REQ packet @ 0x00;
