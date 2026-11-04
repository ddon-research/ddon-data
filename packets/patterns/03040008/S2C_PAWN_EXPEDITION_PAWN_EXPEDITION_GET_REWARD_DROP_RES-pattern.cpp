// 58.7.2 S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 4.5.
// PC handler 0x7e9fe0, reader 0x811be0: RES header, u32, list 0x75e8e0 (CDataCommonU32), list 0x75e9b0
// (CDataCommonU8) (V). PS4 GET_REWARD_DROP_RES::ReadPacket 0x19e0470: u32 m_unRewardDropNum,
// m_BoxIdVec, m_MdlTypeVec (V). No Season 3 change. Walk: 25/25 fit, slack 14.
// Body: s32 Error [, s32 Result, u32 RewardDropNum, list CDataCommonU32, list CDataCommonU8].
// packet-id: 58.7.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 RewardDropNum;
        MtTypedArray<CDataCommonU32> BoxIdVec;                 // PC 0x75e8e0
        MtTypedArray<CDataCommonU8> MdlTypeVec;                // PC 0x75e9b0
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_REWARD_DROP_RES packet @ 0x00;
