// 29.17.16 S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T012-achievement-equip-skill.md
// section 14.
// PC handler 0x7d4470, reader 0x807830: Read_u32, Read_u8, list 0x765fb0, list 0x765fb0 (Season 3
// CDataEquipItemInfo, include/Login.hexpat) (V); the consumer checks sAreaExt::isLobby. PS4
// OnPacket_S2C_CHANGE_CHARACTER_EQUIP_LOBBY_NOTICE 0x310870 -> ReadPacket 0x19d89c0: u16 error, u32
// m_unCharacterID, u8 m_ucJob, m_EquipItemList, m_VisualEquipItemList: match V (shape + lobby). No
// error header: the PC reader reads none (V); the PS4 framing fails 23/23, the PS4 element 23/23.
// Walk: 23/23 fit, slack 1-15; both lists 15 entries; Job 1/2/6/8/9/11.
// Body: u32 CharacterID, u8 Job, 2 x list CDataEquipItemInfo (Season 3).
// packet-id: 29.17.16
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "Login.hexpat"

struct S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    u32 CharacterID;
    u8 Job;
    MtTypedArray<CDataEquipItemInfo> EquipItemList;         // PC 0x765fb0 (Login.hexpat)
    MtTypedArray<CDataEquipItemInfo> VisualEquipItemList;   // PC 0x765fb0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_EQUIP_CHANGE_CHARACTER_EQUIP_LOBBY_NTC packet @ 0x00;
