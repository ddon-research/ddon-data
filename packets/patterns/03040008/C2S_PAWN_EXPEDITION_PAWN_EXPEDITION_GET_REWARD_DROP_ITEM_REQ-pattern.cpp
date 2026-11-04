// 58.9.1 C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_REQ (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 4.7.
// PC writer 0x832b10 (58, 9, 1): u32, list writer 0x77f9d0 {u32, u32} (Instance.hexpat
// CDataGatheringItemGetRequest) (V). PS4 CPacket_C2S_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_REQ::
// WritePacket 0x1a32010: u32 m_unPawnRewardBoxId, m_GatheringItemGetRequestList (V).
// Walk: 25/25 fit, slack 7-15.
// Body: u32 PawnRewardBoxId, list CDataGatheringItemGetRequest (8 + 8n bytes).
// packet-id: 58.9.1
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Instance.hexpat"

struct C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_REQ : CPacket {
    bool sourceOk = source == 0x00 [[export]];  // header source byte: 0x00 client (Packet.hexpat)
    u32 PawnRewardBoxId;
    MtTypedArray<CDataGatheringItemGetRequest> GatheringItemGetRequestList;  // PC 0x77f9d0
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

C2S_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_ITEM_REQ packet @ 0x00;
