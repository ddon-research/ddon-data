// 58.8.2 S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 4.6.
// PC handler 0x7e9de0, reader 0x811ab0: RES header, u32, list 0x769100 (Instance.hexpat
// CDataGatheringItemElement, Season 3 17 bytes) (V). PS4 OnPacket_GET_REWARD_DROP_ITEM_LIST_RES
// 0x339b40: u32 m_unPawnRewardBoxId, MtTypedArray<CDataGatheringItemElement> m_GatheringItemList (V).
// Season 3: the element (the PS4 element fails 10/50). Walk: 50/50 fit, slack 2-7.
// Body: s32 Error [, s32 Result, u32 PawnRewardBoxId, list CDataGatheringItemElement] (16 + 17n bytes).
// packet-id: 58.8.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 PawnRewardBoxId;
        MtTypedArray<CDataGatheringItemElement> GatheringItemList;  // PC 0x769100
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_LIST_RES packet @ 0x00;
