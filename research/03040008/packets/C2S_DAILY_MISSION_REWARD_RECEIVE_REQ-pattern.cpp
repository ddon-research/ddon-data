// 72.2.1 C2S_DAILY_MISSION_REWARD_RECEIVE_REQ (client 03040008).
// Evidence: specs/008-remaining-packets/research/T004-batches-B1-B4.md § 72.2.1.
// PC writer 0x826180 cSeedGameSvConnection::Send_C2S_DAILY_MISSION_REWARD_RECEIVE_REQ (V name):
// WritePacket(0x48, 2, 1), list writer 0x77df90 {Write_u32 of element +4}, Write_u8 (V). 008 T001's
// width_seq `77df90{4 4}` counted the list count as an element field: the element is one u32 (V).
// No server structure. PS4 counterpart: none (Season 3 group).
// Walk: 8/8 fit, slack 14; 1 id in 8/8.
// Body: list CDataCommonU32, u8.
// packet-id: 72.2.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct C2S_DAILY_MISSION_REWARD_RECEIVE_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    // T004 I (value: 8/8 are MissionIds of 72.0.2 whose State is 2 before and 3 after)
    MtTypedArray<CDataCommonU32> MissionIdList;     // PC 0x77df90
    // T004 I (value: 19 (6), 20 (1), 13 (1): the server StorageType values ReceiveInItemBagCraft,
    // ReceiveInStorageCraft and ItemPost, the three destinations of the gmd prompt
    // daily_mission_get_reward_bag/storage/post)
    u8 StorageType;
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_DAILY_MISSION_REWARD_RECEIVE_REQ packet @ 0x00;
