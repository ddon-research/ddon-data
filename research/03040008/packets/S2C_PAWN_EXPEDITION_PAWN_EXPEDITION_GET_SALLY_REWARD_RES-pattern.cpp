// 58.5.2 S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T007-pawn-partner.md
// section 4.4.
// PC handler 0x7ea150, reader 0x811d40: RES header, 0x7595a0 {u32, u32}, u8, list 0x759f80 (read
// linearly: u32 count, Read_u32 x3 per element), bool, bool (V). PS4
// CPacket_S2C_PAWN_EXPEDITION_GET_SALLY_REWARD_RES::ReadPacket 0x19e0390 (and the recompilation,
// S2C.cpp:8724): CAreaSpotSet m_SallySpotInfo, u8 m_ucSearchSpotType, CBattleResultInfo m_BattleResult,
// b8 m_bIsGoldenSally (V). Season 3: BattleResult becomes a list and a bool is appended (V by code;
// every captured list holds 1 element, so the PS4 body fits too). Which bool is IsGoldenSally is I
// (position: the first, as in PS4). Walk: 25/25 fit, slack 4.
// Body: s32 Error [, s32 Result, CDataAreaSpotSet, u8, list CDataBattleResultInfo, bool, bool] (23 + 12n bytes).
// packet-id: 58.5.2
// Fit flag `fits`: the raws store no body length, so a decode fits when it ends within the
// last 15 bytes of the file (cipher block padding); reading past the end fails the decode.
// A fit does not prove field widths: when the slack (`paddingSize`, exported) exceeds a field, a
// body that is that field shorter or longer fits too; such widths rest on the PC code (R1 F3).
#pragma endian big

import std.mem;

#include "Packet.hexpat"
#include "PawnExpedition.hexpat"

struct S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        CDataAreaSpotSet SallySpotInfo;                         // PC 0x7595a0
        u8 SearchSpotType;
        MtTypedArray<CDataBattleResultInfo> BattleResultList;  // Season 3 list (PS4 one m_BattleResult), PC 0x759f80
        bool IsGoldenSally;                                     // I (position)
        bool unk_bool;                                          // Season 3, no PS4 member
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_PAWN_EXPEDITION_PAWN_EXPEDITION_GET_SALLY_REWARD_RES packet @ 0x00;
